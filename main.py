import streamlit as st
import pandas as pd
from datetime import datetime, date
import json
import os
from typing import Dict, List

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
    st.markdown("*Path to $1M Payouts - Track Every Step*")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Page",
        ["📊 Dashboard", "⚙️ Configuration", "📝 Trade Journal", "📈 Performance Analysis"]
    )
    
    # Quick stats in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("Quick Stats")
    
    withdrawals = st.session_state.data_storage.load_withdrawals()
    trades = st.session_state.data_storage.load_trades()
    
    total_withdrawn = sum(w.get('amount', 0) for w in withdrawals)
    st.sidebar.metric("Total Withdrawn", f"${total_withdrawn:,.2f}")
    
    if trades:
        today_trades = [t for t in trades if t.get('date') == date.today().isoformat()]
        today_pnl = sum(t.get('pnl', 0) for t in today_trades)
        st.sidebar.metric("Today's P&L", f"${today_pnl:+,.2f}")
        
        a_b_trades = len([t for t in trades if t.get('grade') in ['A', 'B']])
        total_trades = len(trades)
        st.sidebar.metric("A/B Setup Rate", f"{a_b_trades / total_trades * 100:.0f}%" if total_trades > 0 else "N/A")
    
    # Goal progress
    goal = 1000000
    progress = min(total_withdrawn / goal * 100, 100)
    st.sidebar.progress(progress / 100)
    st.sidebar.caption(f"{progress:.2f}% to $1M Goal")
    
    st.sidebar.markdown("---")
    
    # Backup button
    if st.sidebar.button("📦 Create Backup"):
        backup_file = st.session_state.data_storage.create_backup()
        st.sidebar.success(f"Backup created: {backup_file}")
    
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
        total_withdrawn = sum(w['amount'] for w in withdrawals)
        progress = min(total_withdrawn / 1000000 * 100, 100)
        st.metric("Total Withdrawn", f"${total_withdrawn:,.2f}")
        st.progress(progress / 100)
        st.caption(f"{progress:.2f}% to $1M Goal")
    
    with col2:
        funded_accounts = [acc for acc in accounts if acc['status'] == 'funded']
        st.metric("Funded Accounts", len(funded_accounts))
    
    with col3:
        eval_accounts = [acc for acc in accounts if acc['status'] == 'evaluation']
        st.metric("Evaluation Accounts", len(eval_accounts))
    
    with col4:
        loan_repaid = sum(w['amount'] for w in withdrawals if w.get('use_type') == 'Loan Repayment')
        st.metric("Loan Repaid", f"${loan_repaid:,.2f}")
    
    # Today's check-in status
    checkin = st.session_state.data_storage.get_today_checkin()
    if checkin:
        if checkin.get('approved_to_trade'):
            st.success("✅ Pre-market check-in complete. You're cleared to trade.")
        else:
            st.error("🚫 Pre-market check-in flagged issues. Review before trading.")
    else:
        st.warning("⚠️ No pre-market check-in today. Complete it in Trade Journal → Daily Check-in")
    
    # Account overview
    st.subheader("Account Overview")
    if accounts:
        for acc in accounts:
            status_emoji = {"funded": "✅", "evaluation": "📝", "blown": "❌", "payout_pending": "💰"}.get(acc['status'], "❓")
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"{status_emoji} **{acc['name']}** ({acc['firm']})")
            with col2:
                st.write(f"${acc.get('balance', acc.get('size', 0)):,.2f}")
            with col3:
                st.write(acc['status'].title())
    else:
        st.info("No accounts configured. Go to Configuration to add your accounts.")
    
    # Recent trades with grades
    st.subheader("Recent Trades")
    if trades:
        recent_trades = sorted(trades, key=lambda x: x['date'], reverse=True)[:10]
        for trade in recent_trades:
            grade = trade.get('grade', 'C')
            grade_emoji = {'A': '🟢', 'B': '🟡', 'C': '🟠', 'F': '🔴'}.get(grade, '⚪')
            pnl = trade.get('pnl', 0)
            pnl_color = "green" if pnl > 0 else "red"
            
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            with col1:
                st.write(f"{trade['date']} - {trade.get('instrument', 'N/A')}")
            with col2:
                st.write(f"{grade_emoji} {grade}")
            with col3:
                st.markdown(f":{pnl_color}[${pnl:+,.2f}]")
            with col4:
                st.write(trade.get('playbook', 'N/A'))
    else:
        st.info("No trades logged yet. Start journaling in Trade Journal!")

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
