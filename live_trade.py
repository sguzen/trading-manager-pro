import streamlit as st
from datetime import datetime, date, time
from typing import Dict, List, Tuple

class LiveTradeSession:
    def __init__(self, data_storage):
        self.data_storage = data_storage
    
    def calculate_grade(self, must_have_checked: Dict[str, bool], 
                       conditions_checked: Dict[str, bool]) -> Tuple[str, str]:
        """
        Calculate grade based on checked conditions.
        - All must-haves required or F
        - Highest unlocked grade from conditions wins
        - Default to C if must-haves met but no conditions
        """
        settings = self.data_storage.load_settings()
        must_have_rules = settings.get('must_have_rules', [])
        conditions = settings.get('conditions', [])
        sizing = settings.get('position_sizing', {})
        
        # Safe defaults
        default_sizing = {
            "A": {"drawdown_pct": 50, "label": "Full Size"},
            "B": {"drawdown_pct": 30, "label": "Reduced"},
            "C": {"drawdown_pct": 15, "label": "Minimum"},
            "F": {"drawdown_pct": 0, "label": "NO TRADE"}
        }
        
        # Check must-haves
        if must_have_rules:
            all_must_have = all(must_have_checked.get(f"must_{i}", False) 
                               for i in range(len(must_have_rules)))
            if not all_must_have:
                f_info = sizing.get('F', default_sizing['F'])
                dd = f_info.get('drawdown_pct', 0)
                lbl = f_info.get('label', 'NO TRADE')
                return "F", f"{dd}% ({lbl})"
        
        # Find highest grade from checked conditions
        highest_grade = "C"  # Default if must-haves met
        
        for i, cond in enumerate(conditions):
            if conditions_checked.get(f"cond_{i}", False):
                unlocks = cond.get('unlocks', 'C')
                if unlocks == "A":
                    highest_grade = "A"
                elif unlocks == "B" and highest_grade != "A":
                    highest_grade = "B"
        
        size_info = sizing.get(highest_grade, default_sizing.get(highest_grade, {}))
        dd = size_info.get('drawdown_pct', 0)
        lbl = size_info.get('label', highest_grade)
        size_label = f"{dd}% ({lbl})"
        
        return highest_grade, size_label
    
    def render_sidebar(self):
        settings = self.data_storage.load_settings()
        must_have_rules = settings.get('must_have_rules', [])
        conditions = settings.get('conditions', [])
        
        st.sidebar.markdown("---")
        st.sidebar.header("🎯 Live Trade Grader")
        
        if not must_have_rules and not conditions:
            st.sidebar.warning("No rules configured. Go to **Settings > Grade Rules**")
            return
        
        # Init session state
        if 'live_active' not in st.session_state:
            st.session_state.live_active = False
        if 'must_checked' not in st.session_state:
            st.session_state.must_checked = {}
        if 'cond_checked' not in st.session_state:
            st.session_state.cond_checked = {}
        
        # Start/Clear
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("🟢 Start", disabled=st.session_state.live_active):
                st.session_state.live_active = True
                st.session_state.must_checked = {f"must_{i}": False for i in range(len(must_have_rules))}
                st.session_state.cond_checked = {f"cond_{i}": False for i in range(len(conditions))}
                st.rerun()
        with col2:
            if st.button("🔴 Clear", disabled=not st.session_state.live_active):
                st.session_state.live_active = False
                st.session_state.must_checked = {}
                st.session_state.cond_checked = {}
                st.rerun()
        
        if not st.session_state.live_active:
            st.sidebar.info("Click **Start** when stalking a setup")
            return
        
        # Must-haves
        if must_have_rules:
            st.sidebar.markdown("### 🔒 Must-Have")
            for i, rule in enumerate(must_have_rules):
                key = f"must_{i}"
                st.session_state.must_checked[key] = st.sidebar.checkbox(
                    rule, value=st.session_state.must_checked.get(key, False),
                    key=f"live_must_{i}"
                )
        
        # Conditions (unified list)
        if conditions:
            st.sidebar.markdown("### 📋 Conditions")
            for i, cond in enumerate(conditions):
                key = f"cond_{i}"
                grade_emoji = {"A": "🟢", "B": "🟡", "C": "🟠"}.get(cond.get('unlocks', 'C'), "⚪")
                label = f"{cond['condition']} [{grade_emoji}]"
                st.session_state.cond_checked[key] = st.sidebar.checkbox(
                    label, value=st.session_state.cond_checked.get(key, False),
                    key=f"live_cond_{i}"
                )
        
        # Calculate grade
        grade, size_label = self.calculate_grade(
            st.session_state.must_checked,
            st.session_state.cond_checked
        )
        
        st.sidebar.markdown("---")
        
        # Grade display
        grade_emoji = {"A": "🟢", "B": "🟡", "C": "🟠", "F": "🔴"}.get(grade, "⚪")
        st.sidebar.markdown(f"## {grade_emoji} Grade: **{grade}**")
        
        # Must-have status
        if must_have_rules:
            must_count = sum(1 for v in st.session_state.must_checked.values() if v)
            if must_count < len(must_have_rules):
                st.sidebar.error(f"⚠️ Must-Have: {must_count}/{len(must_have_rules)}")
            else:
                st.sidebar.success(f"✓ Must-Have: {must_count}/{len(must_have_rules)}")
        
        # Position sizing
        st.sidebar.markdown("---")
        if grade == "F":
            st.sidebar.error(f"⛔ {size_label}")
        elif grade == "C":
            st.sidebar.warning(f"⚠️ {size_label}")
        elif grade == "B":
            st.sidebar.info(f"📊 {size_label}")
        else:
            st.sidebar.success(f"✅ {size_label}")
        
        # Log trade button
        st.sidebar.markdown("---")
        if st.sidebar.button("📝 Log This Trade", type="primary"):
            st.session_state.show_trade_entry_form = True
            st.session_state.trade_entry_grade = grade
            st.session_state.trade_entry_must = st.session_state.must_checked.copy()
            st.session_state.trade_entry_cond = st.session_state.cond_checked.copy()
    
    def render_trade_entry_modal(self):
        if not st.session_state.get('show_trade_entry_form', False):
            return
        
        settings = self.data_storage.load_settings()
        accounts = self.data_storage.load_accounts()
        must_have_rules = settings.get('must_have_rules', [])
        conditions = settings.get('conditions', [])
        
        st.header("📝 Log Trade")
        
        grade = st.session_state.get('trade_entry_grade', '?')
        grade_colors = {"A": "green", "B": "orange", "C": "red", "F": "red"}
        st.markdown(f"### Grade: :{grade_colors.get(grade, 'gray')}[**{grade}**]")
        
        # Show checked rules
        with st.expander("Rules Checked", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**🔒 Must-Have:**")
                must_checked = st.session_state.get('trade_entry_must', {})
                for i, rule in enumerate(must_have_rules):
                    icon = "✅" if must_checked.get(f"must_{i}", False) else "❌"
                    st.write(f"{icon} {rule}")
            
            with col2:
                st.write("**📋 Conditions:**")
                cond_checked = st.session_state.get('trade_entry_cond', {})
                for i, cond in enumerate(conditions):
                    icon = "✅" if cond_checked.get(f"cond_{i}", False) else "⬜"
                    grade_emoji = {"A": "🟢", "B": "🟡", "C": "🟠"}.get(cond.get('unlocks', 'C'), "⚪")
                    st.write(f"{icon} {cond['condition']} [{grade_emoji}]")
        
        with st.form("trade_entry"):
            col1, col2 = st.columns(2)
            
            with col1:
                active_accounts = [a for a in accounts if a.get('status') in ['evaluation', 'funded']]
                if active_accounts:
                    account_options = [f"{a.get('prop_firm', '?')} - ${a.get('account_size', 0):,} ({a.get('account_number', 'N/A')})" 
                                      for a in active_accounts]
                    selected_account = st.selectbox("Account", account_options)
                else:
                    st.warning("No active accounts")
                    selected_account = None
                
                symbol = st.text_input("Symbol", value="ES")
                direction = st.selectbox("Direction", ["Long", "Short"])
                position_size = st.number_input("Contracts", min_value=1, value=1)
                trade_date = st.date_input("Date", value=date.today())
            
            with col2:
                entry_price = st.number_input("Entry", min_value=0.0, step=0.25)
                stop_loss = st.number_input("Stop", min_value=0.0, step=0.25)
                take_profit = st.number_input("Target", min_value=0.0, step=0.25)
                entry_time = st.time_input("Entry Time", value=time(9, 30))
                exit_time = st.time_input("Exit Time", value=time(10, 0))
            
            st.subheader("Result")
            col1, col2, col3 = st.columns(3)
            with col1:
                pnl_gross = st.number_input("Gross P&L ($)", value=0.0, step=25.0)
            with col2:
                commission = st.number_input("Commission ($)", value=8.4, step=0.1)
            with col3:
                pnl_net = pnl_gross - commission
                st.metric("Net P&L", f"${pnl_net:.2f}")
            
            screenshot_url = st.text_input("Screenshot URL", placeholder="TradingView link")
            notes = st.text_area("Notes", placeholder="What happened?")
            
            col1, col2 = st.columns(2)
            with col1:
                emotional_state = st.slider("Emotional (1=Calm, 10=Tilted)", 1, 10, 5)
            with col2:
                would_repeat = st.checkbox("Would take again")
            
            col1, col2 = st.columns(2)
            submit = col1.form_submit_button("Save Trade", type="primary")
            cancel = col2.form_submit_button("Cancel")
            
            if submit and selected_account and active_accounts:
                acc_idx = account_options.index(selected_account)
                selected_acc = active_accounts[acc_idx]
                
                trade_data = {
                    "date": trade_date.isoformat(),
                    "entry_time": entry_time.isoformat(),
                    "exit_time": exit_time.isoformat(),
                    "account": selected_account,
                    "account_id": selected_acc.get('account_number', ''),
                    "playbook": "Main Setup",
                    "symbol": symbol,
                    "direction": direction,
                    "position_size": position_size,
                    "entry_price": entry_price,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "pnl_gross": pnl_gross,
                    "pnl_net": pnl_net,
                    "commission": commission,
                    "grade": grade,
                    "must_have_compliance": st.session_state.get('trade_entry_must', {}),
                    "conditions_compliance": st.session_state.get('trade_entry_cond', {}),
                    "emotional_state": emotional_state,
                    "would_repeat": would_repeat,
                    "followed_rules": grade in ["A", "B"],
                    "screenshot_url": screenshot_url,
                    "notes": notes,
                    "was_planned": True,
                }
                
                # Update account balance
                all_accounts = self.data_storage.load_accounts()
                for i, acc in enumerate(all_accounts):
                    if acc.get('account_number') == selected_acc.get('account_number'):
                        all_accounts[i]['current_balance'] = acc.get('current_balance', acc.get('account_size', 0)) + pnl_net
                        all_accounts[i]['updated_at'] = datetime.now().isoformat()
                        break
                self.data_storage.save_accounts(all_accounts)
                
                self.data_storage.add_trade(trade_data)
                
                # Clear
                st.session_state.show_trade_entry_form = False
                st.session_state.live_active = False
                st.session_state.must_checked = {}
                st.session_state.cond_checked = {}
                
                st.success(f"Logged! Grade: {grade}, P&L: ${pnl_net:+,.2f}")
                st.balloons()
                st.rerun()
            
            if cancel:
                st.session_state.show_trade_entry_form = False
                st.rerun()
