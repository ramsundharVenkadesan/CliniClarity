from mcp.server.fastmcp import FastMCP
from langchain_community.utilities.pubmed import PubMedAPIWrapper
import os, certifi
from pathlib import Path
import datetime

CURRENT_FOLDER = Path(__file__).parent.absolute()
ACTIVITY_LOG_FILE = CURRENT_FOLDER / "activity.log"

mcp = FastMCP("MedicalDatabase")

@mcp.tool()
def search_medical_literature(query: str):
    os.environ["SSL_CERT_FILE"] = certifi.where()
    os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
    try:
        client = PubMedAPIWrapper(top_k_results=5, doc_content_chars_max=3000)
        result = client.run(query)

        # Add this success log!
        with open(ACTIVITY_LOG_FILE, mode="a") as file:
            file.write(f"[{datetime.datetime.now()}] Successfully queried PubMed for: '{query}'\n")

        if (not result) or "No Good PubMed Result was found" in result:
            return f"Search Completed. No peer-reviewed literature was found for : {query}"
        return result
    except Exception as e:
        error_msg = f"Technical Error occurred while querying PubMed: {str(e)}"
        with open(ACTIVITY_LOG_FILE, mode="a") as file:
            file.write(f"[{datetime.datetime.now()}] {error_msg}\n")
        return error_msg


@mcp.resource("file://activity.log")
def activity_log() -> str:
    with open(ACTIVITY_LOG_FILE, 'r') as file:
        return file.read()


if __name__ == '__main__':
    if not Path(ACTIVITY_LOG_FILE).exists():
        Path(ACTIVITY_LOG_FILE).touch()
    mcp.run(transport="stdio")