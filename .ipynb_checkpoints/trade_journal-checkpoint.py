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
        # Playbook selection
        playbook_names = [pb['name'] for pb in playbooks]
        selected_playbook = st.selectbox("Select Playbook", playbook_names, key="main_playbook_selector")

        selected_pb = next((pb for pb in playbooks if pb['name'] == selected_playbook), None)
        
        with st.form("log_trade"):
            # Basic trade info
            col1, col2 = st.columns(2)
            
            with col1:
                # Account selection
                account_options = [f"{acc['prop_firm']} - {acc['account_type']} ({acc['account_number']})" 
                                 for acc in accounts if acc['status'] in ['evaluation', 'funded']]
                selected_account = st.selectbox("Account", account_options)
                
                # Display selected playbook (read-only)
                st.text_input("Playbook (selected above)", value=selected_playbook, disabled=True)
                
                
                # Trade details
                symbol = st.text_input("Symbol", placeholder="ES", value="ES")
                direction = st.selectbox("Direction", ["Long", "Short"])
                position_size = st.number_input("Position Size (Contracts)", min_value=1, value=1)
            
            with col2:
                trade_date = st.date_input("Trade Date", value=date.today())
                entry_time = st.time_input("Entry Time", value=time(9, 30))
                exit_time = st.time_input("Exit Time", value=time(10, 0))
                
                # P&L Input Method Selection
                pnl_method = st.radio("P&L Input Method", 
                                    ["Manual Entry", "Calculate from Prices"], 
                                    help="Choose how to enter your trade P&L")
            
            # P&L Section
            st.subheader("Trade P&L")
            
            if pnl_method == "Manual Entry":
                col1, col2, col3 = st.columns(3)
                with col1:
                    pnl_gross = st.number_input("Gross P&L ($)", value=0.0, step=25.0,
                                              help="Total P&L before commissions")
                with col2:
                    commission = st.number_input("Commission ($)", value=8.4, step=0.1,
                                               help="Total round-turn commission")
                with col3:
                    pnl_net = pnl_gross - commission
                    st.metric("Net P&L", f"${pnl_net:.2f}")
                
                # Optional price fields for reference
                with st.expander("Price Details (Optional)"):
                    col1, col2 = st.columns(2)
                    with col1:
                        entry_price = st.number_input("Entry Price (Optional)", value=0.0, step=0.25)
                    with col2:
                        exit_price = st.number_input("Exit Price (Optional)", value=0.0, step=0.25)
                    
                    if entry_price > 0 and exit_price > 0:
                        if direction == "Long":
                            price_diff = exit_price - entry_price
                        else:
                            price_diff = entry_price - exit_price
                        st.info(f"Price difference: {price_diff:.2f} points")
            
            else:  # Calculate from Prices
                col1, col2 = st.columns(2)
                with col1:
                    entry_price = st.number_input("Entry Price", min_value=0.01, value=4500.0, step=0.25)
                    exit_price = st.number_input("Exit Price", min_value=0.01, value=4510.0, step=0.25)
                
                with col2:
                    # Point value selection
                    point_values = {
                        "ES (E-mini S&P)": 50,
                        "NQ (E-mini Nasdaq)": 20,
                        "YM (E-mini Dow)": 5,
                        "RTY (E-mini Russell)": 50,
                        "Custom": 0
                    }
                    
                    selected_contract = st.selectbox("Contract Type", list(point_values.keys()))
                    
                    if selected_contract == "Custom":
                        point_value = st.number_input("Point Value ($)", min_value=0.01, value=50.0)
                    else:
                        point_value = point_values[selected_contract]
                        st.write(f"Point Value: ${point_value}")
                    
                    commission = st.number_input("Commission ($)", value=8.4, step=0.1)
                
                # Calculate P&L
                if direction == "Long":
                    pnl_points = exit_price - entry_price
                else:
                    pnl_points = entry_price - exit_price
                
                pnl_gross = pnl_points * position_size * point_value
                pnl_net = pnl_gross - commission
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("P&L Points", f"{pnl_points:.2f}")
                with col2:
                    st.metric("Gross P&L", f"${pnl_gross:.2f}")
                with col3:
                    st.metric("Net P&L", f"${pnl_net:.2f}")
            
            # Rule compliance
            st.subheader("Rule Compliance Check")
            
            rule_compliance = {}
            has_rules = selected_pb and 'rules' in selected_pb and selected_pb['rules']
            
            if has_rules:
                st.write(f"**Rules for {selected_playbook}:**")
                
                for i, rule in enumerate(selected_pb['rules']):
                    rule_compliance[f"rule_{i}"] = st.checkbox(f"✓ {rule}", key=f"trade_rule_{i}")
            else:
                st.info(f"No rules defined for {selected_playbook}.")
            
            # Trade analysis
            st.subheader("Trade Analysis")
            col1, col2 = st.columns(2)
            
            with col1:
                setup_quality = st.slider("Setup Quality (1-10)", 1, 10, 7)
                execution_quality = st.slider("Execution Quality (1-10)", 1, 10, 7)
                emotional_state = st.slider("Emotional State (1-10)", 1, 10, 5,
                                          help="1=Calm, 10=Highly Emotional")
            
            with col2:
                was_planned = st.checkbox("Trade was planned")
                followed_rules = st.checkbox("Followed all rules")
                would_repeat = st.checkbox("Would take this trade again")
            
            # Additional trade details
            with st.expander("Additional Details"):
                col1, col2 = st.columns(2)
                with col1:
                    session = st.selectbox("Trading Session", 
                                         ["Pre-Market", "Open", "Morning", "Lunch", "Afternoon", "Close", "After-Hours"])
                    market_condition = st.selectbox("Market Condition",
                                                  ["Trending Up", "Trending Down", "Choppy", "Range-bound", "News Event"])
                with col2:
                    volume_condition = st.selectbox("Volume", ["Low", "Normal", "High", "Very High"])
                    trade_duration = st.selectbox("Trade Duration", 
                                                ["Scalp (<5min)", "Short (5-30min)", "Medium (30min-2hr)", "Long (>2hr)"])
            
            # Notes
            notes = st.text_area("Trade Notes", 
                               placeholder="What went well? What could improve? Market conditions, emotions, lessons learned...",
                               height=100)
            
            # Screenshot/Chart upload
            uploaded_chart = st.file_uploader("Upload Chart Screenshot (optional)", 
                                            type=['png', 'jpg', 'jpeg'])
            
            # Submit trade
            if st.form_submit_button("Log Trade", type="primary"):
                # Get account info
                account_idx = account_options.index(selected_account)
                selected_acc = [acc for acc in accounts if acc['status'] in ['evaluation', 'funded']][account_idx]
                
                trade_data = {
                    "date": trade_date.isoformat(),
                    "entry_time": entry_time.isoformat(),
                    "exit_time": exit_time.isoformat(),
                    "account": selected_account,
                    "account_id": selected_acc.get('account_number', ''),
                    "playbook": selected_playbook,
                    "symbol": symbol,
                    "direction": direction,
                    "position_size": position_size,
                    "pnl_gross": pnl_gross,
                    "pnl_net": pnl_net,
                    "commission": commission,
                    "setup_quality": setup_quality,
                    "execution_quality": execution_quality,
                    "emotional_state": emotional_state,
                    "was_planned": was_planned,
                    "followed_rules": followed_rules,
                    "would_repeat": would_repeat,
                    "rule_compliance": rule_compliance,
                    "session": session,
                    "market_condition": market_condition,
                    "volume_condition": volume_condition,
                    "trade_duration": trade_duration,
                    "notes": notes,
                }
                
                # Add price data if available
                if pnl_method == "Calculate from Prices" or (entry_price > 0 and exit_price > 0):
                    trade_data.update({
                        "entry_price": entry_price,
                        "exit_price": exit_price,
                        "pnl_points": pnl_points if pnl_method == "Calculate from Prices" else (exit_price - entry_price if direction == "Long" else entry_price - exit_price),
                        "point_value": point_value if pnl_method == "Calculate from Prices" else 0
                    })
                
                # Save chart if uploaded
                if uploaded_chart:
                    trade_data["chart_filename"] = f"chart_{len(self.data_storage.load_trades())+1}_{uploaded_chart.name}"
                
                # Update account balance with P&L
                accounts = self.data_storage.load_accounts()
                for i, acc in enumerate(accounts):
                    if (acc['prop_firm'] == selected_acc['prop_firm'] and 
                        acc['account_type'] == selected_acc['account_type'] and
                        acc['account_number'] == selected_acc['account_number']):
                        accounts[i]['current_balance'] += pnl_net
                        accounts[i]['updated_at'] = datetime.now().isoformat()
                        break
                
                # Save trade and update account
                self.data_storage.add_trade(trade_data)
                self.data_storage.save_accounts(accounts)
                
                st.success(f"Trade logged successfully! Account balance updated by ${pnl_net:+.2f}")
                st.balloons()
                
                # Show warnings if needed
                if emotional_state > 7:
                    st.warning("⚠️ High emotional state detected. Consider taking a break.")
                
                # FIX: Check actual rule compliance, not just the general checkbox
                # A rule is violated if: rules exist AND (any rule is unchecked OR followed_rules is unchecked)
                rules_violated = False
                if has_rules:
                    # Check if any individual rule checkbox is unchecked
                    all_rules_checked = all(rule_compliance.values())
                    if not all_rules_checked or not followed_rules:
                        rules_violated = True
                elif not followed_rules:
                    # No playbook rules defined, just check the general checkbox
                    rules_violated = True
                
                if rules_violated:
                    st.error("🚨 Rule violation logged. Review your discipline.")
                
                if pnl_net < 0:
                    st.info("💡 Loss logged. Review what could be improved for next time.")
    
    def show_trade_history(self):
        st.subheader("Trade History")
        
        trades = self.data_storage.load_trades()
        
        if not trades:
            st.info("No trades logged yet.")
            return
        
        df = pd.DataFrame(trades)
        
        # Filters
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            date_filter = st.date_input("From Date", value=pd.to_datetime(df['date']).min().date(),
                                      key="history_date_filter")
        
        with col2:
            account_filter = st.selectbox("Filter by Account", ["All"] + df['account'].unique().tolist(),
                                        key="history_account_filter")
        
        with col3:
            playbook_filter = st.selectbox("Filter by Playbook", ["All"] + df['playbook'].unique().tolist(),
                                         key="history_playbook_filter")
        
        with col4:
            symbol_filter = st.selectbox("Filter by Symbol", ["All"] + df['symbol'].unique().tolist(),
                                       key="history_symbol_filter")
        
        # Apply filters
        filtered_df = df.copy()
        
        if account_filter != "All":
            filtered_df = filtered_df[filtered_df['account'] == account_filter]
        
        if playbook_filter != "All":
            filtered_df = filtered_df[filtered_df['playbook'] == playbook_filter]
        
        if symbol_filter != "All":
            filtered_df = filtered_df[filtered_df['symbol'] == symbol_filter]
        
        filtered_df = filtered_df[pd.to_datetime(filtered_df['date']) >= pd.to_datetime(date_filter)]
        
        if filtered_df.empty:
            st.info("No trades match the selected filters.")
            return
        
        # Summary metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            total_trades = len(filtered_df)
            st.metric("Total Trades", total_trades)
        
        with col2:
            win_rate = (filtered_df['pnl_net'] > 0).mean() * 100
            st.metric("Win Rate", f"{win_rate:.1f}%")
        
        with col3:
            total_pnl = filtered_df['pnl_net'].sum()
            st.metric("Total P&L", f"${total_pnl:.2f}")
        
        with col4:
            avg_trade = filtered_df['pnl_net'].mean()
            st.metric("Avg Trade", f"${avg_trade:.2f}")
        
        with col5:
            avg_emotional_state = filtered_df['emotional_state'].mean()
            color = "normal" if avg_emotional_state <= 7 else "inverse"
            st.metric("Avg Emotional State", f"{avg_emotional_state:.1f}", delta_color=color)
        
        # Trade table
        available_columns = df.columns.tolist()
        display_columns = ['date', 'symbol', 'direction', 'pnl_net', 'emotional_state', 'followed_rules']
        
        # Add entry/exit prices only if they exist
        if 'entry_price' in available_columns and 'exit_price' in available_columns:
            display_columns.insert(4, 'entry_price')
            display_columns.insert(5, 'exit_price')
        
        # Filter to only include columns that actually exist
        display_columns = [col for col in display_columns if col in available_columns]
        
        column_config = {
            "pnl_net": st.column_config.NumberColumn("P&L", format="$%.2f"),
            "followed_rules": st.column_config.CheckboxColumn("Rules ✓")
        }
        
        # Add price column configs if they exist
        if 'entry_price' in available_columns:
            column_config["entry_price"] = st.column_config.NumberColumn("Entry", format="%.2f")
        if 'exit_price' in available_columns:
            column_config["exit_price"] = st.column_config.NumberColumn("Exit", format="%.2f")
        
        st.dataframe(
            filtered_df[display_columns].sort_values('date', ascending=False),
            use_container_width=True,
            column_config=column_config
        )
        
        # Detailed trade view
        if st.checkbox("Show Detailed View"):
            for i, trade in filtered_df.iterrows():
                with st.expander(f"{trade['date']} - {trade['symbol']} {trade['direction']} - ${trade['pnl_net']:.2f}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Account:** {trade['account']}")
                        st.write(f"**Playbook:** {trade['playbook']}")
                        st.write(f"**Time:** {trade['entry_time']} - {trade['exit_time']}")
                        if 'session' in trade:
                            st.write(f"**Session:** {trade['session']}")
                    
                    with col2:
                        st.write(f"**Position:** {trade['position_size']} contracts")
                        st.write(f"**Gross P&L:** ${trade['pnl_gross']:.2f}")
                        st.write(f"**Commission:** ${trade['commission']:.2f}")
                        st.write(f"**Net P&L:** ${trade['pnl_net']:.2f}")
                        
                        # Show prices if available
                        if 'entry_price' in trade and trade['entry_price'] > 0:
                            st.write(f"**Entry:** {trade['entry_price']}")
                        if 'exit_price' in trade and trade['exit_price'] > 0:
                            st.write(f"**Exit:** {trade['exit_price']}")
                        if 'pnl_points' in trade:
                            st.write(f"**Points:** {trade['pnl_points']:.2f}")
                    
                    with col3:
                        st.write(f"**Setup Quality:** {trade['setup_quality']}/10")
                        st.write(f"**Execution:** {trade['execution_quality']}/10")
                        st.write(f"**Emotional State:** {trade['emotional_state']}/10")
                        
                        # Additional details if available
                        if 'market_condition' in trade:
                            st.write(f"**Market:** {trade['market_condition']}")
                        if 'trade_duration' in trade:
                            st.write(f"**Duration:** {trade['trade_duration']}")
                    
    def edit_trades(self):
        st.subheader("Edit & Delete Trades")
        
        trades = self.data_storage.load_trades()
        accounts = self.data_storage.load_accounts()
        playbooks = self.data_storage.load_playbooks()
        
        if not trades:
            st.info("No trades logged yet.")
            return
        
        # Sort trades by date (newest first)
        trades_sorted = sorted(trades, key=lambda x: x['date'], reverse=True)
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_account = st.selectbox("Filter by Account", 
                                        ["All"] + list(set([t['account'] for t in trades])),
                                        key="edit_filter_account")
        with col2:
            filter_symbol = st.selectbox("Filter by Symbol", 
                                       ["All"] + list(set([t['symbol'] for t in trades])),
                                       key="edit_filter_symbol")
        with col3:
            filter_days = st.selectbox("Show Last", 
                                     ["All", "7 days", "30 days", "90 days"],
                                     key="edit_filter_days")
        
        # Apply filters
        filtered_trades = trades_sorted.copy()
        
        if filter_account != "All":
            filtered_trades = [t for t in filtered_trades if t['account'] == filter_account]
        
        if filter_symbol != "All":
            filtered_trades = [t for t in filtered_trades if t['symbol'] == filter_symbol]
        
        if filter_days != "All":
            days_back = {"7 days": 7, "30 days": 30, "90 days": 90}[filter_days]
            cutoff_date = (datetime.now() - timedelta(days=days_back)).date()
            filtered_trades = [t for t in filtered_trades if pd.to_datetime(t['date']).date() >= cutoff_date]
        
        if not filtered_trades:
            st.warning("No trades match the selected filters.")
            return
        
        st.write(f"**{len(filtered_trades)} trades found**")
        
        # Display trades for editing
        for i, trade in enumerate(filtered_trades):
            # Find original index in trades list
            original_idx = next(j for j, t in enumerate(trades) if t.get('id') == trade.get('id', i))
            
            trade_title = f"{trade['date']} - {trade['symbol']} {trade['direction']} - ${trade['pnl_net']:.2f}"
            
            with st.expander(f"✏️ Edit Trade #{trade.get('id', original_idx+1)}: {trade_title}", expanded=False):
                with st.form(f"edit_trade_{original_idx}"):
                    # Basic trade info
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Account selection
                        account_options = [f"{acc['prop_firm']} - {acc['account_type']} ({acc['account_number']})" 
                                         for acc in accounts if acc['status'] in ['evaluation', 'funded']]
                        
                        try:
                            current_account_idx = account_options.index(trade['account'])
                        except ValueError:
                            current_account_idx = 0
                        
                        edited_account = st.selectbox("Account", account_options, 
                                                    index=current_account_idx, key=f"edit_acc_{original_idx}")
                        
                        # Playbook selection
                        playbook_names = [pb['name'] for pb in playbooks]
                        try:
                            current_playbook_idx = playbook_names.index(trade['playbook'])
                        except ValueError:
                            current_playbook_idx = 0
                        
                        edited_playbook = st.selectbox("Playbook", playbook_names, 
                                                     index=current_playbook_idx, key=f"edit_pb_{original_idx}")
                        
                        edited_symbol = st.text_input("Symbol", value=trade['symbol'], key=f"edit_sym_{original_idx}")
                        edited_direction = st.selectbox("Direction", ["Long", "Short"], 
                                                      index=0 if trade['direction'] == "Long" else 1, 
                                                      key=f"edit_dir_{original_idx}")
                        edited_position_size = st.number_input("Position Size", value=trade['position_size'], 
                                                             min_value=1, key=f"edit_pos_{original_idx}")
                    
                    with col2:
                        edited_date = st.date_input("Trade Date", value=pd.to_datetime(trade['date']).date(), 
                                                  key=f"edit_date_{original_idx}")
                        edited_entry_time = st.time_input("Entry Time", 
                                                        value=pd.to_datetime(trade['entry_time']).time(), 
                                                        key=f"edit_entry_{original_idx}")
                        edited_exit_time = st.time_input("Exit Time", 
                                                       value=pd.to_datetime(trade['exit_time']).time(), 
                                                       key=f"edit_exit_{original_idx}")
                    
                    # P&L editing
                    st.subheader("P&L")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        edited_pnl_gross = st.number_input("Gross P&L", value=trade['pnl_gross'], 
                                                         step=25.0, key=f"edit_gross_{original_idx}")
                    with col2:
                        edited_commission = st.number_input("Commission", value=trade['commission'], 
                                                          step=0.1, key=f"edit_comm_{original_idx}")
                    with col3:
                        edited_pnl_net = edited_pnl_gross - edited_commission
                        st.metric("Net P&L", f"${edited_pnl_net:.2f}")
                    
                    # Price information (optional)
                    st.subheader("Price Details (Optional)")
                    col1, col2 = st.columns(2)
                    with col1:
                        edited_entry_price = st.number_input("Entry Price", 
                                                           value=trade.get('entry_price', 0.0), 
                                                           step=0.25, key=f"edit_eprice_{original_idx}")
                    with col2:
                        edited_exit_price = st.number_input("Exit Price", 
                                                          value=trade.get('exit_price', 0.0), 
                                                          step=0.25, key=f"edit_exprice_{original_idx}")
                    
                    # FIX: Add Rule Compliance Section
                    st.subheader("Rule Compliance")
                    
                    # Get the playbook for this trade to show its rules
                    trade_playbook = next((pb for pb in playbooks if pb['name'] == edited_playbook), None)
                    edited_rule_compliance = {}
                    
                    if trade_playbook and 'rules' in trade_playbook and trade_playbook['rules']:
                        st.write(f"**Rules for {edited_playbook}:**")
                        
                        # Get existing rule compliance from trade
                        existing_compliance = trade.get('rule_compliance', {})
                        
                        for rule_idx, rule in enumerate(trade_playbook['rules']):
                            rule_key = f"rule_{rule_idx}"
                            # Default to existing value if available, otherwise False
                            default_value = existing_compliance.get(rule_key, False)
                            edited_rule_compliance[rule_key] = st.checkbox(
                                f"✓ {rule}", 
                                value=default_value,
                                key=f"edit_rule_{original_idx}_{rule_idx}"
                            )
                    else:
                        st.info(f"No rules defined for {edited_playbook}.")
                    
                    # Trade analysis
                    st.subheader("Trade Analysis")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        edited_setup_quality = st.slider("Setup Quality", 1, 10, 
                                                        value=trade['setup_quality'], 
                                                        key=f"edit_setup_{original_idx}")
                        edited_execution_quality = st.slider("Execution Quality", 1, 10, 
                                                           value=trade['execution_quality'], 
                                                           key=f"edit_exec_{original_idx}")
                        edited_emotional_state = st.slider("Emotional State", 1, 10, 
                                                         value=trade['emotional_state'], 
                                                         key=f"edit_emotion_{original_idx}")
                    
                    with col2:
                        edited_was_planned = st.checkbox("Trade was planned", 
                                                       value=trade['was_planned'], 
                                                       key=f"edit_planned_{original_idx}")
                        edited_followed_rules = st.checkbox("Followed all rules", 
                                                          value=trade['followed_rules'], 
                                                          key=f"edit_rules_{original_idx}")
                        edited_would_repeat = st.checkbox("Would take this trade again", 
                                                        value=trade['would_repeat'], 
                                                        key=f"edit_repeat_{original_idx}")
                    
                    # Additional details
                    st.subheader("Additional Details")
                    col1, col2 = st.columns(2)
                    with col1:
                        session_options = ["Pre-Market", "Open", "Morning", "Lunch", "Afternoon", "Close", "After-Hours"]
                        current_session = trade.get('session', 'Open')
                        try:
                            session_idx = session_options.index(current_session)
                        except ValueError:
                            session_idx = 1
                        
                        edited_session = st.selectbox("Trading Session", session_options, 
                                                    index=session_idx, key=f"edit_session_{original_idx}")
                        
                        market_options = ["Trending Up", "Trending Down", "Choppy", "Range-bound", "News Event"]
                        current_market = trade.get('market_condition', 'Range-bound')
                        try:
                            market_idx = market_options.index(current_market)
                        except ValueError:
                            market_idx = 3
                        
                        edited_market_condition = st.selectbox("Market Condition", market_options, 
                                                             index=market_idx, key=f"edit_market_{original_idx}")
                    
                    with col2:
                        volume_options = ["Low", "Normal", "High", "Very High"]
                        current_volume = trade.get('volume_condition', 'Normal')
                        try:
                            volume_idx = volume_options.index(current_volume)
                        except ValueError:
                            volume_idx = 1
                        
                        edited_volume_condition = st.selectbox("Volume", volume_options, 
                                                             index=volume_idx, key=f"edit_volume_{original_idx}")
                        
                        duration_options = ["Scalp (<5min)", "Short (5-30min)", "Medium (30min-2hr)", "Long (>2hr)"]
                        current_duration = trade.get('trade_duration', 'Short (5-30min)')
                        try:
                            duration_idx = duration_options.index(current_duration)
                        except ValueError:
                            duration_idx = 1
                        
                        edited_trade_duration = st.selectbox("Trade Duration", duration_options, 
                                                           index=duration_idx, key=f"edit_duration_{original_idx}")
                    
                    # Notes
                    edited_notes = st.text_area("Trade Notes", value=trade.get('notes', ''), 
                                              key=f"edit_notes_{original_idx}")
                    
                    # Action buttons
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.form_submit_button("Save Changes", type="primary"):
                            # Calculate balance adjustment
                            old_pnl = trade['pnl_net']
                            pnl_difference = edited_pnl_net - old_pnl
                            
                            # Update trade data
                            updated_trade = {
                                "id": trade.get('id', original_idx + 1),
                                "date": edited_date.isoformat(),
                                "entry_time": edited_entry_time.isoformat(),
                                "exit_time": edited_exit_time.isoformat(),
                                "account": edited_account,
                                "account_id": trade.get('account_id', ''),
                                "playbook": edited_playbook,
                                "symbol": edited_symbol,
                                "direction": edited_direction,
                                "position_size": edited_position_size,
                                "pnl_gross": edited_pnl_gross,
                                "pnl_net": edited_pnl_net,
                                "commission": edited_commission,
                                "setup_quality": edited_setup_quality,
                                "execution_quality": edited_execution_quality,
                                "emotional_state": edited_emotional_state,
                                "was_planned": edited_was_planned,
                                "followed_rules": edited_followed_rules,
                                "would_repeat": edited_would_repeat,
                                "rule_compliance": edited_rule_compliance,  # FIX: Save updated rule compliance
                                "session": edited_session,
                                "market_condition": edited_market_condition,
                                "volume_condition": edited_volume_condition,
                                "trade_duration": edited_trade_duration,
                                "notes": edited_notes,
                                "timestamp": trade.get('timestamp', datetime.now().isoformat()),
                                "updated_at": datetime.now().isoformat()
                            }
                            
                            # Add price data if provided
                            if edited_entry_price > 0:
                                updated_trade['entry_price'] = edited_entry_price
                            if edited_exit_price > 0:
                                updated_trade['exit_price'] = edited_exit_price
                            if edited_entry_price > 0 and edited_exit_price > 0:
                                if edited_direction == "Long":
                                    updated_trade['pnl_points'] = edited_exit_price - edited_entry_price
                                else:
                                    updated_trade['pnl_points'] = edited_entry_price - edited_exit_price
                            
                            # Update trades list
                            trades[original_idx] = updated_trade
                            
                            # Update account balance if P&L changed
                            if pnl_difference != 0:
                                accounts = self.data_storage.load_accounts()
                                account_id = trade.get('account_id', '')
                                
                                for j, acc in enumerate(accounts):
                                    if acc['account_number'] == account_id:
                                        accounts[j]['current_balance'] += pnl_difference
                                        accounts[j]['updated_at'] = datetime.now().isoformat()
                                        self.data_storage.save_accounts(accounts)
                                        break
                            
                            # Save trades
                            self.data_storage.save_trades(trades)
                            
                            success_msg = f"Trade updated successfully!"
                            if pnl_difference != 0:
                                success_msg += f" Account balance adjusted by ${pnl_difference:+.2f}"
                            
                            st.success(success_msg)
                            st.rerun()
                    
                    with col2:
                        if st.form_submit_button("Delete Trade", type="secondary"):
                            # Restore P&L to account balance
                            accounts = self.data_storage.load_accounts()
                            account_id = trade.get('account_id', '')
                            
                            for j, acc in enumerate(accounts):
                                if acc['account_number'] == account_id:
                                    accounts[j]['current_balance'] -= trade['pnl_net']
                                    accounts[j]['updated_at'] = datetime.now().isoformat()
                                    self.data_storage.save_accounts(accounts)
                                    break
                            
                            # Remove trade from list
                            trades.pop(original_idx)
                            self.data_storage.save_trades(trades)
                            
                            st.success(f"Trade deleted! ${trade['pnl_net']:+.2f} removed from account balance.")
                            st.rerun()
                    
                    with col3:
                        st.write("**Current P&L Impact:**")
                        st.write(f"Original: ${trade['pnl_net']:+.2f}")
                        st.write(f"New: ${edited_pnl_net:+.2f}")
                        st.write(f"Difference: ${edited_pnl_net - trade['pnl_net']:+.2f}")
    
    def daily_checkin(self):
        st.subheader("Daily Pre-Market Check-in")
        st.write("Complete your daily psychological check-in before trading.")
        
        checkins = self.data_storage.load_daily_checkins()
        today = date.today().isoformat()
        
        # Check if already checked in today
        today_checkin = next((c for c in checkins if c.get('date') == today), None)
        
        if today_checkin:
            st.success("✅ You've already completed today's check-in!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Sleep Quality", f"{today_checkin['sleep_quality']}/10")
                st.metric("Stress Level", f"{today_checkin['stress_level']}/10")
            
            with col2:
                st.metric("Home Stress", f"{today_checkin['home_stress']}/10")
                alcohol_text = "Yes" if today_checkin['alcohol_24h'] else "No"
                st.metric("Alcohol (24h)", alcohol_text)
            
            with col3:
                exercise_text = "Yes" if today_checkin['exercise'] else "No"
                st.metric("Exercise", exercise_text)
                
            if today_checkin.get('trading_plan'):
                st.write(f"**Today's Trading Plan:** {today_checkin['trading_plan']}")
            
            # Trading approval
            high_risk_factors = (
                today_checkin['stress_level'] > 7 or 
                today_checkin['home_stress'] > 7 or 
                today_checkin['alcohol_24h'] or
                today_checkin['sleep_quality'] < 5
            )
            
            if high_risk_factors:
                st.error("🚨 HIGH RISK TRADING DAY - Consider taking the day off")
                risk_factors = []
                if today_checkin['stress_level'] > 7:
                    risk_factors.append("High stress level")
                if today_checkin['home_stress'] > 7:
                    risk_factors.append("High home stress")
                if today_checkin['alcohol_24h']:
                    risk_factors.append("Alcohol consumed in last 24h")
                if today_checkin['sleep_quality'] < 5:
                    risk_factors.append("Poor sleep quality")
                
                st.write("**Risk factors:**")
                for factor in risk_factors:
                    st.write(f"- {factor}")
            else:
                st.success("✅ CLEARED FOR TRADING - Good psychological state")
        else:
            # New check-in form
            with st.form("daily_checkin"):
                st.write("Rate each factor honestly (1-10 scale):")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    sleep_quality = st.slider("Sleep Quality", 1, 10, 7,
                                            help="10 = Excellent, refreshing sleep")
                    stress_level = st.slider("Current Stress Level", 1, 10, 5,
                                           help="10 = Extremely stressed")
                    home_stress = st.slider("Home/Relationship Stress", 1, 10, 5,
                                          help="10 = Major relationship issues")
                
                with col2:
                    alcohol_24h = st.checkbox("Consumed alcohol in last 24 hours")
                    exercise = st.checkbox("Did exercise/movement today or yesterday")
                    
                # Trading plan
                trading_plan = st.text_area("Today's Trading Plan",
                                          placeholder="What setups will you look for? Max trades? Position sizing plan?")
                
                # Emotional state
                current_emotions = st.text_area("Current Emotional State",
                                              placeholder="How are you feeling? Any concerns or distractions?")
                
                if st.form_submit_button("Complete Check-in", type="primary"):
                    checkin_data = {
                        "sleep_quality": sleep_quality,
                        "stress_level": stress_level,
                        "home_stress": home_stress,
                        "alcohol_24h": alcohol_24h,
                        "exercise": exercise,
                        "trading_plan": trading_plan,
                        "current_emotions": current_emotions
                    }
                    
                    self.data_storage.add_daily_checkin(checkin_data)
                    st.success("Check-in completed!")
                    st.rerun()
        
        # Recent check-ins
        if len(checkins) > 1:
            st.subheader("Recent Check-ins")
            recent_checkins = sorted(checkins, key=lambda x: x['date'], reverse=True)[:7]
            
            df_checkins = pd.DataFrame(recent_checkins)
            
            # Create trend chart
            fig_data = {
                'Date': [c['date'] for c in recent_checkins],
                'Sleep Quality': [c['sleep_quality'] for c in recent_checkins],
                'Stress Level': [c['stress_level'] for c in recent_checkins],
                'Home Stress': [c['home_stress'] for c in recent_checkins]
            }
            
            st.line_chart(pd.DataFrame(fig_data).set_index('Date'))