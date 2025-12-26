import streamlit as st
import pandas as pd
from datetime import datetime, date
import json
import os
from typing import Dict, List
import plotly.graph_objects as go
import plotly.express as px

# Import custom modules
from config_manager import ConfigManager
from trade_journal import TradeJournal
from dashboard import Dashboard
from data_storage import DataStorage

# Page configuration
st.set_page_config(
    page_title="Trading Manager Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data_storage' not in st.session_state:
    st.session_state.data_storage = DataStorage()

if 'config_manager' not in st.session_state:
    st.session_state.config_manager = ConfigManager(st.session_state.data_storage)

if 'trade_journal' not in st.session_state:
    st.session_state.trade_journal = TradeJournal(st.session_state.data_storage)

if 'dashboard' not in st.session_state:
    st.session_state.dashboard = Dashboard(st.session_state.data_storage)

def main():
    st.title("🎯 Trading Manager Pro")
    st.markdown("*Path to $1M Withdrawn - Track Every Step*")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Page",
        ["📊 Dashboard", "⚙️ Configuration", "📝 Trade Journal", "📈 Performance Analysis"]
    )
    
    # Main content based on selection
    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "⚙️ Configuration":
        show_configuration()
    elif page == "📝 Trade Journal":
        show_trade_journal()
    elif page == "📈 Performance Analysis":
        show_performance_analysis()

def show_dashboard():
    st.header("📊 Dashboard")
    
    # Load data
    accounts = st.session_state.data_storage.load_accounts()
    trades = st.session_state.data_storage.load_trades()
    withdrawals = st.session_state.data_storage.load_withdrawals()
    
    # Goal tracking
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_withdrawn = sum(w['amount'] for w in withdrawals if w.get('status') == 'paid')
        progress = min(total_withdrawn / 1000000 * 100, 100)
        st.metric("Total Withdrawn", f"${total_withdrawn:,.2f}")
        st.progress(progress / 100)
        st.caption(f"{progress:.2f}% to $1M Goal")
    
    with col2:
        funded_accounts = [acc for acc in accounts if acc.get('status') == 'funded']
        st.metric("Funded Accounts", len(funded_accounts))
    
    with col3:
        eval_accounts = [acc for acc in accounts if acc.get('status') == 'evaluation']
        st.metric("Evaluation Accounts", len(eval_accounts))
    
    with col4:
        reinvest_available = sum(w['amount'] for w in withdrawals 
                                if w.get('status') == 'paid' and w.get('allocation') == 'Reinvestment')
        st.metric("Reinvested", f"${reinvest_available:,.2f}")
    
    # Debt tracking
    st.subheader("💳 Debt Payoff Progress")
    col1, col2 = st.columns(2)
    with col1:
        debt_payments = sum(w['amount'] for w in withdrawals 
                          if w.get('status') == 'paid' and w.get('allocation') == 'Debt Payment')
        debt_remaining = max(0, 5000 - debt_payments)
        st.metric("Debt Paid", f"${debt_payments:,.2f}")
    with col2:
        st.metric("Remaining Debt", f"${debt_remaining:,.2f}")
        if debt_remaining > 0:
            st.progress(debt_payments / 5000)
    
    # Account overview
    st.subheader("Account Overview")
    if accounts:
        account_data = []
        for acc in accounts:
            account_size = acc.get('account_size', 0)
            current_balance = acc.get('current_balance', account_size)
            pnl = current_balance - account_size
            account_data.append({
                'Firm': acc.get('prop_firm', 'Unknown'),
                'Account': acc.get('account_number', 'N/A'),
                'Size': f"${account_size:,}",
                'Balance': f"${current_balance:,.2f}",
                'P&L': f"${pnl:+,.2f}",
                'Status': acc.get('status', 'unknown').capitalize(),
                'Style': acc.get('account_style', 'Standard')
            })
        
        df_accounts = pd.DataFrame(account_data)
        st.dataframe(df_accounts, use_container_width=True, hide_index=True)
    else:
        st.info("No accounts configured. Go to Configuration to add your accounts.")
    
    # Recent trades
    st.subheader("Recent Trades")
    if trades:
        recent_trades = sorted(trades, key=lambda x: x.get('date', ''), reverse=True)[:10]
        trade_data = []
        for t in recent_trades:
            trade_data.append({
                'Date': t.get('date', 'N/A'),
                'Symbol': t.get('symbol', 'N/A'),
                'Direction': t.get('direction', 'N/A'),
                'P&L': f"${t.get('pnl_net', 0):+,.2f}",
                'Playbook': t.get('playbook', 'N/A'),
                'Rules': '✓' if t.get('followed_rules') else '✗'
            })
        df_trades = pd.DataFrame(trade_data)
        st.dataframe(df_trades, use_container_width=True, hide_index=True)
    else:
        st.info("No trades logged yet.")

def show_configuration():
    st.header("⚙️ Configuration")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Prop Firms", "Accounts", "Playbooks", "Withdrawals"])
    
    with tab1:
        st.session_state.config_manager.manage_prop_firms()
    
    with tab2:
        st.session_state.config_manager.manage_accounts()
    
    with tab3:
        st.session_state.config_manager.manage_playbooks()
    
    with tab4:
        st.session_state.config_manager.manage_withdrawals()

def show_trade_journal():
    st.header("📝 Trade Journal")
    st.session_state.trade_journal.show_journal()

def show_performance_analysis():
    st.header("📈 Performance Analysis")
    st.session_state.dashboard.show_performance_analysis()

if __name__ == "__main__":
    main()