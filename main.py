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
from live_trade import LiveTradeSession
from settings_manager import SettingsManager
from psychological_manager import PsychologicalManager

# Page configuration
st.set_page_config(
    page_title="Trading Manager Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_data_storage():
    """Get or create DataStorage instance"""
    if 'data_storage' not in st.session_state or st.session_state.data_storage is None:
        st.session_state.data_storage = DataStorage()
    return st.session_state.data_storage

def get_config_manager():
    """Get or create ConfigManager instance"""
    if 'config_manager' not in st.session_state or st.session_state.config_manager is None:
        st.session_state.config_manager = ConfigManager(get_data_storage())
    return st.session_state.config_manager

def get_trade_journal():
    """Get or create TradeJournal instance"""
    if 'trade_journal' not in st.session_state or st.session_state.trade_journal is None:
        st.session_state.trade_journal = TradeJournal(get_data_storage())
    return st.session_state.trade_journal

def get_dashboard():
    """Get or create Dashboard instance"""
    if 'dashboard' not in st.session_state or st.session_state.dashboard is None:
        st.session_state.dashboard = Dashboard(get_data_storage())
    return st.session_state.dashboard

def get_live_trade():
    """Get or create LiveTradeSession instance"""
    if 'live_trade' not in st.session_state or st.session_state.live_trade is None:
        st.session_state.live_trade = LiveTradeSession(get_data_storage())
    return st.session_state.live_trade

def get_settings_manager():
    """Get or create SettingsManager instance"""
    if 'settings_manager' not in st.session_state or st.session_state.settings_manager is None:
        st.session_state.settings_manager = SettingsManager(get_data_storage())
    return st.session_state.settings_manager

def get_psychological_manager():
    """Get or create PsychologicalManager instance"""
    if 'psychological_manager' not in st.session_state or st.session_state.psychological_manager is None:
        st.session_state.psychological_manager = PsychologicalManager(get_data_storage())
    return st.session_state.psychological_manager

def main():
    # Sidebar navigation
    st.sidebar.title("📈 Trading Manager")
    
    # Add Daily Discipline section at top
    with st.sidebar.expander("🧠 Daily Discipline", expanded=False):
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("📝 Check-In", use_container_width=True, key="psych_checkin"):
                st.session_state.special_page = "Daily Check-In"
                st.rerun()
        with col2:
            if st.button("🚦 Status", use_container_width=True, key="psych_status"):
                st.session_state.special_page = "Trading Clearance"
                st.rerun()
    
    st.sidebar.markdown("---")
    
    # Check if on special page
    if 'special_page' in st.session_state and st.session_state.special_page:
        # Show back button
        if st.sidebar.button("⬅️ Back to Main", use_container_width=True, type="primary"):
            st.session_state.special_page = None
            st.rerun()
        
        # Render special page
        if st.session_state.special_page == "Daily Check-In":
            show_daily_checkin()
            return
        elif st.session_state.special_page == "Trading Clearance":
            show_clearance_status()
            return
    
    # Regular navigation
    page = st.sidebar.selectbox(
        "Navigate",
        ["📊 Dashboard", "⚙️ Configuration", "📓 Trade Journal", "📈 Performance", "🔧 Settings", "💾 Backup"]
    )
    
    # Show clearance status banner (optional, can be toggled in settings)
    settings = get_data_storage().load_settings()
    if settings.get('show_clearance_banner', True):
        clearance = get_psychological_manager().get_trading_clearance()
        if clearance['status'] == 'RED':
            st.error(f"🚫 {clearance['message']}")
        elif clearance['status'] == 'YELLOW':
            st.warning(f"⚠️ {clearance['message']}")
        elif clearance['status'] == 'GREEN':
            st.success(f"✅ {clearance['message']}")
    
    # Render live trade grader in sidebar (YOUR ORIGINAL FEATURE)
    get_live_trade().render_sidebar()
    
    # Check if we need to show the trade entry modal
    if st.session_state.get('show_trade_entry_form', False):
        get_live_trade().render_trade_entry_modal()
    else:
        # Main content based on selection
        if page == "📊 Dashboard":
            show_dashboard()
        elif page == "⚙️ Configuration":
            show_configuration()
        elif page == "📓 Trade Journal":
            show_trade_journal()
        elif page == "📈 Performance":
            show_performance_analysis()
        elif page == "🔧 Settings":
            show_settings()
        elif page == "💾 Backup":
            show_backup()

def show_daily_checkin():
    """NEW - Daily psychological check-in"""
    col1, col2 = st.columns([1, 6])
    with col1:
        if st.button("⬅️ Back", use_container_width=True):
            st.session_state.special_page = None
            st.rerun()
    
    get_psychological_manager().show_daily_checkin_form()

def show_clearance_status():
    """NEW - Trading clearance dashboard"""
    col1, col2 = st.columns([1, 6])
    with col1:
        if st.button("⬅️ Back", use_container_width=True):
            st.session_state.special_page = None
            st.rerun()
    
    get_psychological_manager().show_clearance_dashboard()

def show_dashboard():
    st.title("🎯 Trading Manager Pro")
    
    data_storage = get_data_storage()
    settings = data_storage.load_settings()
    accounts = data_storage.load_accounts()
    trades = data_storage.load_trades()
    withdrawals = data_storage.load_withdrawals()
    
    # Goal tracking row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_withdrawn = sum(w['amount'] for w in withdrawals if w.get('status') == 'paid')
        goal = settings.get('goal_amount', 1000000)
        progress = min(total_withdrawn / goal * 100, 100) if goal > 0 else 0
        st.metric("Total Withdrawn", f"${total_withdrawn:,.2f}")
        st.progress(progress / 100)
        st.caption(f"{progress:.2f}% to ${goal:,.0f}")
    
    with col2:
        funded_accounts = [acc for acc in accounts if acc.get('status') == 'funded']
        st.metric("Funded Accounts", len(funded_accounts))
    
    with col3:
        eval_accounts = [acc for acc in accounts if acc.get('status') == 'evaluation']
        st.metric("Evaluation Accounts", len(eval_accounts))
    
    with col4:
        # Debt tracking - handle both old and new format
        debt_amount = settings.get('debt_amount', 5000)
        debt_paid = 0
        for w in withdrawals:
            if w.get('status') != 'paid':
                continue
            if 'allocations' in w:
                debt_paid += w['allocations'].get('debt', 0)
            elif w.get('allocation') == 'Debt Payment':
                debt_paid += w.get('amount', 0)
        
        debt_remaining = max(0, debt_amount - debt_paid)
        st.metric(f"{settings.get('debt_name', 'Debt')} Left", f"${debt_remaining:,.2f}")
        if debt_amount > 0:
            st.progress(min(debt_paid / debt_amount, 1.0))
    
    # Account overview
    st.subheader("📋 Account Overview")
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
    
    # Recent trades with grades
    st.subheader("📓 Recent Trades")
    if trades:
        recent_trades = sorted(trades, key=lambda x: x.get('date', ''), reverse=True)[:10]
        trade_data = []
        for t in recent_trades:
            grade = t.get('grade', '-')
            grade_emoji = {"A": "🟢", "B": "🟡", "C": "🟠", "F": "🔴"}.get(grade, "⚪")
            trade_data.append({
                'Date': t.get('date', 'N/A'),
                'Grade': f"{grade_emoji} {grade}",
                'Symbol': t.get('symbol', 'N/A'),
                'Direction': t.get('direction', 'N/A'),
                'P&L': f"${t.get('pnl_net', 0):+,.2f}",
                'Emotional': t.get('emotional_state', '-'),
            })
        df_trades = pd.DataFrame(trade_data)
        st.dataframe(df_trades, use_container_width=True, hide_index=True)
        
        # Quick stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total_pnl = sum(t.get('pnl_net', 0) for t in trades)
            st.metric("Total P&L", f"${total_pnl:,.2f}")
        with col2:
            wins = sum(1 for t in trades if t.get('pnl_net', 0) > 0)
            win_rate = (wins / len(trades) * 100) if trades else 0
            st.metric("Win Rate", f"{win_rate:.1f}%")
        with col3:
            a_trades = [t for t in trades if t.get('grade') == 'A']
            a_pnl = sum(t.get('pnl_net', 0) for t in a_trades)
            st.metric("A-Grade P&L", f"${a_pnl:,.2f}")
        with col4:
            f_trades = [t for t in trades if t.get('grade') == 'F']
            f_pnl = sum(t.get('pnl_net', 0) for t in f_trades)
            st.metric("F-Grade P&L", f"${f_pnl:,.2f}")
    else:
        st.info("No trades logged yet. Use the Live Trade Grader in the sidebar!")

def show_configuration():
    st.header("⚙️ Configuration")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Prop Firms", "Accounts", "Playbooks", "Withdrawals"])
    
    with tab1:
        get_config_manager().manage_prop_firms()
    
    with tab2:
        get_config_manager().manage_accounts()
    
    with tab3:
        get_config_manager().manage_playbooks()
    
    with tab4:
        get_config_manager().manage_withdrawals()

def show_trade_journal():
    st.header("📓 Trade Journal")
    get_trade_journal().show_journal()

def show_performance_analysis():
    st.header("📈 Performance Analysis")
    get_dashboard().show_performance_analysis()

def show_settings():
    """UPDATED - Merged settings"""
    st.header("🔧 Settings")
    
    tab1, tab2, tab3, tab4 = st.tabs(["💰 Financial", "📋 Grade Rules", "📊 Position Sizing", "🧠 Discipline"])
    
    with tab1:
        get_settings_manager().manage_financial_settings()
    
    with tab2:
        get_settings_manager().manage_grade_rules()
    
    with tab3:
        get_settings_manager().manage_position_sizing()
    
    with tab4:
        # NEW - Psychological settings
        show_discipline_settings()

def show_discipline_settings():
    """NEW - Discipline/Clearance settings"""
    st.subheader("🧠 Trading Discipline Settings")
    
    data_storage = get_data_storage()
    settings = data_storage.load_settings()
    
    with st.form("discipline_settings"):
        st.markdown("**Clearance System**")
        
        show_banner = st.checkbox(
            "Show clearance status banner on all pages",
            value=settings.get('show_clearance_banner', True)
        )
        
        enforcement = st.selectbox(
            "Clearance Enforcement Level",
            ["Soft (Warning Only)", "Medium (Acknowledgment Required)", "Strict (Hard Block)"],
            index=["Soft (Warning Only)", "Medium (Acknowledgment Required)", "Strict (Hard Block)"].index(
                settings.get('enforce_clearance', 'Soft (Warning Only)')
            ),
            help="How strictly to enforce psychological clearance requirements"
        )
        
        track_overrides = st.checkbox(
            "Track when I override clearance warnings",
            value=settings.get('track_overrides', True)
        )
        
        st.markdown("---")
        st.markdown("**Thresholds**")
        
        col1, col2 = st.columns(2)
        with col1:
            min_sleep = st.number_input("Minimum sleep hours", min_value=4, max_value=10, 
                                       value=settings.get('min_sleep_hours', 6))
        with col2:
            max_stress = st.number_input("Maximum stress level", min_value=1, max_value=10,
                                        value=settings.get('max_stress_level', 7))
        
        if st.form_submit_button("💾 Save Discipline Settings", type="primary"):
            settings['show_clearance_banner'] = show_banner
            settings['enforce_clearance'] = enforcement
            settings['track_overrides'] = track_overrides
            settings['min_sleep_hours'] = min_sleep
            settings['max_stress_level'] = max_stress
            data_storage.save_settings(settings)
            st.success("✅ Discipline settings saved!")
            st.rerun()

def show_backup():
    st.header("💾 Backup & Restore")
    
    data_storage = get_data_storage()
    
    st.markdown("""
    **Your data is stored locally** on Streamlit's servers and can be lost when the app restarts or redeploys.
    
    **Download backups regularly!**
    """)
    
    st.markdown("---")
    
    # DOWNLOAD BACKUP
    st.subheader("⬇️ Download Backup")
    
    all_data = data_storage.export_all_data()
    json_str = json.dumps(all_data, indent=2, default=str)
    
    # Show summary
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Trades", len(all_data.get('trades', [])))
    col2.metric("Accounts", len(all_data.get('accounts', [])))
    col3.metric("Daily Entries", len(all_data.get('daily_entries', [])))
    col4.metric("Check-ins", len(all_data.get('psychological_checkins', [])))
    
    filename = f"trading_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    st.download_button(
        label="📥 Download Full Backup",
        data=json_str,
        file_name=filename,
        mime="application/json",
        type="primary"
    )
    
    st.markdown("---")
    
    # RESTORE BACKUP
    st.subheader("⬆️ Restore from Backup")
    
    st.warning("⚠️ Restoring will **OVERWRITE** all current data!")
    
    uploaded_file = st.file_uploader("Upload backup JSON file", type=['json'])
    
    if uploaded_file is not None:
        try:
            backup_data = json.loads(uploaded_file.read().decode('utf-8'))
            
            # Show what's in the backup
            st.write("**Backup contents:**")
            col1, col2, col3, col4 = st.columns(4)
            col1.write(f"Trades: {len(backup_data.get('trades', []))}")
            col2.write(f"Accounts: {len(backup_data.get('accounts', []))}")
            col3.write(f"Daily Entries: {len(backup_data.get('daily_entries', []))}")
            col4.write(f"Check-ins: {len(backup_data.get('psychological_checkins', []) or backup_data.get('daily_checkins', []))}")
            
            if backup_data.get('exported_at'):
                st.write(f"Backup date: {backup_data['exported_at']}")
            
            # Confirm restore
            confirm = st.checkbox("I understand this will overwrite all current data")
            
            if confirm:
                if st.button("🔄 Restore Backup", type="primary"):
                    data_storage.import_data(backup_data)
                    st.success("✅ Backup restored successfully!")
                    st.balloons()
                    st.rerun()
        
        except json.JSONDecodeError:
            st.error("Invalid JSON file")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    st.markdown("---")
    
    # AUTO-BACKUP REMINDER
    st.subheader("💡 Backup Tips")
    st.markdown("""
    - **Download backup after every trading session**
    - Store backups in Google Drive, Dropbox, or your computer
    - Keep multiple versions (don't overwrite old backups)
    - Backup filename includes date/time for easy tracking
    """)

if __name__ == "__main__":
    main()