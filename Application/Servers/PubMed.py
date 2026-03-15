from mcp.server.fastmcp import FastMCP
from langchain_community.utilities.pubmed import PubMedAPIWrapper
import logging
import os, ssl, certifi

mcp = FastMCP("MedicalDatabase")

@mcp.tool()
async def search_medical_literature(query:str):
    os.environ["SSL_CERT_FILE"] = certifi.where()
    os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
    try:
        client = PubMedAPIWrapper(top_k_results=5, doc_content_chars_max=3000)
        result = client.run(query)
        if (not result) or "No Good PubMed Result was found" in result:
            return f"Search Completed. No peer-reviewed literature was found for : {query}"
        return result
    except Exception as e:
        logging.error(f"PubMed Tool Error: {str(e)}")
        return f"Technical Error occurred while querying PubMed"



if __name__ == '__main__':
    mcp.run(transport="stdio")