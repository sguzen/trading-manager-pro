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
    st.title("🎯 Trading Manager Pro")
    st.markdown("*Path to $1M Annual Payouts - Track Every Step*")
    
    # Load settings to check if we should show clearance banner
    settings = st.session_state.data_storage.load_settings()
    show_banner = settings.get('show_clearance_banner', True)
    
    # Show trading clearance status at the top (if enabled in settings)
    if show_banner:
        clearance = st.session_state.psychological_manager.get_trading_clearance()
        if clearance['status'] == 'RED':
            st.error(f"🚫 {clearance['message']}")
        elif clearance['status'] == 'YELLOW':
            st.warning(f"⚠️ {clearance['message']}")
        elif clearance['status'] == 'GREEN':
            st.success(f"✅ {clearance['message']}")
        elif clearance['status'] == 'NO_CHECKIN':
            st.info(f"ℹ️ {clearance['message']}")
    
    # Sidebar navigation - RESTORED YOUR ORIGINAL STRUCTURE
    st.sidebar.title("Navigation")
    
    # Add psychological check-in section at top of sidebar
    with st.sidebar.expander("🧠 Daily Discipline", expanded=False):
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("📝 Check-In", use_container_width=True):
                st.session_state.page_override = "Daily Check-In"
        with col2:
            if st.button("🚦 Status", use_container_width=True):
                st.session_state.page_override = "Trading Clearance"
    
    st.sidebar.markdown("---")
    
    # Your original navigation
    page = st.sidebar.selectbox(
        "Select Page",
        ["📊 Dashboard", "⚙️ Configuration", "📝 Trade Journal", "📈 Performance Analysis", "⚙️ Settings"]
    )
    
    # Check for page override from buttons
    if 'page_override' in st.session_state:
        page = st.session_state.page_override
        del st.session_state.page_override
    
    # Main content based on selection - YOUR ORIGINAL PAGES
    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "⚙️ Configuration":
        show_configuration()
    elif page == "📝 Trade Journal":
        show_trade_journal()
    elif page == "📈 Performance Analysis":
        show_performance_analysis()
    elif page == "⚙️ Settings":
        show_settings()
    elif page == "Daily Check-In":
        show_daily_checkin()
    elif page == "Trading Clearance":
        show_clearance_status()

def show_clearance_status():
    """Show current trading clearance status."""
    st.session_state.psychological_manager.show_clearance_dashboard()
    
    if st.button("← Back to Dashboard"):
        st.session_state.page_override = "📊 Dashboard"
        st.rerun()

def show_daily_checkin():
    """Show daily psychological check-in form."""
    st.session_state.psychological_manager.show_daily_checkin_form()
    
    if st.button("← Back to Dashboard"):
        st.session_state.page_override = "📊 Dashboard"
        st.rerun()

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
        progress = min(total_withdrawn / 5000000 * 100, 100)
        st.metric("Total Withdrawn", f"${total_withdrawn:,.2f}")
        st.progress(progress / 100)
        st.caption(f"{progress:.1f}% to $5M Goal")
    
    with col2:
        funded_accounts = [acc for acc in accounts if acc['status'] == 'funded']
        st.metric("Funded Accounts", len(funded_accounts))
    
    with col3:
        eval_accounts = [acc for acc in accounts if acc['status'] == 'evaluation']
        st.metric("Evaluation Accounts", len(eval_accounts))
    
    with col4:
        available_for_reinvest = sum(w['amount'] for w in withdrawals if not w.get('used_for_personal', False))
        st.metric("Available for Reinvestment", f"${available_for_reinvest:,.2f}")
    
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
    st.header("📝 Trade Journal")
    
    # Load settings to check enforcement level
    settings = st.session_state.data_storage.load_settings()
    enforcement = settings.get('enforce_clearance', 'Soft (Warning Only)')
    
    # Check clearance status
    clearance = st.session_state.psychological_manager.get_trading_clearance()
    
    # Handle different enforcement levels
    if clearance['status'] == 'RED':
        if enforcement == "Strict (Hard Block)":
            st.error("🚫 Trading journal LOCKED. You have RED clearance status.")
            st.info("👉 Complete your daily check-in and resolve red flags to unlock trading.")
            if st.button("Go to Daily Check-In"):
                st.session_state.page_override = "Daily Check-In"
                st.rerun()
            return
        
        elif enforcement == "Medium (Acknowledgment Required)":
            st.warning("⚠️ You have RED clearance status. Trading against clearance status increases risk of self-sabotage.")
            if not st.checkbox("I acknowledge the risks and choose to proceed"):
                st.info("Complete your check-in or acknowledge risks to continue.")
                return
            
            # Track override if setting enabled
            if settings.get('track_overrides', True):
                st.caption("⚠️ Override logged for pattern analysis")
        
        else:  # Soft warning
            st.warning("⚠️ You have RED clearance status. Consider completing your check-in before trading.")
    
    elif clearance['status'] == 'YELLOW':
        st.info(f"ℹ️ {clearance['message']}")
        if 'restrictions' in clearance:
            with st.expander("View Today's Restrictions"):
                for restriction in clearance['restrictions']:
                    st.markdown(f"- {restriction}")
    
    # Show trade journal
    st.session_state.trade_journal.show_journal()

def show_performance_analysis():
    st.header("📈 Performance Analysis")
    st.session_state.dashboard.show_performance_analysis()

def show_settings():
    st.header("⚙️ Settings")
    
    settings = st.session_state.data_storage.load_settings()
    
    st.subheader("Application Settings")
    
    # Theme/Display Settings
    with st.expander("🎨 Display Settings", expanded=True):
        default_view = st.selectbox(
            "Default Dashboard View",
            ["Overview", "Accounts", "Trades", "Performance"],
            index=["Overview", "Accounts", "Trades", "Performance"].index(
                settings.get('default_view', 'Overview')
            )
        )
        
        show_clearance_banner = st.checkbox(
            "Show Trading Clearance Banner",
            value=settings.get('show_clearance_banner', True),
            help="Display psychological clearance status at top of pages"
        )
    
    # Trading Rules Settings
    with st.expander("📋 Trading Rules", expanded=True):
        enforce_clearance = st.selectbox(
            "Clearance Enforcement Level",
            ["Soft (Warning Only)", "Medium (Acknowledgment Required)", "Strict (Hard Block)"],
            index=["Soft (Warning Only)", "Medium (Acknowledgment Required)", "Strict (Hard Block)"].index(
                settings.get('enforce_clearance', 'Soft (Warning Only)')
            ),
            help="How strictly to enforce psychological clearance requirements"
        )
        
        track_overrides = st.checkbox(
            "Track Clearance Overrides",
            value=settings.get('track_overrides', True),
            help="Log when you trade despite RED/YELLOW warnings"
        )
    
    # Notification Settings
    with st.expander("🔔 Notifications & Reminders", expanded=False):
        remind_checkin = st.checkbox(
            "Remind to Complete Check-In",
            value=settings.get('remind_checkin', True),
            help="Show reminder if check-in not completed"
        )
        
        end_of_day_summary = st.checkbox(
            "End of Day Summary",
            value=settings.get('end_of_day_summary', False),
            help="Generate end-of-day trading summary (coming in Phase 4)"
        )
    
    # Data Management
    with st.expander("💾 Data Management", expanded=False):
        st.markdown("**Backup & Restore**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📦 Create Backup", use_container_width=True):
                backup_path = st.session_state.data_storage.backup_all_data()
                st.success(f"✅ Backup created: {backup_path}")
        
        with col2:
            if st.button("🗑️ Clear All Data", use_container_width=True, type="secondary"):
                st.warning("⚠️ This action cannot be undone!")
                if st.checkbox("I understand this will delete all data"):
                    st.error("Please create a backup first, then contact support for data clearing.")
        
        st.markdown("---")
        st.markdown("**Import & Export**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Export Data
            if st.button("📤 Export All Data (JSON)", use_container_width=True):
                export_data = st.session_state.data_storage.export_all_data()
                json_str = json.dumps(export_data, indent=2, default=str)
                
                st.download_button(
                    label="⬇️ Download JSON File",
                    data=json_str,
                    file_name=f"trading_manager_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
        
        with col2:
            # Import Data
            uploaded_file = st.file_uploader(
                "📥 Import Data (JSON)",
                type=['json'],
                help="Upload a previously exported JSON file"
            )
            
            if uploaded_file is not None:
                try:
                    import_data = json.load(uploaded_file)
                    
                    # Show preview of what will be imported (no nested expander)
                    st.markdown("**📋 Preview Import Data:**")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.write(f"• Prop Firms: **{len(import_data.get('prop_firms', []))}**")
                        st.write(f"• Accounts: **{len(import_data.get('accounts', []))}**")
                        st.write(f"• Playbooks: **{len(import_data.get('playbooks', []))}**")
                        st.write(f"• Trades: **{len(import_data.get('trades', []))}**")
                    with col_b:
                        st.write(f"• Withdrawals: **{len(import_data.get('withdrawals', []))}**")
                        st.write(f"• Check-ins: **{len(import_data.get('daily_checkins', []) or import_data.get('psychological_checkins', []))}**")
                        st.write(f"• Journal Entries: **{len(import_data.get('daily_entries', []))}**")
                    
                    if 'settings' in import_data:
                        st.success("✓ Settings data included")
                    
                    st.warning("⚠️ This will overwrite existing data!")
                    
                    if st.button("✅ Confirm Import", type="primary", use_container_width=True):
                        if st.session_state.data_storage.import_all_data(import_data):
                            st.success("✅ Data imported successfully!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ Error importing data. Check console for details.")
                except json.JSONDecodeError as e:
                    st.error(f"❌ Invalid JSON file: {str(e)}")
                except Exception as e:
                    st.error(f"❌ Error reading file: {str(e)}")
                    import traceback
                    st.text("Error Details:")
                    st.code(traceback.format_exc())
    
    # Save Settings Button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("💾 Save Settings", type="primary", use_container_width=True):
            settings_data = {
                'default_view': default_view,
                'show_clearance_banner': show_clearance_banner,
                'enforce_clearance': enforce_clearance,
                'track_overrides': track_overrides,
                'remind_checkin': remind_checkin,
                'end_of_day_summary': end_of_day_summary,
                'last_updated': datetime.now().isoformat()
            }
            
            if st.session_state.data_storage.save_settings(settings_data):
                st.success("✅ Settings saved successfully!")
                st.rerun()
            else:
                st.error("❌ Error saving settings")

if __name__ == "__main__":
    main()