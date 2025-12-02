## Title: MarketSense AI- An Autonomous Financial Analyst

## Overview
MarketSense AI is an intelligent financial decision support agent that helps retail investors avoid emotional trading and the lack of reliable information. Unlike normal trading bots that only look at price charts, MarketSense AI uses LangGraph to run a multi stage analysis pipeline. It reads live market data through tool calling, interprets fresh news using sentiment analysis, and uses Dynamic RAG to check these signals against the official risk factors inside SEC 10-K filings. By combining real-time sentiment with long term fundamental risks, the system generates structured and evidence based trading recommendations.

## Reason for picking up this project

This project is aligned with the MAT496 course content as it demonstrates a mastery of "reading" unstructured data to drive complex decision making. 
Unstructured Text Processing: The core engine ingests messy, human written text specifically financial news articles and SEC filings which requires LLM reasoning rather than simple keyword matching.

Tool Calling: It utilizes the yfinance tool for real time price math and the Tavily search tool for live news, ensuring the LLM is grounded in reality.

LangGraph Orchestration: It uses a stateful graph to manage the workflow, passing context between the news reader, the risk analyst, and the final decision maker.

Structured Output: The final deliverable is not a chat, but a strict JSON object suitable for integration into a trading dashboard

## Plan
I executed the following steps to complete this project:

[DONE] Step 1: Project Setup & State Definition Initialized the project structure, configured environment variables (OpenAI, Tavily, LangSmith), and defined the AgentState schema to strictly type the data flowing between graph nodes.

[DONE] Step 2: Market Data Integration Implemented the yfinance tools to fetch live stock prices and calculated the user's Realized/Unrealized P&L. Added helper functions to fetch historical data for "Market Mover" widgets.

[DONE] Step 3: News Search Engine Built the Tavily Search Tool integration to scrape real-time financial news headlines and implemented a cleaning filter to remove web-scraping noise (ads/promos).

[DONE] Step 4: Sentiment Analysis Engine Created the SentimentAnalysis node with a "Cynical Analyst" persona. This node processes raw news text and returns a calibrated floating-point sentiment score to avoid false positives.

[DONE] Step 5: Dynamic RAG System (The "Reader") Implemented rag.py to autonomously download SEC 10-K filings, chunk the text, and create vector embeddings using ChromaDB for semantic retrieval.

[DONE] Step 6: Risk Analysis Logic Developed the RiskAnalysis node that performs semantic search on the indexed 10-K documents to extract specific "Risk Factors" (e.g., regulation, supply chain) relevant to the user's query.

[DONE] Step 7: Portfolio Manager Logic Implemented the final Decision node. This uses a "Senior Portfolio Manager" prompt to synthesize the quantitative data (P&L), qualitative data (News), and fundamental risks (10-K) into a coherent BUY/SELL/HOLD recommendation.

[DONE] Step 8: LangGraph Orchestration Wired all the components together into a StateGraph. Defined the edges to ensure the correct flow of data: Input → Market Data → Sentiment → Risk → Decision.

[DONE] Step 9: Interactive UI & Visualization Built a professional Streamlit dashboard featuring a "Widget-style" sidebar for top market movers (with Sparkline charts) and a clean, split-view display for the AI's final verdict and evidence.

## Video link:
https://youtu.be/nR-PClxyiiI

## Conclusion:
I had planned to achieve an autonomous agent that could synthesize price, news, and risk data. I think I have achieved the conclusion satisfactorily. The system successfully combines three distinct data sources that usually require three different websites, and synthesizes them into a single, coherent "Buy/Sell" recommendation. The RAG implementation was particularly successful in finding hidden risks that recent news articles often missed.

## Fix Error
If anyone faces the following error:
"An error occurred: Query error: Database error: error returned from database: (code: 1032) attempt to write a readonly database"

You need to manually delete the following folders in your project directory:

1. The Chroma Database folder for your specific stock (e.g., "chroma_db_NVDA", "chroma_db_AAPL", etc.).
2. The "sec-edgar-filings" folder.

After deleting these folders, restart the application.
