from fastapi import Request, APIRouter

from langchain_classic.agents import AgentExecutor
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_classic.agents.react.agent import create_react_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import create_retriever_tool
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_pinecone import PineconeVectorStore
import os


router = APIRouter(tags=["Questions"], prefix="/question")


@router.post("/")
async def ask_question(request: Request):
    data = await request.json()
    user_query = data.get("question")
    embeddings_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001",
                                                    output_dimensionality=1536,
                                                    google_api_key=os.environ.get("GOOGLE_API_KEY"))
    vector_store = PineconeVectorStore(embedding=embeddings_model, index_name=os.environ.get("INDEX_NAME"))
    retriever_object = vector_store.as_retriever(search_kwargs={"k": 3})

    retriever_tool = create_retriever_tool(retriever_object, "clini_clarity_docs",
                                           "Search for information within the patient's specific medical report. Use this first!")
    tavily_search = TavilySearchResults(max_results=3, include_domains=["pubmed.ncbi.nlm.nih.gov"])
    tools = [retriever_tool, tavily_search]

    model = ChatGoogleGenerativeAI(model="gemini-3-flash-preview", temperature=0.0)
    react_prompt = ChatPromptTemplate.from_template("""
        Answer the following questions as best as you can. 
        IMPORTANT GOAL: You are a patient advocate. Your final answer must be written at a 6th-grade reading level. 
        Explain any complex medical terms using simple, everyday language.

        You have access to following tools: {tools}

        Use the following format:
        Question: The input question you must answer
        Thought: You should always think about what to do
        Action: The action to take, should be one of [{tool_names}]
        Action Input: The input to the action
        Observation: The result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: The final answer to the original input question.

        Begin!
        Question: {input}
        Thought: {agent_scratchpad}
        """)
    agent = create_react_agent(llm=model, tools=tools, prompt=react_prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
    result = agent_executor.invoke(input={"input": user_query})
    return {"answer": result['output']}