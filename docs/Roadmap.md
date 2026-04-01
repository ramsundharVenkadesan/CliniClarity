# CliniClarity: V1.0 Execution Roadmap (Spring 2026)

This document outlines the technical evolution and upcoming deployment path for the CliniClarity patient advocate agent. The roadmap tracks the transition from a monolithic LangChain script to a modular, secured, and cloud-native agentic architecture.

## 📅 Phase I: Foundations & Integration (February 2026)
**Goal:** Establish the core reasoning loop and persistent memory layer.
 * [X] **Initial Agent Build:** Developed the primary ReAct agent and RAG pipeline using plain LangChain to handle medical document queries
 * [X] **API & Vector Layer:** Integrated FastAPI to serve the agent and transitioned memory to Pinecone for high-dimensional vector storage (1536-dim)
 * [X] **Document Processing** Implemented RecursiveCharacterTextSplitter and Presidio-based PII redaction to ensure HIPAA-aligned data ingestion

## 🧠 Phase II: Architectural Evolution & Standardization (March 2026)
**Goal:** Transition to stateful orchestration and standardized tool protocols.
 * [X] **LangGraph Migration:** Refactored the linear RAG pipeline into a stateful graph using LangGraph, allowing for more complex multi-turn medical research cycles.
 * [X] **Tool-Calling Upgrade:** Updated the manual ReAct logic to a modern Tool-Calling Agent pattern, improving the reliability of external API invocations.
 * [X] **MCP Integrations:** Migrated the PubMed and Tavily search functionalities into a standalone Model Context Protocol (MCP) server, standardizing how the agent discovers and uses medical research tools.

## 🛡️ Phase III: Guardrails & Cloud Deployment (April - May 2026)
**Goal:** Implement enterprise-grade security and automate infrastructure.
 * [X] **Security Integration:** Deployed Protect AI to intercept and mitigate prompt injection attempts at the API gateway.
 * [X] **Quality Assurance:** Integrated DeepEval into the pipeline to automate hallucination checking and enforce a high "Grounding Rate" for clinical summaries
 * [ ] **Infrastructure as Code (Next Step):** Transition the entire stack from local development to a production AWS environment using Terraform for automated provisioning

## 📊 Success Milestones
| Milestone | Target Date | Deliverable |
| :--- | :--- | :--- |
| **Foundations Complete** | Feb 28, 2026 | Functional LangChain ReAct agent with FastAPI and Pinecone. |
| **Agentic Refactor** | Mar 15, 2026 | Migration to LangGraph, Tool-Calling, and MCP Server architecture. |
| **Security Freeze** | Apr 15, 2026 | Hallucination checking (DeepEval) and injection defense (Protect AI) active. |
| **Cloud Release (V1.0)** | May 12, 2026 | Fully automated AWS deployment via Terraform with integrated audit logs. |
