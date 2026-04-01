import datetime
from langchain_core.callbacks import BaseCallbackHandler
from typing import Any, Dict, List
from langchain_core.outputs import LLMResult


ACTIVITY_LOG_FILE = "/Users/ram/Downloads/CliniGraph/activity.log"

class CallBackHandler(BaseCallbackHandler):
    def on_llm_start(self, serialized:Dict[str, Any], prompts:List[str], **kwargs:Any) -> Any:
        with open(ACTIVITY_LOG_FILE, mode="a") as file:
            file.write(f"[{datetime.datetime.now()}] Final Prompt Sent to LLM: '{prompts[0]}'\n")

    def on_llm_end(self, response:LLMResult,  **kwargs:Any) -> Any:
        with open(ACTIVITY_LOG_FILE, mode="a") as file:
            file.write(f"[{datetime.datetime.now()}] Raw Response From LLM: '{response.generations[0][0].text}'\n")