from mcp.server.fastmcp import FastMCP # Import library to create MCP servers
from langchain_community.utilities.pubmed import PubMedAPIWrapper # Import the PubMed database wrapper
import os, certifi # Import packages to deal with transport issues

mcp = FastMCP(name="MedicalDatabase") # Initialize the server and set its identity

@mcp.tool() # Decorator required to create an MCP tool that can be called by the LLM model
def search_medical_literature(query: str): # Function to query PubMed API
    os.environ["SSL_CERT_FILE"] = certifi.where() # Force environment to use Certifi's bundle
    os.environ["REQUESTS_CA_BUNDLE"] = certifi.where() # Prevent SSL/Handshake errors during API calls

    try: # Attempt a connection to API
        client = PubMedAPIWrapper(top_k_results=5, doc_content_chars_max=3000) # Initialize PubMed Client to return top 5 results, capped to 3000 characters each
        result = client.run(query) # Execute the search with the input query from a model

        if (not result) or "No Good PubMed Result was found" in result: # Handle cases where a search returns no relevant data
            return f"Search Completed. No peer-reviewed literature was found for : {query}" # Data sent to LLM

        return result # Return the result from API to the MCP Host

    except Exception as e: # Connection to PubMed API failed
        error_msg = f"Technical Error occurred while querying PubMed: {str(e)}" # Formatted error message
        return error_msg # Return the error message back to Host


if __name__ == '__main__': # A safeguard to ensure the server starts only when a file is executed directly
    mcp.run(transport="stdio") # Use STDIO (Standard Input/Output) to communicate with MCP Host/Client