from dotenv import load_dotenv
from langchain_core.tools import create_retriever_tool
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore

from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from Agent.Prompts import Query_Prompt
from mcp import StdioServerParameters, ClientSession
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp.client.stdio import stdio_client
import os
from Agent.Quality.PromptInjection import is_prompt_injection

load_dotenv()



embedding_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", output_dimensionality=1536, google_api_key=os.environ.get("GOOGLE_API_KEY"))
vector_database = PineconeVectorStore(embedding=embedding_model, index_name=os.environ.get("INDEX_NAME"))

retriever = vector_database.as_retriever(search_kwargs={'k': 5})
retriever_tool = create_retriever_tool(retriever=retriever,
                                       name='clini_clarity_documents',
                                       description="Search for information within the patient's specific medical report. Use this first!")




custom_instructions = """You are a Compassionate Patient Advocate. 
Your final answer MUST be at a 6th-grade reading level. 
Explain complex medical terms simply. 
"""

mcp_server_parameters = StdioServerParameters(command="/Users/ram/Downloads/CliniGraph/.venv/bin/python",
                                              args=["/Users/ram/Downloads/CliniGraph/Servers/PubMed.py"])


async def ask_question(query:str, model: str, provider: str):
    is_safe = await is_prompt_injection(query)
    if is_safe:
        yield "Security Alert: This query violates system safety protocols and has been blocked."
        return

    async with stdio_client(mcp_server_parameters) as (read, write):
        async with ClientSession(read_stream=read, write_stream=write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            tools.append(retriever_tool)

            prompt = ChatPromptTemplate.from_messages([
                ("system", Query_Prompt.query_prompt.format(system_prompt=custom_instructions)),
                ("human", "{input}"),
                ('placeholder', "{agent_scratchpad}")
            ])
            dynamic_model = init_chat_model(model=model, model_provider=provider, temperature=0.0, streaming=True)
            agent = create_tool_calling_agent(llm=dynamic_model, tools=tools, prompt=prompt)
            agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True,
                                           max_iterations=10)

            async for event in agent_executor.astream_events(input={"input": query}, version="v2"):
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