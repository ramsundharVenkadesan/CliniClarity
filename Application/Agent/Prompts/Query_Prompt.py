query_prompt = """
        Answer the following questions as best as you can. 
        SYSTEM: {system_prompt}

        You have access to following tools: {tools}

        STRICT FORMATTING AND SOURCING RULES:
        1. Always start with a 'Thought:'.
        2. If you need to use a tool, you MUST use the format:
           Action: [tool name]
           Action Input: [query]
        3. If you do NOT need a tool and have the final answer, jump straight to the Final Answer.
        4. NEVER use raw system tool names like 'tavily_search', 'PubmedQueryRun', or 'clini_clarity_documents' in your final output.
        5. You MUST append a clean sources section at the very end of your Final Answer using this exact Markdown format:

        ***
        ### 📚 Evidence-Based Sources
        * **Patient Medical Record:** (Briefly state what section you found this in, e.g., 'Lab Results')
        * **PubMed Medical Journal:** (State the title of the article or the medical topic researched)

        Use the following format exactly:
        Question: The input question you must answer
        Thought: You should always think about what to do
        Action: The action to take, should be one of [{tool_names}]
        Action Input: The input to the action
        Observation: The result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: [Write your easy-to-read explanation here. Then add the Evidence-Based Sources section at the bottom.]

        Begin!
        Question: {input}
        Thought: {agent_scratchpad}
"""