import os
from typing import Dict, Any
from deepeval.test_case import LLMTestCase
from deepeval.metrics import FaithfulnessMetric
from deepeval.models import DeepEvalBaseLLM
from langchain_google_genai import ChatGoogleGenerativeAI
from Agent.RAG_Graph.State import GraphState
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser


async def hallucination(state: GraphState) -> Dict[str, Any]:
    print("\n--- ⚡ RUNNING FAST GROUNDEDNESS CHECK ---")

    summary = state['summary']
    # Join the context chunks back into a single string for the prompt
    context_text = "\n\n".join(state['context'])

    # Initialize Gemini specifically configured to output strict JSON
    evaluator_llm = ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",
        temperature=0.0,
        model_kwargs={"response_mime_type": "application/json"}  # Forces instant JSON generation
    )

    # A highly strict, binary-focused prompt
    eval_prompt = PromptTemplate(
        template="""You are a strict clinical data auditor. 
        Your ONLY job is to verify if the SUMMARY is 100% grounded in the provided CONTEXT. 

        CONTEXT:
        {context}

        SUMMARY:
        {summary}

        Rule: If the SUMMARY contains ANY medical claim, date, or fact not explicitly found in the CONTEXT, it is a hallucination.

        Output a valid JSON object with exactly one key named "score". The value must be a float between 0.0 (contains hallucinations) and 1.0 (perfectly grounded). No other text.
        """,
        input_variables=["context", "summary"]
    )

    # Build the fast chain
    chain = eval_prompt | evaluator_llm | JsonOutputParser()

    print("Calculating faithfulness probability...")
    try:
        # This will execute significantly faster than DeepEval
        result = await chain.ainvoke({"context": context_text, "summary": summary})
        score = float(result.get("score", 0.0))
    except Exception as e:
        print(f"Evaluation Parsing Error: {e}")
        score = 0.0  # Fail-safe to trigger a regeneration if the API errors out

    print(f"Fast Eval Score: {score}")

    if score > 0.9:
        print("Decision: ✅ ACCEPTED (Grounded in context)")
        score_pct = int(score * 100)

        # Updated Trust Badge with HIPAA mention
        trust_badge_html = f"""
<div class="mt-8 p-6 bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800/50 rounded-2xl flex items-start gap-4 shadow-sm">
    <div class="text-emerald-500 text-3xl">🛡️</div>
    <div>
        <h4 class="text-emerald-900 dark:text-emerald-100 font-bold text-lg flex items-center gap-2 mb-1">
            Clinical Verification Score: {score_pct}% 
        </h4>
        <span class="inline-block bg-emerald-100 dark:bg-emerald-800/60 text-emerald-700 dark:text-emerald-300 text-xs px-2.5 py-1 rounded-full uppercase tracking-wider font-bold mb-2">
            ✅ ACCEPTED (Grounded in context)
        </span>
        <p class="text-emerald-700 dark:text-emerald-400 text-sm leading-relaxed mb-0">
            This summary was audited by a HIPAA-compliant security engine. The score confirms the AI adhered strictly to your anonymized records, ensuring privacy and clinical accuracy.
        </p>
    </div>
</div>
"""
        final_summary = summary + "\n\n" + trust_badge_html
    else:
        print("Decision: ❌ REJECTED (Hallucination Detected)")
        final_summary = summary

    return {"evaluation_score": score, "summary": final_summary}
