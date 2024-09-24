import streamlit as st
import numpy as np
from scipy.stats import norm

def black_scholes(S, K, T, r, sigma, option_type='call'):
    # Calculate d1 and d2
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type == 'call':
        option_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    elif option_type == 'put':
        option_price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    else:
        raise ValueError("Invalid option type. Use 'call' or 'put'.")

    return option_price

# Streamlit UI
st.title("Black-Scholes Option Pricing Calculator")

# Input fields
S = st.number_input("Stock Price (S):", value=100.0, step=0.01)
K = st.number_input("Strike Price (K):", value=100.0, step=0.01)
T = st.number_input("Time to Expiry (T in years):", value=1.0, step=0.01)
r = st.number_input("Risk-Free Rate (r):", value=0.05, step=0.01)
sigma = st.number_input("Volatility (σ):", value=0.2, step=0.01)

# Calculate button
if st.button("Calculate Prices"):
    call_price = black_scholes(S, K, T, r, sigma, option_type='call')
    put_price = black_scholes(S, K, T, r, sigma, option_type='put')

    # Custom CSS to style the buttons with market-inspired colors and larger size
    st.markdown(
        """
        <style>
        .buy-button {
            background-color: #28a745; /* Green tone for "Call" */
            color: white;
            padding: 40px 80px; /* Make buttons bigger */
            font-size: 30px; /* Bigger text size */
            border: none;
            border-radius: 10px;
            margin: 10px;
            cursor: default;
        }
        .sell-button {
            background-color: #dc3545; /* Red tone for "Put" */
            color: white;
            padding: 40px 80px; /* Make buttons bigger */
            font-size: 30px; /* Bigger text size */
            border: none;
            border-radius: 10px;
            margin: 10px;
            cursor: default;
        }
        </style>
        """, unsafe_allow_html=True
    )

    # Display Buy (Call) and Sell (Put) buttons with prices inside the buttons
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<button class="buy-button">Call: ${call_price:.2f}</button>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<button class="sell-button">Put: ${put_price:.2f}</button>', unsafe_allow_html=True)

