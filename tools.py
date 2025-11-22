import yfinance as yf
from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv
import os

# 1. LOAD THE API KEYS
load_dotenv()

def get_stock_data(ticker: str):
    """
    Fetches the last closing price.
    """
    try:
        stock = yf.Ticker(ticker)
        history = stock.history(period="1d")
        
        if history.empty:
            return None
            
        current_price = history['Close'].iloc[-1]
        return round(current_price, 2)
    except Exception as e:
        return f"Error fetching price: {e}"

def get_financial_news(ticker: str):
    """
    Fetches top 3 financial news headlines for a ticker using Tavily.
    """
    try:
        # LangChain automatically looks for 'TAVILY_API_KEY' in environment variables
        tool = TavilySearchResults(max_results=3)
        response = tool.invoke(f"{ticker} stock financial news today")
        
        # Tavily returns a list of dictionaries. We extract just the text content.
        news_summary = []
        for item in response:
            news_summary.append(f"- {item['content']}")
            
        return "\n".join(news_summary)
    except Exception as e:
        return f"Error fetching news: {e}"

# --- TEST AREA (Run this file to see if it works) ---
# ... (Keep the imports and functions exactly the same) ...

# --- UPDATED TEST AREA ---
if __name__ == "__main__":
    print("--- TESTING TOOLS ---")
    
    # ASK USER FOR INPUT INSTEAD OF HARDCODING
    user_ticker = input("Enter a stock ticker (e.g., TSLA, AAPL, MSFT): ").upper()
    
    print(f"\n1. Fetching Price for {user_ticker}...")
    price = get_stock_data(user_ticker)
    print(f"   Price: ${price}")
    
    print(f"\n2. Fetching News for {user_ticker}...")
    news = get_financial_news(user_ticker)
    print(f"   News:\n{news}")