import streamlit as st
from datetime import datetime
from typing import Dict, List

class ConfigManager:
    def __init__(self, data_storage):
        self.data_storage = data_storage
    
    def manage_prop_firms(self):
        st.subheader("Prop Firm Configuration")
        
        firms = self.data_storage.load_prop_firms()
        
        # Add new firm
        with st.expander("âž• Add New Prop Firm", expanded=not firms):
            with st.form("add_firm"):
                col1, col2 = st.columns(2)
                
                with col1:
                    firm_name = st.text_input("Firm Name", placeholder="e.g., Tradeify")
                    payout_schedule = st.selectbox("Payout Schedule", 
                                                  ["Weekly", "Bi-Weekly", "Monthly", "On Demand", "Daily"])
                    min_payout = st.number_input("Minimum Payout ($)", min_value=0, value=100)
                
                with col2:
                    payout_split = st.slider("Profit Split (%)", 0, 100, 80)
                    max_daily_loss = st.number_input("Max Daily Loss (%)", min_value=0.0, value=3.0, step=0.5)
                    max_drawdown = st.number_input("Max Drawdown (%)", min_value=0.0, value=6.0, step=0.5)
                
                notes = st.text_area("Notes", placeholder="Any special rules or notes...")
                
                if st.form_submit_button("Add Prop Firm"):
                    if firm_name:
                        firm_data = {
                            "name": firm_name,
                            "payout_schedule": payout_schedule,
                            "payout_split": payout_split,
                            "min_payout": min_payout,
                            "max_daily_loss": max_daily_loss,
                            "max_drawdown": max_drawdown,
                            "notes": notes
                        }
                        self.data_storage.add_prop_firm(firm_data)
                        st.success(f"Added {firm_name}!")
                        st.rerun()
                    else:
                        st.error("Please enter a firm name")
        
        # Display existing firms
        if firms:
            st.write("### Existing Prop Firms")
            for i, firm in enumerate(firms):
                with st.expander(f"ðŸ“Š {firm.get('name', 'Unknown')}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Payout Schedule:** {firm.get('payout_schedule', 'N/A')}")
                        st.write(f"**Min Payout:** ${firm.get('min_payout', 0)}")
                    
                    with col2:
                        st.write(f"**Profit Split:** {firm.get('payout_split', 0)}%")
                        st.write(f"**Max Daily Loss:** {firm.get('max_daily_loss', 0)}%")
                    
                    with col3:
                        st.write(f"**Max Drawdown:** {firm.get('max_drawdown', 0)}%")
                    
                    if firm.get('notes'):
                        st.write(f"**Notes:** {firm['notes']}")
                    
                    # Delete button
                    if st.button(f"Delete {firm.get('name', 'Unknown')}", key=f"del_firm_{i}"):
                        firms.pop(i)
                        self.data_storage.save_prop_firms(firms)
                        st.success(f"Deleted {firm.get('name', 'firm')}")
                        st.rerun()
    
    def manage_accounts(self):
        st.subheader("Account Management")
        
        accounts = self.data_storage.load_accounts()
        firms = self.data_storage.load_prop_firms()
        
        if not firms:
            st.warning("Please add at least one prop firm first.")
            return
        
        # Add new account
        with st.expander("âž• Add New Account", expanded=not accounts):
            with st.form("add_account"):
                col1, col2 = st.columns(2)
                
                with col1:
                    firm_names = [f.get('name', 'Unknown') for f in firms]
                    selected_firm = st.selectbox("Prop Firm", firm_names)
                    
                    account_type = st.selectbox("Account Type", 
                                               ["evaluation", "funded", "blown", "inactive"])
                    account_size = st.selectbox("Account Size", 
                                               [25000, 50000, 100000, 150000, 200000, 250000, 300000])
                    account_number = st.text_input("Account Number/ID", placeholder="e.g., ACC-12345")
                
                with col2:
                    current_balance = st.number_input("Current Balance ($)", 
                                                     min_value=0.0, value=float(account_size))
                    purchase_cost = st.number_input("Purchase Cost ($)", min_value=0.0, value=0.0)
                    purchase_date = st.date_input("Purchase Date")
                    growth_or_static = st.selectbox("Account Style", ["Growth", "Static", "Standard"])
                
                account_notes = st.text_area("Account Notes", placeholder="Any specific notes...")
                
                if st.form_submit_button("Add Account"):
                    if account_number:
                        account_data = {
                            "prop_firm": selected_firm,
                            "account_type": account_type,
                            "account_size": account_size,
                            "account_number": account_number,
                            "current_balance": current_balance,
                            "purchase_cost": purchase_cost,
                            "purchase_date": purchase_date.isoformat(),
                            "account_style": growth_or_static,
                            "notes": account_notes,
                            "status": account_type
                        }
                        self.data_storage.add_account(account_data)
                        st.success(f"Added account {account_number}!")
                        st.rerun()
                    else:
                        st.error("Please enter an account number")
        
        # Display existing accounts
        if accounts:
            st.write("### Existing Accounts")
            
            # Filter by status
            status_filter = st.selectbox("Filter by Status", 
                                        ["All", "evaluation", "funded", "blown", "inactive"])
            
            filtered_accounts = accounts if status_filter == "All" else \
                               [a for a in accounts if a.get('status') == status_filter]
            
            for i, acc in enumerate(filtered_accounts):
                status_emoji = {"evaluation": "ðŸ“", "funded": "ðŸ’°", "blown": "ðŸ’¥", "inactive": "â¸ï¸"}
                emoji = status_emoji.get(acc.get('status', ''), "ðŸ“Š")
                
                account_size = acc.get('account_size', 0)
                current_balance = acc.get('current_balance', account_size)
                pnl = current_balance - account_size
                
                with st.expander(f"{emoji} {acc.get('prop_firm', 'Unknown')} - {acc.get('account_type', 'N/A')} ${account_size:,} ({acc.get('account_number', 'N/A')})"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Current Balance:** ${current_balance:,.2f}")
                        color = 'green' if pnl >= 0 else 'red'
                        st.write(f"**P&L:** :{color}[${pnl:+,.2f}]")
                        st.write(f"**Status:** {acc.get('status', 'unknown')}")
                    
                    with col2:
                        st.write(f"**Account Style:** {acc.get('account_style', 'Standard')}")
                        st.write(f"**Purchase Cost:** ${acc.get('purchase_cost', 0):.2f}")
                        st.write(f"**Purchase Date:** {acc.get('purchase_date', 'N/A')}")
                    
                    with col3:
                        # Quick actions
                        new_status = st.selectbox(f"Change Status", 
                                                 ["evaluation", "funded", "blown", "inactive"],
                                                 index=["evaluation", "funded", "blown", "inactive"].index(acc.get('status', 'evaluation')),
                                                 key=f"status_{i}")
                        
                        if new_status != acc.get('status'):
                            if st.button("Update Status", key=f"update_status_{i}"):
                                original_idx = accounts.index(acc)
                                accounts[original_idx]['status'] = new_status
                                accounts[original_idx]['updated_at'] = datetime.now().isoformat()
                                self.data_storage.save_accounts(accounts)
                                st.success("Status updated!")
                                st.rerun()
                    
                    # Balance adjustment
                    st.write("---")
                    col1, col2 = st.columns(2)
                    with col1:
                        new_balance = st.number_input("Adjust Balance", 
                                                     value=current_balance,
                                                     key=f"balance_{i}")
                    with col2:
                        if st.button("Update Balance", key=f"update_bal_{i}"):
                            original_idx = accounts.index(acc)
                            accounts[original_idx]['current_balance'] = new_balance
                            accounts[original_idx]['updated_at'] = datetime.now().isoformat()
                            self.data_storage.save_accounts(accounts)
                            st.success("Balance updated!")
                            st.rerun()
                    
                    # Delete account
                    if st.button(f"ðŸ—‘ï¸ Delete Account", key=f"del_acc_{i}"):
                        original_idx = accounts.index(acc)
                        accounts.pop(original_idx)
                        self.data_storage.save_accounts(accounts)
                        st.success("Account deleted!")
                        st.rerun()
    
    def manage_playbooks(self):
        st.subheader("Trading Playbooks")
        st.write("Define your proven setups with specific rules for each.")
        st.info("ðŸ’¡ Tip: Use **Settings > Grade Rules** for your main setup's real-time grading checklist.")
        
        playbooks = self.data_storage.load_playbooks()
        
        # Add new playbook
        with st.expander("âž• Add New Playbook", expanded=not playbooks):
            with st.form("add_playbook"):
                playbook_name = st.text_input("Playbook Name", placeholder="e.g., Opening Range Breakout")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    description = st.text_area("Description", 
                                              placeholder="Describe the setup, when it works best...")
                    timeframes = st.multiselect("Timeframes", 
                                               ["1m", "5m", "15m", "30m", "1H", "4H", "Daily"])
                
                with col2:
                    markets = st.multiselect("Markets", 
                                            ["ES", "NQ", "YM", "RTY", "CL", "GC", "6E", "Other"])
                    win_rate_target = st.slider("Expected Win Rate (%)", 0, 100, 50)
                    risk_reward = st.text_input("Risk:Reward", placeholder="e.g., 1:2")
                
                # Rules section
                st.write("**Trading Rules (one per line)**")
                rules_text = st.text_area("Rules", 
                                         placeholder="Enter each rule on a new line:\nWait for confirmation\nUse proper position sizing\nSet stop loss before entry",
                                         height=150)
                
                entry_criteria = st.text_area("Entry Criteria", 
                                             placeholder="What conditions must be met to enter?")
                exit_criteria = st.text_area("Exit Criteria", 
                                            placeholder="When do you exit? (targets, stops, time)")
                
                if st.form_submit_button("Add Playbook"):
                    if playbook_name:
                        rules = [r.strip() for r in rules_text.split('\n') if r.strip()]
                        
                        playbook_data = {
                            "name": playbook_name,
                            "description": description,
                            "timeframes": timeframes,
                            "markets": markets,
                            "win_rate_target": win_rate_target,
                            "risk_reward": risk_reward,
                            "rules": rules,
                            "entry_criteria": entry_criteria,
                            "exit_criteria": exit_criteria
                        }
                        self.data_storage.add_playbook(playbook_data)
                        st.success(f"Added playbook: {playbook_name}!")
                        st.rerun()
                    else:
                        st.error("Please enter a playbook name")
        
        # Display existing playbooks
        if playbooks:
            st.write("### Your Playbooks")
            
            for i, pb in enumerate(playbooks):
                with st.expander(f"ðŸ“– {pb.get('name', 'Unknown')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Description:** {pb.get('description', 'N/A')}")
                        st.write(f"**Timeframes:** {', '.join(pb.get('timeframes', []))}")
                        st.write(f"**Markets:** {', '.join(pb.get('markets', []))}")
                    
                    with col2:
                        st.write(f"**Target Win Rate:** {pb.get('win_rate_target', 'N/A')}%")
                        st.write(f"**Risk:Reward:** {pb.get('risk_reward', 'N/A')}")
                    
                    if pb.get('rules'):
                        st.write("**Rules:**")
                        for rule in pb['rules']:
                            st.write(f"  âœ“ {rule}")
                    
                    if pb.get('entry_criteria'):
                        st.write(f"**Entry:** {pb['entry_criteria']}")
                    
                    if pb.get('exit_criteria'):
                        st.write(f"**Exit:** {pb['exit_criteria']}")
                    
                    # Calculate performance from trades
                    trades = self.data_storage.load_trades()
                    pb_trades = [t for t in trades if t.get('playbook') == pb.get('name')]
                    
                    if pb_trades:
                        st.write("---")
                        st.write("**Performance Stats:**")
                        total = len(pb_trades)
                        wins = sum(1 for t in pb_trades if t.get('pnl_net', 0) > 0)
                        total_pnl = sum(t.get('pnl_net', 0) for t in pb_trades)
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Trades", total)
                        with col2:
                            st.metric("Win Rate", f"{(wins/total*100):.1f}%")
                        with col3:
                            st.metric("Total P&L", f"${total_pnl:.2f}")
                    
                    # Delete playbook
                    if st.button(f"ðŸ—‘ï¸ Delete Playbook", key=f"del_pb_{i}"):
                        playbooks.pop(i)
                        self.data_storage.save_playbooks(playbooks)
                        st.success("Playbook deleted!")
                        st.rerun()
    
    def manage_withdrawals(self):
        st.subheader("Withdrawal Tracking")
        
        withdrawals = self.data_storage.load_withdrawals()
        accounts = self.data_storage.load_accounts()
        settings = self.data_storage.load_settings()
        
        funded_accounts = [a for a in accounts if a.get('status') == 'funded']
        
        if not funded_accounts:
            st.info("No funded accounts available for withdrawals.")
        else:
            # Add withdrawal
            with st.expander("âž• Log New Withdrawal", expanded=not withdrawals):
                with st.form("add_withdrawal"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        account_options = [f"{a.get('prop_firm', 'Unknown')} - ${a.get('account_size', 0):,} ({a.get('account_number', 'N/A')})" 
                                          for a in funded_accounts]
                        selected_account = st.selectbox("Account", account_options)
                        
                        amount = st.number_input("Total Withdrawal ($)", min_value=0.01, value=100.0)
                        withdrawal_date = st.date_input("Withdrawal Date")
                    
                    with col2:
                        status = st.selectbox("Status", ["pending", "approved", "paid", "rejected"])
                    
                    # Multi-allocation
                    st.write("**Allocation Breakdown:**")
                    st.caption("Split this payout across multiple purposes")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        debt_amt = st.number_input("Debt Payment ($)", min_value=0.0, value=0.0, step=10.0)
                    with col2:
                        reinvest_amt = st.number_input("Reinvestment ($)", min_value=0.0, value=0.0, step=10.0)
                    with col3:
                        savings_amt = st.number_input("Savings ($)", min_value=0.0, value=0.0, step=10.0)
                    with col4:
                        personal_amt = st.number_input("Personal ($)", min_value=0.0, value=0.0, step=10.0)
                    
                    # Validation
                    allocated = debt_amt + reinvest_amt + savings_amt + personal_amt
                    remaining = amount - allocated
                    
                    if remaining > 0:
                        st.warning(f"${remaining:.2f} unallocated")
                    elif remaining < 0:
                        st.error(f"Over-allocated by ${abs(remaining):.2f}")
                    else:
                        st.success("âœ“ Fully allocated")
                    
                    reinvest_details = st.text_input("Reinvestment Details", 
                                                    placeholder="e.g., New 100K eval from Tradeify")
                    notes = st.text_area("Notes", placeholder="Any additional details...")
                    
                    if st.form_submit_button("Log Withdrawal"):
                        if remaining != 0:
                            st.error("Please allocate the exact withdrawal amount")
                        else:
                            acc_idx = account_options.index(selected_account)
                            selected_acc = funded_accounts[acc_idx]
                            
                            withdrawal_data = {
                                "account": selected_account,
                                "account_id": selected_acc.get('account_number', ''),
                                "prop_firm": selected_acc.get('prop_firm', ''),
                                "amount": amount,
                                "date": withdrawal_date.isoformat(),
                                "status": status,
                                "allocations": {
                                    "debt": debt_amt,
                                    "reinvestment": reinvest_amt,
                                    "savings": savings_amt,
                                    "personal": personal_amt
                                },
                                "reinvest_details": reinvest_details,
                                "notes": notes
                            }
                            self.data_storage.add_withdrawal(withdrawal_data)
                            
                            # Deduct from account balance
                            all_accounts = self.data_storage.load_accounts()
                            for i, acc in enumerate(all_accounts):
                                if acc.get('account_number') == selected_acc.get('account_number'):
                                    current_bal = acc.get('current_balance', acc.get('account_size', 0))
                                    all_accounts[i]['current_balance'] = current_bal - amount
                                    all_accounts[i]['updated_at'] = datetime.now().isoformat()
                                    break
                            self.data_storage.save_accounts(all_accounts)
                            
                            st.success(f"Logged ${amount:.2f} withdrawal! Account balance updated.")
                            st.rerun()
        
        # Display withdrawals
        if withdrawals:
            st.write("### Withdrawal History")
            
            # Summary - handle both old and new format
            total_withdrawn = sum(w.get('amount', 0) for w in withdrawals if w.get('status') == 'paid')
            pending = sum(w.get('amount', 0) for w in withdrawals if w.get('status') == 'pending')
            
            # Calculate from allocations (new format) or allocation field (old format)
            reinvested = 0
            debt_paid = 0
            savings = 0
            personal = 0
            
            for w in withdrawals:
                if w.get('status') != 'paid':
                    continue
                    
                if 'allocations' in w:
                    # New format
                    alloc = w['allocations']
                    reinvested += alloc.get('reinvestment', 0)
                    debt_paid += alloc.get('debt', 0)
                    savings += alloc.get('savings', 0)
                    personal += alloc.get('personal', 0)
                else:
                    # Old format - single allocation
                    amt = w.get('amount', 0)
                    alloc_type = w.get('allocation', '')
                    if alloc_type == 'Reinvestment':
                        reinvested += amt
                    elif alloc_type == 'Debt Payment':
                        debt_paid += amt
                    elif alloc_type == 'Savings':
                        savings += amt
                    elif alloc_type == 'Personal':
                        personal += amt
            
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Total Paid", f"${total_withdrawn:,.2f}")
            col2.metric("Debt Paid", f"${debt_paid:,.2f}")
            col3.metric("Reinvested", f"${reinvested:,.2f}")
            col4.metric("Savings", f"${savings:,.2f}")
            col5.metric("Personal", f"${personal:,.2f}")
            
            # Pending
            if pending > 0:
                st.info(f"â³ Pending: ${pending:,.2f}")
            
            # Withdrawal list
            for i, w in enumerate(sorted(withdrawals, key=lambda x: x.get('date', ''), reverse=True)):
                status_emoji = {"pending": "â³", "approved": "âœ…", "paid": "ðŸ’°", "rejected": "âŒ"}
                emoji = status_emoji.get(w.get('status', ''), "ðŸ“Š")
                
                with st.expander(f"{emoji} ${w.get('amount', 0):,.2f} - {w.get('prop_firm', 'Unknown')} ({w.get('date', 'N/A')})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Account:** {w.get('account', 'N/A')}")
                        st.write(f"**Status:** {w.get('status', 'N/A')}")
                        
                        # Show allocations
                        if 'allocations' in w:
                            st.write("**Allocations:**")
                            alloc = w['allocations']
                            if alloc.get('debt', 0) > 0:
                                st.write(f"  â€¢ Debt: ${alloc['debt']:,.2f}")
                            if alloc.get('reinvestment', 0) > 0:
                                st.write(f"  â€¢ Reinvest: ${alloc['reinvestment']:,.2f}")
                            if alloc.get('savings', 0) > 0:
                                st.write(f"  â€¢ Savings: ${alloc['savings']:,.2f}")
                            if alloc.get('personal', 0) > 0:
                                st.write(f"  â€¢ Personal: ${alloc['personal']:,.2f}")
                        else:
                            st.write(f"**Allocation:** {w.get('allocation', 'N/A')}")
                    
                    with col2:
                        if w.get('reinvest_details'):
                            st.write(f"**Reinvestment:** {w['reinvest_details']}")
                        if w.get('notes'):
                            st.write(f"**Notes:** {w['notes']}")
                    
                    # Update status
                    new_status = st.selectbox("Update Status", 
                                             ["pending", "approved", "paid", "rejected"],
                                             index=["pending", "approved", "paid", "rejected"].index(w.get('status', 'pending')),
                                             key=f"w_status_{i}")
                    
                    if new_status != w.get('status'):
                        if st.button("Update", key=f"update_w_{i}"):
                            withdrawals[i]['status'] = new_status
                            self.data_storage.save_withdrawals(withdrawals)
                            st.success("Status updated!")
                            st.rerun()
