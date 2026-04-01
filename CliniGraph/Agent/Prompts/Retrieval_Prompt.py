medical_summary_template = """
                    SYSTEM: {system_prompt}

                    CLINICAL CONTEXT: 
                    {context}

                    USER QUERY: 
                    {query}

                    INSTRUCTIONS for Accessibility:
                    - Use a 6th-grade reading level. 
                    - Avoid medical jargon. If you must use a term (e.g., 'Spiculated'), explain it simply (e.g., 'spiky or irregular shape').
                    - Use the 'What, So What, Now What' framework.
                    - Use emojis to make the report less intimidating.

                    # 🩺 Your Health Summary (Simplified)
                    ---
                    ## 💡 The Main Takeaway (The 'What')
                    [Provide a 2-sentence summary using everyday language. Example: 'The doctors found a spot on your lung that needs more testing right away.']

                    ## 🔍 What the Results Mean (The 'So What')
                    - **The Finding:** [Explain the primary issue without using scary jargon unless defined.]
                    - **Why it matters:** [Explain why the doctor is concerned in a calm, supportive way.]

                    ## 📊 Key Labs & Vitals
                    [Only list the most important ones. Explain 'High' or 'Low' instead of just numbers.]
                    - **Blood Sugar:** [Explain it like: 'Higher than normal, which means your diabetes needs more attention.']

                    ## 🚶 Your Next Steps (The 'Now What')
                    1. **Priority 1:** [Most urgent action]
                    2. **Priority 2:** [Next follow-up]

                    ## ❓ Questions for your Doctor
                    [Provide 2 questions the patient can literally read out loud to their doctor at the next visit.]

                    ---
                    *Disclaimer: This is an AI-generated summary to help you understand your report. Please discuss all findings with your healthcare team.*"""