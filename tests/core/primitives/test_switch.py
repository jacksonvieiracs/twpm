import pytest

from twpm.core.base import ListData, NodeResult, NodeStatus
from twpm.core.primitives.switch import SwitchNode
from twpm.core.primitives.task import TaskNode


@pytest.fixture
async def dummy_task():
    """Fixture providing a simple task function."""

    async def task(data: ListData) -> bool:
        return True

    return task


@pytest.fixture
def create_nodes(dummy_task):
    """Fixture to create commonly used test nodes."""

    def _create_nodes(*keys):
        return {key: TaskNode(dummy_task, key=key) for key in keys}

    return _create_nodes


def create_switch_node(switch_func, case_nodes, default_node):
    """Helper to create and configure a SwitchNode."""
    node = SwitchNode()
    node.set_switch(switch_func, case_nodes, default_node)
    return node


@pytest.mark.asyncio
class TestSwitchNode:
    """Test suite for SwitchNode."""

    async def test_switch_node_initial_state(self):
        """Test switch node initial state."""
        switch_node = SwitchNode()

        assert switch_node.switch_func is None
        assert switch_node.case_nodes == {}
        assert switch_node.default_node is None
        assert switch_node.status == NodeStatus.DEFAULT

    async def test_switch_node_case_match(self, create_nodes):
        """Test switch node routes to matching case."""
        nodes = create_nodes("case_a", "case_b", "default")

        def switch_to_a(data: ListData) -> str:
            return "a"

        switch_node = create_switch_node(
            switch_to_a, {"a": nodes["case_a"], "b": nodes["case_b"]}, nodes["default"]
        )

        result = await switch_node.execute(ListData(data={}))

        assert result.success is True
        assert switch_node.next == nodes["case_a"]

    async def test_switch_node_default_case(self, create_nodes):
        """Test switch node routes to default when no case matches."""
        nodes = create_nodes("case_a", "case_b", "default")

        def switch_to_unknown(data: ListData) -> str:
            return "unknown"

        switch_node = create_switch_node(
            switch_to_unknown,
            {"a": nodes["case_a"], "b": nodes["case_b"]},
            nodes["default"],
        )

        result = await switch_node.execute(ListData(data={}))

        assert result.success is True
        assert switch_node.next == nodes["default"]

    async def test_switch_node_multiple_cases(self, create_nodes):
        """Test switch node with multiple cases."""
        nodes = create_nodes("case_a", "case_b", "case_c", "default")

        def switch_to_c(data: ListData) -> str:
            return "c"

        switch_node = create_switch_node(
            switch_to_c,
            {"a": nodes["case_a"], "b": nodes["case_b"], "c": nodes["case_c"]},
            nodes["default"],
        )

        result = await switch_node.execute(ListData(data={}))

        assert result.success is True
        assert switch_node.next == nodes["case_c"]

    @pytest.mark.parametrize(
        "status,expected_key",
        [
            ("success", "case_success"),
            ("failure", "case_failure"),
            (None, "default"),
        ],
    )
    async def test_switch_node_with_data_based_switch(
        self, create_nodes, status, expected_key
    ):
        """Test switch node with data-based switch function."""
        nodes = create_nodes("case_success", "case_failure", "default")

        def data_switch(data: ListData) -> str:
            status = data.get("status")
            return status if status else "unknown"

        switch_node = create_switch_node(
            data_switch,
            {"success": nodes["case_success"], "failure": nodes["case_failure"]},
            nodes["default"],
        )

        data = ListData(data={"status": status} if status else {})
        await switch_node.execute(data)

        assert switch_node.next == nodes[expected_key]

    async def test_switch_node_without_switch_func_raises_error(self):
        """Test that executing without setting switch function returns failed result."""
        switch_node = SwitchNode()
        result = await switch_node.execute(ListData(data={}))

        assert result.success is False
        assert "Condition function is not set" in result.message

    async def test_set_switch_updates_properties(self, create_nodes):
        """Test that set_switch properly updates all properties."""
        nodes = create_nodes("case_a", "default")

        def switch_func(data: ListData) -> str:
            return "a"

        switch_node = SwitchNode()
        switch_node.set_switch(switch_func, {"a": nodes["case_a"]}, nodes["default"])

        assert switch_node.switch_func == switch_func
        assert switch_node.case_nodes == {"a": nodes["case_a"]}
        assert switch_node.default_node == nodes["default"]

    async def test_switch_node_returns_success(self, create_nodes):
        """Test that switch node always returns success when properly configured."""
        nodes = create_nodes("case_a", "default")

        def switch_func(data: ListData) -> str:
            return "a"

        switch_node = create_switch_node(
            switch_func, {"a": nodes["case_a"]}, nodes["default"]
        )

        result = await switch_node.execute(ListData(data={}))

        assert result.success is True
        assert isinstance(result, NodeResult)

    async def test_switch_node_returns_empty_data(self, create_nodes):
        """Test that switch node returns empty data."""
        nodes = create_nodes("case_a", "default")

        def switch_func(data: ListData) -> str:
            return "a"

        switch_node = create_switch_node(
            switch_func, {"a": nodes["case_a"]}, nodes["default"]
        )

        result = await switch_node.execute(ListData(data={}))

        assert result.data == {}
        assert result.message == ""

    @pytest.mark.parametrize(
        "score,expected_key",
        [
            ("20", "case_low"),
            ("50", "case_medium"),
            ("90", "case_high"),
            (None, "default"),
        ],
    )
    async def test_switch_node_complex_switch_logic(
        self, create_nodes, score, expected_key
    ):
        """Test switch node with complex switch logic."""
        nodes = create_nodes("case_low", "case_medium", "case_high", "default")

        def complex_switch(data: ListData) -> str:
            score = data.get("score")
            if not score:
                return "unknown"

            score_int = int(score)
            if score_int < 33:
                return "low"
            elif score_int < 66:
                return "medium"
            else:
                return "high"

        switch_node = create_switch_node(
            complex_switch,
            {
                "low": nodes["case_low"],
                "medium": nodes["case_medium"],
                "high": nodes["case_high"],
            },
            nodes["default"],
        )

        data = ListData(data={"score": score} if score else {})
        await switch_node.execute(data)

        assert switch_node.next == nodes[expected_key]

    @pytest.mark.parametrize(
        "role,expected_key",
        [
            ("admin", "case_admin"),
            ("user", "case_user"),
        ],
    )
    async def test_switch_node_with_string_comparison(
        self, create_nodes, role, expected_key
    ):
        """Test switch node with string-based case matching."""
        nodes = create_nodes("case_admin", "case_user", "case_guest", "default")

        def role_switch(data: ListData) -> str:
            return data.get("role", "unknown")

        switch_node = create_switch_node(
            role_switch,
            {
                "admin": nodes["case_admin"],
                "user": nodes["case_user"],
                "guest": nodes["case_guest"],
            },
            nodes["default"],
        )

        data = ListData(data={"role": role})
        await switch_node.execute(data)

        assert switch_node.next == nodes[expected_key]

    @pytest.mark.parametrize(
        "value,expected_key",
        [
            ("TEST", "default"),
            ("test", "case_lower"),
        ],
    )
    async def test_switch_node_case_sensitive_matching(
        self, create_nodes, value, expected_key
    ):
        """Test that case matching is case-sensitive."""
        nodes = create_nodes("case_lower", "default")

        def case_switch(data: ListData) -> str:
            return data.get("value", "")

        switch_node = create_switch_node(
            case_switch, {"test": nodes["case_lower"]}, nodes["default"]
        )

        data = ListData(data={"value": value})
        result = await switch_node.execute(data)

        assert result.success is True
        assert switch_node.next == nodes[expected_key]

    async def test_switch_node_chaining(self, dummy_task, create_nodes):
        """Test that switch nodes can be part of a chain."""
        nodes = create_nodes("case_a", "default")
        pre_node = TaskNode(dummy_task, key="pre_node")

        def switch_func(data: ListData) -> str:
            return "a"

        switch_node = create_switch_node(
            switch_func, {"a": nodes["case_a"]}, nodes["default"]
        )

        pre_node.next = switch_node
        switch_node.previous = pre_node

        assert pre_node.next == switch_node
        assert switch_node.previous == pre_node

    @pytest.mark.parametrize(
        "chosen_case,expected_chain_keys",
        [
            ("a", ["pre_node", "switch", "case_a", "post_node"]),
            ("b", ["pre_node", "switch", "case_b", "post_node"]),
            ("unknown", ["pre_node", "switch", "default", "post_node"]),
        ],
    )
    async def test_switch_node_inserts_into_existing_chain(
        self, dummy_task, create_nodes, chosen_case, expected_chain_keys
    ):
        """Test that switch node correctly inserts chosen case into existing chain using Cursor.insert."""
        nodes = create_nodes("case_a", "case_b", "default", "post_node")
        pre_node = TaskNode(dummy_task, key="pre_node")

        def switch_func(data: ListData) -> str:
            return data.get("choice", "unknown")

        switch_node = SwitchNode(key="switch")
        switch_node.set_switch(
            switch_func,
            {"a": nodes["case_a"], "b": nodes["case_b"]},
            nodes["default"],
        )

        pre_node.next = switch_node
        switch_node.previous = pre_node
        switch_node.next = nodes["post_node"]
        nodes["post_node"].previous = switch_node

        data = ListData(data={"choice": chosen_case})
        await switch_node.execute(data)

        chain = []
        current = pre_node
        while current is not None:
            chain.append(current.key)
            current = current.next

        assert chain == expected_chain_keys

    async def test_switch_node_empty_case_dict(self, create_nodes):
        """Test switch node with empty case dictionary routes to default."""
        nodes = create_nodes("default")

        def switch_func(data: ListData) -> str:
            return "any_value"

        switch_node = create_switch_node(switch_func, {}, nodes["default"])

        result = await switch_node.execute(ListData(data={}))

        assert result.success is True
        assert switch_node.next == nodes["default"]
