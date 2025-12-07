import argparse
import asyncio

from twpm.core import Chain, Orchestrator
from twpm.core.base import ListData
from twpm.core.base.node import Node
from twpm.core.container import Container, ServiceScope
from twpm.core.depedencies import Output
from twpm.core.primitives import (
    ConditionalNode,
    DisplayMessageNode,
    PoolNode,
    QuestionNode,
    QuizNode,
    QuizSummaryNode,
    SummaryNode,
)


def create_chain() -> Node:
    welcome_node = DisplayMessageNode(
        message="=== Bem-vindo ao configurador! ===", key="welcome"
    )

    name_node = QuestionNode(question="Seu nome", key="user_name")

    company_node = QuestionNode(question="Nome da sua empresa", key="company_name")

    employees_node = QuestionNode(
        question="Total de funcionários", key="total_employees"
    )

    company_type_node = PoolNode(
        question="Tipo de empresa",
        options=["Petshop", "Hospital veterinário", "Clínica veterinária", "Outro"],
        key="company_type",
    )

    final_node = SummaryNode(
        title="Obrigado, em breve vamos entrar em contato!",
        fields=[
            ("Nome", "user_name"),
            ("Empresa", "company_name"),
            ("Funcionários", "total_employees"),
            ("Tipo", "company_type"),
        ],
        key="summary",
    )

    progress_fields = [
        ("Seu nome", "user_name"),
        ("Nome da empresa", "company_name"),
        ("Total de funcionários", "total_employees"),
        ("Tipo de empresa", "company_type"),
    ]

    return (
        Chain()
        .add(welcome_node)
        .add_section([name_node, company_node, employees_node, company_type_node])
        .with_progress(
            fields=progress_fields,
            after_each=(QuestionNode, PoolNode),
        )
        .add(final_node)
        .build()
    )


class ConsoleOutput:
    async def send_text(self, text: str):
        print(text, end=" ")


def create_quiz_chain() -> Node:
    """Create a quiz chain with 5 questions and conditional final message."""
    welcome_node = DisplayMessageNode(
        message="=== Bem-vindo ao Quiz! ===", key="quiz_welcome"
    )

    quiz1 = QuizNode(
        question="Quanto é 15 + 27?",
        options=["40", "42", "43", "45"],
        expected_answer="42",
        key="quiz1",
    )

    quiz2 = QuizNode(
        question="Qual filme ganhou o Oscar de Melhor Filme em 2020?",
        options=["1917", "Parasita", "Joker", "Coringa"],
        expected_answer="Parasita",
        key="quiz2",
    )

    quiz3 = QuizNode(
        question="Qual é a raiz quadrada de 144?",
        options=["10", "11", "12", "13"],
        expected_answer="12",
        key="quiz3",
    )

    quiz4 = QuizNode(
        question="Em que ano foi lançado o filme 'Matrix'?",
        options=["1997", "1999", "2001", "2003"],
        expected_answer="1999",
        key="quiz4",
    )

    quiz5 = QuizNode(
        question="Quanto é 8 × 7?",
        options=["54", "56", "58", "60"],
        expected_answer="56",
        key="quiz5",
    )

    quiz_summary = QuizSummaryNode(
        title="=== Resultado do Quiz ===",
        quiz_keys=["quiz1", "quiz2", "quiz3", "quiz4", "quiz5"],
        key="quiz_summary",
    )

    condition_node = ConditionalNode()

    success_message = DisplayMessageNode(
        message="\n🎉 Parabéns! Você acertou todas as respostas! 🎉",
        key="success_message",
    )

    almost_message = DisplayMessageNode(
        message="\nVocê quase conseguiu! Continue praticando e você vai melhorar! 💪",
        key="almost_message",
    )

    def check_all_correct(data: ListData) -> bool:
        score = int(data.get("quiz_summary_score", "0"))
        total = int(data.get("quiz_summary_total", "5"))
        return score == total

    condition_node.set_condition(check_all_correct, success_message, almost_message)

    return (
        Chain()
        .add(welcome_node)
        .add_section([quiz1, quiz2, quiz3, quiz4, quiz5])
        .add(quiz_summary)
        .add(condition_node)
        .build()
    )


async def main():
    parser = argparse.ArgumentParser(description="CLI Example with Quiz")
    parser.add_argument(
        "--quiz",
        action="store_true",
        help="Run quiz workflow instead of normal workflow",
    )
    args = parser.parse_args()

    if args.quiz:
        chain = create_quiz_chain()
    else:
        chain = create_chain()

    container = Container()
    container.register(Output, lambda: ConsoleOutput(), ServiceScope.SINGLETON)
    orchestrator = Orchestrator(container)
    orchestrator.start("test-session", chain)

    await orchestrator.process()

    while not orchestrator.is_finished:
        user_input = await asyncio.to_thread(input, ">> ")
        user_input = user_input.strip()
        await orchestrator.process(input=user_input)


if __name__ == "__main__":
    asyncio.run(main())
