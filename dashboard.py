import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date, timedelta
from typing import Dict, List

class Dashboard:
    def __init__(self, data_storage):
        self.data_storage = data_storage
    
    def show_performance_analysis(self):
        trades = self.data_storage.load_trades()
        withdrawals = self.data_storage.load_withdrawals()
        accounts = self.data_storage.load_accounts()
        
        if not trades:
            st.info("No trades logged yet. Start journaling to see performance analytics!")
            return
        
        # Date range filter
        st.subheader("📅 Date Range")
        col1, col2 = st.columns(2)
        
        trade_dates = [datetime.fromisoformat(t['date']).date() for t in trades if t.get('date')]
        min_date = min(trade_dates) if trade_dates else date.today()
        max_date = max(trade_dates) if trade_dates else date.today()
        
        with col1:
            start_date = st.date_input("From", value=min_date, min_value=min_date, max_value=max_date)
        with col2:
            end_date = st.date_input("To", value=max_date, min_value=min_date, max_value=max_date)
        
        # Filter trades by date
        filtered_trades = [t for t in trades if start_date.isoformat() <= t.get('date', '') <= end_date.isoformat()]
        
        if not filtered_trades:
            st.warning("No trades in the selected date range.")
            return
        
        # Overall metrics
        st.subheader("📊 Overall Performance")
        self._show_overall_metrics(filtered_trades, withdrawals)
        
        # Grade performance
        st.subheader("🎯 Performance by Grade")
        self._show_grade_performance(filtered_trades)
        
        # Equity curve
        st.subheader("📈 Equity Curve")
        self._show_equity_curve(filtered_trades)
        
        # Emotional analysis
        st.subheader("🧠 Psychology Analysis")
        self._show_psychology_analysis(filtered_trades)
        
        # Playbook performance
        st.subheader("📋 Playbook Performance")
        self._show_playbook_performance(filtered_trades)
        
        # Account breakdown
        st.subheader("💼 Account Performance")
        self._show_account_performance(filtered_trades, accounts)
    
    def _show_overall_metrics(self, trades: List[Dict], withdrawals: List[Dict]):
        col1, col2, col3, col4, col5 = st.columns(5)
        
        total_pnl = sum(t.get('pnl', 0) for t in trades)
        winners = [t for t in trades if t.get('pnl', 0) > 0]
        losers = [t for t in trades if t.get('pnl', 0) < 0]
        win_rate = len(winners) / len(trades) * 100 if trades else 0
        
        avg_win = sum(t.get('pnl', 0) for t in winners) / len(winners) if winners else 0
        avg_loss = sum(t.get('pnl', 0) for t in losers) / len(losers) if losers else 0
        profit_factor = abs(sum(t.get('pnl', 0) for t in winners) / sum(t.get('pnl', 0) for t in losers)) if losers and sum(t.get('pnl', 0) for t in losers) != 0 else 0
        
        with col1:
            st.metric("Total P&L", f"${total_pnl:,.2f}", delta=f"{len(trades)} trades")
        with col2:
            st.metric("Win Rate", f"{win_rate:.1f}%", delta=f"{len(winners)}W / {len(losers)}L")
        with col3:
            st.metric("Avg Win", f"${avg_win:,.2f}")
        with col4:
            st.metric("Avg Loss", f"${avg_loss:,.2f}")
        with col5:
            st.metric("Profit Factor", f"{profit_factor:.2f}")
        
        # Second row - withdrawals and goal
        col1, col2, col3, col4 = st.columns(4)
        
        total_withdrawn = sum(w.get('amount', 0) for w in withdrawals)
        goal = 1000000  # $1M goal
        progress = total_withdrawn / goal * 100
        
        with col1:
            st.metric("Total Withdrawn", f"${total_withdrawn:,.2f}")
        with col2:
            st.metric("Progress to $1M", f"{progress:.2f}%")
        with col3:
            loan_repaid = sum(w.get('amount', 0) for w in withdrawals if w.get('use_type') == 'Loan Repayment')
            st.metric("Loan Repaid", f"${loan_repaid:,.2f}")
        with col4:
            a_b_rate = len([t for t in trades if t.get('grade') in ['A', 'B']]) / len(trades) * 100 if trades else 0
            st.metric("A/B Setup Rate", f"{a_b_rate:.1f}%")
    
    def _show_grade_performance(self, trades: List[Dict]):
        grades = ['A', 'B', 'C', 'F']
        grade_data = []
        
        for grade in grades:
            grade_trades = [t for t in trades if t.get('grade') == grade]
            if grade_trades:
                wins = [t for t in grade_trades if t.get('pnl', 0) > 0]
                total_pnl = sum(t.get('pnl', 0) for t in grade_trades)
                win_rate = len(wins) / len(grade_trades) * 100
                avg_pnl = total_pnl / len(grade_trades)
                
                grade_data.append({
                    "Grade": grade,
                    "Trades": len(grade_trades),
                    "Total P&L": f"${total_pnl:,.2f}",
                    "Win Rate": f"{win_rate:.1f}%",
                    "Avg P&L": f"${avg_pnl:,.2f}",
                    "% of Trades": f"{len(grade_trades) / len(trades) * 100:.1f}%"
                })
        
        if grade_data:
            df = pd.DataFrame(grade_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Grade distribution chart
            col1, col2 = st.columns(2)
            
            with col1:
                grade_counts = {g: len([t for t in trades if t.get('grade') == g]) for g in grades}
                fig = px.pie(
                    values=list(grade_counts.values()),
                    names=list(grade_counts.keys()),
                    title="Trade Distribution by Grade",
                    color=list(grade_counts.keys()),
                    color_discrete_map={'A': 'green', 'B': 'yellow', 'C': 'orange', 'F': 'red'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                grade_pnl = {g: sum(t.get('pnl', 0) for t in trades if t.get('grade') == g) for g in grades}
                fig = px.bar(
                    x=list(grade_pnl.keys()),
                    y=list(grade_pnl.values()),
                    title="P&L by Grade",
                    color=list(grade_pnl.keys()),
                    color_discrete_map={'A': 'green', 'B': 'yellow', 'C': 'orange', 'F': 'red'}
                )
                fig.update_layout(showlegend=False, xaxis_title="Grade", yaxis_title="P&L ($)")
                st.plotly_chart(fig, use_container_width=True)
            
            # Key insight
            if grade_data:
                a_trades = [t for t in trades if t.get('grade') == 'A']
                f_trades = [t for t in trades if t.get('grade') == 'F']
                a_pnl = sum(t.get('pnl', 0) for t in a_trades) if a_trades else 0
                f_pnl = sum(t.get('pnl', 0) for t in f_trades) if f_trades else 0
                
                if a_pnl > 0 and f_pnl < 0:
                    st.success(f"💡 Insight: Your A-grade setups made ${a_pnl:,.2f} while rule violations (F) cost ${abs(f_pnl):,.2f}. Stick to A/B setups!")
                elif len(f_trades) > len(trades) * 0.2:
                    st.error(f"⚠️ Warning: {len(f_trades) / len(trades) * 100:.0f}% of your trades are rule violations. Focus on waiting for proper setups.")
    
    def _show_equity_curve(self, trades: List[Dict]):
        sorted_trades = sorted(trades, key=lambda x: (x.get('date', ''), x.get('time', '')))
        
        cumulative_pnl = []
        running_total = 0
        dates = []
        grades = []
        
        for trade in sorted_trades:
            running_total += trade.get('pnl', 0)
            cumulative_pnl.append(running_total)
            dates.append(trade.get('date', ''))
            grades.append(trade.get('grade', 'C'))
        
        fig = go.Figure()
        
        # Color points by grade
        grade_colors = {'A': 'green', 'B': 'gold', 'C': 'orange', 'F': 'red'}
        colors = [grade_colors.get(g, 'gray') for g in grades]
        
        fig.add_trace(go.Scatter(
            x=list(range(len(cumulative_pnl))),
            y=cumulative_pnl,
            mode='lines+markers',
            name='Equity',
            line=dict(color='blue', width=2),
            marker=dict(color=colors, size=8)
        ))
        
        fig.update_layout(
            title="Equity Curve (colored by grade)",
            xaxis_title="Trade #",
            yaxis_title="Cumulative P&L ($)",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _show_psychology_analysis(self, trades: List[Dict]):
        col1, col2 = st.columns(2)
        
        with col1:
            # Emotional state vs P&L
            emotional_buckets = {
                "1-3 (Calm)": [],
                "4-6 (Neutral)": [],
                "7-10 (Emotional)": []
            }
            
            for trade in trades:
                em = trade.get('emotional_state', 5)
                if em <= 3:
                    emotional_buckets["1-3 (Calm)"].append(trade)
                elif em <= 6:
                    emotional_buckets["4-6 (Neutral)"].append(trade)
                else:
                    emotional_buckets["7-10 (Emotional)"].append(trade)
            
            bucket_data = []
            for bucket, bucket_trades in emotional_buckets.items():
                if bucket_trades:
                    pnl = sum(t.get('pnl', 0) for t in bucket_trades)
                    wins = len([t for t in bucket_trades if t.get('pnl', 0) > 0])
                    wr = wins / len(bucket_trades) * 100
                    bucket_data.append({
                        "Emotional State": bucket,
                        "Trades": len(bucket_trades),
                        "P&L": pnl,
                        "Win Rate": wr
                    })
            
            if bucket_data:
                df = pd.DataFrame(bucket_data)
                fig = px.bar(df, x="Emotional State", y="P&L", color="Win Rate",
                            title="P&L by Emotional State")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Grade distribution by emotional state
            emotional_grades = {}
            for trade in trades:
                em = trade.get('emotional_state', 5)
                grade = trade.get('grade', 'C')
                
                if em <= 3:
                    key = "Calm (1-3)"
                elif em <= 6:
                    key = "Neutral (4-6)"
                else:
                    key = "Emotional (7-10)"
                
                if key not in emotional_grades:
                    emotional_grades[key] = {'A': 0, 'B': 0, 'C': 0, 'F': 0}
                emotional_grades[key][grade] += 1
            
            if emotional_grades:
                em_df = pd.DataFrame(emotional_grades).T
                fig = px.bar(em_df, barmode='stack', title="Grades by Emotional State",
                            color_discrete_map={'A': 'green', 'B': 'gold', 'C': 'orange', 'F': 'red'})
                st.plotly_chart(fig, use_container_width=True)
        
        # Insight
        emotional_trades = [t for t in trades if t.get('emotional_state', 5) >= 7]
        calm_trades = [t for t in trades if t.get('emotional_state', 5) <= 3]
        
        if emotional_trades and calm_trades:
            emotional_pnl = sum(t.get('pnl', 0) for t in emotional_trades)
            calm_pnl = sum(t.get('pnl', 0) for t in calm_trades)
            
            if calm_pnl > emotional_pnl:
                diff = calm_pnl - emotional_pnl
                st.success(f"💡 You make ${diff:,.2f} more when trading calm vs emotional. Stick to your check-in rules!")
            else:
                st.warning("🧘 Consider only trading when emotional state is 5 or below.")
    
    def _show_playbook_performance(self, trades: List[Dict]):
        playbooks = list(set(t.get('playbook', 'Unknown') for t in trades))
        
        pb_data = []
        for pb in playbooks:
            pb_trades = [t for t in trades if t.get('playbook') == pb]
            if pb_trades:
                pnl = sum(t.get('pnl', 0) for t in pb_trades)
                wins = len([t for t in pb_trades if t.get('pnl', 0) > 0])
                wr = wins / len(pb_trades) * 100
                a_b_count = len([t for t in pb_trades if t.get('grade') in ['A', 'B']])
                
                pb_data.append({
                    "Playbook": pb,
                    "Trades": len(pb_trades),
                    "P&L": f"${pnl:,.2f}",
                    "Win Rate": f"{wr:.1f}%",
                    "A/B Setups": a_b_count,
                    "Avg P&L": f"${pnl / len(pb_trades):,.2f}"
                })
        
        if pb_data:
            df = pd.DataFrame(pb_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
    
    def _show_account_performance(self, trades: List[Dict], accounts: List[Dict]):
        account_names = list(set(t.get('account', 'Unknown') for t in trades))
        
        acc_data = []
        for acc_name in account_names:
            acc_trades = [t for t in trades if t.get('account') == acc_name]
            if acc_trades:
                pnl = sum(t.get('pnl', 0) for t in acc_trades)
                wins = len([t for t in acc_trades if t.get('pnl', 0) > 0])
                wr = wins / len(acc_trades) * 100
                
                # Get account info
                acc_info = next((a for a in accounts if a.get('name') == acc_name), {})
                status = acc_info.get('status', 'unknown')
                balance = acc_info.get('balance', 0)
                
                acc_data.append({
                    "Account": acc_name,
                    "Status": status.title(),
                    "Balance": f"${balance:,.2f}",
                    "Trades": len(acc_trades),
                    "P&L": f"${pnl:,.2f}",
                    "Win Rate": f"{wr:.1f}%"
                })
        
        if acc_data:
            df = pd.DataFrame(acc_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
