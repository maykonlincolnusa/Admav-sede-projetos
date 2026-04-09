from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from app.agents import (
    AgentState,
    CadastroAgent,
    DevotionalAgent,
    EngagementAgent,
    OrchestratorAgent,
    RAGAgent,
    SecretaryAgent,
    WelcomeAgent,
)


class OrchestratorService:
    def __init__(
        self,
        *,
        orchestrator_agent: OrchestratorAgent,
        cadastro_agent: CadastroAgent,
        welcome_agent: WelcomeAgent,
        devotional_agent: DevotionalAgent,
        rag_agent: RAGAgent,
        engagement_agent: EngagementAgent,
        secretary_agent: SecretaryAgent,
    ) -> None:
        self._graph = self._build_graph(
            orchestrator_agent=orchestrator_agent,
            cadastro_agent=cadastro_agent,
            welcome_agent=welcome_agent,
            devotional_agent=devotional_agent,
            rag_agent=rag_agent,
            engagement_agent=engagement_agent,
            secretary_agent=secretary_agent,
        )

    async def route(self, state: AgentState) -> AgentState:
        return await self._graph.ainvoke(state)

    def _build_graph(
        self,
        *,
        orchestrator_agent: OrchestratorAgent,
        cadastro_agent: CadastroAgent,
        welcome_agent: WelcomeAgent,
        devotional_agent: DevotionalAgent,
        rag_agent: RAGAgent,
        engagement_agent: EngagementAgent,
        secretary_agent: SecretaryAgent,
    ):
        graph = StateGraph(AgentState)
        graph.add_node("orchestrator", orchestrator_agent)
        graph.add_node("cadastro", cadastro_agent)
        graph.add_node("welcome", welcome_agent)
        graph.add_node("devotional", devotional_agent)
        graph.add_node("rag", rag_agent)
        graph.add_node("engagement", engagement_agent)
        graph.add_node("secretary", secretary_agent)

        graph.add_edge(START, "orchestrator")
        graph.add_conditional_edges(
            "orchestrator",
            self._select_route,
            {
                "cadastro": "cadastro",
                "welcome": "welcome",
                "devotional": "devotional",
                "rag": "rag",
                "engagement": "engagement",
                "secretary": "secretary",
            },
        )
        for node_name in ("cadastro", "welcome", "devotional", "rag", "engagement", "secretary"):
            graph.add_edge(node_name, END)
        return graph.compile()

    @staticmethod
    def _select_route(state: AgentState) -> str:
        return state.get("intent", "rag")
