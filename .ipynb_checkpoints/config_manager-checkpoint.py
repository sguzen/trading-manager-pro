import streamlit as st
import pandas as pd
from datetime import date, datetime
from typing import Dict, List

class ConfigManager:
    def __init__(self, data_storage):
        self.data_storage = data_storage
    
    def manage_prop_firms(self):
        st.subheader("Prop Firm Configuration")
        
        prop_firms = self.data_storage.load_prop_firms()
        
        # Add new prop firm
        with st.expander("Add New Prop Firm"):
            with st.form("add_prop_firm"):
                name = st.text_input("Prop Firm Name")
                account_types = st.text_area("Account Types (one per line)", 
                                           placeholder="50K\n100K\n150K")
                
                col1, col2 = st.columns(2)
                with col1:
                    payout_percentage = st.number_input("Payout Percentage", 
                                                      min_value=50, max_value=95, value=80)
                    min_trading_days = st.number_input("Minimum Trading Days", 
                                                     min_value=1, max_value=20, value=5)
                
                with col2:
                    max_daily_loss_base = st.number_input("Max Daily Loss (for base account)", 
                                                        min_value=100, value=2000)
                    max_total_loss_base = st.number_input("Max Total Loss (for base account)", 
                                                        min_value=100, value=3000)
                    profit_target_base = st.number_input("Profit Target (for base account)", 
                                                       min_value=100, value=3000)
                
                special_features = st.text_area("Special Features (one per line)", 
                                              placeholder="Daily Payouts\nHigh Leverage")
                
                if st.form_submit_button("Add Prop Firm"):
                    if name and account_types:
                        account_list = [acc.strip() for acc in account_types.split('\n') if acc.strip()]
                        
                        new_firm = {
                            "name": name,
                            "account_types": account_list,
                            "max_daily_loss": {acc: max_daily_loss_base for acc in account_list},
                            "max_total_loss": {acc: max_total_loss_base for acc in account_list},
                            "profit_target": {acc: profit_target_base for acc in account_list},
                            "payout_percentage": payout_percentage,
                            "min_trading_days": min_trading_days
                        }
                        
                        if special_features:
                            new_firm["special_features"] = [feat.strip() for feat in special_features.split('\n') if feat.strip()]
                        
                        prop_firms.append(new_firm)
                        self.data_storage.save_prop_firms(prop_firms)
                        st.success(f"Added {name} successfully!")
                        st.rerun()
        
        # Display and edit existing prop firms
        st.subheader("Edit Existing Prop Firms")
        
        if not prop_firms:
            st.info("No prop firms configured yet.")
            return
        
        for i, firm in enumerate(prop_firms):
            with st.expander(f"✏️ Edit {firm['name']} - {len(firm['account_types'])} Account Types", expanded=False):
                with st.form(f"edit_firm_{i}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        edited_name = st.text_input("Firm Name", value=firm['name'], key=f"name_{i}")
                        edited_payout = st.number_input("Payout %", 
                                                      value=firm['payout_percentage'],
                                                      min_value=50, max_value=95, key=f"payout_{i}")
                        edited_min_days = st.number_input("Min Trading Days",
                                                        value=firm['min_trading_days'],
                                                        min_value=1, max_value=20, key=f"days_{i}")
                    
                    with col2:
                        edited_account_types = st.text_area("Account Types (one per line)",
                                                          value='\n'.join(firm['account_types']),
                                                          key=f"types_{i}")
                        edited_features = st.text_area("Special Features (one per line)",
                                                     value='\n'.join(firm.get('special_features', [])),
                                                     key=f"features_{i}")
                    
                    # Account-specific rules editing
                    st.write("**Edit Rules by Account Type:**")
                    edited_daily_loss = {}
                    edited_total_loss = {}
                    edited_profit_target = {}
                    
                    for acc_type in firm['account_types']:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            edited_daily_loss[acc_type] = st.number_input(
                                f"Max Daily Loss - {acc_type}",
                                value=firm['max_daily_loss'].get(acc_type, 0),
                                min_value=0,
                                key=f"daily_{i}_{acc_type}"
                            )
                        with col2:
                            edited_total_loss[acc_type] = st.number_input(
                                f"Max Total Loss - {acc_type}",
                                value=firm['max_total_loss'].get(acc_type, 0),
                                min_value=0,
                                key=f"total_{i}_{acc_type}"
                            )
                        with col3:
                            edited_profit_target[acc_type] = st.number_input(
                                f"Profit Target - {acc_type}",
                                value=firm['profit_target'].get(acc_type, 0),
                                min_value=0,
                                key=f"target_{i}_{acc_type}"
                            )
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.form_submit_button("Save Changes", type="primary"):
                            account_list = [acc.strip() for acc in edited_account_types.split('\n') if acc.strip()]
                            feature_list = [feat.strip() for feat in edited_features.split('\n') if feat.strip()]
                            
                            prop_firms[i] = {
                                "name": edited_name,
                                "account_types": account_list,
                                "max_daily_loss": edited_daily_loss,
                                "max_total_loss": edited_total_loss,
                                "profit_target": edited_profit_target,
                                "payout_percentage": edited_payout,
                                "min_trading_days": edited_min_days
                            }
                            
                            if feature_list:
                                prop_firms[i]["special_features"] = feature_list
                            
                            self.data_storage.save_prop_firms(prop_firms)
                            st.success(f"Updated {edited_name} successfully!")
                            st.rerun()
                    
                    with col2:
                        if st.form_submit_button("Delete Firm", type="secondary"):
                            prop_firms.pop(i)
                            self.data_storage.save_prop_firms(prop_firms)
                            st.success(f"Deleted {firm['name']}")
                            st.rerun()
    
    def manage_accounts(self):
        st.subheader("Account Management")
        
        accounts = self.data_storage.load_accounts()
        prop_firms = self.data_storage.load_prop_firms()
        
        # Add new account
        with st.expander("Add New Account"):
            with st.form("add_account"):
                prop_firm = st.selectbox("Prop Firm", [firm['name'] for firm in prop_firms])
                
                if prop_firm:
                    selected_firm = next((firm for firm in prop_firms if firm['name'] == prop_firm), None)
                    if selected_firm:
                        account_type = st.selectbox("Account Type", selected_firm['account_types'])
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            status = st.selectbox("Status", ["evaluation", "funded", "failed", "passed"])
                            account_number = st.text_input("Account Number (optional)")
                        
                        with col2:
                            start_date = st.date_input("Start Date", value=date.today())
                            current_balance = st.number_input("Current Balance", value=0.0)
                        
                        notes = st.text_area("Notes")
                        
                        if st.form_submit_button("Add Account"):
                            new_account = {
                                "prop_firm": prop_firm,
                                "account_type": account_type,
                                "account_number": account_number or f"{prop_firm}_{len(accounts)+1}",
                                "status": status,
                                "start_date": start_date.isoformat(),
                                "current_balance": current_balance,
                                "max_daily_loss": selected_firm['max_daily_loss'].get(account_type, 0),
                                "max_total_loss": selected_firm['max_total_loss'].get(account_type, 0),
                                "profit_target": selected_firm['profit_target'].get(account_type, 0),
                                "payout_percentage": selected_firm['payout_percentage'],
                                "notes": notes,
                                "created_at": datetime.now().isoformat()
                            }
                            
                            accounts.append(new_account)
                            self.data_storage.save_accounts(accounts)
                            st.success("Account added successfully!")
                            st.rerun()
        
        # Display and edit existing accounts
        st.subheader("Edit Your Accounts")
        
        if not accounts:
            st.info("No accounts configured yet.")
            return
        
        for i, account in enumerate(accounts):
            status_emoji = {"evaluation": "🔍", "funded": "💰", "failed": "❌", "passed": "✅"}
            
            with st.expander(f"✏️ Edit {status_emoji.get(account['status'], '📊')} {account['prop_firm']} - {account['account_type']}", expanded=False):
                with st.form(f"edit_account_{i}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Account basics
                        edited_prop_firm = st.selectbox("Prop Firm", 
                                                      [firm['name'] for firm in prop_firms],
                                                      index=[firm['name'] for firm in prop_firms].index(account['prop_firm']) if account['prop_firm'] in [firm['name'] for firm in prop_firms] else 0,
                                                      key=f"acc_firm_{i}")
                        
                        selected_firm = next((firm for firm in prop_firms if firm['name'] == edited_prop_firm), None)
                        if selected_firm:
                            current_type_idx = selected_firm['account_types'].index(account['account_type']) if account['account_type'] in selected_firm['account_types'] else 0
                            edited_account_type = st.selectbox("Account Type",
                                                             selected_firm['account_types'],
                                                             index=current_type_idx,
                                                             key=f"acc_type_{i}")
                        
                        edited_account_number = st.text_input("Account Number",
                                                            value=account['account_number'],
                                                            key=f"acc_num_{i}")
                        
                        edited_status = st.selectbox("Status",
                                                   ["evaluation", "funded", "failed", "passed"],
                                                   index=["evaluation", "funded", "failed", "passed"].index(account['status']),
                                                   key=f"acc_status_{i}")
                    
                    with col2:
                        edited_start_date = st.date_input("Start Date",
                                                        value=pd.to_datetime(account['start_date']).date(),
                                                        key=f"acc_date_{i}")
                        
                        edited_balance = st.number_input("Current Balance",
                                                       value=account['current_balance'],
                                                       key=f"acc_balance_{i}")
                        
                        # Manual rule overrides
                        edited_daily_loss = st.number_input("Max Daily Loss Override",
                                                          value=account['max_daily_loss'],
                                                          min_value=0,
                                                          key=f"acc_daily_{i}")
                        
                        edited_total_loss = st.number_input("Max Total Loss Override",
                                                          value=account['max_total_loss'],
                                                          min_value=0,
                                                          key=f"acc_total_{i}")
                    
                    edited_profit_target = st.number_input("Profit Target Override",
                                                         value=account['profit_target'],
                                                         min_value=0,
                                                         key=f"acc_target_{i}")
                    
                    edited_notes = st.text_area("Notes",
                                              value=account.get('notes', ''),
                                              key=f"acc_notes_{i}")
                    
                    # Progress indicator
                    if edited_profit_target > 0:
                        progress = (edited_balance / edited_profit_target) * 100
                        st.progress(min(progress / 100, 1.0))
                        st.write(f"Progress to target: {progress:.1f}%")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.form_submit_button("Save Changes", type="primary"):
                            accounts[i] = {
                                "prop_firm": edited_prop_firm,
                                "account_type": edited_account_type,
                                "account_number": edited_account_number,
                                "status": edited_status,
                                "start_date": edited_start_date.isoformat(),
                                "current_balance": edited_balance,
                                "max_daily_loss": edited_daily_loss,
                                "max_total_loss": edited_total_loss,
                                "profit_target": edited_profit_target,
                                "payout_percentage": selected_firm['payout_percentage'] if selected_firm else account.get('payout_percentage', 80),
                                "notes": edited_notes,
                                "created_at": account.get('created_at', datetime.now().isoformat()),
                                "updated_at": datetime.now().isoformat()
                            }
                            
                            self.data_storage.save_accounts(accounts)
                            st.success("Account updated successfully!")
                            st.rerun()
                    
                    with col2:
                        if st.form_submit_button("Delete Account", type="secondary"):
                            accounts.pop(i)
                            self.data_storage.save_accounts(accounts)
                            st.success("Account deleted!")
                            st.rerun()
    
    def manage_playbooks(self):
        st.subheader("Trading Playbooks")
        
        playbooks = self.data_storage.load_playbooks()
        
        # Add new playbook
        with st.expander("Create New Playbook"):
            with st.form("add_playbook"):
                name = st.text_input("Playbook Name")
                description = st.text_area("Description")
                
                rules = st.text_area("Rules (one per line)", 
                                   placeholder="Only trade during high volume hours\nMaximum 3 trades per day\nStop loss maximum 8 ticks")
                
                col1, col2 = st.columns(2)
                with col1:
                    max_daily_loss = st.number_input("Max Daily Loss", min_value=0, value=400)
                    first_trade_size = st.number_input("First Trade Size", min_value=1, value=200)
                
                with col2:
                    second_trade_size = st.number_input("Second Trade Size", min_value=1, value=100)
                    third_trade_size = st.number_input("Third Trade Size", min_value=1, value=100)
                
                if st.form_submit_button("Create Playbook"):
                    if name:
                        new_playbook = {
                            "name": name,
                            "description": description,
                            "rules": [rule.strip() for rule in rules.split('\n') if rule.strip()],
                            "max_position_size": {
                                "first_trade": first_trade_size,
                                "second_trade": second_trade_size,
                                "third_trade": third_trade_size
                            },
                            "max_daily_loss": max_daily_loss,
                            "created_at": datetime.now().isoformat()
                        }
                        
                        playbooks.append(new_playbook)
                        self.data_storage.save_playbooks(playbooks)
                        st.success(f"Created playbook: {name}")
                        st.rerun()
        
        # Display and edit existing playbooks
        st.subheader("Edit Existing Playbooks")
        
        if not playbooks:
            st.info("No playbooks created yet.")
            return
        
        for i, playbook in enumerate(playbooks):
            with st.expander(f"✏️ Edit {playbook['name']}", expanded=False):
                with st.form(f"edit_playbook_{i}"):
                    edited_name = st.text_input("Playbook Name", value=playbook['name'], key=f"pb_name_{i}")
                    edited_description = st.text_area("Description", value=playbook['description'], key=f"pb_desc_{i}")
                    
                    edited_rules = st.text_area("Rules (one per line)", 
                                              value='\n'.join(playbook['rules']),
                                              key=f"pb_rules_{i}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        edited_max_daily_loss = st.number_input("Max Daily Loss", 
                                                              value=playbook['max_daily_loss'], 
                                                              min_value=0, key=f"pb_loss_{i}")
                        edited_first_trade = st.number_input("First Trade Size", 
                                                           value=playbook['max_position_size']['first_trade'], 
                                                           min_value=1, key=f"pb_first_{i}")
                    
                    with col2:
                        edited_second_trade = st.number_input("Second Trade Size", 
                                                            value=playbook['max_position_size']['second_trade'], 
                                                            min_value=1, key=f"pb_second_{i}")
                        edited_third_trade = st.number_input("Third Trade Size", 
                                                           value=playbook['max_position_size']['third_trade'], 
                                                           min_value=1, key=f"pb_third_{i}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.form_submit_button("Save Changes", type="primary"):
                            playbooks[i] = {
                                "name": edited_name,
                                "description": edited_description,
                                "rules": [rule.strip() for rule in edited_rules.split('\n') if rule.strip()],
                                "max_position_size": {
                                    "first_trade": edited_first_trade,
                                    "second_trade": edited_second_trade,
                                    "third_trade": edited_third_trade
                                },
                                "max_daily_loss": edited_max_daily_loss,
                                "created_at": playbook.get('created_at', datetime.now().isoformat()),
                                "updated_at": datetime.now().isoformat()
                            }
                            
                            self.data_storage.save_playbooks(playbooks)
                            st.success(f"Updated playbook: {edited_name}")
                            st.rerun()
                    
                    with col2:
                        if st.form_submit_button("Delete Playbook", type="secondary"):
                            playbooks.pop(i)
                            self.data_storage.save_playbooks(playbooks)
                            st.success(f"Deleted playbook: {playbook['name']}")
                            st.rerun()
    
    def manage_withdrawals(self):
        st.subheader("Withdrawal Management")
        
        withdrawals = self.data_storage.load_withdrawals()
        accounts = self.data_storage.load_accounts()
        
        # Add new withdrawal
        with st.expander("Record New Withdrawal"):
            with st.form("add_withdrawal"):
                funded_accounts = [acc for acc in accounts if acc['status'] == 'funded']
                
                if funded_accounts:
                    account_options = [f"{acc['prop_firm']} - {acc['account_type']} ({acc['account_number']})" 
                                     for acc in funded_accounts]
                    selected_account_idx = st.selectbox("Account", range(len(account_options)), format_func=lambda x: account_options[x])
                    
                    # Show current account balance
                    selected_acc = funded_accounts[selected_account_idx]
                    st.info(f"Current Balance: ${selected_acc['current_balance']:,.2f}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        max_withdrawal = selected_acc['current_balance']
                        amount = st.number_input("Withdrawal Amount", 
                                               min_value=0.01, 
                                               max_value=max_withdrawal,
                                               value=min(1000.0, max_withdrawal),
                                               help=f"Maximum available: ${max_withdrawal:,.2f}")
                        withdrawal_date = st.date_input("Withdrawal Date", value=date.today())
                    
                    with col2:
                        purpose = st.selectbox("Purpose", ["Reinvestment", "Personal Use", "Loan Repayment", "Other"])
                        used_for_personal = st.checkbox("Used for Personal Expenses")
                    
                    notes = st.text_area("Notes")
                    
                    if st.form_submit_button("Record Withdrawal"):
                        if amount > selected_acc['current_balance']:
                            st.error("Withdrawal amount cannot exceed account balance!")
                        else:
                            # Create withdrawal record
                            new_withdrawal = {
                                "account": account_options[selected_account_idx],
                                "account_id": selected_acc['account_number'],
                                "amount": amount,
                                "date": withdrawal_date.isoformat(),
                                "purpose": purpose,
                                "used_for_personal": used_for_personal,
                                "notes": notes
                            }
                            
                            # Update account balance
                            accounts = self.data_storage.load_accounts()  # Reload to get latest
                            for i, acc in enumerate(accounts):
                                if (acc['prop_firm'] == selected_acc['prop_firm'] and 
                                    acc['account_type'] == selected_acc['account_type'] and
                                    acc['account_number'] == selected_acc['account_number']):
                                    accounts[i]['current_balance'] -= amount
                                    accounts[i]['updated_at'] = datetime.now().isoformat()
                                    break
                            
                            # Save both withdrawal and updated accounts
                            self.data_storage.add_withdrawal(new_withdrawal)
                            self.data_storage.save_accounts(accounts)
                            
                            st.success(f"Recorded withdrawal of ${amount:,.2f} - Account balance updated to ${accounts[i]['current_balance']:,.2f}")
                            st.rerun()
                else:
                    st.warning("No funded accounts available. You need funded accounts to record withdrawals.")
        
        # Display and edit withdrawal history
        st.subheader("Edit Withdrawal History")
        
        if not withdrawals:
            st.info("No withdrawals recorded yet.")
            return
        
        for i, withdrawal in enumerate(withdrawals):
            with st.expander(f"✏️ Edit Withdrawal #{withdrawal.get('id', i+1)} - ${withdrawal['amount']:,.2f}", expanded=False):
                with st.form(f"edit_withdrawal_{i}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        edited_account = st.text_input("Account", 
                                                     value=withdrawal['account'],
                                                     key=f"wd_acc_{i}")
                        edited_amount = st.number_input("Amount", 
                                                      value=withdrawal['amount'], 
                                                      min_value=0.01,
                                                      key=f"wd_amt_{i}")
                        edited_date = st.date_input("Withdrawal Date",
                                                  value=pd.to_datetime(withdrawal['date']).date(),
                                                  key=f"wd_date_{i}")
                    
                    with col2:
                        edited_purpose = st.selectbox("Purpose",
                                                    ["Reinvestment", "Personal Use", "Loan Repayment", "Other"],
                                                    index=["Reinvestment", "Personal Use", "Loan Repayment", "Other"].index(withdrawal['purpose']) if withdrawal['purpose'] in ["Reinvestment", "Personal Use", "Loan Repayment", "Other"] else 0,
                                                    key=f"wd_purpose_{i}")
                        
                        edited_personal = st.checkbox("Used for Personal Expenses",
                                                    value=withdrawal.get('used_for_personal', False),
                                                    key=f"wd_personal_{i}")
                    
                    edited_notes = st.text_area("Notes",
                                              value=withdrawal.get('notes', ''),
                                              key=f"wd_notes_{i}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.form_submit_button("Save Changes", type="primary"):
                            # Calculate difference in withdrawal amount to adjust account balance
                            old_amount = withdrawal['amount']
                            amount_difference = edited_amount - old_amount
                            
                            # Update withdrawal record
                            withdrawals[i] = {
                                "id": withdrawal.get('id', i+1),
                                "account": edited_account,
                                "account_id": withdrawal.get('account_id', ''),
                                "amount": edited_amount,
                                "date": edited_date.isoformat(),
                                "purpose": edited_purpose,
                                "used_for_personal": edited_personal,
                                "notes": edited_notes,
                                "timestamp": withdrawal.get('timestamp', datetime.now().isoformat()),
                                "updated_at": datetime.now().isoformat()
                            }
                            
                            # Update corresponding account balance if amount changed
                            if amount_difference != 0:
                                accounts = self.data_storage.load_accounts()
                                account_id = withdrawal.get('account_id', '')
                                
                                for j, acc in enumerate(accounts):
                                    if acc['account_number'] == account_id:
                                        accounts[j]['current_balance'] -= amount_difference
                                        accounts[j]['updated_at'] = datetime.now().isoformat()
                                        self.data_storage.save_accounts(accounts)
                                        break
                            
                            self.data_storage.save_withdrawals(withdrawals)
                            st.success(f"Updated withdrawal - Balance adjusted by ${amount_difference:+.2f}" if amount_difference != 0 else "Updated withdrawal")
                            st.rerun()
                    
                    with col2:
                        if st.form_submit_button("Delete Withdrawal", type="secondary"):
                            # Restore the withdrawal amount to account balance
                            accounts = self.data_storage.load_accounts()
                            account_id = withdrawal.get('account_id', '')
                            
                            for j, acc in enumerate(accounts):
                                if acc['account_number'] == account_id:
                                    accounts[j]['current_balance'] += withdrawal['amount']
                                    accounts[j]['updated_at'] = datetime.now().isoformat()
                                    self.data_storage.save_accounts(accounts)
                                    break
                            
                            withdrawals.pop(i)
                            self.data_storage.save_withdrawals(withdrawals)
                            st.success(f"Withdrawal deleted - ${withdrawal['amount']:,.2f} restored to account balance!")
                            st.rerun()