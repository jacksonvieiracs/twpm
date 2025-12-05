import asyncio

from nodes import DisplayMessageNode, PoolNode, QuestionNode, SummaryNode

from twpm.core import Chain, Orchestrator
from twpm.core.base.node import Node
from twpm.core.container import Container, ServiceScope
from twpm.core.depedencies import Output


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
    def send_text(self, text: str):
        print(text, end=" ")


async def main():
    chain = create_chain()
    container = Container()
    container.register(Output, lambda: ConsoleOutput(), ServiceScope.SINGLETON)
    orchestrator = Orchestrator(container)
    orchestrator.start(chain)

    await orchestrator.process()

    while not orchestrator.is_ended:
        user_input = await asyncio.to_thread(input, ">> ")
        user_input = user_input.strip()
        await orchestrator.process(input=user_input)


if __name__ == "__main__":
    asyncio.run(main())
