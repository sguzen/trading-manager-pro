import streamlit as st
import pandas as pd
from datetime import date, datetime, time, timedelta
from typing import Dict, List

class TradeJournal:
    def __init__(self, data_storage):
        self.data_storage = data_storage
    
    def show_journal(self):
        tab1, tab2, tab3, tab4 = st.tabs(["📝 Log Trade", "📊 Trade History", "✏️ Edit Trades", "🎯 Daily Check-in"])
        
        with tab1:
            self.log_new_trade()
        
        with tab2:
            self.show_trade_history()
        
        with tab3:
            self.edit_trades()
        
        with tab4:
            self.daily_checkin()
    
    def calculate_grade(self, rules_c_met: Dict[str, bool], rules_b_met: Dict[str, bool], rules_a_met: Dict[str, bool],
                       rules_c: List, rules_b: List, rules_a: List) -> str:
        """Calculate trade grade based on MANDATORY rules met only"""
        
        def get_mandatory_compliance(rules, compliance):
            """Get list of bools for mandatory rules only"""
            mandatory_met = []
            for rule in rules:
                rule_text = rule.get('text', rule) if isinstance(rule, dict) else rule
                is_mandatory = rule.get('mandatory', True) if isinstance(rule, dict) else True
                if is_mandatory:
                    mandatory_met.append(compliance.get(rule_text, False))
            return mandatory_met
        
        c_mandatory = get_mandatory_compliance(rules_c, rules_c_met)
        b_mandatory = get_mandatory_compliance(rules_b, rules_b_met)
        a_mandatory = get_mandatory_compliance(rules_a, rules_a_met)
        
        # All mandatory C rules must be met for any valid grade
        if c_mandatory and not all(c_mandatory):
            return "F"  # Failed - minimum criteria not met
        
        c_complete = not c_mandatory or all(c_mandatory)
        b_complete = not b_mandatory or all(b_mandatory)
        a_complete = not a_mandatory or all(a_mandatory)
        
        if c_complete and b_complete and a_complete:
            return "A"
        elif c_complete and b_complete:
            return "B"
        elif c_complete:
            return "C"
        else:
            return "F"
    
    def log_new_trade(self):
        st.subheader("Log New Trade")
        
        accounts = self.data_storage.load_accounts()
        playbooks = self.data_storage.load_playbooks()
        
        if not accounts:
            st.warning("No accounts configured. Please add accounts in Configuration first.")
            return
        
        if not playbooks:
            st.warning("No playbooks configured. Please add playbooks in Configuration first.")
            return
        
        account_options = [f"{acc['name']} ({acc['firm']})" for acc in accounts]
        playbook_options = [pb['name'] for pb in playbooks]
        
        with st.form("log_trade"):
            col1, col2 = st.columns(2)
            
            with col1:
                selected_account = st.selectbox("Account", account_options)
                selected_playbook = st.selectbox("Playbook", playbook_options)
                trade_date = st.date_input("Trade Date", value=date.today())
                trade_time = st.time_input("Trade Time", value=datetime.now().time())
            
            with col2:
                instrument = st.text_input("Instrument", placeholder="e.g., NQ, ES, GC")
                direction = st.selectbox("Direction", ["Long", "Short"])
                entry_price = st.number_input("Entry Price", min_value=0.0, format="%.2f")
                exit_price = st.number_input("Exit Price", min_value=0.0, format="%.2f")
            
            col3, col4 = st.columns(2)
            with col3:
                position_size = st.number_input("Position Size", min_value=1, value=1)
                pnl_input_type = st.radio("P&L Input", ["Calculate", "Manual"], horizontal=True)
            
            with col4:
                if pnl_input_type == "Manual":
                    pnl = st.number_input("P&L ($)", value=0.0, format="%.2f")
                else:
                    tick_value = st.number_input("Tick Value ($)", min_value=0.01, value=5.0)
                    tick_size = st.number_input("Tick Size", min_value=0.01, value=0.25, format="%.4f")
            
            emotional_state = st.slider("Emotional State (1=Calm, 10=Emotional)", 1, 10, 5)
            
            # Get selected playbook for rules
            playbook_idx = playbook_options.index(selected_playbook)
            playbook = playbooks[playbook_idx]
            
            # Migrate old playbook if needed
            def migrate_rules(rules):
                if not rules:
                    return []
                if isinstance(rules[0], str):
                    return [{"text": r, "mandatory": True} for r in rules]
                return rules
            
            if 'rules_c' not in playbook:
                playbook['rules_c'] = migrate_rules(playbook.get('rules', []))
                playbook['rules_b'] = []
                playbook['rules_a'] = []
            else:
                playbook['rules_c'] = migrate_rules(playbook.get('rules_c', []))
                playbook['rules_b'] = migrate_rules(playbook.get('rules_b', []))
                playbook['rules_a'] = migrate_rules(playbook.get('rules_a', []))
            
            st.markdown("---")
            st.markdown("### 📋 Rule Compliance Check")
            st.caption("🔒 = Mandatory (affects grade) | 📝 = Optional (tracked for refinement)")
            
            rule_compliance_c = {}
            rule_compliance_b = {}
            rule_compliance_a = {}
            
            def render_rule_checkboxes(rules, prefix, grade_label, grade_emoji):
                compliance = {}
                if rules:
                    st.markdown(f"#### {grade_emoji} {grade_label}")
                    for rule in rules:
                        rule_text = rule.get('text', rule) if isinstance(rule, dict) else rule
                        is_mandatory = rule.get('mandatory', True) if isinstance(rule, dict) else True
                        icon = "🔒" if is_mandatory else "📝"
                        compliance[rule_text] = st.checkbox(f"{icon} {rule_text}", key=f"{prefix}_{rule_text}")
                return compliance
            
            # C Rules - Minimum Requirements
            rule_compliance_c = render_rule_checkboxes(
                playbook.get('rules_c', []), "new_c", 
                "C Setup Rules (MUST have all mandatory)", "🔴"
            )
            
            # B Rules - Better probability
            rule_compliance_b = render_rule_checkboxes(
                playbook.get('rules_b', []), "new_b",
                "B Setup Rules (Better probability)", "🟡"
            )
            
            # A Rules - Best probability
            rule_compliance_a = render_rule_checkboxes(
                playbook.get('rules_a', []), "new_a",
                "A Setup Rules (Highest probability)", "🟢"
            )
            
            st.markdown("---")
            notes = st.text_area("Trade Notes", placeholder="What went well? What could improve?")
            
            if st.form_submit_button("Log Trade", type="primary"):
                # Calculate P&L
                if pnl_input_type == "Calculate":
                    ticks = (exit_price - entry_price) / tick_size
                    if direction == "Short":
                        ticks = -ticks
                    pnl = ticks * tick_value * position_size
                
                # Calculate grade based on mandatory rules only
                grade = self.calculate_grade(
                    rule_compliance_c, rule_compliance_b, rule_compliance_a,
                    playbook.get('rules_c', []),
                    playbook.get('rules_b', []),
                    playbook.get('rules_a', [])
                )
                
                # Get account info
                account_idx = account_options.index(selected_account)
                account = accounts[account_idx]
                
                trade_data = {
                    "id": datetime.now().strftime("%Y%m%d%H%M%S"),
                    "date": trade_date.isoformat(),
                    "time": trade_time.strftime("%H:%M"),
                    "account": account['name'],
                    "account_firm": account['firm'],
                    "playbook": selected_playbook,
                    "instrument": instrument,
                    "direction": direction,
                    "entry_price": entry_price,
                    "exit_price": exit_price,
                    "position_size": position_size,
                    "pnl": pnl,
                    "emotional_state": emotional_state,
                    "grade": grade,
                    "rule_compliance_c": rule_compliance_c,
                    "rule_compliance_b": rule_compliance_b,
                    "rule_compliance_a": rule_compliance_a,
                    # Backward compatibility
                    "rule_compliance": {**rule_compliance_c, **rule_compliance_b, **rule_compliance_a},
                    "notes": notes,
                    "created_at": datetime.now().isoformat()
                }
                
                self.data_storage.add_trade(trade_data)
                
                # Update account balance
                account['balance'] = account.get('balance', account['size']) + pnl
                self.data_storage.save_accounts(accounts)
                
                # Grade-based feedback
                if grade == "F":
                    st.error(f"🚨 Grade: F - Minimum C-setup criteria NOT met. This was a rule violation trade!")
                elif grade == "C":
                    st.warning(f"📝 Grade: C - Minimum criteria met. P&L: ${pnl:+,.2f}")
                elif grade == "B":
                    st.info(f"📈 Grade: B - Good setup quality. P&L: ${pnl:+,.2f}")
                else:
                    st.success(f"🎯 Grade: A - Premium setup! P&L: ${pnl:+,.2f}")
                
                st.rerun()
    
    def show_trade_history(self):
        st.subheader("Trade History")
        
        trades = self.data_storage.load_trades()
        
        if not trades:
            st.info("No trades logged yet.")
            return
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        accounts = list(set(t.get('account', 'Unknown') for t in trades))
        playbooks = list(set(t.get('playbook', 'Unknown') for t in trades))
        grades = ["All", "A", "B", "C", "F"]
        
        with col1:
            filter_account = st.selectbox("Filter by Account", ["All"] + accounts, key="hist_acc")
        with col2:
            filter_playbook = st.selectbox("Filter by Playbook", ["All"] + playbooks, key="hist_pb")
        with col3:
            filter_grade = st.selectbox("Filter by Grade", grades, key="hist_grade")
        
        # Apply filters
        filtered = trades.copy()
        if filter_account != "All":
            filtered = [t for t in filtered if t.get('account') == filter_account]
        if filter_playbook != "All":
            filtered = [t for t in filtered if t.get('playbook') == filter_playbook]
        if filter_grade != "All":
            filtered = [t for t in filtered if t.get('grade') == filter_grade]
        
        if filtered:
            # Summary metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            
            total_pnl = sum(t.get('pnl', 0) for t in filtered)
            win_trades = [t for t in filtered if t.get('pnl', 0) > 0]
            win_rate = len(win_trades) / len(filtered) * 100 if filtered else 0
            
            # Grade distribution
            grade_counts = {"A": 0, "B": 0, "C": 0, "F": 0}
            for t in filtered:
                g = t.get('grade', 'C')
                if g in grade_counts:
                    grade_counts[g] += 1
            
            with col1:
                st.metric("Total P&L", f"${total_pnl:,.2f}")
            with col2:
                st.metric("Trades", len(filtered))
            with col3:
                st.metric("Win Rate", f"{win_rate:.1f}%")
            with col4:
                st.metric("A/B Setups", f"{grade_counts['A'] + grade_counts['B']}")
            with col5:
                st.metric("Rule Violations", f"{grade_counts['F']}")
            
            # Trade table
            df = pd.DataFrame(filtered)
            display_cols = ['date', 'time', 'account', 'playbook', 'instrument', 'direction', 
                           'entry_price', 'exit_price', 'pnl', 'grade', 'emotional_state']
            display_cols = [c for c in display_cols if c in df.columns]
            
            st.dataframe(df[display_cols].sort_values('date', ascending=False), 
                        use_container_width=True)
            
            # Grade breakdown by P&L
            st.subheader("Performance by Grade")
            grade_perf = {}
            for grade in ["A", "B", "C", "F"]:
                grade_trades = [t for t in filtered if t.get('grade') == grade]
                if grade_trades:
                    grade_pnl = sum(t.get('pnl', 0) for t in grade_trades)
                    grade_wins = len([t for t in grade_trades if t.get('pnl', 0) > 0])
                    grade_wr = grade_wins / len(grade_trades) * 100
                    grade_perf[grade] = {
                        "trades": len(grade_trades),
                        "pnl": grade_pnl,
                        "win_rate": grade_wr
                    }
            
            if grade_perf:
                perf_df = pd.DataFrame(grade_perf).T
                perf_df.index.name = "Grade"
                st.dataframe(perf_df, use_container_width=True)
        else:
            st.info("No trades match the selected filters.")
    
    def edit_trades(self):
        st.subheader("Edit Trades")
        
        trades = self.data_storage.load_trades()
        playbooks = self.data_storage.load_playbooks()
        
        if not trades:
            st.info("No trades to edit.")
            return
        
        # Select trade to edit
        trade_options = [f"{t['date']} {t.get('time', '')} - {t.get('instrument', 'Unknown')} ({t.get('grade', 'C')}) ${t.get('pnl', 0):+,.2f}" for t in trades]
        selected_idx = st.selectbox("Select Trade to Edit", range(len(trades)), 
                                    format_func=lambda x: trade_options[x])
        
        trade = trades[selected_idx]
        
        # Find matching playbook
        playbook_names = [pb['name'] for pb in playbooks]
        current_pb_idx = playbook_names.index(trade.get('playbook', playbook_names[0])) if trade.get('playbook') in playbook_names else 0
        
        with st.form(f"edit_trade_{trade.get('id', selected_idx)}"):
            col1, col2 = st.columns(2)
            
            with col1:
                edit_date = st.date_input("Date", value=datetime.fromisoformat(trade['date']).date() if trade.get('date') else date.today())
                edit_instrument = st.text_input("Instrument", value=trade.get('instrument', ''))
                edit_direction = st.selectbox("Direction", ["Long", "Short"], 
                                              index=0 if trade.get('direction') == 'Long' else 1)
                edit_entry = st.number_input("Entry Price", value=float(trade.get('entry_price', 0)))
            
            with col2:
                edit_playbook = st.selectbox("Playbook", playbook_names, index=current_pb_idx)
                edit_exit = st.number_input("Exit Price", value=float(trade.get('exit_price', 0)))
                edit_size = st.number_input("Position Size", value=int(trade.get('position_size', 1)), min_value=1)
                edit_pnl = st.number_input("P&L ($)", value=float(trade.get('pnl', 0)))
            
            edit_emotional = st.slider("Emotional State", 1, 10, int(trade.get('emotional_state', 5)))
            
            # Get playbook for rules
            playbook = playbooks[playbook_names.index(edit_playbook)]
            
            # Migrate old playbook if needed
            def migrate_rules(rules):
                if not rules:
                    return []
                if isinstance(rules[0], str):
                    return [{"text": r, "mandatory": True} for r in rules]
                return rules
            
            if 'rules_c' not in playbook:
                playbook['rules_c'] = migrate_rules(playbook.get('rules', []))
                playbook['rules_b'] = []
                playbook['rules_a'] = []
            else:
                playbook['rules_c'] = migrate_rules(playbook.get('rules_c', []))
                playbook['rules_b'] = migrate_rules(playbook.get('rules_b', []))
                playbook['rules_a'] = migrate_rules(playbook.get('rules_a', []))
            
            st.markdown("---")
            st.markdown("### 📋 Rule Compliance")
            st.caption("🔒 = Mandatory (affects grade) | 📝 = Optional (tracked for refinement)")
            
            # Get existing compliance or default to empty
            existing_c = trade.get('rule_compliance_c', {})
            existing_b = trade.get('rule_compliance_b', {})
            existing_a = trade.get('rule_compliance_a', {})
            
            # Fall back to old format if new format doesn't exist
            if not existing_c and not existing_b and not existing_a:
                old_compliance = trade.get('rule_compliance', {})
                for rule in playbook.get('rules_c', []):
                    rule_text = rule.get('text', rule) if isinstance(rule, dict) else rule
                    existing_c[rule_text] = old_compliance.get(rule_text, False)
                for rule in playbook.get('rules_b', []):
                    rule_text = rule.get('text', rule) if isinstance(rule, dict) else rule
                    existing_b[rule_text] = old_compliance.get(rule_text, False)
                for rule in playbook.get('rules_a', []):
                    rule_text = rule.get('text', rule) if isinstance(rule, dict) else rule
                    existing_a[rule_text] = old_compliance.get(rule_text, False)
            
            def render_edit_checkboxes(rules, existing, prefix, grade_label, grade_emoji):
                compliance = {}
                if rules:
                    st.markdown(f"#### {grade_emoji} {grade_label}")
                    for rule in rules:
                        rule_text = rule.get('text', rule) if isinstance(rule, dict) else rule
                        is_mandatory = rule.get('mandatory', True) if isinstance(rule, dict) else True
                        icon = "🔒" if is_mandatory else "📝"
                        compliance[rule_text] = st.checkbox(
                            f"{icon} {rule_text}", 
                            value=existing.get(rule_text, False),
                            key=f"{prefix}_{selected_idx}_{rule_text}"
                        )
                return compliance
            
            edit_compliance_c = render_edit_checkboxes(
                playbook.get('rules_c', []), existing_c,
                "edit_c", "C Setup Rules", "🔴"
            )
            edit_compliance_b = render_edit_checkboxes(
                playbook.get('rules_b', []), existing_b,
                "edit_b", "B Setup Rules", "🟡"
            )
            edit_compliance_a = render_edit_checkboxes(
                playbook.get('rules_a', []), existing_a,
                "edit_a", "A Setup Rules", "🟢"
            )
            
            edit_notes = st.text_area("Notes", value=trade.get('notes', ''))
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.form_submit_button("Save Changes", type="primary"):
                    # Recalculate grade based on mandatory rules only
                    new_grade = self.calculate_grade(
                        edit_compliance_c, edit_compliance_b, edit_compliance_a,
                        playbook.get('rules_c', []),
                        playbook.get('rules_b', []),
                        playbook.get('rules_a', [])
                    )
                    
                    trades[selected_idx] = {
                        **trade,
                        "date": edit_date.isoformat(),
                        "playbook": edit_playbook,
                        "instrument": edit_instrument,
                        "direction": edit_direction,
                        "entry_price": edit_entry,
                        "exit_price": edit_exit,
                        "position_size": edit_size,
                        "pnl": edit_pnl,
                        "emotional_state": edit_emotional,
                        "grade": new_grade,
                        "rule_compliance_c": edit_compliance_c,
                        "rule_compliance_b": edit_compliance_b,
                        "rule_compliance_a": edit_compliance_a,
                        "rule_compliance": {**edit_compliance_c, **edit_compliance_b, **edit_compliance_a},
                        "notes": edit_notes,
                        "updated_at": datetime.now().isoformat()
                    }
                    
                    self.data_storage.save_trades(trades)
                    st.success(f"Trade updated! Grade: {new_grade}")
                    st.rerun()
            
            with col2:
                if st.form_submit_button("Delete Trade", type="secondary"):
                    trades.pop(selected_idx)
                    self.data_storage.save_trades(trades)
                    st.success("Trade deleted!")
                    st.rerun()
    
    def daily_checkin(self):
        st.subheader("🎯 Pre-Market Check-in")
        
        checkins = self.data_storage.load_checkins()
        today = date.today().isoformat()
        
        # Check if already checked in today
        today_checkin = next((c for c in checkins if c.get('date') == today), None)
        
        if today_checkin:
            st.success("✅ You've already completed today's check-in!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Sleep Quality", f"{today_checkin.get('sleep_quality', 'N/A')}/10")
                st.metric("Stress Level", f"{today_checkin.get('stress_level', 'N/A')}/10")
            with col2:
                st.metric("Home Stress", f"{today_checkin.get('home_stress', 'N/A')}/10")
                st.metric("Alcohol (24h)", "Yes" if today_checkin.get('alcohol') else "No")
            with col3:
                st.metric("Exercise", "Yes" if today_checkin.get('exercise') else "No")
                st.metric("Clear to Trade", "✅ Yes" if today_checkin.get('approved_to_trade') else "🚫 No")
            
            st.markdown("**Trading Plan:**")
            st.write(today_checkin.get('trading_plan', 'None recorded'))
            
            if st.button("Reset Today's Check-in"):
                checkins = [c for c in checkins if c.get('date') != today]
                self.data_storage.save_checkins(checkins)
                st.rerun()
        else:
            with st.form("daily_checkin"):
                st.markdown("### How are you feeling today?")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    sleep_quality = st.slider("Sleep Quality (1-10)", 1, 10, 7)
                    stress_level = st.slider("Stress Level (1-10)", 1, 10, 3)
                    home_stress = st.slider("Home Stress Level (1-10)", 1, 10, 3)
                
                with col2:
                    alcohol = st.checkbox("Alcohol consumed in last 24 hours?")
                    exercise = st.checkbox("Exercised today or yesterday?")
                    good_sleep = st.checkbox("Got at least 6 hours of sleep?")
                
                trading_plan = st.text_area("Today's Trading Plan", 
                    placeholder="What setups are you looking for? What's your max loss? Any news events?")
                
                if st.form_submit_button("Complete Check-in", type="primary"):
                    # Determine if approved to trade
                    approved = True
                    warnings = []
                    
                    if alcohol:
                        approved = False
                        warnings.append("🚫 Alcohol consumed - NO TRADING TODAY")
                    
                    if stress_level >= 7:
                        approved = False
                        warnings.append(f"🚫 Stress level too high ({stress_level}/10)")
                    
                    if home_stress >= 7:
                        warnings.append(f"⚠️ High home stress ({home_stress}/10) - trade with caution")
                    
                    if sleep_quality <= 4:
                        approved = False
                        warnings.append(f"🚫 Poor sleep quality ({sleep_quality}/10)")
                    
                    if not good_sleep:
                        warnings.append("⚠️ Less than 6 hours sleep - reduced position size recommended")
                    
                    checkin_data = {
                        "date": today,
                        "sleep_quality": sleep_quality,
                        "stress_level": stress_level,
                        "home_stress": home_stress,
                        "alcohol": alcohol,
                        "exercise": exercise,
                        "good_sleep": good_sleep,
                        "trading_plan": trading_plan,
                        "approved_to_trade": approved,
                        "warnings": warnings,
                        "created_at": datetime.now().isoformat()
                    }
                    
                    checkins.append(checkin_data)
                    self.data_storage.save_checkins(checkins)
                    
                    if approved:
                        st.success("✅ You're cleared to trade today! Stick to your plan.")
                    else:
                        st.error("🚫 NOT APPROVED TO TRADE TODAY")
                    
                    for warning in warnings:
                        st.warning(warning)
                    
                    st.rerun()
        
        # Show recent check-ins
        st.markdown("---")
        st.subheader("Recent Check-in History")
        
        recent = sorted(checkins, key=lambda x: x.get('date', ''), reverse=True)[:7]
        if recent:
            df = pd.DataFrame(recent)
            display_cols = ['date', 'sleep_quality', 'stress_level', 'home_stress', 'alcohol', 'approved_to_trade']
            display_cols = [c for c in display_cols if c in df.columns]
            st.dataframe(df[display_cols], use_container_width=True)
