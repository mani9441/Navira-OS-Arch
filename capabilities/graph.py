# capabilities/graph.py

from langgraph.graph import (
    StateGraph,
    END
)

from capabilities.capability_state import (
    CapabilityState
)


def build_capability_graph(
    runtime
):

    graph = StateGraph(
        CapabilityState
    )

    graph.add_node(
        "select_capability",
        runtime.select_capability
    )

    graph.add_node(
        "resolve_inputs",
        runtime.resolve_inputs
    )

    graph.add_node(
        "validate_inputs",
        runtime.validate_inputs
    )

    graph.add_node(
        "human_input",
        runtime.human_input
    )

    graph.add_node(
        "execute_capability",
        runtime.execute_capability
    )

    graph.set_entry_point(
        "select_capability"
    )

    graph.add_edge(
        "select_capability",
        "resolve_inputs"
    )

    graph.add_edge(
        "resolve_inputs",
        "validate_inputs"
    )

    graph.add_conditional_edges(
        "validate_inputs",
        runtime.route_validation,
        {
            "human":
                "human_input",

            "execute":
                "execute_capability"
        }
    )

    graph.add_edge(
        "human_input",
        END
    )

    graph.add_edge(
        "execute_capability",
        END
    )

    return graph.compile()