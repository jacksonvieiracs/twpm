import asyncio

from nodes import DisplayMessageNode, PoolNode, QuestionNode, SummaryNode

from midnight.core import Chain, Orchestrator
from midnight.core.base.node import Node


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


async def main():
    chain = create_chain()
    orchestrator = Orchestrator()
    orchestrator.start(chain)

    await orchestrator.process()

    while not orchestrator.is_ended:
        user_input = await asyncio.to_thread(input, ">> ")
        user_input = user_input.strip()
        await orchestrator.process(input=user_input)


if __name__ == "__main__":
    asyncio.run(main())
