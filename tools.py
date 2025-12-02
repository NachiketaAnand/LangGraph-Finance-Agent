import yfinance as yf
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import json

load_dotenv()

# Static map for professional display names
COMPANY_NAMES = {
    "NVDA": "NVIDIA Corp", "TSLA": "Tesla Inc", "AAPL": "Apple Inc", 
    "AMZN": "Amazon.com", "MSFT": "Microsoft", "GOOGL": "Alphabet Inc", 
    "META": "Meta Platforms", "AMD": "Adv. Micro Devices", "NFLX": "Netflix Inc", 
    "INTC": "Intel Corp", "PYPL": "PayPal Holdings", "COIN": "Coinbase Global", 
    "HOOD": "Robinhood", "GME": "GameStop Corp", "SPY": "S&P 500 ETF", 
    "QQQ": "Invesco QQQ", "BABA": "Alibaba Group", "PLTR": "Palantir Tech",
    "DIS": "Walt Disney", "BA": "Boeing Co", "JPM": "JPMorgan Chase"
}

def parse_user_input(user_text: str):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    prompt = f"""
    Extract: 1. Ticker (Symbol) 2. Buy Price (Float) 3. Quantity (Int).
    Input: "{user_text}"
    Return ONLY JSON. Example: {{"ticker": "AAPL", "buy_price": 150.0, "quantity": 10}}
    """
    try:
        response = llm.invoke(prompt)
        clean_content = response.content.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_content)
    except Exception as e:
        return {"ticker": "UNKNOWN", "buy_price": 0.0, "quantity": 1, "error": str(e)}

def get_stock_data(ticker: str):
    """
    Fetches the last closing price for the main analysis.
    """
    try:
        stock = yf.Ticker(ticker)
        history = stock.history(period="5d")
        if history.empty: return None
        return round(history['Close'].iloc[-1], 2)
    except Exception:
        return None

def process_stock_data(ticker, series):
    """Helper to format data for the widget"""
    if len(series) < 2: return None
    curr = series.iloc[-1]
    prev = series.iloc[-2]
    change_pct = ((curr - prev) / prev) * 100
    sparkline_data = series.tail(15).tolist()
    
    return {
        "ticker": ticker.upper(),
        "name": COMPANY_NAMES.get(ticker.upper(), ticker.upper()),
        "price": curr,
        "change": change_pct,
        "sparkline": sparkline_data
    }

def get_top_movers():
    """Fetches data for the default top 10 list."""
    watchlist = list(COMPANY_NAMES.keys())
    try:
        tickers_str = " ".join(watchlist)
        data = yf.Tickers(tickers_str)
        history = data.history(period="1mo")
        if history.empty: return []

        movers = []
        closes = history['Close']

        for ticker in watchlist:
            if ticker in closes.columns:
                data_point = process_stock_data(ticker, closes[ticker].dropna())
                if data_point:
                    movers.append(data_point)
        
        movers.sort(key=lambda x: abs(x['change']), reverse=True)
        return movers[:10]
    except Exception as e:
        print(f"Error fetching movers: {e}")
        return []

def get_specific_mover(ticker: str):
    """
    Fetches widget data for a SPECIFIC single ticker (Search functionality).
    """
    try:
        stock = yf.Ticker(ticker)
        history = stock.history(period="1mo")
        if history.empty: return None
        
        return process_stock_data(ticker, history['Close'].dropna())
    except Exception:
        return None

def get_financial_news(ticker: str):
    try:
        tool = TavilySearchResults(max_results=5)
        response = tool.invoke(f"{ticker} stock financial news analysis")
        clean_news = []
        junk = ["subscribe", "login", "advertisement", "cookies"]
        
        for item in response:
            content = item['content']
            if len(content) < 150 or "|" in content: continue
            if any(term in content.lower() for term in junk): continue
            clean_news.append(f"- {content}")
        return "\n\n".join(clean_news[:3])
    except Exception as e:
        return f"Error fetching news: {e}"