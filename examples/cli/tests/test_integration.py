import pytest
from nodes import DisplayMessageNode, PoolNode, QuestionNode

from twpm.core.orchestrator import Orchestrator


@pytest.mark.asyncio
class TestIntegration:
    """Integration tests for node chains."""

    async def test_complete_workflow_execution(self):
        # Arrange
        welcome = DisplayMessageNode(message="Welcome!", key="welcome")
        name_q = QuestionNode(question="Name", key="name")
        color_q = PoolNode(
            question="Favorite color", options=["Red", "Blue", "Green"], key="color"
        )
        goodbye = DisplayMessageNode(message="Goodbye!", key="goodbye")

        welcome.next = name_q
        name_q.next = color_q
        color_q.next = goodbye

        orch = Orchestrator()
        orch.start(welcome)

        # Act
        await orch.process()
        await orch.process(input="Alice")
        await orch.process(input="2")
        await orch.process()

        # Assert
        assert orch.is_ended
        assert orch._data["name"] == "Alice"
        assert orch._data["color"] == "Blue"

    async def test_sequential_question_nodes(self):
        # Arrange
        name_q = QuestionNode(question="Name", key="name")
        age_q = QuestionNode(question="Age", key="age")
        city_q = QuestionNode(question="City", key="city")

        name_q.next = age_q
        age_q.next = city_q

        orch = Orchestrator()
        orch.start(name_q)

        # Act
        await orch.process()
        await orch.process(input="Bob")
        await orch.process(input="30")
        await orch.process(input="NYC")

        # Assert
        assert orch.is_ended
        assert orch._data["name"] == "Bob"
        assert orch._data["age"] == "30"
        assert orch._data["city"] == "NYC"

    async def test_mixed_node_types_chain(self):
        # Arrange
        msg1 = DisplayMessageNode(message="Start", key="start")
        question = QuestionNode(question="Name", key="name")
        pool = PoolNode(question="Option", options=["A", "B"], key="choice")
        msg2 = DisplayMessageNode(message="End", key="end")

        msg1.next = question
        question.next = pool
        pool.next = msg2

        orch = Orchestrator()
        orch.start(msg1)

        # Act
        await orch.process()
        await orch.process(input="Test")
        await orch.process(input="1")
        await orch.process()

        # Assert
        assert orch.is_ended
        assert orch._data["name"] == "Test"
        assert orch._data["choice"] == "A"
