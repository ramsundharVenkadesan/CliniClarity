import ssl, certifi, os

os.environ["SSL_CERT_FILE"] = certifi.where() # Set environment variable to use certifi certificates
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where() # Set environment variable to use certifi certificates
ssl_context = ssl.create_default_context(cafile=certifi.where())

from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_tavily import TavilySearch
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.tools import create_retriever_tool
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableLambda



load_dotenv()

class Sources(BaseModel):
    url:str = Field(description="The url of the source")
    title:str = Field(description="The title of the source")

class AgentResponse(BaseModel):
    sources:List[Sources] = Field(description="The sources used to answer the question", default_factory=list)
    answer:str = Field(description="Agent's answer to the question")

parser = PydanticOutputParser(pydantic_object=AgentResponse)

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

        STRICT FORMATTING AND SOURCING RULES:
        1. Always start with a 'Thought:'.
        2. If you need to use a tool, you MUST use the format:
           Action: [tool name]
           Action Input: [query]
        3. If you do NOT need a tool and have the final answer, jump straight to the Final Answer.
        4. SOURCING YOUR JSON: 
           - If you used the 'tavily_search_results_json' tool, you MUST extract the exact 'url' and 'title' from the Observation and include them in the "sources" JSON array.
           - If you only used the 'clini_clarity_documents' tool, add a source with the url "Patient Medical Report" and the title of the section you found it in.

        Use the following format exactly:
        Question: The input question you must answer
        Thought: You should always think about what to do
        Action: The action to take, should be one of [{tool_names}]
        Action Input: The input to the action
        Observation: The result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: {format_instructions}

        Begin!
        Question: {input}
        Thought: {agent_scratchpad}
"""

async def ask_question(query:str):
    prompt_template = ChatPromptTemplate.from_template(template=prompt).partial(tools=tools, format_instructions=parser.get_format_instructions())
    agent = create_react_agent(llm=model, tools=tools, prompt=prompt_template)
    runtime_environment = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True, max_iterations=10)

    def clean_json_string(text: str):
        # Handle cases where result might not be a string (rare but possible)
        if not isinstance(text, str):
            return str(text)
        return text.replace("```json", "").replace("```", "").strip()

    extract_output = RunnableLambda(lambda result: result['output'])
    parser_output = RunnableLambda(lambda result: parser.parse(clean_json_string(result)))
    agent_execution = runtime_environment | extract_output | parser_output
    result = await agent_execution.ainvoke(input={"input": query})
    return result



