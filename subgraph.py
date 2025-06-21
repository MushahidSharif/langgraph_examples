"""
This code demonstates how to create subgraphs in LangGraph. It creates two graphs. One generate key points from a given topic and the other generates
questions from the same topic. two subgraphs are then combined into a parent graph which runs both subgraphs in parallel.
"""

import operator
from langgraph.graph import add_messages, StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from typing import List,  TypedDict, Annotated
import dotenv

# A sample topic about Apple Inc copied from Wikipedia.
datatopic = """
Apple Inc. is an American multinational corporation and technology company headquartered in Cupertino, California, in Silicon Valley. It is best known for its consumer electronics, software, 
and services. Founded in 1976 as Apple Computer Company by Steve Jobs, Steve Wozniak and Ronald Wayne, the company was incorporated by Jobs and Wozniak as Apple Computer, 
Inc. the following year. It was renamed Apple Inc. in 2007 as the company had expanded its focus from computers to consumer electronics. 
Apple is the largest technology company by revenue, with US$391.04 billion in the 2024 fiscal year.
The company was founded to produce and market Wozniak's Apple I personal computer. Its second computer, the Apple II, became a best seller as one of the 
first mass-produced microcomputers. Apple introduced the Lisa in 1983 and the Macintosh in 1984, as some of the first computers to use a 
graphical user interface and a mouse. By 1985, internal company problems led to Jobs leaving to form NeXT, and Wozniak 
withdrawing to other ventures; John Sculley served as long-time CEO for over a decade. In the 1990s, Apple lost considerable market share in the 
personal computer industry to the lower-priced Wintel duopoly of the Microsoft Windows operating system on Intel-powered PC clones. 
In 1997, Apple was weeks away from bankruptcy. To resolve its failed operating system strategy, it bought NeXT, effectively bringing 
Jobs back to the company, who guided Apple back to profitability over the next decade with the introductions of the iMac, iPod, iPhone, 
and iPad devices to critical acclaim as well as the iTunes Store, launching the "Think different" advertising campaign, and opening the Apple Store 
retail chain. These moves elevated Apple to consistently be one of the world's most valuable brands since about 2010. Jobs resigned in 2011 
for health reasons, and died two months later; he was succeeded as CEO by Tim Cook.
Apple's product lineup includes portable and home hardware such as the iPhone, iPad, Apple Watch, Mac, and Apple TV; operating
systems such as iOS, iPadOS, and macOS; and various software and services including Apple Pay, iCloud, and multimedia streaming services like 
Apple Music and Apple TV+. Apple is one of the Big Five American information technology companies;[a] for the most part since 2011,[b] Apple has been 
the world's largest company by market capitalization, and, as of 2023, is the largest manufacturing company by revenue, 
the fourth-largest personal computer vendor by unit sales, the largest vendor of tablet computers, and the largest vendor of mobile phones in the world. 
Apple became the first publicly traded U.S. company to be valued at over $1 trillion in 2018, and, as of December 2024, is valued at 
just over $3.74 trillion. Apple is the largest company on the Nasdaq, where it trades under the ticker symbol "AAPL".  
"""

# The structure of the State schema for the subgraphs and parent graph.
class KeyPointsState(TypedDict):
    # we do not need to concatenate topic but it is used in both subgraph which run in parallel so without this it will give error.
    # another workaround is to use a different key for topic in both subgraphs or we can use different input and output schema with no topic key in output schema.
    topic: Annotated[str, operator.add]
    keypoints:  str

class QuestionsState(TypedDict):
    topic: Annotated[str, operator.add]
    questions:  str

class MainGraphState(TypedDict):
    topic: Annotated[str, operator.add]
    keypoints: str
    questions: str


def get_llm_model():
    # uncomment this line if you want to use OpenAI server/model and comment out the next line
    # llm = ChatOpenAI(model_name="gpt-4o")

    # We are using github models for testing as they are free and available for testing purpose. Github access token is required to be used as API key.
    # Access token should have read access to the models.

    llm = ChatOpenAI(model="openai/gpt-4o", base_url="https://models.github.ai/inference/")
    return llm

def generate_keypoints(state: KeyPointsState) -> KeyPointsState:
    """
    A node which generates key points from a given topic.
    """
    llm = get_llm_model()
    topic = state["topic"]
    llm_messages = [
        SystemMessage(content='You are a helpful assistant. Please generate a five key points from the given text.'),
        HumanMessage(content=topic)
    ]

    result = llm.invoke(llm_messages)
    return {
        "topic": topic,
        "keypoints": result.content
    }

def generate_question(state: QuestionsState) -> QuestionsState:
    """
    A node which generates questions from a given topic.
    """
    llm = get_llm_model()

    topic = state["topic"]
    llm_messages = [
        SystemMessage(content='You are a helpful assistant. Please generate a five questions from the given text.'),
        HumanMessage(content=topic)
    ]
    result = llm.invoke(llm_messages)
    return {
        "topic": topic,
        "questions": result.content
    }


def get_keypoints_subgraph():
    graph = StateGraph(KeyPointsState)
    graph.add_node("generate_keypoints", generate_keypoints)
    graph.set_entry_point("generate_keypoints")
    graph.add_edge("generate_keypoints", END)

    app = graph.compile()
    return app

def get_questions_subgraph():
    graph = StateGraph(QuestionsState)
    graph.add_node("generate_question", generate_question)
    graph.set_entry_point("generate_question")
    graph.add_edge("generate_question", END)

    app = graph.compile()
    return app

def run_keypoints_subgraph():
    """
    Sample function to run and test the keypoints subgraph.
    """
    app = get_keypoints_subgraph()
    result = app.invoke({"topic": datatopic })
    print(result['keypoints'])

def run_questions_subgraph():
    """
    Sample function to run and test the questions subgraph.
    """
    app = get_questions_subgraph()
    result = app.invoke({"topic": datatopic })
    print(result['questions'])


def get_topic(state: MainGraphState):
    """
    An entry node for the parent graph which gets the topic from the state and return it to be passed to the subgraphs.
    """

    topic = state["topic"]
    return {"topic": topic}

def run_parent_graph():

    kp_subgraph = get_keypoints_subgraph()
    ques_subgraph = get_questions_subgraph()

    main_graph = StateGraph(MainGraphState)
    main_graph.add_node("get_topic", get_topic)
    main_graph.add_node("kp_subgraph", kp_subgraph)
    main_graph.add_node("ques_subgraph", ques_subgraph)

    main_graph.add_edge(START, "get_topic")
    main_graph.add_edge("get_topic", "kp_subgraph")
    main_graph.add_edge("get_topic", "ques_subgraph")
    main_graph.add_edge("kp_subgraph", END)
    main_graph.add_edge("ques_subgraph", END)

    main_app = main_graph.compile()
    print(main_app.get_graph().draw_ascii())

    result = main_app.invoke({"topic":datatopic})
    print(result['keypoints'])
    print(result['questions'])


if __name__ == '__main__':
    dotenv.load_dotenv()
    #run_questions_subgraph()
    #run_keypoints_subgraph()
    run_parent_graph()