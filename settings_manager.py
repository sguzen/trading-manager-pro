import streamlit as st
from typing import Dict, List

class SettingsManager:
    """Manage app settings including debt, goals, and trade grading rules"""
    
    def __init__(self, data_storage):
        self.data_storage = data_storage
    
    def show_settings(self):
        st.header("⚙️ Settings")
        
        tab1, tab2, tab3 = st.tabs(["💰 Financial Goals", "📋 Grade Rules", "📊 Position Sizing"])
        
        with tab1:
            self.manage_financial_settings()
        
        with tab2:
            self.manage_grade_rules()
        
        with tab3:
            self.manage_position_sizing()
    
    def manage_financial_settings(self):
        st.subheader("Financial Goals & Debt")
        
        settings = self.data_storage.load_settings()
        
        with st.form("financial_settings"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Debt Tracking**")
                debt_name = st.text_input("Debt Name", value=settings.get('debt_name', 'Trading Loan'))
                debt_amount = st.number_input("Total Debt Amount ($)", 
                                             min_value=0.0, 
                                             value=float(settings.get('debt_amount', 5000)),
                                             step=100.0)
            
            with col2:
                st.write("**Payout Goal**")
                goal_amount = st.number_input("Goal Amount ($)", 
                                             min_value=0.0, 
                                             value=float(settings.get('goal_amount', 1000000)),
                                             step=10000.0)
            
            if st.form_submit_button("Save Financial Settings", type="primary"):
                settings['debt_name'] = debt_name
                settings['debt_amount'] = debt_amount
                settings['goal_amount'] = goal_amount
                self.data_storage.save_settings(settings)
                st.success("Saved!")
                st.rerun()
        
        # Show current status
        st.markdown("---")
        withdrawals = self.data_storage.load_withdrawals()
        
        col1, col2 = st.columns(2)
        with col1:
            debt_paid = sum(w['amount'] for w in withdrawals 
                          if w.get('status') == 'paid' and w.get('allocation') == 'Debt Payment')
            remaining = max(0, settings.get('debt_amount', 5000) - debt_paid)
            
            st.metric(f"{settings.get('debt_name', 'Debt')} Remaining", f"${remaining:,.2f}")
            if settings.get('debt_amount', 0) > 0:
                st.progress(min(debt_paid / settings.get('debt_amount', 1), 1.0))
        
        with col2:
            total_withdrawn = sum(w['amount'] for w in withdrawals if w.get('status') == 'paid')
            goal = settings.get('goal_amount', 1000000)
            
            st.metric("Progress to Goal", f"${total_withdrawn:,.2f} / ${goal:,.0f}")
            if goal > 0:
                st.progress(min(total_withdrawn / goal, 1.0))
    
    def manage_grade_rules(self):
        st.subheader("Trade Grading Rules")
        
        settings = self.data_storage.load_settings()
        must_have_rules = settings.get('must_have_rules', [])
        a_rules = settings.get('a_rules', [])
        b_rules = settings.get('b_rules', [])
        c_rules = settings.get('c_rules', [])
        
        st.markdown("""
        **How it works:**
        - 🔒 **Must-Have**: ALL must be checked or F-grade (no trade)
        - 🟢 **A-rules**: Check ANY → A-grade
        - 🟡 **B-rules**: Check ANY (no A) → B-grade  
        - 🟠 **C-rules**: Check ANY (no A/B) → C-grade
        - If must-haves met but no other rules → C-grade
        """)
        
        st.markdown("---")
        
        # MUST-HAVE RULES
        st.markdown("### 🔒 Must-Have Rules")
        st.caption("ALL required or trade is F-grade")
        
        self._render_rule_section(settings, 'must_have_rules', must_have_rules, "must")
        
        st.markdown("---")
        
        # A, B, C RULES in columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🟢 A-Grade Rules")
            st.caption("Any checked → A-grade")
            self._render_rule_section(settings, 'a_rules', a_rules, "a")
        
        with col2:
            st.markdown("### 🟡 B-Grade Rules")
            st.caption("Any checked → B-grade")
            self._render_rule_section(settings, 'b_rules', b_rules, "b")
        
        with col3:
            st.markdown("### 🟠 C-Grade Rules")
            st.caption("Any checked → C-grade")
            self._render_rule_section(settings, 'c_rules', c_rules, "c")
        
        # Summary
        st.markdown("---")
        st.subheader("Summary")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Must-Have", len(must_have_rules))
        with col2:
            st.metric("A-Rules", len(a_rules))
        with col3:
            st.metric("B-Rules", len(b_rules))
        with col4:
            st.metric("C-Rules", len(c_rules))
    
    def _render_rule_section(self, settings: Dict, rules_key: str, rules: List[str], prefix: str):
        """Render a rule section with add/delete/move functionality"""
        
        # Display existing rules with move dropdown
        if rules:
            for i, rule in enumerate(rules):
                col1, col2, col3 = st.columns([4, 2, 1])
                
                with col1:
                    st.write(f"{i+1}. {rule}")
                
                with col2:
                    # Move dropdown (only show for non-must-have)
                    if prefix != "must":
                        move_options = ["—", "→ Must-Have", "→ A", "→ B", "→ C"]
                        move_to = st.selectbox(
                            "Move",
                            move_options,
                            key=f"move_{prefix}_{i}",
                            label_visibility="collapsed"
                        )
                        
                        if move_to != "—":
                            # Remove from current list
                            rules.pop(i)
                            settings[rules_key] = rules
                            
                            # Add to target list
                            target_map = {
                                "→ Must-Have": "must_have_rules",
                                "→ A": "a_rules",
                                "→ B": "b_rules",
                                "→ C": "c_rules"
                            }
                            target_key = target_map[move_to]
                            target_rules = settings.get(target_key, [])
                            target_rules.append(rule)
                            settings[target_key] = target_rules
                            
                            self.data_storage.save_settings(settings)
                            st.rerun()
                    else:
                        # Must-have can move to A/B/C
                        move_options = ["—", "→ A", "→ B", "→ C"]
                        move_to = st.selectbox(
                            "Move",
                            move_options,
                            key=f"move_{prefix}_{i}",
                            label_visibility="collapsed"
                        )
                        
                        if move_to != "—":
                            rules.pop(i)
                            settings[rules_key] = rules
                            
                            target_map = {
                                "→ A": "a_rules",
                                "→ B": "b_rules",
                                "→ C": "c_rules"
                            }
                            target_key = target_map[move_to]
                            target_rules = settings.get(target_key, [])
                            target_rules.append(rule)
                            settings[target_key] = target_rules
                            
                            self.data_storage.save_settings(settings)
                            st.rerun()
                
                with col3:
                    if st.button("🗑️", key=f"del_{prefix}_{i}"):
                        rules.pop(i)
                        settings[rules_key] = rules
                        self.data_storage.save_settings(settings)
                        st.rerun()
        else:
            st.caption("No rules yet")
        
        # Add new rule
        with st.form(f"add_{prefix}_rule"):
            new_rule = st.text_input("New rule", placeholder="Enter rule...", key=f"new_{prefix}_input", label_visibility="collapsed")
            if st.form_submit_button("➕ Add", use_container_width=True):
                if new_rule.strip():
                    rules.append(new_rule.strip())
                    settings[rules_key] = rules
                    self.data_storage.save_settings(settings)
                    st.rerun()
    
    def manage_position_sizing(self):
        st.subheader("Position Sizing")
        st.write("Position size as **% of daily drawdown** allowed per grade.")
        
        settings = self.data_storage.load_settings()
        sizing = settings.get('position_sizing', {
            "A": {"drawdown_pct": 50, "label": "Full Size"},
            "B": {"drawdown_pct": 30, "label": "Reduced"},
            "C": {"drawdown_pct": 15, "label": "Minimum"},
            "F": {"drawdown_pct": 0, "label": "NO TRADE"}
        })
        
        with st.form("sizing_settings"):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("### 🟢 A-Grade")
                a_dd = st.number_input("% Drawdown", min_value=0, max_value=100,
                                      value=sizing.get('A', {}).get('drawdown_pct', 50), key="a_dd")
                a_label = st.text_input("Label", value=sizing.get('A', {}).get('label', 'Full Size'), key="a_label")
            
            with col2:
                st.markdown("### 🟡 B-Grade")
                b_dd = st.number_input("% Drawdown", min_value=0, max_value=100,
                                      value=sizing.get('B', {}).get('drawdown_pct', 30), key="b_dd")
                b_label = st.text_input("Label", value=sizing.get('B', {}).get('label', 'Reduced'), key="b_label")
            
            with col3:
                st.markdown("### 🟠 C-Grade")
                c_dd = st.number_input("% Drawdown", min_value=0, max_value=100,
                                      value=sizing.get('C', {}).get('drawdown_pct', 15), key="c_dd")
                c_label = st.text_input("Label", value=sizing.get('C', {}).get('label', 'Minimum'), key="c_label")
            
            with col4:
                st.markdown("### 🔴 F-Grade")
                st.write("NO TRADE")
                st.write("0% drawdown")
            
            if st.form_submit_button("Save Position Sizing", type="primary"):
                settings['position_sizing'] = {
                    "A": {"drawdown_pct": a_dd, "label": a_label},
                    "B": {"drawdown_pct": b_dd, "label": b_label},
                    "C": {"drawdown_pct": c_dd, "label": c_label},
                    "F": {"drawdown_pct": 0, "label": "NO TRADE"}
                }
                self.data_storage.save_settings(settings)
                st.success("Saved!")
                st.rerun()
        
        # Example calculation
        st.markdown("---")
        st.subheader("Position Calculator")
        
        col1, col2 = st.columns(2)
        with col1:
            example_dd = st.number_input("Daily Drawdown Limit ($)", value=400.0, step=50.0)
        with col2:
            example_risk = st.number_input("Risk per Contract ($)", value=100.0, step=25.0,
                                          help="e.g., ES 8 ticks = $100")
        
        if example_dd > 0 and example_risk > 0:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                a_dollars = example_dd * a_dd / 100
                a_contracts = int(a_dollars / example_risk)
                st.success(f"🟢 A\n${a_dollars:.0f}\n**{a_contracts} contracts**")
            with col2:
                b_dollars = example_dd * b_dd / 100
                b_contracts = int(b_dollars / example_risk)
                st.info(f"🟡 B\n${b_dollars:.0f}\n**{b_contracts} contracts**")
            with col3:
                c_dollars = example_dd * c_dd / 100
                c_contracts = int(c_dollars / example_risk)
                st.warning(f"🟠 C\n${c_dollars:.0f}\n**{c_contracts} contracts**")
            with col4:
                st.error(f"🔴 F\n$0\n**0 contracts**")
