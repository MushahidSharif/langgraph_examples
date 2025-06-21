from typing import TypedDict, Annotated
from langgraph.graph import add_messages, StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool
import dotenv
from langgraph.prebuilt import ToolNode


# Sample FAQ data (replace with a file load or API call as needed)
FAQS = [
    {
        "question": "What is BoostNutri+?",
        "answer": "BoostNutri+ is a plant-based nutritional supplement designed to support energy, immunity, and overall wellness. It combines essential vitamins, minerals, and organic superfoods."
    },
    {
        "question": "What are the key ingredients in BoostNutri+?",
        "answer": "BoostNutri+ contains organic spirulina, ashwagandha, turmeric, green tea extract, Vitamin B12, Vitamin D3, and magnesium."
    },
    {
        "question": "Is BoostNutri+ suitable for vegans?",
        "answer": "Yes, BoostNutri+ is 100% vegan, gluten-free, and non-GMO. It contains no animal-derived ingredients."
    },
    {
        "question": "What package sizes are available for BoostNutri+?",
        "answer": "BoostNutri+ is available in 30-serving (300g), 60-serving (600g), and 90-serving (900g) packages."
    },
    {
        "question": "How much does BoostNutri+ cost?",
        "answer": "The 30-serving package is priced at $29.99, 60-serving at $49.99, and 90-serving at $69.99."
    },
    {
        "question": "How do I use BoostNutri+?",
        "answer": "Mix one scoop (10g) of BoostNutri+ with water, juice, or a smoothie once daily, preferably in the morning."
    },
    {
        "question": "Can children use BoostNutri+?",
        "answer": "BoostNutri+ is formulated for adults. Please consult a pediatrician before giving it to children under 12."
    },
    {
        "question": "Does BoostNutri+ contain caffeine?",
        "answer": "Yes, it contains a small amount of natural caffeine (40mg per serving) from green tea extract."
    },
    {
        "question": "Where is BoostNutri+ manufactured?",
        "answer": "BoostNutri+ is manufactured in the USA in an FDA-registered, GMP-certified facility."
    },
    {
        "question": "How should I store BoostNutri+?",
        "answer": "Store in a cool, dry place away from direct sunlight. Reseal the package tightly after each use."
    }
]


def get_llm_model():
    # uncomment this line if you want to use OpenAI server/model and comment out the next line
    # llm = ChatOpenAI(model_name="gpt-4o")

    # We are using github models for testing as they are free and available for testing purpose. Github access token is required to be used as API key.
    # Access token should have read access to the models.

    llm = ChatOpenAI(model="openai/gpt-4o", base_url="https://models.github.ai/inference/")
    return llm


llm = None
class BasicChatState(TypedDict):
    messages: Annotated[list, add_messages]

def chatbot(state: BasicChatState):
    return {
        "messages": [llm.invoke(state["messages"])]
    }

def run_simple_chatbot(with_memory=False):
    """
    A simple chatbot which just send a message to llm and get answer
    """
    global llm
    llm = get_llm_model()

    graph = StateGraph(BasicChatState)

    graph.add_node("chatbot", chatbot)
    graph.set_entry_point("chatbot")
    graph.add_edge("chatbot", END)

    config = None
    if with_memory:
        memory = MemorySaver()
        app = graph.compile(checkpointer=memory)
        config = {"configurable": {
            "thread_id": 1
        }}
    else:
        app = graph.compile()

    # asc1= app.get_graph().draw_ascii()
    # print(asc1)

    while True:
        user_input = input("User: ")
        if(user_input == "exit"):
            break
        else:
            result = app.invoke({
                "messages": [HumanMessage(content=user_input)]
            }, config=config)

            print(result)


llm_with_tools = None
def chatbot_withtool(state: BasicChatState):
    return {
        "messages": [llm_with_tools.invoke(state["messages"])],
    }

@tool
def get_faq(search_word_list: list[str])-> str:
    """
    Searches FAQs about the BoostNutri+ product that matches one or more keywords in the parameter list.
    search_word_list: list of all words to search in the FAQ answers.
    Returns string with all relevant information
    """
    if len(search_word_list) == 0:
        raise ValueError("Atleast one search word is required.")

    # Normalize search terms (ignore case)
    terms = [term.lower() for term in search_word_list if term]

    matches = []
    for faq in FAQS:
        answer_lower = faq["answer"].lower()
        if any(term in answer_lower for term in terms):
            matches.append(faq["answer"])

    return ''.join(matches) if matches else "No relevant information found."

def tools_router(state: BasicChatState):
    last_message = state["messages"][-1]

    if(hasattr(last_message, "tool_calls") and len(last_message.tool_calls) > 0):
        return "tool_node"
    else:
        return END

def run_chatbot_with_tool():
    """
    A simple chatbot which als uses tools. A function get_faq is used as a tool to get information about a dummy product
    """

    global llm_with_tools

    #search_tool = TavilySearchResults(max_results=2)
    search_tool = get_faq
    tools = [search_tool]

    llm = get_llm_model()

    llm_with_tools = llm.bind_tools(tools=tools)

    tool_node = ToolNode(tools=tools)

    graph = StateGraph(BasicChatState)

    graph.add_node("chatbot", chatbot_withtool)
    graph.add_node("tool_node", tool_node)
    graph.set_entry_point("chatbot")

    graph.add_conditional_edges("chatbot", tools_router)
    graph.add_edge("tool_node", "chatbot")

    app = graph.compile()

    asc1= app.get_graph().draw_ascii()
    print(asc1)

    while True:
        user_input = input("User: ")
        if (user_input =="exit"):
            break
        else:
            result = app.invoke({
                "messages": [HumanMessage(content=user_input)]
            })

            print(result)



if __name__ == '__main__':
    dotenv.load_dotenv()
    #run_simple_chatbot(with_memory=False)
    run_chatbot_with_tool()
