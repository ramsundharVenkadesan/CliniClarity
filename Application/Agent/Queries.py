from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_tavily import TavilySearch
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.tools import create_retriever_tool
from langchain_core.prompts import ChatPromptTemplate
import os


load_dotenv()

embedding_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", output_dimensionality=1536, google_api_key=os.environ.get("GOOGLE_API_KEY"))
vector_database = PineconeVectorStore(embedding=embedding_model, index_name=os.environ.get("INDEX_NAME"))
retriever = vector_database.as_retriever(search_kwargs={'k': 5})
retriever_tool = create_retriever_tool(retriever=retriever,
                                       name='clini_clarity_documents',
                                       description="Search for information within the patient's specific medical report. Use this first!")
tavily_search = TavilySearch(max_results=3, include_domains=['pubmed.ncbi.nlm.nih.gov'])

tools = [retriever_tool, tavily_search]

model = init_chat_model(model="gemini-3-flash-preview", model_provider="google_genai", temperature=0.0)
prompt = """
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
"""

async def ask_question(query:str):
    prompt_template = ChatPromptTemplate.from_template(template=prompt).partial(tools=tools)
    agent = create_react_agent(llm=model, tools=tools, prompt=prompt_template)
    agent_execution = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
    result = await agent_execution.ainvoke(input={"input": query})
    return result['output']



