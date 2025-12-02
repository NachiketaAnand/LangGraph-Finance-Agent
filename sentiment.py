from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

def analyze_sentiment(news_text: str):
    """
    Analyzes news text and returns a score from -1 (Bearish) to 1 (Bullish).
    """
    if not news_text:
        return 0.0
    prompt = f"""
    You are a cynical financial analyst. 
    Analyze the provided news snippets.
    
    CRITICAL RULES:
    1. If the news is just generic updates or marketing fluff, score it 0.0 (Neutral).
    2. Only give high positive scores (> 0.5) for CONCRETE hard data (Record earnings, New huge contract).
    3. Look for hidden negatives (Delays, missed expectations, regulatory issues).
    
    Return ONLY a floating point number between -1.0 (Negative) and 1.0 (Positive).
    NEWS: {news_text}
    """
    
    try:
        result = llm.invoke(prompt)
        return float(result.content.strip())
    except Exception as e:
        print(f"Sentiment Error: {e}")
        return 0.0

def summarize_news(news_text: str):
    """
    Uses LLM to summarize and clean raw news into professional bullet points.
    """
    if not news_text:
        return "No news found."
        
    prompt = f"""
    You are a financial news editor. 
    Read the following raw news snippets (which may contain web scraping garbage) and summarize the key facts.
    
    Instructions:
    1. Extract the top 3 most important financial updates (Earnings, M&A, Product Launches, Stock Moves).
    2. Remove all marketing fluff ("Join Pro", "Subscribe", "Login").
    3. Format as a clean Markdown list of bullet points.
    4. Keep it concise (1 sentence per bullet).

    RAW TEXT:
    {news_text}
    """
    
    try:
        result = llm.invoke(prompt)
        return result.content.strip()
    except Exception as e:
        return f"Error summarizing news: {e}"

def summarize_risks(risk_text: str):
    """
    Uses LLM to summarize raw 10-K risk text into concise bullet points.
    """
    if not risk_text or "No 10-K indexed" in risk_text:
        return "No specific risks identified from 10-K."
        
    prompt = f"""
    You are a Risk Analyst reading an SEC 10-K filing.
    Read the following raw "Risk Factors" text.
    
    Instructions:
    1. Identify the top 3 SPECIFIC risks to this company (e.g., "Supply chain dependence on Taiwan", "Antitrust investigation", "Declining iPhone sales").
    2. Ignore generic boilerplate risks (e.g., "Stock price may fluctuate", "General economic conditions").
    3. Format as a clean Markdown list.
    4. Be extremely concise.

    RAW TEXT:
    {risk_text[:20000]}
    """
    
    try:
        result = llm.invoke(prompt)
        return result.content.strip()
    except Exception as e:
        return f"Error summarizing risks: {e}"