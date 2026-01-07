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
from psychological_manager import PsychologicalManager

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

if 'psychological_manager' not in st.session_state:
    st.session_state.psychological_manager = PsychologicalManager(st.session_state.data_storage)

def main():
    # Check trading clearance status for sidebar alert
    clearance = st.session_state.psychological_manager.get_trading_clearance()
    
    st.title("🎯 Trading Manager Pro")
    st.markdown("*Path to $1M Annual Payouts - Every Trade Matters*")
    
    # Prominent clearance status at top
    if clearance['status'] == 'RED':
        st.error(f"🚫 {clearance['message']}")
    elif clearance['status'] == 'YELLOW':
        st.warning(f"⚠️ {clearance['message']}")
    elif clearance['status'] == 'GREEN':
        st.success(f"✅ {clearance['message']}")
    else:
        st.info(f"ℹ️ {clearance['message']}")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    
    # Highlight psychological check-in
    st.sidebar.markdown("### 🧠 Discipline System")
    page = st.sidebar.radio(
        "Pre-Trading",
        ["🚦 Trading Clearance", "📝 Daily Check-In", "📅 Check-In History"],
        label_visibility="collapsed"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Trading Operations")
    
    if page in ["🚦 Trading Clearance", "📝 Daily Check-In", "📅 Check-In History"]:
        pass  # Already selected above
    else:
        page = st.sidebar.selectbox(
            "Select Page",
            ["📊 Dashboard", "⚙️ Configuration", "📒 Trade Journal", "📈 Performance Analysis"]
        )
    
    # Main content based on selection
    if page == "🚦 Trading Clearance":
        show_clearance_status()
    elif page == "📝 Daily Check-In":
        show_daily_checkin()
    elif page == "📅 Check-In History":
        show_checkin_history()
    elif page == "📊 Dashboard":
        show_dashboard()
    elif page == "⚙️ Configuration":
        show_configuration()
    elif page == "📒 Trade Journal":
        show_trade_journal()
    elif page == "📈 Performance Analysis":
        show_performance_analysis()

def show_clearance_status():
    """Show current trading clearance status."""
    st.session_state.psychological_manager.show_clearance_dashboard()

def show_daily_checkin():
    """Show daily psychological check-in form."""
    st.session_state.psychological_manager.show_daily_checkin_form()

def show_checkin_history():
    """Show historical check-in data."""
    st.session_state.psychological_manager.show_history()

def show_dashboard():
    st.header("📊 Dashboard")
    
    # Add clearance widget at top
    clearance = st.session_state.psychological_manager.get_trading_clearance()
    if not clearance['cleared']:
        st.warning("⚠️ Trading operations restricted. Complete your daily check-in and resolve any red flags.")
    
    # Load data
    accounts = st.session_state.data_storage.load_accounts()
    trades = st.session_state.data_storage.load_trades()
    withdrawals = st.session_state.data_storage.load_withdrawals()
    
    # Goal tracking
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_withdrawn = sum(w['amount'] for w in withdrawals)
        progress = min(total_withdrawn / 1000000 * 100, 100)
        st.metric("Total Withdrawn", f"${total_withdrawn:,.2f}")
        st.progress(progress / 100)
        st.caption(f"{progress:.1f}% to $1M Goal")
    
    with col2:
        funded_accounts = [acc for acc in accounts if acc['status'] == 'funded']
        st.metric("Funded Accounts", len(funded_accounts))
    
    with col3:
        eval_accounts = [acc for acc in accounts if acc['status'] == 'evaluation']
        st.metric("Evaluation Accounts", len(eval_accounts))
    
    with col4:
        # Next milestone calculation
        if total_withdrawn < 5000:
            st.metric("Next Milestone", "$5K", delta="Loan Repayment")
        elif total_withdrawn < 20000:
            st.metric("Next Milestone", "$20K", delta="Scale Phase 1")
        else:
            st.metric("Next Milestone", "$100K", delta="Multiple Accounts")
    
    # Account overview
    st.subheader("Account Overview")
    if accounts:
        df_accounts = pd.DataFrame(accounts)
        st.dataframe(df_accounts, use_container_width=True)
    else:
        st.info("No accounts configured. Go to Configuration to add your accounts.")
    
    # Recent trades
    st.subheader("Recent Trades")
    if trades:
        recent_trades = sorted(trades, key=lambda x: x['date'], reverse=True)[:10]
        df_trades = pd.DataFrame(recent_trades)
        st.dataframe(df_trades, use_container_width=True)

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
    st.header("📒 Trade Journal")
    
    # Check clearance before allowing trade entry
    clearance = st.session_state.psychological_manager.get_trading_clearance()
    
    if not clearance['cleared']:
        st.error("🚫 Trading journal locked. You are not cleared for trading today.")
        st.info("👉 Complete your daily check-in and resolve red flags to unlock trading.")
        
        if st.button("Go to Daily Check-In"):
            st.session_state.page = "📝 Daily Check-In"
            st.rerun()
        
        return
    
    if clearance['status'] == 'YELLOW':
        st.warning("⚠️ Caution: Trading with restrictions today")
        if 'restrictions' in clearance:
            for restriction in clearance['restrictions']:
                st.markdown(f"- {restriction}")
    
    st.session_state.trade_journal.show_journal()

def show_performance_analysis():
    st.header("📈 Performance Analysis")
    st.session_state.dashboard.show_performance_analysis()

if __name__ == "__main__":
    main()
