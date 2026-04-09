from __future__ import annotations

from app.agents import (
    CadastroAgent,
    DevotionalAgent,
    EngagementAgent,
    OrchestratorAgent,
    RAGAgent,
    SecretaryAgent,
    WelcomeAgent,
)
from app.config import Settings
from app.db import InteractionRepository, KnowledgeBaseRepository, MemberRepository, MongoManager
from app.rag import EmbeddingService, RAGService
from app.services.communication_service import CommunicationService
from app.services.devotional_service import DevotionalService
from app.services.interaction_service import InteractionService
from app.services.llm_service import LLMService
from app.services.member_service import MemberService
from app.services.orchestrator_service import OrchestratorService
from app.services.unit_resolver_service import UnitResolverService


class ServiceContainer:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.mongo = MongoManager(settings)

        self.member_repository = MemberRepository(self.mongo.database, settings)
        self.knowledge_repository = KnowledgeBaseRepository(self.mongo.database, settings)
        self.interaction_repository = InteractionRepository(self.mongo.database, settings)

        self.llm_service = LLMService(settings)
        self.embedding_service = EmbeddingService(settings)
        self.rag_service = RAGService(
            settings=settings,
            repository=self.knowledge_repository,
            embedding_service=self.embedding_service,
        )
        self.communication_service = CommunicationService()
        self.unit_resolver_service = UnitResolverService()
        self.interaction_service = InteractionService(
            interaction_repository=self.interaction_repository,
            member_repository=self.member_repository,
        )

        self.orchestrator_agent = OrchestratorAgent(
            llm_service=self.llm_service,
            member_repository=self.member_repository,
            rag_service=self.rag_service,
        )
        self.cadastro_agent = CadastroAgent(self.llm_service)
        self.welcome_agent = WelcomeAgent(self.llm_service)
        self.devotional_agent = DevotionalAgent(self.llm_service)
        self.rag_agent = RAGAgent(rag_service=self.rag_service, llm_service=self.llm_service)
        self.engagement_agent = EngagementAgent(
            llm_service=self.llm_service,
            interaction_repository=self.interaction_repository,
        )
        self.secretary_agent = SecretaryAgent(self.llm_service)

        self.member_service = MemberService(
            member_repository=self.member_repository,
            welcome_agent=self.welcome_agent,
            communication_service=self.communication_service,
            interaction_service=self.interaction_service,
        )
        self.devotional_service = DevotionalService(
            devotional_agent=self.devotional_agent,
            member_repository=self.member_repository,
            communication_service=self.communication_service,
            interaction_service=self.interaction_service,
        )
        self.orchestrator_service = OrchestratorService(
            orchestrator_agent=self.orchestrator_agent,
            cadastro_agent=self.cadastro_agent,
            welcome_agent=self.welcome_agent,
            devotional_agent=self.devotional_agent,
            rag_agent=self.rag_agent,
            engagement_agent=self.engagement_agent,
            secretary_agent=self.secretary_agent,
        )

    async def startup(self) -> None:
        await self.mongo.ping()

    async def shutdown(self) -> None:
        await self.mongo.close()
