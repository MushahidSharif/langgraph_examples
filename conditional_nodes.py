
from typing import TypedDict # Imports all the data types we need
from langgraph.graph import StateGraph, START, END

class AgentState(TypedDict):
    number1: int
    operation: str
    number2: int
    op_result: int


class ConditionalNodesGraph():
    def __init__(self):
        pass

    def adder(self, state: AgentState) -> AgentState:
        """This node adds the 2 numbers"""
        state["op_result"] = state["number1"] + state["number2"]

        return state

    def multiplier(self, state: AgentState) -> AgentState:
        """This node multiplies the 2 numbers"""
        state["op_result"] = state["number1"] * state["number2"]
        return state

    def find_next_node(self, state: AgentState) -> str:
        """This node will find out which node wil be next to process"""

        if state["operation"] == "+":
            return "addition_operation"

        elif state["operation"] == "*":
            return "subtraction_operation"

        else:
            return END

    def run_graph(self):
        graph = StateGraph(AgentState)

        graph.add_node("add_node", self.adder)
        graph.add_node("subtract_node", self.multiplier)
        graph.add_node("router", lambda state: state)  # passthrough function

        graph.add_edge(START, "router")

        graph.add_conditional_edges(
            "router",
            self.find_next_node,
            {
                # Edge: Node
                "addition_operation": "add_node",
                "subtraction_operation": "subtract_node",
                END:END
            }

        )

        graph.add_edge("add_node", END)
        graph.add_edge("subtract_node", END)

        app = graph.compile()
        print(app.get_graph().draw_ascii())

        initial_state_1 = AgentState(number1=20, operation="*", number2=10)
        result = app.invoke(initial_state_1)
        print(result)



if __name__ == "__main__":
    g = ConditionalNodesGraph()
    g.run_graph()






