from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from datetime import timedelta
from pathlib import Path
from typing import Any

from joblib import dump
from sklearn.cluster import MiniBatchKMeans
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sqlalchemy.orm import Session

from app.config import settings
from app.models import InteractionLog, Member


class CommunityMLService:
    channel_pattern = re.compile(r"\[channel:([^\]]+)\]")
    topic_interactions = {"inbound_message"}
    outgoing_interactions = {"good_news", "weekly_devotional", "inbound_reply"}

    def __init__(self):
        self.artifacts_dir = Path(settings.ml_artifacts_dir)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.topic_vectorizer_path = self.artifacts_dir / "topic_vectorizer.joblib"
        self.topic_model_path = self.artifacts_dir / "topic_model.joblib"
        self.eng_vectorizer_path = self.artifacts_dir / "engagement_vectorizer.joblib"
        self.eng_model_path = self.artifacts_dir / "engagement_model.joblib"
        self.profiles_path = self.artifacts_dir / "member_profiles.json"
        self.metadata_path = self.artifacts_dir / "metadata.json"

    def _extract_channel(self, content: str) -> str:
        match = self.channel_pattern.search(content or "")
        if not match:
            return "whatsapp"
        channel = match.group(1).strip().lower()
        return channel if channel in {"sms", "whatsapp"} else "whatsapp"

    def _time_bucket(self, hour: int) -> str:
        if 5 <= hour <= 11:
            return "morning"
        if 12 <= hour <= 17:
            return "afternoon"
        return "evening"

    def _has_response_within_window(self, sent_at, incoming_times: list) -> bool:
        deadline = sent_at + timedelta(hours=settings.ml_response_window_hours)
        for ts in incoming_times:
            if sent_at < ts <= deadline:
                return True
        return False

    def _load_profiles(self) -> dict[str, Any]:
        if not self.profiles_path.exists():
            return {}
        try:
            return json.loads(self.profiles_path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def get_member_profile(self, member_id: int) -> dict[str, Any] | None:
        profiles = self._load_profiles()
        return profiles.get(str(member_id))

    def recommended_channel(self, member: Member) -> str | None:
        profile = self.get_member_profile(member.id)
        if not profile:
            return None
        channel = (profile.get("recommended_channel") or "").lower()
        return channel if channel in {"sms", "whatsapp"} else None

    def communication_hint(self, member: Member) -> str | None:
        profile = self.get_member_profile(member.id)
        if not profile:
            return None
        keywords = profile.get("topic_keywords") or []
        keyword_text = ", ".join(keywords[:3]) if keywords else "comunhao, oracao, Palavra"
        style_hint = profile.get("style_hint") or "tom acolhedor e objetivo"
        engagement = profile.get("engagement_score", 0.5)
        return (
            f"Insight de ML: interesse provavel em [{keyword_text}]. "
            f"Engajamento previsto={engagement:.2f}. "
            f"Estilo recomendado: {style_hint}."
        )

    def _build_style_hint(self, age_group: str, engagement_score: float, keywords: list[str]) -> str:
        keyword_line = ", ".join(keywords[:3]) if keywords else "fe, oracao, comunhao"
        if age_group == "youth":
            base = "mensagens curtas, dinamicas e com convite pratico"
        elif age_group == "senior":
            base = "mensagens respeitosas, claras e afetuosas"
        else:
            base = "mensagens objetivas, acolhedoras e aplicaveis ao dia a dia"

        if engagement_score < 0.35:
            cadence = "inclua pergunta aberta e incentivo para resposta"
        elif engagement_score > 0.7:
            cadence = "inclua chamada para servir e compartilhar testemunho"
        else:
            cadence = "inclua encorajamento simples e versiculo pratico"
        return f"{base}; foco tematico: {keyword_line}; estrategia: {cadence}"

    def _train_topics(self, logs: list[InteractionLog]) -> tuple[dict[int, int], dict[int, list[str]], dict[str, Any]]:
        texts: list[str] = []
        member_ids: list[int] = []

        for log in logs:
            if not log.member_id:
                continue
            if (log.content or "").strip():
                texts.append(log.content.strip())
                member_ids.append(log.member_id)

        if len(texts) < settings.ml_min_topic_samples:
            return {}, {}, {"topic_model_trained": False, "topic_samples": len(texts)}

        max_clusters = max(2, settings.ml_max_topic_clusters)
        n_clusters = min(max_clusters, max(2, int(round(math.sqrt(len(texts))))))

        vectorizer = TfidfVectorizer(max_features=500, ngram_range=(1, 2))
        matrix = vectorizer.fit_transform(texts)
        kmeans = MiniBatchKMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
        labels = kmeans.fit_predict(matrix)

        dump(vectorizer, self.topic_vectorizer_path)
        dump(kmeans, self.topic_model_path)

        cluster_votes: dict[int, Counter] = defaultdict(Counter)
        for member_id, label in zip(member_ids, labels):
            cluster_votes[member_id][int(label)] += 1

        dominant_topic = {member_id: votes.most_common(1)[0][0] for member_id, votes in cluster_votes.items()}

        terms = vectorizer.get_feature_names_out()
        sorted_terms = kmeans.cluster_centers_.argsort()[:, ::-1]
        cluster_keywords = {
            int(cluster_id): [terms[idx] for idx in sorted_terms[cluster_id, :5]]
            for cluster_id in range(n_clusters)
        }

        summary = {
            "topic_model_trained": True,
            "topic_samples": len(texts),
            "topic_clusters": n_clusters,
        }
        return dominant_topic, cluster_keywords, summary

    def _engagement_features(self, member: Member, interaction_type: str, channel: str, hour: int, weekday: int) -> dict[str, Any]:
        return {
            "age_group": member.age_group or "adult",
            "interaction_type": interaction_type,
            "channel": channel,
            "weekday": weekday,
            "time_bucket": self._time_bucket(hour),
        }

    def _train_engagement(
        self,
        members_by_id: dict[int, Member],
        outgoing_logs: list[InteractionLog],
        incoming_times: dict[int, list],
    ) -> tuple[DictVectorizer | None, LogisticRegression | None, dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        labels: list[int] = []

        for log in outgoing_logs:
            if not log.member_id:
                continue
            member = members_by_id.get(log.member_id)
            if not member:
                continue
            channel = self._extract_channel(log.content)
            response = self._has_response_within_window(log.created_at, incoming_times.get(log.member_id, []))
            rows.append(
                self._engagement_features(
                    member=member,
                    interaction_type=log.interaction_type,
                    channel=channel,
                    hour=log.created_at.hour,
                    weekday=log.created_at.weekday(),
                )
            )
            labels.append(1 if response else 0)

        if len(rows) < settings.ml_min_engagement_samples or len(set(labels)) < 2:
            return None, None, {"engagement_model_trained": False, "engagement_samples": len(rows)}

        vectorizer = DictVectorizer(sparse=True)
        matrix = vectorizer.fit_transform(rows)
        model = LogisticRegression(max_iter=400, class_weight="balanced")
        model.fit(matrix, labels)

        dump(vectorizer, self.eng_vectorizer_path)
        dump(model, self.eng_model_path)

        summary = {
            "engagement_model_trained": True,
            "engagement_samples": len(rows),
            "positive_rate": round(sum(labels) / len(labels), 4),
        }
        return vectorizer, model, summary

    def _predict_engagement(
        self,
        vectorizer: DictVectorizer | None,
        model: LogisticRegression | None,
        member: Member,
        interaction_type: str,
        channel: str,
        hour: int,
        weekday: int,
    ) -> float:
        if not vectorizer or not model:
            return 0.5
        row = self._engagement_features(member, interaction_type, channel, hour, weekday)
        matrix = vectorizer.transform([row])
        return float(model.predict_proba(matrix)[0][1])

    def train(self, db: Session) -> dict[str, Any]:
        members = db.query(Member).all()
        members_by_id = {m.id: m for m in members}

        inbound_logs = (
            db.query(InteractionLog)
            .filter(InteractionLog.direction == "incoming")
            .filter(InteractionLog.interaction_type.in_(self.topic_interactions))
            .all()
        )
        outgoing_logs = (
            db.query(InteractionLog)
            .filter(InteractionLog.direction == "outgoing")
            .filter(InteractionLog.interaction_type.in_(self.outgoing_interactions))
            .all()
        )

        incoming_times: dict[int, list] = defaultdict(list)
        for log in inbound_logs:
            if log.member_id:
                incoming_times[log.member_id].append(log.created_at)
        for member_id in incoming_times:
            incoming_times[member_id].sort()

        dominant_topic, cluster_keywords, topic_summary = self._train_topics(inbound_logs)
        eng_vectorizer, eng_model, eng_summary = self._train_engagement(
            members_by_id=members_by_id,
            outgoing_logs=outgoing_logs,
            incoming_times=incoming_times,
        )

        profiles: dict[str, Any] = {}
        for member in members:
            topic_id = dominant_topic.get(member.id)
            topic_words = cluster_keywords.get(topic_id, [])

            score_whatsapp = self._predict_engagement(
                vectorizer=eng_vectorizer,
                model=eng_model,
                member=member,
                interaction_type="weekly_devotional",
                channel="whatsapp",
                hour=settings.weekly_whatsapp_devotional_hour,
                weekday=0,
            )
            score_sms = self._predict_engagement(
                vectorizer=eng_vectorizer,
                model=eng_model,
                member=member,
                interaction_type="weekly_devotional",
                channel="sms",
                hour=settings.weekly_message_hour,
                weekday=0,
            )

            recommended_channel = "whatsapp" if score_whatsapp >= score_sms else "sms"
            engagement_score = max(score_whatsapp, score_sms)

            member_hours = [ts.hour for ts in incoming_times.get(member.id, [])]
            preferred_hour = Counter(member_hours).most_common(1)[0][0] if member_hours else settings.weekly_message_hour

            profiles[str(member.id)] = {
                "member_id": member.id,
                "age_group": member.age_group,
                "topic_cluster": topic_id,
                "topic_keywords": topic_words,
                "engagement_score": round(engagement_score, 4),
                "recommended_channel": recommended_channel,
                "preferred_send_hour": int(preferred_hour),
                "style_hint": self._build_style_hint(member.age_group or "adult", engagement_score, topic_words),
            }

        self.profiles_path.write_text(json.dumps(profiles, indent=2), encoding="utf-8")
        metadata = {
            "members_profiled": len(profiles),
            "topic_summary": topic_summary,
            "engagement_summary": eng_summary,
        }
        self.metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        return metadata

    def summary(self, db: Session) -> dict[str, Any]:
        profiles = self._load_profiles()
        if not profiles:
            return {
                "trained": False,
                "members_profiled": 0,
                "message": "Nenhum perfil de ML encontrado. Rode POST /ml/train.",
            }

        channel_counter = Counter()
        topic_counter = Counter()
        age_counter = Counter()

        for profile in profiles.values():
            channel_counter[profile.get("recommended_channel") or "unknown"] += 1
            topic_counter[str(profile.get("topic_cluster"))] += 1
            age_counter[profile.get("age_group") or "unknown"] += 1

        return {
            "trained": True,
            "members_profiled": len(profiles),
            "recommended_channel_distribution": dict(channel_counter),
            "topic_distribution": dict(topic_counter),
            "age_group_distribution": dict(age_counter),
            "active_members": db.query(Member).filter(Member.is_active.is_(True)).count(),
        }
