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
        with st.expander("➕ Add New Prop Firm", expanded=not firms):
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
        
        # Display existing firms
        st.subheader("Your Prop Firms")
        for i, firm in enumerate(firms):
            with st.expander(f"🏢 {firm['name']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Payout Schedule:** {firm['payout_schedule']}")
                    st.write(f"**Profit Split:** {firm['payout_split']}%")
                    st.write(f"**Min Payout:** ${firm['min_payout']}")
                with col2:
                    st.write(f"**Max Daily Loss:** {firm['max_daily_loss']}%")
                    st.write(f"**Max Drawdown:** {firm['max_drawdown']}%")
                
                if firm.get('notes'):
                    st.write(f"**Notes:** {firm['notes']}")
                
                if st.button(f"Delete Firm", key=f"delete_firm_{i}"):
                    firms.pop(i)
                    self.data_storage.save_prop_firms(firms)
                    st.success(f"Deleted {firm['name']}")
                    st.rerun()
    
    def manage_accounts(self):
        st.subheader("Account Management")
        
        accounts = self.data_storage.load_accounts()
        firms = self.data_storage.load_prop_firms()
        firm_names = [f['name'] for f in firms]
        
        # Add new account
        with st.expander("➕ Add New Account", expanded=not accounts):
            with st.form("add_account"):
                col1, col2 = st.columns(2)
                
                with col1:
                    if firm_names:
                        firm = st.selectbox("Prop Firm", firm_names)
                    else:
                        st.warning("Add a prop firm first!")
                        firm = None
                    
                    account_size = st.selectbox("Account Size", [25000, 50000, 100000, 150000, 200000, 250000, 300000])
                    account_type = st.selectbox("Account Type", ["Evaluation", "Funded"])
                
                with col2:
                    account_name = st.text_input("Account Nickname", placeholder="e.g., TF-50K-1")
                    status = st.selectbox("Status", ["evaluation", "funded", "blown", "payout_pending"])
                    current_balance = st.number_input("Current Balance ($)", min_value=0.0, value=float(account_size) if account_size else 0.0)
                
                if st.form_submit_button("Add Account"):
                    if firm and account_name:
                        account_data = {
                            "name": account_name,
                            "firm": firm,
                            "size": account_size,
                            "type": account_type.lower(),
                            "status": status,
                            "balance": current_balance,
                            "created_at": datetime.now().isoformat()
                        }
                        self.data_storage.add_account(account_data)
                        st.success(f"Added account: {account_name}")
                        st.rerun()
        
        # Display and edit existing accounts
        st.subheader("Edit Your Accounts")
        
        if not accounts:
            st.info("No accounts configured yet.")
        
        for i, account in enumerate(accounts):
            with st.expander(f"💼 {account['name']} - {account['firm']} ({account['status']})"):
                with st.form(f"edit_account_{i}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        edited_name = st.text_input("Account Name", value=account['name'], key=f"acc_name_{i}")
                        edited_firm = st.selectbox("Prop Firm", firm_names, 
                                                   index=firm_names.index(account['firm']) if account['firm'] in firm_names else 0,
                                                   key=f"acc_firm_{i}")
                        edited_size = st.selectbox("Account Size", 
                                                   [25000, 50000, 100000, 150000, 200000, 250000, 300000],
                                                   index=[25000, 50000, 100000, 150000, 200000, 250000, 300000].index(account['size']) if account['size'] in [25000, 50000, 100000, 150000, 200000, 250000, 300000] else 0,
                                                   key=f"acc_size_{i}")
                    
                    with col2:
                        edited_type = st.selectbox("Account Type", ["evaluation", "funded"],
                                                   index=["evaluation", "funded"].index(account['type']) if account['type'] in ["evaluation", "funded"] else 0,
                                                   key=f"acc_type_{i}")
                        edited_status = st.selectbox("Status", ["evaluation", "funded", "blown", "payout_pending"],
                                                     index=["evaluation", "funded", "blown", "payout_pending"].index(account['status']) if account['status'] in ["evaluation", "funded", "blown", "payout_pending"] else 0,
                                                     key=f"acc_status_{i}")
                        edited_balance = st.number_input("Current Balance", value=float(account['balance']), key=f"acc_balance_{i}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.form_submit_button("Save Changes", type="primary"):
                            accounts[i] = {
                                **account,
                                "name": edited_name,
                                "firm": edited_firm,
                                "size": edited_size,
                                "type": edited_type,
                                "status": edited_status,
                                "balance": edited_balance,
                                "updated_at": datetime.now().isoformat()
                            }
                            self.data_storage.save_accounts(accounts)
                            st.success("Account updated!")
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
        
        # Grading explanation
        with st.expander("ℹ️ About Setup Grades"):
            st.markdown("""
            **Setup Grading System:**
            
            - **C Setup (Minimum):** The absolute must-have criteria. If ANY C rule is missing, don't take the trade.
            - **B Setup (Better):** All C rules met + additional criteria that increase probability.
            - **A Setup (Best):** All C + B rules met + premium criteria for highest probability trades.
            
            *Example: C = structure break, B = C + clean retracement, A = B + HTF confluence*
            """)
        
        # Add new playbook
        with st.expander("➕ Create New Playbook"):
            with st.form("add_playbook"):
                name = st.text_input("Playbook Name", placeholder="e.g., ICT Silver Bullet")
                description = st.text_area("Description", placeholder="Brief description of this setup...")
                
                st.markdown("---")
                st.markdown("### 📊 Setup Grade Rules")
                st.caption("Enter rules one per line. Mark each as mandatory (affects grade) or optional (tracked for refinement).")
                
                # C Setup - Minimum Requirements
                st.markdown("#### 🔴 C Setup Rules (Minimum - MUST have all mandatory)")
                rules_c_text = st.text_area(
                    "C Setup Rules (one per line)", 
                    placeholder="Market structure break confirmed\nFair value gap present\nWithin kill zone time",
                    key="new_rules_c",
                    height=100
                )
                rules_c_mandatory_default = st.checkbox("All C rules mandatory by default", value=True, key="new_c_mandatory_default")
                
                # B Setup - Better probability
                st.markdown("#### 🟡 B Setup Rules (Better - adds to C)")
                rules_b_text = st.text_area(
                    "B Setup Rules (one per line)", 
                    placeholder="Clean 50% retracement\nLiquidity swept before entry\nNo major news within 30min",
                    key="new_rules_b",
                    height=100
                )
                rules_b_mandatory_default = st.checkbox("All B rules mandatory by default", value=True, key="new_b_mandatory_default")
                
                # A Setup - Best probability
                st.markdown("#### 🟢 A Setup Rules (Best - adds to C + B)")
                rules_a_text = st.text_area(
                    "A Setup Rules (one per line)", 
                    placeholder="HTF confluence (4H or Daily)\nPrevious session high/low taken\nOptimal trade entry pattern",
                    key="new_rules_a",
                    height=100
                )
                rules_a_mandatory_default = st.checkbox("All A rules mandatory by default", value=True, key="new_a_mandatory_default")
                
                st.markdown("---")
                st.markdown("### 💰 Risk Management")
                
                col1, col2 = st.columns(2)
                with col1:
                    max_daily_loss = st.number_input("Max Daily Loss ($)", min_value=0, value=400)
                    first_trade_size = st.number_input("First Trade Size (contracts/lots)", min_value=1, value=2)
                
                with col2:
                    second_trade_size = st.number_input("Second Trade Size", min_value=1, value=1)
                    third_trade_size = st.number_input("Third Trade Size", min_value=1, value=1)
                
                if st.form_submit_button("Create Playbook", type="primary"):
                    if name:
                        # Parse rules into objects with mandatory flag
                        def parse_rules(text, mandatory_default):
                            rules = []
                            for line in text.split('\n'):
                                line = line.strip()
                                if line:
                                    rules.append({"text": line, "mandatory": mandatory_default})
                            return rules
                        
                        rules_c = parse_rules(rules_c_text, rules_c_mandatory_default)
                        rules_b = parse_rules(rules_b_text, rules_b_mandatory_default)
                        rules_a = parse_rules(rules_a_text, rules_a_mandatory_default)
                        
                        new_playbook = {
                            "name": name,
                            "description": description,
                            "rules_c": rules_c,
                            "rules_b": rules_b,
                            "rules_a": rules_a,
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
                    else:
                        st.error("Please enter a playbook name")
        
        # Display existing playbooks
        st.subheader("Your Playbooks")
        
        if not playbooks:
            st.info("No playbooks configured yet. Create one above!")
        
        for i, playbook in enumerate(playbooks):
            # Migrate old playbooks to new structure if needed
            if 'rules_c' not in playbook:
                # Old format: rules was a list of strings
                old_rules = playbook.get('rules', [])
                playbook['rules_c'] = [{"text": r, "mandatory": True} for r in old_rules]
                playbook['rules_b'] = []
                playbook['rules_a'] = []
            else:
                # Check if rules are in old string format vs new dict format
                def migrate_rules(rules):
                    if not rules:
                        return []
                    if isinstance(rules[0], str):
                        return [{"text": r, "mandatory": True} for r in rules]
                    return rules
                
                playbook['rules_c'] = migrate_rules(playbook.get('rules_c', []))
                playbook['rules_b'] = migrate_rules(playbook.get('rules_b', []))
                playbook['rules_a'] = migrate_rules(playbook.get('rules_a', []))
            
            with st.expander(f"📋 {playbook['name']}"):
                with st.form(f"edit_playbook_{i}"):
                    edited_name = st.text_input("Playbook Name", value=playbook['name'], key=f"pb_name_{i}")
                    edited_description = st.text_area("Description", value=playbook.get('description', ''), key=f"pb_desc_{i}")
                    
                    st.markdown("---")
                    st.markdown("### 📊 Setup Grade Rules")
                    st.caption("🔒 = Mandatory (affects grade) | 📝 = Optional (tracked for refinement)")
                    
                    # Helper to render rules with mandatory toggle
                    def render_rules_section(grade_label, grade_color, rules, key_prefix):
                        st.markdown(f"#### {grade_color} {grade_label}")
                        edited_rules = []
                        
                        for j, rule in enumerate(rules):
                            rule_text = rule.get('text', rule) if isinstance(rule, dict) else rule
                            rule_mandatory = rule.get('mandatory', True) if isinstance(rule, dict) else True
                            
                            col1, col2 = st.columns([4, 1])
                            with col1:
                                new_text = st.text_input(
                                    f"Rule {j+1}", 
                                    value=rule_text, 
                                    key=f"{key_prefix}_{i}_{j}_text",
                                    label_visibility="collapsed"
                                )
                            with col2:
                                new_mandatory = st.checkbox(
                                    "🔒", 
                                    value=rule_mandatory, 
                                    key=f"{key_prefix}_{i}_{j}_mandatory",
                                    help="Mandatory (affects grade)"
                                )
                            
                            if new_text.strip():
                                edited_rules.append({"text": new_text.strip(), "mandatory": new_mandatory})
                        
                        # Add new rule input
                        new_rule = st.text_input(
                            f"Add new {grade_label} rule",
                            placeholder="Type new rule and save...",
                            key=f"{key_prefix}_{i}_new"
                        )
                        if new_rule.strip():
                            edited_rules.append({"text": new_rule.strip(), "mandatory": True})
                        
                        return edited_rules
                    
                    # C Rules
                    edited_rules_c = render_rules_section("C Setup Rules (Minimum)", "🔴", playbook.get('rules_c', []), "pb_c")
                    
                    # B Rules
                    edited_rules_b = render_rules_section("B Setup Rules (Better)", "🟡", playbook.get('rules_b', []), "pb_b")
                    
                    # A Rules
                    edited_rules_a = render_rules_section("A Setup Rules (Best)", "🟢", playbook.get('rules_a', []), "pb_a")
                    
                    st.markdown("---")
                    st.markdown("### 💰 Risk Management")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        edited_max_daily_loss = st.number_input("Max Daily Loss", 
                                                                value=playbook.get('max_daily_loss', 400), 
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
                                "rules_c": edited_rules_c,
                                "rules_b": edited_rules_b,
                                "rules_a": edited_rules_a,
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
        with st.expander("💸 Record New Withdrawal"):
            with st.form("add_withdrawal"):
                col1, col2 = st.columns(2)
                
                funded_accounts = [acc for acc in accounts if acc['status'] in ['funded', 'payout_pending']]
                account_names = [acc['name'] for acc in funded_accounts]
                
                with col1:
                    if account_names:
                        from_account = st.selectbox("From Account", account_names)
                    else:
                        st.warning("No funded accounts available")
                        from_account = None
                    
                    amount = st.number_input("Withdrawal Amount ($)", min_value=0.0, value=0.0)
                
                with col2:
                    withdrawal_date = st.date_input("Withdrawal Date", value=datetime.now().date())
                    use_type = st.selectbox("Usage", ["Reinvestment", "Personal", "Loan Repayment"])
                
                notes = st.text_area("Notes", placeholder="Optional notes about this withdrawal...")
                
                if st.form_submit_button("Record Withdrawal"):
                    if from_account and amount > 0:
                        withdrawal_data = {
                            "account": from_account,
                            "amount": amount,
                            "date": withdrawal_date.isoformat(),
                            "use_type": use_type,
                            "used_for_personal": use_type == "Personal",
                            "notes": notes,
                            "created_at": datetime.now().isoformat()
                        }
                        self.data_storage.add_withdrawal(withdrawal_data)
                        st.success(f"Recorded ${amount:,.2f} withdrawal!")
                        st.rerun()
        
        # Summary metrics
        if withdrawals:
            col1, col2, col3, col4 = st.columns(4)
            
            total = sum(w['amount'] for w in withdrawals)
            reinvested = sum(w['amount'] for w in withdrawals if w.get('use_type') == 'Reinvestment')
            personal = sum(w['amount'] for w in withdrawals if w.get('use_type') == 'Personal')
            loan_repaid = sum(w['amount'] for w in withdrawals if w.get('use_type') == 'Loan Repayment')
            
            with col1:
                st.metric("Total Withdrawn", f"${total:,.2f}")
            with col2:
                st.metric("Reinvested", f"${reinvested:,.2f}")
            with col3:
                st.metric("Personal Use", f"${personal:,.2f}")
            with col4:
                st.metric("Loan Repaid", f"${loan_repaid:,.2f}")
        
        # Display withdrawals
        st.subheader("Withdrawal History")
        if withdrawals:
            for i, w in enumerate(sorted(withdrawals, key=lambda x: x['date'], reverse=True)):
                with st.expander(f"💵 ${w['amount']:,.2f} from {w['account']} - {w['date']}"):
                    st.write(f"**Usage:** {w.get('use_type', 'Unknown')}")
                    if w.get('notes'):
                        st.write(f"**Notes:** {w['notes']}")
                    
                    if st.button("Delete", key=f"del_withdrawal_{i}"):
                        withdrawals.pop(i)
                        self.data_storage.save_withdrawals(withdrawals)
                        st.success("Withdrawal deleted!")
                        st.rerun()
        else:
            st.info("No withdrawals recorded yet.")
