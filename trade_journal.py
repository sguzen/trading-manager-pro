import streamlit as st
import pandas as pd
from datetime import date, datetime, time, timedelta
from typing import Dict, List

class TradeJournal:
    def __init__(self, data_storage):
        self.data_storage = data_storage
    
    def show_journal(self):
        tab1, tab2, tab3 = st.tabs(["📊 Trade History", "✏️ Edit Trades", "🎯 Daily Check-in"])
        
        with tab1:
            self.show_trade_history()
        
        with tab2:
            self.edit_trades()
        
        with tab3:
            self.daily_checkin()
    
    def show_trade_history(self):
        st.subheader("Trade History")
        st.info("💡 Use the **Live Trade Grader** in the sidebar to log new trades!")
        
        trades = self.data_storage.load_trades()
        
        if not trades:
            st.write("No trades logged yet.")
            return
        
        df = pd.DataFrame(trades)
        df['date'] = pd.to_datetime(df['date'])
        
        # Summary
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Trades", len(df))
        with col2:
            win_rate = (df['pnl_net'] > 0).mean() * 100
            st.metric("Win Rate", f"{win_rate:.1f}%")
        with col3:
            st.metric("Total P&L", f"${df['pnl_net'].sum():,.2f}")
        with col4:
            st.metric("Avg P&L", f"${df['pnl_net'].mean():,.2f}")
        
        # Display trades
        display_df = df.sort_values('date', ascending=False)
        
        for _, trade in display_df.iterrows():
            grade = trade.get('grade', '-')
            grade_emoji = {"A": "🟢", "B": "🟡", "C": "🟠", "F": "🔴"}.get(grade, "⚪")
            pnl = trade.get('pnl_net', 0)
            pnl_color = "green" if pnl >= 0 else "red"
            
            with st.expander(f"{grade_emoji} {trade['date'].strftime('%Y-%m-%d')} | {trade.get('symbol', 'N/A')} {trade.get('direction', '')} | ${pnl:+,.2f}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Grade:** {grade} ({trade.get('grade_percentage', 0):.0f}%)")
                    st.write(f"**Entry:** {trade.get('entry_price', '-')} | **Stop:** {trade.get('stop_loss', '-')} | **TP:** {trade.get('take_profit', '-')}")
                    st.write(f"**Position:** {trade.get('position_size', 1)} contracts")
                with col2:
                    st.write(f"**Emotional State:** {trade.get('emotional_state', '-')}/10")
                    st.write(f"**Would Repeat:** {'✓' if trade.get('would_repeat') else '✗'}")
                    if trade.get('screenshot_url'):
                        st.write(f"[Screenshot]({trade['screenshot_url']})")
                if trade.get('notes'):
                    st.write(f"**Notes:** {trade['notes']}")
    
    def edit_trades(self):
        st.subheader("Edit & Delete Trades")
        
        trades = self.data_storage.load_trades()
        
        if not trades:
            st.write("No trades to edit.")
            return
        
        trades_sorted = sorted(trades, key=lambda x: x.get('date', ''), reverse=True)
        
        for i, trade in enumerate(trades_sorted[:20]):  # Show last 20
            original_idx = next((j for j, t in enumerate(trades) if t.get('id') == trade.get('id')), i)
            
            grade = trade.get('grade', '-')
            grade_emoji = {"A": "🟢", "B": "🟡", "C": "🟠", "F": "🔴"}.get(grade, "⚪")
            
            with st.expander(f"✏️ {trade.get('date', 'N/A')} | {grade_emoji} | ${trade.get('pnl_net', 0):+,.2f}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_pnl = st.number_input("Net P&L ($)", value=float(trade.get('pnl_net', 0)),
                                             key=f"pnl_{original_idx}")
                    new_emotion = st.slider("Emotional State", 1, 10, 
                                           value=int(trade.get('emotional_state', 5)),
                                           key=f"emotion_{original_idx}")
                
                with col2:
                    new_notes = st.text_area("Notes", value=trade.get('notes', ''),
                                            key=f"notes_{original_idx}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Save", key=f"save_{original_idx}"):
                        # Update trade
                        old_pnl = trade.get('pnl_net', 0)
                        pnl_diff = new_pnl - old_pnl
                        
                        trades[original_idx]['pnl_net'] = new_pnl
                        trades[original_idx]['pnl_gross'] = new_pnl + trade.get('commission', 0)
                        trades[original_idx]['emotional_state'] = new_emotion
                        trades[original_idx]['notes'] = new_notes
                        trades[original_idx]['updated_at'] = datetime.now().isoformat()
                        
                        self.data_storage.save_trades(trades)
                        
                        # Update account balance if P&L changed
                        if pnl_diff != 0:
                            accounts = self.data_storage.load_accounts()
                            account_id = trade.get('account_id', '')
                            for j, acc in enumerate(accounts):
                                if acc.get('account_number') == account_id:
                                    accounts[j]['current_balance'] = acc.get('current_balance', 0) + pnl_diff
                                    self.data_storage.save_accounts(accounts)
                                    break
                        
                        st.success("Saved!")
                        st.rerun()
                
                with col2:
                    if st.button("🗑️ Delete", key=f"del_{original_idx}"):
                        # Reverse P&L from account
                        accounts = self.data_storage.load_accounts()
                        account_id = trade.get('account_id', '')
                        for j, acc in enumerate(accounts):
                            if acc.get('account_number') == account_id:
                                accounts[j]['current_balance'] = acc.get('current_balance', 0) - trade.get('pnl_net', 0)
                                self.data_storage.save_accounts(accounts)
                                break
                        
                        trades.pop(original_idx)
                        self.data_storage.save_trades(trades)
                        st.success("Deleted!")
                        st.rerun()
    
    def daily_checkin(self):
        st.subheader("Daily Pre-Market Check-in")
        
        checkins = self.data_storage.load_daily_checkins()
        today = date.today().isoformat()
        
        today_checkin = next((c for c in checkins if c.get('date') == today), None)
        
        if today_checkin:
            st.success("✅ Today's check-in complete!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Sleep", f"{today_checkin.get('sleep_quality', '-')}/10")
                st.metric("Stress", f"{today_checkin.get('stress_level', '-')}/10")
            with col2:
                st.metric("Home Stress", f"{today_checkin.get('home_stress', '-')}/10")
                st.metric("Alcohol 24h", "Yes" if today_checkin.get('alcohol_24h') else "No")
            with col3:
                st.metric("Exercise", "Yes" if today_checkin.get('exercise') else "No")
            
            # Risk assessment
            high_risk = (
                today_checkin.get('stress_level', 0) > 7 or
                today_checkin.get('home_stress', 0) > 7 or
                today_checkin.get('alcohol_24h', False) or
                today_checkin.get('sleep_quality', 10) < 5
            )
            
            if high_risk:
                st.error("🚨 HIGH RISK - Consider taking the day off")
            else:
                st.success("✅ CLEARED FOR TRADING")
            
            if today_checkin.get('trading_plan'):
                st.write(f"**Plan:** {today_checkin['trading_plan']}")
        
        else:
            with st.form("checkin"):
                col1, col2 = st.columns(2)
                
                with col1:
                    sleep = st.slider("Sleep Quality", 1, 10, 7)
                    stress = st.slider("Stress Level", 1, 10, 5)
                    home_stress = st.slider("Home Stress", 1, 10, 5)
                
                with col2:
                    alcohol = st.checkbox("Alcohol in last 24h")
                    exercise = st.checkbox("Exercise today/yesterday")
                
                plan = st.text_area("Today's Trading Plan")
                emotions = st.text_area("Current Emotional State")
                
                if st.form_submit_button("Complete Check-in", type="primary"):
                    checkin_data = {
                        "sleep_quality": sleep,
                        "stress_level": stress,
                        "home_stress": home_stress,
                        "alcohol_24h": alcohol,
                        "exercise": exercise,
                        "trading_plan": plan,
                        "current_emotions": emotions
                    }
                    self.data_storage.add_daily_checkin(checkin_data)
                    st.success("Check-in complete!")
                    st.rerun()
        
        # Recent check-ins
        if len(checkins) > 1:
            st.subheader("Recent Check-ins")
            recent = sorted(checkins, key=lambda x: x.get('date', ''), reverse=True)[:7]
            
            data = {
                'Date': [c.get('date') for c in recent],
                'Sleep': [c.get('sleep_quality') for c in recent],
                'Stress': [c.get('stress_level') for c in recent],
                'Home': [c.get('home_stress') for c in recent]
            }
            st.line_chart(pd.DataFrame(data).set_index('Date'))
