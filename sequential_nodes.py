
from typing import TypedDict # Imports all the data types we need
from langgraph.graph import StateGraph


class DataState(TypedDict):
    name: str
    greet: str


def first_node(state: DataState) -> DataState:
    """This is the first node of our sequence"""

    state["greet"] = f"Hi {state["name"]}!"
    return state

def second_node(state: DataState) -> DataState:
    """This is the second node of our sequence"""

    state["greet"] = state["greet"] + " You are welcome here "

    return state

def run_graph():
    """
    This function demonstrate a simple graph with multiple sequential nodes.
    """

    graph = StateGraph(DataState)

    graph.add_node("first_node", first_node)
    graph.add_node("second_node", second_node)

    graph.set_entry_point("first_node")
    graph.add_edge("first_node", "second_node")
    graph.set_finish_point("second_node")
    app = graph.compile()

    print(app.get_graph().draw_ascii())

    result = app.invoke({"name": "john"})
    print(result)

if __name__ == "__main__":
    run_graph()






