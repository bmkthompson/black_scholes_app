import streamlit as st
import math
import numpy as np
from scipy.stats import norm
import plotly.graph_objs as go

# Black-Scholes formula implementation
def black_scholes(S, K, T, r, sigma, option_type='call'):
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    
    if option_type == 'call':
        option_price = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    elif option_type == 'put':
        option_price = K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    
    return option_price, d1, d2

# Calculate Greeks
def calculate_greeks(S, K, T, r, sigma):
    _, d1, d2 = black_scholes(S, K, T, r, sigma, 'call')
    delta_call = norm.cdf(d1)
    delta_put = norm.cdf(d1) - 1
    gamma = norm.pdf(d1) / (S * sigma * math.sqrt(T))
    theta_call = (-S * norm.pdf(d1) * sigma / (2 * math.sqrt(T)) - r * K * math.exp(-r * T) * norm.cdf(d2))
    theta_put = (-S * norm.pdf(d1) * sigma / (2 * math.sqrt(T)) + r * K * math.exp(-r * T) * norm.cdf(-d2))
    vega = S * norm.pdf(d1) * math.sqrt(T)
    
    return delta_call, delta_put, gamma, theta_call, theta_put, vega

# Function to calculate P&L for Call and Put options
def calculate_pnl(stock_prices, strike_price, premium):
    pnl_call = np.maximum(0, stock_prices - strike_price) - premium
    pnl_put = np.maximum(0, strike_price - stock_prices) - premium
    return pnl_call, pnl_put

# Streamlit app UI
st.title("Black-Scholes Option Pricing Calculator")

# Create a container for the input parameters
with st.container():
    col1, col2 = st.columns([2, 1])  # Two columns, with different widths

    with col1:
        S = st.number_input("Stock Price (S)", value=100.0, step=0.10)
        K = st.number_input("Strike Price (K)", value=100.0, step=0.10)
        T = st.number_input("Time to Expiry (T in years)", value=1.0, step=0.10)
        r = st.number_input("Risk-Free Rate (r as a decimal)", value=0.05, step=0.01)
        sigma = st.number_input("Volatility (σ as a decimal)", value=0.2, step=0.01)

    with col2:
        if S > 0 and K > 0 and T > 0 and r >= 0 and sigma >= 0:
            call_price, _, _ = black_scholes(S, K, T, r, sigma, 'call')
            put_price, _, _ = black_scholes(S, K, T, r, sigma, 'put')

            # CSS for the unclickable buttons
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
                    color: black;
                    background-color: #c42f2f;
                    border: none;
                    padding: 10px 50px;
                    border-radius: 12px;
                    font-weight: bold;
                    cursor: default;
                }
                </style>
                """, unsafe_allow_html=True)

            # Display Call and Put buttons next to each other
            st.markdown(f"""
                <div class="button-row">
                    <button class="button-call">Call: ${call_price:.2f}</button>
                    <button class="button-put">Put: ${put_price:.2f}</button>
                </div>
                """, unsafe_allow_html=True)

            # Calculate Greeks
            delta_call, delta_put, gamma, theta_call, theta_put, vega = calculate_greeks(S, K, T, r, sigma)

            # Display Greeks in a single horizontal bar graph
            greeks = {
                "Delta (Call)": delta_call,
                "Delta (Put)": delta_put,
                "Gamma": gamma,
                "Theta (Call)": theta_call,
                "Theta (Put)": theta_put,
                "Vega": vega
            }
            colors = ["blue", "orange", "green", "red", "purple", "cyan"]

            # Create a horizontal bar graph for all Greeks
            fig = go.Figure(go.Bar(
                x=list(greeks.values()), 
                y=list(greeks.keys()),
                orientation='h',
                marker=dict(color=colors),
                width=0.2,  # Adjust this value to make the bars thinner or thicker
                textposition='none'  # Hide automatic text positioning
            ))

            # Manually add annotations to place values on the right side of bars
            for index, value in enumerate(greeks.values()):
                fig.add_annotation(
                    x=value + 20.00,  # Position text slightly to the right of the bar, increased space
                    y=list(greeks.keys())[index],
                    text=f"{value:.2f}",
                    showarrow=False,
                    font=dict(size=12)  # Increase font size for the text
                )

            fig.update_layout(
                showlegend=False,
                height=330,  # Adjust height to align with input box
                margin=dict(t=10, b=20, l=20, r=20)  # Adjust margins
            )
            fig.update_xaxes(showticklabels=False)  # Hide tick labels on the x-axis
            st.plotly_chart(fig)

# Ask for premium input or calculate automatically
premium_input = st.number_input("Enter Option Premium (or leave blank to use Call Price)", value=call_price, step=0.01)

# Generate stock prices for heatmap
stock_prices = np.linspace(S * 0.5, S * 1.5, 10)  # Reduced to 10 for a clearer square representation

# Calculate P&L for the stock price range
pnl_call, pnl_put = calculate_pnl(stock_prices, K, premium_input)

# Create heatmap data
heatmap_data = np.vstack([pnl_call, pnl_put])

# Create heatmap using Plotly with square aspect ratio
fig = go.Figure(data=go.Heatmap(
    z=heatmap_data,
    x=stock_prices,
    y=["Call", "Put"],  # Labels for Call and Put
    text=heatmap_data.round(2),  # Display P&L values in the boxes
    texttemplate="%{text}$",  # Format the text to include the dollar sign
    colorscale=[
        [0, "red"], 
        [1, "green"]
    ],
    showscale=False,  # No color bar
    zmin=-np.max(abs(heatmap_data)),  # Symmetric scaling
    zmax=np.max(abs(heatmap_data)),
    hoverongaps=False,  # Avoid gaps in the hover labels
    xgap=1,  # Set the gap between x-axis tiles
    ygap=1,   # Set the gap between y-axis tiles
    hovertemplate="<b>P&L: %{z:.2f}$</b><br>Stock Price: %{x:.2f}$<br>Option Type: %{y}<extra></extra>"
))

# Set the layout for square appearance without axis titles
fig.update_layout(
    title="Profit and Loss Heatmap",
    height=300,  # Adjust height to fit square shape
    width=600,   # Adjust width for visual balance
    font=dict(size=12)
)

# Update x-axis title and remove it
fig.update_xaxes(title_text="", visible=False)  # Remove x-axis title
fig.update_yaxes(title_text="", visible=True)  # Keep y-axis titles visible

# Show heatmap in Streamlit
st.plotly_chart(fig)
