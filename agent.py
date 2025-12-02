from typing import TypedDict
from langgraph.graph import StateGraph, END
from tools import get_stock_data, get_financial_news, parse_user_input
from sentiment import analyze_sentiment, summarize_news, summarize_risks
from rag import download_and_index_10k, query_risks
from langchain_openai import ChatOpenAI

class AgentState(TypedDict):
    user_query: str
    ticker: str
    buy_price: float
    quantity: int
    price: float
    pnl: float
    news_summary: str
    sentiment_score: float
    risk_analysis: str
    final_decision: str

def input_parser_node(state: AgentState):
    parsed = parse_user_input(state["user_query"])
    return {
        "ticker": parsed.get("ticker", "UNKNOWN"),
        "buy_price": parsed.get("buy_price", 0.0),
        "quantity": parsed.get("quantity", 1)
    }

def market_data_node(state: AgentState):
    price = get_stock_data(state["ticker"])
    pnl = 0.0
    if price and state['buy_price'] > 0:
        pnl = (price - state['buy_price']) * state['quantity']
    return {"price": price, "pnl": pnl}

def news_sentiment_node(state: AgentState):
    raw_news = get_financial_news(state["ticker"])
    clean_summary = summarize_news(raw_news)
    sentiment = analyze_sentiment(clean_summary)
    return {"news_summary": clean_summary, "sentiment_score": sentiment}

def risk_analysis_node(state: AgentState):
    ticker = state["ticker"]
    download_and_index_10k(ticker)
    raw_risks = query_risks(ticker, "market risks competition regulation")
    clean_risks = summarize_risks(raw_risks)
    return {"risk_analysis": clean_risks}

def decision_node(state: AgentState):
    llm = ChatOpenAI(model="gpt-4o", temperature=0.00)
    
    pct_gain = 0.0
    if state['buy_price'] > 0:
        pct_gain = (state['pnl'] / (state['buy_price'] * state['quantity'])) * 100

    # UPDATED PROMPT: Conversational & Direct
    prompt = f"""
    You are a Senior Portfolio Manager. 
    
    USER POSITION:
    - Stock: {state['ticker']}
    - PnL: ${state['pnl']:.2f} ({pct_gain:.2f}%)
    
    DATA:
    - Sentiment: {state['sentiment_score']} (Scale: -1.0 to 1.0)
    - News: {state['news_summary']}
    - Risks: {state['risk_analysis']}
    
    DECISION LOGIC:
    - SELL if PnL > 10% and news is weak (Take Profit).
    - SELL if PnL < -5% and news is negative (Stop Loss).
    - BUY if PnL is negative but Sentiment is > 0.5 (Buy Dip).
    - HOLD otherwise.

    OUTPUT FORMAT:
    start with one word: BUY, SELL, or HOLD. 
    Then, write a short, human-like explanation. 
    DO NOT mention "Rule #1" or "Trading Rule". Just explain the logic directly.
    
    Example:
    SELL. We are up 15% and the news is cooling off. It's smart to lock in these gains now.
    """
    
    response = llm.invoke(prompt)
    return {"final_decision": response.content}

workflow = StateGraph(AgentState)
workflow.add_node("input_parser", input_parser_node)
workflow.add_node("market_data", market_data_node)
workflow.add_node("news_sentiment", news_sentiment_node)
workflow.add_node("risk_analysis", risk_analysis_node)
workflow.add_node("decision_maker", decision_node)

workflow.set_entry_point("input_parser")
workflow.add_edge("input_parser", "market_data")
workflow.add_edge("market_data", "news_sentiment")
workflow.add_edge("news_sentiment", "risk_analysis")
workflow.add_edge("risk_analysis", "decision_maker")
workflow.add_edge("decision_maker", END)

app_graph = workflow.compile()