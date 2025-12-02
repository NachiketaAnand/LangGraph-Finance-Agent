import streamlit as st
from agent import app_graph
from tools import get_top_movers, get_specific_mover 

st.set_page_config(page_title="MarketSense AI", layout="wide")

# --- CSS ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #1c1c1e; }
    .stock-card {
        background-color: #2c2c2e;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid #3a3a3c;
    }
    .stock-info { display: flex; flex-direction: column; min-width: 80px; }
    .ticker { font-weight: 700; font-size: 1.1em; color: white; }
    .company-name { font-size: 0.75em; color: #98989d; max-width: 90px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
    .price-info { text-align: right; display: flex; flex-direction: column; align-items: flex-end; min-width: 70px; }
    .price { font-weight: 600; color: white; }
    .change-pill { font-size: 0.8em; padding: 2px 8px; border-radius: 6px; font-weight: 600; margin-top: 4px; }
    .positive { background-color: #30d158; color: white; }
    .negative { background-color: #ff453a; color: white; }
</style>
""", unsafe_allow_html=True)

# --- HELPERS ---
def make_sparkline_svg(data, color="#30d158"):
    if not data or len(data) < 2: return ""
    width, height = 60, 25
    min_val, max_val = min(data), max(data)
    val_range = max_val - min_val if max_val != min_val else 1
    points = [f"{(i / (len(data) - 1)) * width},{height - ((val - min_val) / val_range) * height}" for i, val in enumerate(data)]
    return f'<svg width="{width}" height="{height}" style="margin: 0 8px;"><polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="2" /></svg>'

def render_stock_card(stock):
    is_pos = stock['change'] >= 0
    color_class = "positive" if is_pos else "negative"
    line_color = "#30d158" if is_pos else "#ff453a"
    sign = "+" if is_pos else ""
    return f"""<div class="stock-card"><div class="stock-info"><span class="ticker">{stock['ticker']}</span><span class="company-name">{stock['name']}</span></div>{make_sparkline_svg(stock['sparkline'], line_color)}<div class="price-info"><span class="price">${stock['price']:.2f}</span><span class="change-pill {color_class}">{sign}{stock['change']:.2f}%</span></div></div>"""

# --- SIDEBAR ---
with st.sidebar:
    st.header("🔍 Market Watch")
    search_query = st.text_input("Search", placeholder="Ticker...")
    st.markdown("### Movers")
    with st.spinner("Updating..."):
        if search_query:
            data = get_specific_mover(search_query)
            if data: st.markdown(render_stock_card(data), unsafe_allow_html=True)
            else: st.error("Not found.")
        else:
            for stock in get_top_movers(): st.markdown(render_stock_card(stock), unsafe_allow_html=True)

# --- MAIN APP ---
st.title("MarketSense AI")
st.caption("Autonomous Financial Analyst")

user_query = st.text_area("Position:", placeholder="Example: I bought 50 shares of NVDA at $120.", height=100)

if st.button("Analyze Stock"):
    if not user_query: st.error("Please describe your position.")
    else:
        with st.spinner("Analyzing..."):
            try:
                result = app_graph.invoke({"user_query": user_query})
                
                # Metrics
                st.divider()
                st.subheader(f"Analysis for: {result.get('ticker')}")
                c1, c2, c3 = st.columns(3)
                p = result.get('price')
                b = result.get('buy_price', 0)
                
                with c1: st.metric("Price", f"${p}")
                with c2: 
                    pct = ((p - b) / b) * 100 if p and b else 0
                    st.metric("P&L", f"${result.get('pnl'):.2f}", f"{pct:.2f}%")
                with c3: st.metric("Sentiment", f"{result.get('sentiment_score')} / 1.0")

                # --- NEW DECISION DISPLAY ---
                st.divider()
                raw_decision = result.get('final_decision', "")
                
                # Parse the Action vs Reason
                action_color = "gray"
                action_text = "HOLD"
                reason_text = raw_decision
                
                if "SELL" in raw_decision.upper():
                    action_text = "SELL"
                    action_color = "red"
                    # Remove the first word "SELL" or "SELL." to get clean reason
                    reason_text = raw_decision.replace("SELL", "").replace(".", "", 1).strip()
                elif "BUY" in raw_decision.upper():
                    action_text = "BUY"
                    action_color = "green"
                    reason_text = raw_decision.replace("BUY", "").replace(".", "", 1).strip()
                elif "HOLD" in raw_decision.upper():
                    action_text = "HOLD"
                    action_color = "orange"
                    reason_text = raw_decision.replace("HOLD", "").replace(".", "", 1).strip()

                # Render the split view
                st.markdown(f"""
                <div style="padding: 20px; border-radius: 10px; background-color: #262730; border-left: 5px solid {action_color};">
                    <h3 style="margin: 0; color: white;">AI thinks it's better to <span style="color: {action_color};">{action_text}</span></h3>
                    <p style="margin-top: 10px; font-size: 1.1em;">{reason_text}</p>
                </div>
                """, unsafe_allow_html=True)
                # ---------------------------

                st.divider()
                c1, c2 = st.columns(2)
                with c1:
                    with st.expander("📰 News", expanded=True): st.markdown(result.get('news_summary'))
                with c2:
                    with st.expander("⚠️ Risks", expanded=False): st.write(result.get('risk_analysis'))

            except Exception as e: st.error(f"Error: {e}")