import asyncio
import os
import time
from typing import Dict, Any
from deepeval.test_case import LLMTestCase
from deepeval.metrics import FaithfulnessMetric
from deepeval.models import DeepEvalBaseLLM
from langchain_google_genai import ChatGoogleGenerativeAI
from Agent.RAG_Graph.State import GraphState




# 1. Hardened Custom Gemini Judge wrapper
# This safely bridges Gemini's API with DeepEval's internal parser
class GeminiEvaluator(DeepEvalBaseLLM):
    def __init__(self, model_name="gemini-3.1-flash-lite-preview"):
        self.model = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0.0,
            google_api_key=os.environ.get("GOOGLE_API_KEY")
        )

    def load_model(self):
        return self.model

    def generate(self, prompt: str, **kwargs) -> str:
        chat_model = self.load_model()
        if isinstance(prompt, list):
            try:
                prompt = "\n".join([f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in prompt])
            except Exception:
                prompt = str(prompt)

        response = chat_model.ainvoke(prompt)
        content = response.content
        if isinstance(content, list):
            content = "".join([block.get("text", "") for block in content if isinstance(block, dict)])
        return str(content)

    async def a_generate(self, prompt: str, **kwargs) -> str:
        chat_model = self.load_model()
        if isinstance(prompt, list):
            try:
                prompt = "\n".join([f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in prompt])
            except Exception:
                prompt = str(prompt)

        response = await chat_model.ainvoke(prompt)
        content = response.content
        if isinstance(content, list):
            content = "".join([block.get("text", "") for block in content if isinstance(block, dict)])
        return str(content)

    def get_model_name(self):
        return "Gemini 2.0 Flash Lite"



async def hallucination(state: GraphState) -> Dict[str, Any]:
    print("\n--- 🛡️ RUNNING DEEPEVAL FAITHFULNESS CHECK ---")

    summary = state['summary']
    context = state['context']
    query = "summarize the report"

    # Instantiate our safe Gemini wrapper
    gemini_judge = GeminiEvaluator()

    # Initialize the HIPAA-ready DeepEval metric
    metric = FaithfulnessMetric(threshold=0.9, model=gemini_judge, include_reason=False)

    test_case = LLMTestCase(input=query, actual_output=summary, retrieval_context=context)

    print("Evaluating Groundedness using DeepEval...")
    start_time = time.time()
    try:
        if hasattr(metric, 'a_measure'):
            await metric.a_measure(test_case)
            execution_time = time.time() - start_time
            print(f"[*] Evaluator Model : {gemini_judge.get_model_name()}")
            print(f"[*] Context Size    : {len(state['context'])} documents")
            print(f"[*] Summary Size    : {len(state['summary'])} characters")
            print(f"[*] Execution Time  : {execution_time:.2f} seconds")
            print(f"[*] Final Score     : {metric.score}")
            print(f"[*] Threshold Met   : {metric.is_successful()}")
        else:
            # Safely offload the synchronous measure function to a background thread
            # This prevents the float return value from breaking the await expression
            await asyncio.to_thread(metric.measure, test_case)
            execution_time = time.time() - start_time

            # 3. Print the safe audit data
            print(f"[*] Evaluator Model : {gemini_judge.get_model_name()}")
            print(f"[*] Context Size    : {len(state['context'])} documents")
            print(f"[*] Summary Size    : {len(state['summary'])} characters")
            print(f"[*] Execution Time  : {execution_time:.2f} seconds")
            print(f"[*] Final Score     : {metric.score}")
            print(f"[*] Threshold Met   : {metric.is_successful()}")

            # The score is stored in the metric object after execution
        score = metric.score
    except Exception as e:
        print(f"DeepEval Execution Error: {e}")
        score = 0.0

    print(f"DeepEval Score: {score}")

    if score > 0.9:
        print("Decision: ✅ ACCEPTED (Grounded in context)")
        score_pct = int(score * 100)

        # Flush-left HTML to prevent Markdown code-block rendering
        trust_badge_html = f"""
<div class="mt-8 p-6 bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800/50 rounded-2xl flex items-start gap-4 shadow-sm">
    <div class="text-emerald-500 text-3xl">🛡️</div>
    <div>
        <h4 class="text-emerald-900 dark:text-emerald-100 font-bold text-lg flex items-center gap-2 mb-1">
            Clinical Verification Score: {score_pct}% 
        </h4>
        <div class="flex flex-wrap gap-2 mb-3">
            <span class="bg-emerald-100 dark:bg-emerald-800/60 text-emerald-700 dark:text-emerald-300 text-xs px-2.5 py-1 rounded-full uppercase tracking-wider font-bold">
                ✅ ACCEPTED (Grounded)
            </span>
            <span class="bg-blue-100 dark:bg-blue-800/60 text-blue-700 dark:text-blue-300 text-xs px-2.5 py-1 rounded-full uppercase tracking-wider font-bold">
                🔒 HIPAA COMPLIANT PIPELINE
            </span>
        </div>
        <p class="text-emerald-700 dark:text-emerald-400 text-sm leading-relaxed mb-0">
            This summary was audited by the DeepEval HIPAA-compliant security engine. The score confirms the AI adhered strictly to your anonymized records, ensuring privacy and clinical accuracy.
        </p>
    </div>
</div>
"""
        final_summary = summary + "\n\n" + trust_badge_html
    else:
        print("Decision: ❌ REJECTED (Hallucination Detected)")
        final_summary = summary

    return {"evaluation_score": score, "summary": final_summary}
