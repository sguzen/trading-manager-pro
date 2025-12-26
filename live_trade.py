import streamlit as st
from datetime import datetime, date, time
from typing import Dict, List, Tuple

class LiveTradeSession:
    """Floating sidebar for real-time trade grading and logging"""
    
    def __init__(self, data_storage):
        self.data_storage = data_storage
    
    def calculate_grade(self, must_have_checked: Dict[str, bool], 
                       a_checked: Dict[str, bool],
                       b_checked: Dict[str, bool], 
                       c_checked: Dict[str, bool]) -> Tuple[str, str]:
        """
        Calculate trade grade based on rules.
        - All must-have required or F
        - Any A-rule checked → A
        - Any B-rule checked → B
        - Any C-rule checked or just must-haves → C
        Returns: (grade, size_label)
        """
        settings = self.data_storage.load_settings()
        must_have_rules = settings.get('must_have_rules', [])
        sizing = settings.get('position_sizing', {
            "A": {"drawdown_pct": 50, "label": "Full Size"},
            "B": {"drawdown_pct": 30, "label": "Reduced"},
            "C": {"drawdown_pct": 15, "label": "Minimum"},
            "F": {"drawdown_pct": 0, "label": "NO TRADE"}
        })
        
        # Check if ALL must-have rules are checked
        all_must_have = True
        if must_have_rules:
            all_must_have = all(must_have_checked.get(f"must_{i}", False) for i in range(len(must_have_rules)))
        
        # If any must-have is missing, it's F-grade
        if not all_must_have:
            return "F", f"0% drawdown ({sizing.get('F', {}).get('label', 'NO TRADE')})"
        
        # Check grade rules in order of priority: A > B > C
        any_a = any(v for v in a_checked.values())
        any_b = any(v for v in b_checked.values())
        any_c = any(v for v in c_checked.values())
        
        if any_a:
            grade = "A"
        elif any_b:
            grade = "B"
        else:
            grade = "C"  # Default if must-haves met but no A/B rules
        
        size_info = sizing.get(grade, {"drawdown_pct": 0, "label": "Unknown"})
        size_label = f"{size_info['drawdown_pct']}% drawdown ({size_info['label']})"
        
        return grade, size_label
    
    def render_sidebar(self):
        """Render the live trade grading sidebar"""
        settings = self.data_storage.load_settings()
        must_have_rules = settings.get('must_have_rules', [])
        a_rules = settings.get('a_rules', [])
        b_rules = settings.get('b_rules', [])
        c_rules = settings.get('c_rules', [])
        
        st.sidebar.markdown("---")
        st.sidebar.header("🎯 Live Trade Grader")
        
        if not must_have_rules and not a_rules and not b_rules and not c_rules:
            st.sidebar.warning("No rules configured. Go to **Settings > Grade Rules**")
            return
        
        # Initialize session state
        if 'live_trade_active' not in st.session_state:
            st.session_state.live_trade_active = False
        if 'must_have_checked' not in st.session_state:
            st.session_state.must_have_checked = {}
        if 'a_checked' not in st.session_state:
            st.session_state.a_checked = {}
        if 'b_checked' not in st.session_state:
            st.session_state.b_checked = {}
        if 'c_checked' not in st.session_state:
            st.session_state.c_checked = {}
        
        # Start/Clear buttons
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("🟢 Start", key="start_session", disabled=st.session_state.live_trade_active):
                st.session_state.live_trade_active = True
                st.session_state.must_have_checked = {f"must_{i}": False for i in range(len(must_have_rules))}
                st.session_state.a_checked = {f"a_{i}": False for i in range(len(a_rules))}
                st.session_state.b_checked = {f"b_{i}": False for i in range(len(b_rules))}
                st.session_state.c_checked = {f"c_{i}": False for i in range(len(c_rules))}
                st.rerun()
        
        with col2:
            if st.button("🔴 Clear", key="clear_session", disabled=not st.session_state.live_trade_active):
                st.session_state.live_trade_active = False
                st.session_state.must_have_checked = {}
                st.session_state.a_checked = {}
                st.session_state.b_checked = {}
                st.session_state.c_checked = {}
                st.rerun()
        
        if not st.session_state.live_trade_active:
            st.sidebar.info("Click **Start** when stalking a setup")
            return
        
        # MUST-HAVE RULES
        if must_have_rules:
            st.sidebar.markdown("### 🔒 Must-Have")
            for i, rule in enumerate(must_have_rules):
                key = f"must_{i}"
                st.session_state.must_have_checked[key] = st.sidebar.checkbox(
                    rule,
                    value=st.session_state.must_have_checked.get(key, False),
                    key=f"live_must_{i}"
                )
        
        # A RULES
        if a_rules:
            st.sidebar.markdown("### 🟢 A-Grade")
            for i, rule in enumerate(a_rules):
                key = f"a_{i}"
                st.session_state.a_checked[key] = st.sidebar.checkbox(
                    rule,
                    value=st.session_state.a_checked.get(key, False),
                    key=f"live_a_{i}"
                )
        
        # B RULES
        if b_rules:
            st.sidebar.markdown("### 🟡 B-Grade")
            for i, rule in enumerate(b_rules):
                key = f"b_{i}"
                st.session_state.b_checked[key] = st.sidebar.checkbox(
                    rule,
                    value=st.session_state.b_checked.get(key, False),
                    key=f"live_b_{i}"
                )
        
        # C RULES
        if c_rules:
            st.sidebar.markdown("### 🟠 C-Grade")
            for i, rule in enumerate(c_rules):
                key = f"c_{i}"
                st.session_state.c_checked[key] = st.sidebar.checkbox(
                    rule,
                    value=st.session_state.c_checked.get(key, False),
                    key=f"live_c_{i}"
                )
        
        # Calculate and display grade
        grade, size_label = self.calculate_grade(
            st.session_state.must_have_checked,
            st.session_state.a_checked,
            st.session_state.b_checked,
            st.session_state.c_checked
        )
        
        st.sidebar.markdown("---")
        
        # Grade display
        grade_colors = {"A": "🟢", "B": "🟡", "C": "🟠", "F": "🔴"}
        grade_emoji = grade_colors.get(grade, "⚪")
        
        st.sidebar.markdown(f"## {grade_emoji} Grade: **{grade}**")
        
        # Show must-have status
        if must_have_rules:
            must_count = sum(1 for k, v in st.session_state.must_have_checked.items() if v)
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
        if st.sidebar.button("📝 Log This Trade", type="primary", key="log_trade_btn"):
            st.session_state.show_trade_entry_form = True
            st.session_state.trade_entry_grade = grade
            st.session_state.trade_entry_must_have = st.session_state.must_have_checked.copy()
            st.session_state.trade_entry_a = st.session_state.a_checked.copy()
            st.session_state.trade_entry_b = st.session_state.b_checked.copy()
            st.session_state.trade_entry_c = st.session_state.c_checked.copy()
    
    def render_trade_entry_modal(self):
        """Render the trade entry form after clicking Log Trade"""
        if not st.session_state.get('show_trade_entry_form', False):
            return
        
        settings = self.data_storage.load_settings()
        accounts = self.data_storage.load_accounts()
        must_have_rules = settings.get('must_have_rules', [])
        a_rules = settings.get('a_rules', [])
        b_rules = settings.get('b_rules', [])
        c_rules = settings.get('c_rules', [])
        
        st.header("📝 Log Trade")
        
        grade = st.session_state.get('trade_entry_grade', '?')
        
        # Show grade summary
        grade_colors = {"A": "green", "B": "orange", "C": "red", "F": "red"}
        st.markdown(f"### Trade Grade: :{grade_colors.get(grade, 'gray')}[**{grade}**]")
        
        # Show rules summary
        with st.expander("Rules Checked", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**🔒 Must-Have:**")
                must_checked = st.session_state.get('trade_entry_must_have', {})
                for i, rule in enumerate(must_have_rules):
                    icon = "✅" if must_checked.get(f"must_{i}", False) else "❌"
                    st.write(f"{icon} {rule}")
            
            with col2:
                st.write("**🟢 A-Grade:**")
                a_checked = st.session_state.get('trade_entry_a', {})
                for i, rule in enumerate(a_rules):
                    icon = "✅" if a_checked.get(f"a_{i}", False) else "⬜"
                    st.write(f"{icon} {rule}")
                
                st.write("**🟡 B-Grade:**")
                b_checked = st.session_state.get('trade_entry_b', {})
                for i, rule in enumerate(b_rules):
                    icon = "✅" if b_checked.get(f"b_{i}", False) else "⬜"
                    st.write(f"{icon} {rule}")
                
                st.write("**🟠 C-Grade:**")
                c_checked = st.session_state.get('trade_entry_c', {})
                for i, rule in enumerate(c_rules):
                    icon = "✅" if c_checked.get(f"c_{i}", False) else "⬜"
                    st.write(f"{icon} {rule}")
        
        with st.form("trade_entry_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Account selection
                active_accounts = [a for a in accounts if a.get('status') in ['evaluation', 'funded']]
                if active_accounts:
                    account_options = [f"{a.get('prop_firm', 'Unknown')} - ${a.get('account_size', 0):,} ({a.get('account_number', 'N/A')})" 
                                      for a in active_accounts]
                    selected_account = st.selectbox("Account", account_options)
                else:
                    st.warning("No active accounts")
                    selected_account = None
                
                symbol = st.text_input("Symbol", value="ES")
                direction = st.selectbox("Direction", ["Long", "Short"])
                position_size = st.number_input("Position Size (Contracts)", min_value=1, value=1)
                trade_date = st.date_input("Trade Date", value=date.today())
            
            with col2:
                entry_price = st.number_input("Entry Price", min_value=0.0, value=0.0, step=0.25)
                stop_loss = st.number_input("Stop Loss", min_value=0.0, value=0.0, step=0.25)
                take_profit = st.number_input("Take Profit", min_value=0.0, value=0.0, step=0.25)
                entry_time = st.time_input("Entry Time", value=time(9, 30))
                exit_time = st.time_input("Exit Time", value=time(10, 0))
            
            # P&L
            st.subheader("Result")
            col1, col2, col3 = st.columns(3)
            with col1:
                pnl_gross = st.number_input("Gross P&L ($)", value=0.0, step=25.0)
            with col2:
                commission = st.number_input("Commission ($)", value=8.4, step=0.1)
            with col3:
                pnl_net = pnl_gross - commission
                st.metric("Net P&L", f"${pnl_net:.2f}")
            
            # Screenshot and notes
            screenshot_url = st.text_input("Screenshot URL", placeholder="TradingView link, etc.")
            notes = st.text_area("Trade Notes", placeholder="What happened? Lessons?")
            
            # Emotional state
            col1, col2 = st.columns(2)
            with col1:
                emotional_state = st.slider("Emotional State (1=Calm, 10=Tilted)", 1, 10, 5)
            with col2:
                would_repeat = st.checkbox("Would take this trade again")
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("Save Trade", type="primary")
            with col2:
                cancel = st.form_submit_button("Cancel")
            
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
                    "must_have_compliance": st.session_state.get('trade_entry_must_have', {}),
                    "a_compliance": st.session_state.get('trade_entry_a', {}),
                    "b_compliance": st.session_state.get('trade_entry_b', {}),
                    "c_compliance": st.session_state.get('trade_entry_c', {}),
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
                
                # Save trade
                self.data_storage.add_trade(trade_data)
                
                # Clear session
                st.session_state.show_trade_entry_form = False
                st.session_state.live_trade_active = False
                st.session_state.must_have_checked = {}
                st.session_state.a_checked = {}
                st.session_state.b_checked = {}
                st.session_state.c_checked = {}
                
                st.success(f"Trade logged! Grade: {grade}, P&L: ${pnl_net:+,.2f}")
                st.balloons()
                st.rerun()
            
            if cancel:
                st.session_state.show_trade_entry_form = False
                st.rerun()
