
## Title: MarketSense AI- An Autonomous Financial Analyst

## Overview
MarketSense AI is an intelligent financial decision-support agent that helps retail investors avoid emotional trading and the lack of reliable information. Unlike normal trading bots that only look at price charts, MarketSense AI uses LangGraph to run a multi-stage analysis pipeline. It reads live market data through tool calling, interprets fresh news using sentiment analysis, and uses Dynamic RAG to check these signals against the official risk factors inside SEC 10-K filings. By combining real-time sentiment with long-term fundamental risks, the system generates structured and evidence-based trading recommendations.

## Reason for picking up this project

This project is aligned with the MAT496 course content as it demonstrates a mastery of "reading" unstructured data to drive complex decision-making. 
Unstructured Text Processing: The core engine ingests messy, human-written text—specifically financial news articles and SEC filings—which requires LLM reasoning rather than simple keyword matching.
Tool Calling: It utilizes the yfinance tool for real-time price math and the Tavily search tool for live news, ensuring the LLM is grounded in reality.
LangGraph Orchestration: It uses a stateful graph to manage the workflow, passing context between the news reader, the risk analyst, and the final decision maker.
Structured Output: The final deliverable is not a chat, but a strict JSON object suitable for integration into a trading dashboard

## Plan
I plan to execute these steps to complete my project.

[TODO] Step 1: Initialize project structure, set up environment variables (OPENAI, TAVILY), and define the AgentState schema.

[TODO] Step 2: Implement the yfinance Tool to fetch live stock prices and calculate unrealized P&L based on user input.

[TODO] Step 3: Implement the Tavily Search Tool to scrape the top 5 financial news headlines for a specific ticker.

[TODO] Step 4: Create the SentimentAnalysis Node that takes raw news text and returns a floating-point sentiment score.

## Conclusion:

I had planned to achieve {this this}. I think I have/have-not achieved the conclusion satisfactorily. The reason for your satisfaction/unsatisfaction.
