import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta, date
import numpy as np

class Dashboard:
    def __init__(self, data_storage):
        self.data_storage = data_storage
    
    def show_performance_analysis(self):
        trades = self.data_storage.load_trades()
        accounts = self.data_storage.load_accounts()
        withdrawals = self.data_storage.load_withdrawals()
        checkins = self.data_storage.load_daily_checkins()
        
        if not trades:
            st.info("No trades recorded yet. Start logging trades to see performance analysis.")
            return
        
        df = pd.DataFrame(trades)
        df['date'] = pd.to_datetime(df['date'])
        
        # Time period selector
        col1, col2 = st.columns(2)
        with col1:
            period = st.selectbox("Analysis Period", 
                                ["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"])
        
        with col2:
            account_filter = st.selectbox("Account Filter", 
                                        ["All Accounts"] + df['account'].unique().tolist())
        
        # Apply filters
        if period != "All Time":
            days = {"Last 7 Days": 7, "Last 30 Days": 30, "Last 90 Days": 90}[period]
            cutoff_date = datetime.now() - timedelta(days=days)
            df = df[df['date'] >= cutoff_date]
        
        if account_filter != "All Accounts":
            df = df[df['account'] == account_filter]
        
        if df.empty:
            st.warning("No trades found for the selected filters.")
            return
        
        # Main metrics
        self.show_key_metrics(df)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            self.show_pnl_curve(df)
            self.show_win_loss_distribution(df)
        
        with col2:
            self.show_daily_pnl(df)
            self.show_emotional_correlation(df)
        
        # Detailed analysis
        st.subheader("Detailed Analysis")
        
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Trade Breakdown", "🎯 Rule Compliance", "😤 Psychology", "📈 Account Progress"])
        
        with tab1:
            self.show_trade_breakdown(df)
        
        with tab2:
            self.show_rule_compliance(df)
        
        with tab3:
            self.show_psychology_analysis(df, checkins)
        
        with tab4:
            self.show_account_progress(accounts, withdrawals)
    
    def show_key_metrics(self, df):
        st.subheader("Performance Overview")
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        # Basic metrics
        total_trades = len(df)
        winning_trades = len(df[df['pnl_net'] > 0])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        total_pnl = df['pnl_net'].sum()
        avg_win = df[df['pnl_net'] > 0]['pnl_net'].mean() if winning_trades > 0 else 0
        avg_loss = df[df['pnl_net'] < 0]['pnl_net'].mean() if total_trades - winning_trades > 0 else 0
        
        with col1:
            st.metric("Total Trades", total_trades)
        
        with col2:
            delta_color = "normal" if win_rate >= 50 else "inverse"
            st.metric("Win Rate", f"{win_rate:.1f}%", delta_color=delta_color)
        
        with col3:
            delta_color = "normal" if total_pnl >= 0 else "inverse"
            st.metric("Total P&L", f"${total_pnl:.2f}", delta_color=delta_color)
        
        with col4:
            profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
            delta_color = "normal" if profit_factor >= 1.5 else "inverse"
            st.metric("Profit Factor", f"{profit_factor:.2f}", delta_color=delta_color)
        
        with col5:
            avg_trade = df['pnl_net'].mean()
            delta_color = "normal" if avg_trade >= 0 else "inverse"
            st.metric("Avg Trade", f"${avg_trade:.2f}", delta_color=delta_color)
        
        with col6:
            rule_compliance = df['followed_rules'].mean() * 100 if 'followed_rules' in df.columns else 0
            delta_color = "normal" if rule_compliance >= 80 else "inverse"
            st.metric("Rule Compliance", f"{rule_compliance:.0f}%", delta_color=delta_color)
    
    def show_pnl_curve(self, df):
        st.subheader("P&L Curve")
        
        df_sorted = df.sort_values('date')
        df_sorted['cumulative_pnl'] = df_sorted['pnl_net'].cumsum()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_sorted['date'],
            y=df_sorted['cumulative_pnl'],
            mode='lines+markers',
            name='Cumulative P&L',
            line=dict(color='green' if df_sorted['cumulative_pnl'].iloc[-1] >= 0 else 'red', width=2),
            hovertemplate='Date: %{x}<br>Cumulative P&L: $%{y:.2f}<extra></extra>'
        ))
        
        fig.update_layout(
            title="Cumulative P&L Over Time",
            xaxis_title="Date",
            yaxis_title="Cumulative P&L ($)",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def show_daily_pnl(self, df):
        st.subheader("Daily P&L")
        
        daily_pnl = df.groupby(df['date'].dt.date)['pnl_net'].sum().reset_index()
        daily_pnl['color'] = daily_pnl['pnl_net'].apply(lambda x: 'green' if x >= 0 else 'red')
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=daily_pnl['date'],
            y=daily_pnl['pnl_net'],
            marker_color=daily_pnl['color'],
            name='Daily P&L',
            hovertemplate='Date: %{x}<br>Daily P&L: $%{y:.2f}<extra></extra>'
        ))
        
        fig.update_layout(
            title="Daily P&L Distribution",
            xaxis_title="Date",
            yaxis_title="P&L ($)",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def show_win_loss_distribution(self, df):
        st.subheader("Win/Loss Distribution")
        
        wins = df[df['pnl_net'] > 0]['pnl_net']
        losses = df[df['pnl_net'] < 0]['pnl_net']
        
        fig = go.Figure()
        
        if len(wins) > 0:
            fig.add_trace(go.Histogram(
                x=wins,
                name="Wins",
                marker_color='green',
                opacity=0.7,
                nbinsx=10
            ))
        
        if len(losses) > 0:
            fig.add_trace(go.Histogram(
                x=losses,
                name="Losses",
                marker_color='red',
                opacity=0.7,
                nbinsx=10
            ))
        
        fig.update_layout(
            title="P&L Distribution",
            xaxis_title="P&L ($)",
            yaxis_title="Frequency",
            barmode='overlay'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def show_emotional_correlation(self, df):
        st.subheader("Emotional State vs Performance")
        
        if 'emotional_state' not in df.columns:
            st.info("No emotional state data available.")
            return
        
        fig = px.scatter(
            df,
            x='emotional_state',
            y='pnl_net',
            color='pnl_net',
            size='position_size',
            hover_data=['symbol', 'direction'],
            title="P&L vs Emotional State",
            color_continuous_scale='RdYlGn'
        )
        
        # Add trend line
        z = np.polyfit(df['emotional_state'], df['pnl_net'], 1)
        p = np.poly1d(z)
        fig.add_trace(go.Scatter(
            x=df['emotional_state'].sort_values(),
            y=p(df['emotional_state'].sort_values()),
            mode='lines',
            name='Trend Line',
            line=dict(dash='dash', color='black')
        ))
        
        fig.update_layout(
            xaxis_title="Emotional State (1-10)",
            yaxis_title="P&L ($)"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Correlation analysis
        correlation = df['emotional_state'].corr(df['pnl_net'])
        if abs(correlation) > 0.3:
            if correlation < 0:
                st.warning(f"⚠️ Strong negative correlation ({correlation:.2f}) - Higher emotional states hurt performance")
            else:
                st.info(f"ℹ️ Positive correlation ({correlation:.2f}) - Higher emotional states help performance")
    
    def show_trade_breakdown(self, df):
        col1, col2 = st.columns(2)
        
        with col1:
            # By symbol
            symbol_stats = df.groupby('symbol').agg({
                'pnl_net': ['count', 'sum', 'mean'],
                'followed_rules': 'mean'
            }).round(2)
            
            symbol_stats.columns = ['Trades', 'Total P&L', 'Avg P&L', 'Rule Compliance']
            st.write("**Performance by Symbol**")
            st.dataframe(symbol_stats)
        
        with col2:
            # By direction
            direction_stats = df.groupby('direction').agg({
                'pnl_net': ['count', 'sum', 'mean']
            }).round(2)
            
            direction_stats.columns = ['Trades', 'Total P&L', 'Avg P&L']
            st.write("**Performance by Direction**")
            st.dataframe(direction_stats)
        
        # By playbook
        if 'playbook' in df.columns:
            st.write("**Performance by Playbook**")
            playbook_stats = df.groupby('playbook').agg({
                'pnl_net': ['count', 'sum', 'mean'],
                'followed_rules': 'mean',
                'setup_quality': 'mean',
                'execution_quality': 'mean'
            }).round(2)
            
            playbook_stats.columns = ['Trades', 'Total P&L', 'Avg P&L', 'Rule Compliance', 'Avg Setup', 'Avg Execution']
            st.dataframe(playbook_stats, use_container_width=True)
    
    def show_rule_compliance(self, df):
        if 'followed_rules' not in df.columns:
            st.info("No rule compliance data available.")
            return
        
        # Rule compliance over time
        df_sorted = df.sort_values('date')
        compliance_ma = df_sorted['followed_rules'].rolling(window=10, min_periods=1).mean()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_sorted['date'],
            y=compliance_ma * 100,
            mode='lines',
            name='Rule Compliance (10-trade MA)',
            line=dict(color='blue', width=2),
            hovertemplate='Date: %{x}<br>Compliance: %{y:.1f}%<extra></extra>'
        ))
        
        fig.update_layout(
            title="Rule Compliance Trend",
            xaxis_title="Date",
            yaxis_title="Compliance (%)",
            yaxis=dict(range=[0, 100])
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Rule violations impact
        rule_violators = df[df['followed_rules'] == False]
        rule_followers = df[df['followed_rules'] == True]
        
        if len(rule_violators) > 0 and len(rule_followers) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Avg P&L (Rule Followers)", f"${rule_followers['pnl_net'].mean():.2f}")
                st.metric("Win Rate (Rule Followers)", f"{(rule_followers['pnl_net'] > 0).mean() * 100:.1f}%")
            
            with col2:
                st.metric("Avg P&L (Rule Violators)", f"${rule_violators['pnl_net'].mean():.2f}")
                st.metric("Win Rate (Rule Violators)", f"{(rule_violators['pnl_net'] > 0).mean() * 100:.1f}%")
    
    def show_psychology_analysis(self, df, checkins):
        col1, col2 = st.columns(2)
        
        with col1:
            if 'emotional_state' in df.columns:
                # Emotional state distribution
                fig = px.histogram(
                    df,
                    x='emotional_state',
                    title="Emotional State Distribution During Trading",
                    nbins=10
                )
                fig.update_layout(
                    xaxis_title="Emotional State (1-10)",
                    yaxis_title="Number of Trades"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Performance by emotional state
                emotion_performance = df.groupby('emotional_state')['pnl_net'].mean()
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=emotion_performance.index,
                    y=emotion_performance.values,
                    marker_color=['red' if x < 0 else 'green' for x in emotion_performance.values]
                ))
                
                fig.update_layout(
                    title="Average P&L by Emotional State",
                    xaxis_title="Emotional State",
                    yaxis_title="Average P&L ($)"
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if checkins:
                # Daily check-in trends
                checkin_df = pd.DataFrame(checkins)
                if 'date' in checkin_df.columns:
                    checkin_df['date'] = pd.to_datetime(checkin_df['date'])
                    recent_checkins = checkin_df.tail(30)  # Last 30 days
                    
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=recent_checkins['date'],
                        y=recent_checkins['sleep_quality'],
                        name='Sleep Quality',
                        line=dict(color='blue')
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=recent_checkins['date'],
                        y=recent_checkins['stress_level'],
                        name='Stress Level',
                        line=dict(color='red')
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=recent_checkins['date'],
                        y=recent_checkins['home_stress'],
                        name='Home Stress',
                        line=dict(color='orange')
                    ))
                    
                    fig.update_layout(
                        title="Daily Check-in Trends",
                        xaxis_title="Date",
                        yaxis_title="Rating (1-10)",
                        yaxis=dict(range=[1, 10])
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
        
        # Psychology insights
        st.subheader("Psychology Insights")
        
        insights = []
        
        if 'emotional_state' in df.columns:
            high_emotion_trades = df[df['emotional_state'] > 7]
            if len(high_emotion_trades) > 0:
                high_emotion_pnl = high_emotion_trades['pnl_net'].mean()
                normal_emotion_pnl = df[df['emotional_state'] <= 7]['pnl_net'].mean()
                
                if high_emotion_pnl < normal_emotion_pnl:
                    insights.append("🚨 You perform worse when emotional state is high (>7). Consider mandatory breaks.")
                else:
                    insights.append("✅ High emotional state doesn't seem to hurt your performance.")
        
        if 'followed_rules' in df.columns:
            rule_violation_rate = (df['followed_rules'] == False).mean()
            if rule_violation_rate > 0.2:
                insights.append(f"⚠️ High rule violation rate ({rule_violation_rate*100:.0f}%). Focus on discipline.")
        
        if checkins and len(checkins) > 7:
            recent_checkins = pd.DataFrame(checkins).tail(7)
            avg_stress = recent_checkins['stress_level'].mean()
            if avg_stress > 7:
                insights.append("🔴 High stress levels detected in recent check-ins. Consider stress management.")
            
            alcohol_days = recent_checkins['alcohol_24h'].sum()
            if alcohol_days > 2:
                insights.append(f"⚠️ Alcohol consumption on {alcohol_days} days in last week. Monitor impact on trading.")
        
        if insights:
            for insight in insights:
                st.write(insight)
        else:
            st.success("✅ No major psychological red flags detected!")
    
    def show_account_progress(self, accounts, withdrawals):
        st.subheader("Account Progress Tracking")
        
        if not accounts:
            st.info("No accounts configured.")
            return
        
        # Account status overview
        status_counts = {}
        for account in accounts:
            status = account['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Evaluation", status_counts.get('evaluation', 0))
        with col2:
            st.metric("Funded", status_counts.get('funded', 0))
        with col3:
            st.metric("Passed", status_counts.get('passed', 0))
        with col4:
            st.metric("Failed", status_counts.get('failed', 0))
        
        # Withdrawal progress
        if withdrawals:
            total_withdrawn = sum(w['amount'] for w in withdrawals)
            goal_progress = total_withdrawn / 5000000 * 100
            
            st.subheader("Path to $5M Goal")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number+delta",
                    value = total_withdrawn,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Total Withdrawn ($)"},
                    delta = {'reference': 0, 'increasing': {'color': "green"}},
                    gauge = {
                        'axis': {'range': [None, 5000000]},
                        'bar': {'color': "darkgreen"},
                        'steps': [
                            {'range': [0, 1000000], 'color': "lightgray"},
                            {'range': [1000000, 2500000], 'color': "gray"},
                            {'range': [2500000, 5000000], 'color': "lightgreen"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 5000000
                        }
                    }
                ))
                
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.metric("Progress", f"{goal_progress:.2f}%")
                
                remaining = 5000000 - total_withdrawn
                st.metric("Remaining", f"${remaining:,.0f}")
                
                if total_withdrawn > 0:
                    months_to_goal = remaining / (total_withdrawn / len(withdrawals)) if len(withdrawals) > 0 else float('inf')
                    if months_to_goal < 120:  # Less than 10 years
                        st.metric("Est. Months to Goal", f"{months_to_goal:.0f}")
        
        # Account details table
        if accounts:
            st.subheader("Account Details")
            
            account_data = []
            for account in accounts:
                account_data.append({
                    'Prop Firm': account['prop_firm'],
                    'Account Type': account['account_type'],
                    'Status': account['status'],
                    'Balance': account['current_balance'],
                    'Profit Target': account['profit_target'],
                    'Progress': f"{(account['current_balance'] / account['profit_target'] * 100):.1f}%" if account['profit_target'] > 0 else "0%"
                })
            
            df_accounts = pd.DataFrame(account_data)
            
            st.dataframe(
                df_accounts,
                use_container_width=True,
                column_config={
                    "Balance": st.column_config.NumberColumn("Balance", format="$%.2f"),
                    "Profit Target": st.column_config.NumberColumn("Target", format="$%.2f"),
                    "Status": st.column_config.SelectboxColumn("Status", options=["evaluation", "funded", "passed", "failed"])
                }
            )