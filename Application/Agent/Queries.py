import ssl, certifi, os

os.environ["SSL_CERT_FILE"] = certifi.where() # Set environment variable to use certifi certificates
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where() # Set environment variable to use certifi certificates
ssl_context = ssl.create_default_context(cafile=certifi.where())


from langchain_classic import hub
from dotenv import load_dotenv
from langchain_core.tools import create_retriever_tool
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_tavily import TavilySearch
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from langchain_classic.agents import create_react_agent, AgentExecutor
from Agent.Prompts import Query_Prompt

load_dotenv()

embedding_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", output_dimensionality=1536, google_api_key=os.environ.get("GOOGLE_API_KEY"))
vector_database = PineconeVectorStore(embedding=embedding_model, index_name=os.environ.get("INDEX_NAME"))

retriever = vector_database.as_retriever(search_kwargs={'k': 5})
retriever_tool = create_retriever_tool(retriever=retriever,
                                       name='clini_clarity_documents',
                                       description="Search for information within the patient's specific medical report. Use this first!")
tavily_search = TavilySearch(max_results=3, include_domains=['pubmed.ncbi.nlm.nih.gov'])

tools = [retriever_tool, tavily_search]


custom_instructions = """You are a Compassionate Patient Advocate. 
Your final answer MUST be at a 6th-grade reading level. 
Explain complex medical terms simply. 
"""


async def ask_question(query:str, model: str, provider: str):
    prompt_template = ChatPromptTemplate.from_template(template=Query_Prompt.query_prompt).partial(tools=tools, system_prompt=custom_instructions)
    dynamic_model = init_chat_model(model=model, model_provider=provider, temperature=0.0, streaming=True)
    agent = create_react_agent(llm=dynamic_model, tools=tools, prompt=prompt_template)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True, max_iterations=10)


    is_final_answer = False
    buffer = ""

    async for event in agent_executor.astream_events(input={"input": query}, version="v2"):
        kind = event["event"]
        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content

            chunk_str = ""
            if isinstance(content, str):
                chunk_str = content
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and "text" in item:
                        chunk_str += item["text"]
                    elif isinstance(item, str):
                        chunk_str += item

            if chunk_str:
                if not is_final_answer:
                    buffer += chunk_str
                    if "Final Answer:" in buffer:
                        is_final_answer = True
                        text_to_yield = buffer.split("Final Answer:")[-1].lstrip()
                        if text_to_yield: yield text_to_yield
                else:
                    yield chunk_str