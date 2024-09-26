import streamlit as st
import math
import numpy as np
from scipy.stats import norm
import plotly.graph_objs as go

def black_scholes(S, K, T, r, sigma, option_type='call'):
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    
    if option_type == 'call':
        option_price = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    elif option_type == 'put':
        option_price = K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    
    return option_price, d1, d2

def calculate_greeks(S, K, T, r, sigma):
    _, d1, d2 = black_scholes(S, K, T, r, sigma, 'call')
    delta_call = norm.cdf(d1)
    delta_put = norm.cdf(d1) - 1
    gamma = norm.pdf(d1) / (S * sigma * math.sqrt(T))
    theta_call = (-S * norm.pdf(d1) * sigma / (2 * math.sqrt(T)) - r * K * math.exp(-r * T) * norm.cdf(d2))
    theta_put = (-S * norm.pdf(d1) * sigma / (2 * math.sqrt(T)) + r * K * math.exp(-r * T) * norm.cdf(-d2))
    vega = S * norm.pdf(d1) * math.sqrt(T)
    
    return delta_call, delta_put, gamma, theta_call, theta_put, vega

def calculate_pnl(stock_prices, strike_price, premium):
    pnl_call = np.maximum(0, stock_prices - strike_price) - premium
    pnl_put = np.maximum(0, strike_price - stock_prices) - premium
    return pnl_call, pnl_put

st.title("Black-Scholes Option Pricing Calculator")

with st.container():
    col1, col2 = st.columns([2, 1])  

    with col1:
        S = st.number_input("Stock Price", value=100.0, step=0.10)
        K = st.number_input("Strike Price", value=100.0, step=0.10)
        T = st.number_input("Time to Expiry (Years)", value=1.0, step=0.10)
        r = st.number_input("Risk-Free Rate", value=0.05, step=0.01)
        sigma = st.number_input("Volatility", value=0.2, step=0.01)

    with col2:
        if S > 0 and K > 0 and T > 0 and r >= 0 and sigma >= 0:
            call_price, _, _ = black_scholes(S, K, T, r, sigma, 'call')
            put_price, _, _ = black_scholes(S, K, T, r, sigma, 'put')

            st.markdown(""" 
                <style>
                .button-row {
                    display: flex;
                    justify-content: space-between;
                }
                .button-call {
                    font-size: 20px;
                    color: black;
                    background-color: #4ac436;
                    border: none;
                    padding: 10px 50px;
                    border-radius: 12px;
                    font-weight: bold;
                    cursor: default;
                }
                .button-put {
                    font-size: 20px;
                    color: white;
                    background-color: #c42f2f;
                    border: none;
                    padding: 10px 50px;
                    border-radius: 12px;
                    font-weight: bold;
                    cursor: default;
                }
                </style>
                """, unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class="button-row">
                    <button class="button-call">Call: ${call_price:.2f}</button>
                    <button class="button-put">Put: ${put_price:.2f}</button>
                </div>
                """, unsafe_allow_html=True)

            delta_call, delta_put, gamma, theta_call, theta_put, vega = calculate_greeks(S, K, T, r, sigma)

            greeks = {
                "Δ (Call)": delta_call,
                "Δ (Put)": delta_put,
                "Θ (Call)": theta_call,
                "Θ (Put)": theta_put,
                "Γ": gamma,
                "V": vega
            }
            colors = ["blue", "orange", "green", "red", "purple", "cyan"]

            fig = go.Figure(go.Bar(
                x=list(greeks.values()), 
                y=list(greeks.keys()),
                orientation='h',
                marker=dict(color=colors),
                width=0.2, 
                textposition='none' 
            ))

            for index, value in enumerate(greeks.values()):
                fig.add_annotation(
                    x=value + 20.00, 
                    y=list(greeks.keys())[index],
                    text=f"{value:.2f}",
                    showarrow=False,
                    font=dict(size=14) 
                )

            fig.update_layout(
                showlegend=False,
                height=330, 
                margin=dict(t=10, b=20, l=20, r=20), 
                xaxis=dict(showticklabels=False)
            )
            st.plotly_chart(fig)

premium_input = st.number_input("Enter Option Premium (or leave blank to use Call Price)", value=call_price, step=0.01)

stock_prices = np.linspace(S * 0.5, S * 1.5, 18)  

pnl_call, pnl_put = calculate_pnl(stock_prices, K, premium_input)

heatmap_data = np.vstack([pnl_call, pnl_put])

fig = go.Figure(data=go.Heatmap(
    z=heatmap_data,
    x=stock_prices,
    y=["Call", "Put"], 
    text=heatmap_data.round(2), 
    texttemplate="%{text}",  
    colorscale=[
        [0, "red"], 
        [1, "green"]
    ],
    showscale=False,  
    zmin=-np.max(abs(heatmap_data)),  
    zmax=np.max(abs(heatmap_data)),
    hoverongaps=False,  
    xgap=1,  
    ygap=1,  
    hovertemplate="<b>P&L: %{z:.2f}</b><br>Stock Price: %{x:.2f}<extra></extra>",
    textfont=dict(size=10)
))

fig.add_shape(type="line",
    x0=S, x1=S, 
    y0=-1, y1=2, 
    line=dict(color="white", width=3)  
)

fig.add_annotation(
    x=S, y=1,  
    text=f"S: {S:.2f}",
    showarrow=True,
    arrowhead=2,
    ax=0,
    ay=-80, 
    font=dict(color="white", size=12)
)

fig.update_layout(
    title="Profit and Loss ($)",
    height=400,  
    width=1200,  
    font=dict(size=12)
)

fig.update_xaxes(title_text="", visible=False) 
fig.update_yaxes(title_text="", visible=True)  

st.plotly_chart(fig)
