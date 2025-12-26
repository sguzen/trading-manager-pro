import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List

class Dashboard:
    def __init__(self, data_storage):
        self.data_storage = data_storage
    
    def show_performance_analysis(self):
        trades = self.data_storage.load_trades()
        accounts = self.data_storage.load_accounts()
        withdrawals = self.data_storage.load_withdrawals()
        checkins = self.data_storage.load_daily_checkins()
        
        if not trades:
            st.info("No trades logged yet. Start logging trades to see performance analysis.")
            return
        
        df = pd.DataFrame(trades)
        df['date'] = pd.to_datetime(df['date'])
        
        # Date range filter
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("From", value=df['date'].min().date())
        with col2:
            end_date = st.date_input("To", value=df['date'].max().date())
        
        # Filter data
        mask = (df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)
        filtered_df = df[mask]
        
        if filtered_df.empty:
            st.warning("No trades in selected date range.")
            return
        
        # Key Metrics
        st.subheader("📊 Key Performance Metrics")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        total_trades = len(filtered_df)
        winning_trades = len(filtered_df[filtered_df['pnl_net'] > 0])
        losing_trades = len(filtered_df[filtered_df['pnl_net'] < 0])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        with col1:
            st.metric("Total Trades", total_trades)
        
        with col2:
            st.metric("Win Rate", f"{win_rate:.1f}%")
        
        with col3:
            total_pnl = filtered_df['pnl_net'].sum()
            st.metric("Total P&L", f"${total_pnl:,.2f}")
        
        with col4:
            avg_win = filtered_df[filtered_df['pnl_net'] > 0]['pnl_net'].mean() if winning_trades > 0 else 0
            st.metric("Avg Win", f"${avg_win:,.2f}")
        
        with col5:
            avg_loss = filtered_df[filtered_df['pnl_net'] < 0]['pnl_net'].mean() if losing_trades > 0 else 0
            st.metric("Avg Loss", f"${avg_loss:,.2f}")
        
        # Second row - Grade-based metrics
        st.subheader("📋 Performance by Grade")
        
        if 'grade' in filtered_df.columns:
            col1, col2, col3, col4 = st.columns(4)
            
            for i, (grade, col) in enumerate(zip(['A', 'B', 'C', 'F'], [col1, col2, col3, col4])):
                grade_trades = filtered_df[filtered_df['grade'] == grade]
                with col:
                    grade_emoji = {"A": "🟢", "B": "🟡", "C": "🟠", "F": "🔴"}[grade]
                    st.write(f"**{grade_emoji} {grade}-Grade**")
                    if len(grade_trades) > 0:
                        g_pnl = grade_trades['pnl_net'].sum()
                        g_wins = (grade_trades['pnl_net'] > 0).sum()
                        g_wr = g_wins / len(grade_trades) * 100
                        st.metric("Trades", len(grade_trades))
                        st.metric("P&L", f"${g_pnl:,.2f}")
                        st.metric("Win Rate", f"{g_wr:.0f}%")
                    else:
                        st.write("No trades")
        
        # Charts
        st.subheader("📈 Performance Charts")
        
        tab1, tab2, tab3, tab4 = st.tabs(["Equity Curve", "By Grade", "Daily P&L", "Psychology"])
        
        with tab1:
            # Equity curve
            equity_df = filtered_df.sort_values('date').copy()
            equity_df['cumulative_pnl'] = equity_df['pnl_net'].cumsum()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=equity_df['date'],
                y=equity_df['cumulative_pnl'],
                mode='lines+markers',
                name='Cumulative P&L',
                line=dict(color='green' if equity_df['cumulative_pnl'].iloc[-1] >= 0 else 'red')
            ))
            fig.update_layout(
                title='Equity Curve',
                xaxis_title='Date',
                yaxis_title='Cumulative P&L ($)',
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Performance by grade
            if 'grade' in filtered_df.columns:
                grade_stats = filtered_df.groupby('grade').agg({
                    'pnl_net': ['count', 'sum', 'mean']
                }).round(2)
                grade_stats.columns = ['Trades', 'Total P&L', 'Avg P&L']
                
                # Reorder
                grade_order = ['A', 'B', 'C', 'F']
                grade_stats = grade_stats.reindex([g for g in grade_order if g in grade_stats.index])
                
                st.dataframe(grade_stats, use_container_width=True)
                
                # Grade P&L chart
                fig = go.Figure()
                colors = {'A': 'green', 'B': 'gold', 'C': 'orange', 'F': 'red'}
                for grade in grade_order:
                    if grade in grade_stats.index:
                        fig.add_trace(go.Bar(
                            x=[grade],
                            y=[grade_stats.loc[grade, 'Total P&L']],
                            name=f"{grade}-Grade",
                            marker_color=colors[grade]
                        ))
                fig.update_layout(title='P&L by Trade Grade', yaxis_title='Total P&L ($)')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No grade data available. Use the Live Trade Grader to log trades with grades.")
        
        with tab3:
            # Daily P&L bars
            daily_pnl = filtered_df.groupby(filtered_df['date'].dt.date)['pnl_net'].sum().reset_index()
            daily_pnl.columns = ['date', 'pnl']
            
            colors = ['green' if x >= 0 else 'red' for x in daily_pnl['pnl']]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=daily_pnl['date'],
                y=daily_pnl['pnl'],
                marker_color=colors,
                name='Daily P&L'
            ))
            fig.update_layout(
                title='Daily P&L',
                xaxis_title='Date',
                yaxis_title='P&L ($)'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Daily stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Best Day", f"${daily_pnl['pnl'].max():,.2f}")
            with col2:
                st.metric("Worst Day", f"${daily_pnl['pnl'].min():,.2f}")
            with col3:
                green_days = len(daily_pnl[daily_pnl['pnl'] > 0])
                st.metric("Green Days", f"{green_days}/{len(daily_pnl)} ({green_days/len(daily_pnl)*100:.0f}%)")
        
        with tab4:
            # Psychology analysis
            st.write("### Emotional State Impact")
            
            if 'emotional_state' in filtered_df.columns:
                # P&L by emotional state
                emotion_pnl = filtered_df.groupby('emotional_state')['pnl_net'].agg(['mean', 'sum', 'count'])
                emotion_pnl.columns = ['Avg P&L', 'Total P&L', 'Trades']
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=emotion_pnl.index,
                    y=emotion_pnl['Avg P&L'],
                    marker_color=['green' if x >= 0 else 'red' for x in emotion_pnl['Avg P&L']],
                    name='Avg P&L'
                ))
                fig.update_layout(
                    title='Average P&L by Emotional State',
                    xaxis_title='Emotional State (1=Calm, 10=Tilted)',
                    yaxis_title='Average P&L ($)'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Key insight
                calm_trades = filtered_df[filtered_df['emotional_state'] <= 5]
                tilted_trades = filtered_df[filtered_df['emotional_state'] > 5]
                
                col1, col2 = st.columns(2)
                with col1:
                    if len(calm_trades) > 0:
                        st.metric("Avg P&L (Calm, ≤5)", f"${calm_trades['pnl_net'].mean():,.2f}")
                with col2:
                    if len(tilted_trades) > 0:
                        st.metric("Avg P&L (Tilted, >5)", f"${tilted_trades['pnl_net'].mean():,.2f}")
        
        # Export options
        st.subheader("📥 Export Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="Download Trades CSV",
                data=csv,
                file_name=f"trades_{start_date}_{end_date}.csv",
                mime="text/csv"
            )
        
        with col2:
            all_data = self.data_storage.export_all_data()
            import json
            json_str = json.dumps(all_data, indent=2, default=str)
            st.download_button(
                label="Download All Data JSON",
                data=json_str,
                file_name=f"trading_data_export_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
