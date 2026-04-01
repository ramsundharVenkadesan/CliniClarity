import datetime
from langchain_core.callbacks import BaseCallbackHandler
from typing import Any, Dict, List
from langchain_core.outputs import LLMResult
from pathlib import Path

current_dir = Path(__file__).parent

# 2. Go TWO levels up by chaining .parent twice
ACTIVITY_LOG_FILE = current_dir.parent.parent / "activity.log"

class CallBackHandler(BaseCallbackHandler):
    def on_llm_start(self, serialized:Dict[str, Any], prompts:List[str], **kwargs:Any) -> Any:
        with open(ACTIVITY_LOG_FILE, mode="a") as file:
            file.write(f"[{datetime.datetime.now()}] Final Prompt Sent to LLM: '{prompts[0]}'\n")

    def on_llm_end(self, response:LLMResult,  **kwargs:Any) -> Any:
        with open(ACTIVITY_LOG_FILE, mode="a") as file:
            file.write(f"[{datetime.datetime.now()}] Raw Response From LLM: '{response.generations[0][0].text}'\n")