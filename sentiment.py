from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# 1. Load API Keys
load_dotenv()

# 2. Setup the LLM (GPT-4o-mini is cheap and fast)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def analyze_sentiment(news_text: str):
    """
    Analyzes news text and returns a score from -1 (Bearish) to 1 (Bullish).
    """
    if not news_text:
        return 0.0

    prompt = f"""
    You are a financial sentiment analyzer. 
    Read the following news headlines and determine the overall sentiment score.
    
    Return ONLY a floating point number between -1.0 (Extremely Negative) and 1.0 (Extremely Positive).
    Do not add any text, markdown, or explanation. Just the number.
    
    NEWS:
    {news_text}
    """
    
    try:
        # Call the LLM
        result = llm.invoke(prompt)
        
        # Clean the output (remove extra whitespace) and convert to float
        score = float(result.content.strip())
        return score
    except Exception as e:
        print(f"Sentiment Analysis Error: {e}")
        return 0.0

# --- TEST AREA ---
if __name__ == "__main__":
    print("--- TESTING SENTIMENT NODE ---")
    sample_news = """
    - Nvidia revenue triples, beating all expectations.
    - AI demand is slowing down, analysts warn.
    - CEO says production is back on track.
    """
    print(f"News: {sample_news}")
    
    score = analyze_sentiment(sample_news)
    print(f"Sentiment Score: {score}")
    
    if score > 0.5:
        print("Verdict: BULLISH ")
    elif score < -0.5:
        print("Verdict: BEARISH ")
    else:
        print("Verdict: NEUTRAL ")