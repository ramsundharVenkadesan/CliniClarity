from dotenv import load_dotenv # Import function to load environment variables
from langchain_core.tools import create_retriever_tool # Import function to create a retriever tool
from langchain_google_genai import GoogleGenerativeAIEmbeddings # Import the embeddings model
from langchain_pinecone import PineconeVectorStore # Import Pinecone Vector Database
from langchain_core.prompts import ChatPromptTemplate # Import prompt template class to format prompts
from langchain.chat_models import init_chat_model # Import function to initialize a chat model
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent # Import runtime environment and agent creation function
from Agent.Prompts.Query_Prompt import * # Import prompt string passed to the model
from mcp import StdioServerParameters, ClientSession # Import classes to maintain a session with the MCP server
from langchain_mcp_adapters.tools import load_mcp_tools # Import function to convert MCP tools into LangChain tools
from mcp.client.stdio import stdio_client # Import function to connect to the MCP server
import os # Import package to access OS level tools
from Agent.Security.PromptInjection import is_prompt_injection # Import function to check for prompt injection
from Agent.Logging.CallBack import CallBackHandler # Import class to track model changes
import sys
from pathlib import Path


current_dir = Path(__file__).resolve().parent
pubmed_path = current_dir.parent / "MCP" / "PubMed.py"
load_dotenv() # Invoke function to load API keys

callback_handler = CallBackHandler() # Handler to track LLM changes


embedding_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", output_dimensionality=1536, google_api_key=os.environ.get("GOOGLE_API_KEY")) # Embedding model developed by Google
vector_database = PineconeVectorStore(embedding=embedding_model, index_name=os.environ.get("INDEX_NAME")) # Create an instance representing a Pinecone vector database


custom_instructions = """You are a Compassionate Patient Advocate. 
Your final answer MUST be at a 6th-grade reading level. 
Explain complex medical terms simply. 
""" # Guardrail instructions to ensure output is simple

mcp_server_parameters = StdioServerParameters(command=sys.executable, # Runtime environment of the MCP server
                                              args=[str(pubmed_path)]) # Configuration to find and launch the local PubMed server


async def ask_question(query:str, model: str, provider: str, user_id:str): # Asynchronous function
    is_safe = await is_prompt_injection(query)
    if is_safe:
        yield "Security Alert: This query violates system safety protocols and has been blocked."
        return
    retriever = vector_database.as_retriever(search_kwargs={'k': 5, 'namespace': user_id})  # Retriever object configured to retrieve 5 most relevant documents based on an input query
    retriever_tool = create_retriever_tool(retriever=retriever,  # Wrap the retriever object into an executable tool
                                           name='clini_clarity_documents',  # Equip the tool with a name
                                           description="Search for information within the patient's specific medical report. Use this first!")  # Agent is able to invoke the object as a tool

    async with stdio_client(mcp_server_parameters) as (read, write):
        async with ClientSession(read_stream=read, write_stream=write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            tools.append(retriever_tool)

            prompt = ChatPromptTemplate.from_messages([
                ("system", query_prompt.format(system_prompt=custom_instructions)),
                ("human", "{input}"),
                ('placeholder', "{agent_scratchpad}")
            ])
            dynamic_model = init_chat_model(model=model, model_provider=provider, temperature=0.0, streaming=True)
            agent = create_tool_calling_agent(llm=dynamic_model, tools=tools, prompt=prompt)
            agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True,
                                           max_iterations=10)

            async for event in agent_executor.astream_events(input={"input": query}, version="v2",
                                                             config={"callbacks": [callback_handler]}):
                kind = event["event"]

                if kind == "on_chat_model_stream":
                    chunk = event["data"]["chunk"]

                    if chunk.content and not getattr(chunk, "tool_calls", None):
                        if isinstance(chunk.content, str):
                            yield chunk.content
                        elif isinstance(chunk.content, list):
                            for item in chunk.content:
                                if isinstance(item, dict) and "text" in item:
                                    yield item["text"]
                                elif isinstance(item, str):
                                    yield item