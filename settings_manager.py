import streamlit as st
from typing import Dict, List

class SettingsManager:
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
                debt_amount = st.number_input("Total Debt ($)", min_value=0.0, 
                                             value=float(settings.get('debt_amount', 5000)), step=100.0)
            
            with col2:
                st.write("**Payout Goal**")
                goal_amount = st.number_input("Goal ($)", min_value=0.0, 
                                             value=float(settings.get('goal_amount', 1000000)), step=10000.0)
            
            if st.form_submit_button("Save", type="primary"):
                settings['debt_name'] = debt_name
                settings['debt_amount'] = debt_amount
                settings['goal_amount'] = goal_amount
                self.data_storage.save_settings(settings)
                st.success("Saved!")
                st.rerun()
        
        # Current status
        st.markdown("---")
        withdrawals = self.data_storage.load_withdrawals()
        
        col1, col2 = st.columns(2)
        with col1:
            # Handle both old and new format
            debt_paid = 0
            for w in withdrawals:
                if w.get('status') != 'paid':
                    continue
                if 'allocations' in w:
                    debt_paid += w['allocations'].get('debt', 0)
                elif w.get('allocation') == 'Debt Payment':
                    debt_paid += w.get('amount', 0)
            
            remaining = max(0, settings.get('debt_amount', 5000) - debt_paid)
            st.metric(f"{settings.get('debt_name', 'Debt')} Left", f"${remaining:,.2f}")
            if settings.get('debt_amount', 0) > 0:
                st.progress(min(debt_paid / settings['debt_amount'], 1.0))
        
        with col2:
            total_withdrawn = sum(w['amount'] for w in withdrawals if w.get('status') == 'paid')
            goal = settings.get('goal_amount', 1000000)
            st.metric("Goal Progress", f"${total_withdrawn:,.2f} / ${goal:,.0f}")
            if goal > 0:
                st.progress(min(total_withdrawn / goal, 1.0))
    
    def manage_grade_rules(self):
        st.subheader("Trade Grading Rules")
        
        settings = self.data_storage.load_settings()
        must_have_rules = settings.get('must_have_rules', [])
        conditions = settings.get('conditions', [])
        
        st.markdown("""
        **How it works:**
        - 🔒 **Must-Have**: ALL required or F-grade
        - 📋 **Conditions**: Each unlocks a grade. Highest checked wins.
        
        C (baseline) → B → A
        """)
        
        st.markdown("---")
        
        # MUST-HAVE
        st.markdown("### 🔒 Must-Have Rules")
        st.caption("ALL required or F-grade (no trade)")
        
        if must_have_rules:
            for i, rule in enumerate(must_have_rules):
                col1, col2 = st.columns([6, 1])
                with col1:
                    st.write(f"{i+1}. {rule}")
                with col2:
                    if st.button("🗑️", key=f"del_must_{i}"):
                        must_have_rules.pop(i)
                        settings['must_have_rules'] = must_have_rules
                        self.data_storage.save_settings(settings)
                        st.rerun()
        else:
            st.caption("No must-have rules yet")
        
        with st.form("add_must"):
            new_must = st.text_input("Add must-have", placeholder="e.g., HTF bias confirmed", label_visibility="collapsed")
            if st.form_submit_button("➕ Add Must-Have", use_container_width=True):
                if new_must.strip():
                    must_have_rules.append(new_must.strip())
                    settings['must_have_rules'] = must_have_rules
                    self.data_storage.save_settings(settings)
                    st.rerun()
        
        st.markdown("---")
        
        # CONDITIONS
        st.markdown("### 📋 Setup Conditions")
        st.caption("Check any → unlocks that grade. Highest wins.")
        
        if conditions:
            for i, cond in enumerate(conditions):
                col1, col2, col3 = st.columns([5, 2, 1])
                
                with col1:
                    grade_emoji = {"A": "🟢", "B": "🟡", "C": "🟠"}.get(cond.get('unlocks', 'C'), "⚪")
                    st.write(f"{grade_emoji} {cond['condition']}")
                
                with col2:
                    current = cond.get('unlocks', 'C')
                    new_grade = st.selectbox("Grade", ["C", "B", "A"], 
                                            index=["C", "B", "A"].index(current),
                                            key=f"grade_{i}", label_visibility="collapsed")
                    if new_grade != current:
                        conditions[i]['unlocks'] = new_grade
                        settings['conditions'] = conditions
                        self.data_storage.save_settings(settings)
                        st.rerun()
                
                with col3:
                    if st.button("🗑️", key=f"del_cond_{i}"):
                        conditions.pop(i)
                        settings['conditions'] = conditions
                        self.data_storage.save_settings(settings)
                        st.rerun()
        else:
            st.caption("No conditions yet")
        
        with st.form("add_cond"):
            col1, col2 = st.columns([4, 1])
            with col1:
                new_cond = st.text_input("Condition", placeholder="e.g., Clean FVG entry", label_visibility="collapsed")
            with col2:
                new_grade = st.selectbox("Unlocks", ["C", "B", "A"], label_visibility="collapsed")
            
            if st.form_submit_button("➕ Add Condition", use_container_width=True):
                if new_cond.strip():
                    conditions.append({"condition": new_cond.strip(), "unlocks": new_grade})
                    settings['conditions'] = conditions
                    self.data_storage.save_settings(settings)
                    st.rerun()
        
        # Summary
        st.markdown("---")
        a_count = sum(1 for c in conditions if c.get('unlocks') == 'A')
        b_count = sum(1 for c in conditions if c.get('unlocks') == 'B')
        c_count = sum(1 for c in conditions if c.get('unlocks') == 'C')
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Must-Have", len(must_have_rules))
        col2.metric("🟢 A-Unlocks", a_count)
        col3.metric("🟡 B-Unlocks", b_count)
        col4.metric("🟠 C-Unlocks", c_count)
    
    def manage_position_sizing(self):
        st.subheader("Position Sizing")
        st.write("**% of daily drawdown** per grade")
        
        settings = self.data_storage.load_settings()
        sizing = settings.get('position_sizing', {
            "A": {"drawdown_pct": 50, "label": "Full Size"},
            "B": {"drawdown_pct": 30, "label": "Reduced"},
            "C": {"drawdown_pct": 15, "label": "Minimum"},
            "F": {"drawdown_pct": 0, "label": "NO TRADE"}
        })
        
        with st.form("sizing"):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("### 🟢 A")
                a_dd = st.number_input("% DD", 0, 100, sizing.get('A', {}).get('drawdown_pct', 50), key="a_dd")
                a_label = st.text_input("Label", sizing.get('A', {}).get('label', 'Full Size'), key="a_label")
            
            with col2:
                st.markdown("### 🟡 B")
                b_dd = st.number_input("% DD", 0, 100, sizing.get('B', {}).get('drawdown_pct', 30), key="b_dd")
                b_label = st.text_input("Label", sizing.get('B', {}).get('label', 'Reduced'), key="b_label")
            
            with col3:
                st.markdown("### 🟠 C")
                c_dd = st.number_input("% DD", 0, 100, sizing.get('C', {}).get('drawdown_pct', 15), key="c_dd")
                c_label = st.text_input("Label", sizing.get('C', {}).get('label', 'Minimum'), key="c_label")
            
            with col4:
                st.markdown("### 🔴 F")
                st.write("NO TRADE")
                st.write("0%")
            
            if st.form_submit_button("Save", type="primary"):
                settings['position_sizing'] = {
                    "A": {"drawdown_pct": a_dd, "label": a_label},
                    "B": {"drawdown_pct": b_dd, "label": b_label},
                    "C": {"drawdown_pct": c_dd, "label": c_label},
                    "F": {"drawdown_pct": 0, "label": "NO TRADE"}
                }
                self.data_storage.save_settings(settings)
                st.success("Saved!")
                st.rerun()
        
        # Calculator
        st.markdown("---")
        st.subheader("Calculator")
        
        col1, col2 = st.columns(2)
        with col1:
            dd_limit = st.number_input("Daily Drawdown ($)", value=400.0, step=50.0)
        with col2:
            risk_per = st.number_input("Risk/Contract ($)", value=100.0, step=25.0)
        
        if dd_limit > 0 and risk_per > 0:
            col1, col2, col3, col4 = st.columns(4)
            
            for col, grade, dd in [(col1, "A", a_dd), (col2, "B", b_dd), (col3, "C", c_dd), (col4, "F", 0)]:
                dollars = dd_limit * dd / 100
                contracts = int(dollars / risk_per)
                emoji = {"A": "🟢", "B": "🟡", "C": "🟠", "F": "🔴"}[grade]
                with col:
                    if grade == "F":
                        st.error(f"{emoji} F\n$0\n**0 contracts**")
                    else:
                        st.info(f"{emoji} {grade}\n${dollars:.0f}\n**{contracts} contracts**")
