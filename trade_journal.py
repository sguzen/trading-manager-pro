import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from typing import Dict, List
import calendar

class TradeJournal:
    def __init__(self, data_storage):
        self.data_storage = data_storage
    
    def show_journal(self):
        tab1, tab2, tab3, tab4 = st.tabs(["📅 Calendar", "🎯 Daily Plan & Review", "📊 Trade History", "✏️ Edit Trades"])
        
        with tab1:
            self.show_calendar()
        with tab2:
            self.daily_plan_review()
        with tab3:
            self.show_trade_history()
        with tab4:
            self.edit_trades()
    
    def show_calendar(self):
        st.subheader("📅 Trading Calendar")
        
        # Month/Year selector
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            selected_month = st.selectbox("Month", range(1, 13), 
                                         index=date.today().month - 1,
                                         format_func=lambda x: calendar.month_name[x])
        with col2:
            current_year = date.today().year
            selected_year = st.selectbox("Year", range(current_year - 2, current_year + 2),
                                        index=2)
        
        # Load data
        trades = self.data_storage.load_trades()
        daily_entries = self.data_storage.load_daily_entries()
        
        # Calculate daily P&L
        daily_pnl = {}
        for trade in trades:
            trade_date = trade.get('date', '')[:10]
            if trade_date:
                daily_pnl[trade_date] = daily_pnl.get(trade_date, 0) + trade.get('pnl_net', 0)
        
        # Build calendar
        cal = calendar.Calendar(firstweekday=6)  # Start on Sunday
        month_days = cal.monthdayscalendar(selected_year, selected_month)
        
        # Header
        st.markdown("**Sun | Mon | Tue | Wed | Thu | Fri | Sat**")
        
        # Calendar grid
        for week in month_days:
            cols = st.columns(7)
            for i, day in enumerate(week):
                with cols[i]:
                    if day == 0:
                        st.write("")
                    else:
                        date_str = f"{selected_year}-{selected_month:02d}-{day:02d}"
                        pnl = daily_pnl.get(date_str, None)
                        entry = next((e for e in daily_entries if e.get('date') == date_str), None)
                        
                        # Day number
                        if pnl is not None:
                            if pnl > 0:
                                st.markdown(f"**:green[{day}]**")
                                st.caption(f"+${pnl:.0f}")
                            elif pnl < 0:
                                st.markdown(f"**:red[{day}]**")
                                st.caption(f"-${abs(pnl):.0f}")
                            else:
                                st.markdown(f"**{day}**")
                                st.caption("$0")
                        else:
                            st.markdown(f"{day}")
                        
                        # Indicator for notes
                        if entry:
                            if entry.get('plan') or entry.get('review'):
                                st.caption("📝")
        
        # Summary for selected month
        st.markdown("---")
        st.subheader(f"Summary: {calendar.month_name[selected_month]} {selected_year}")
        
        month_trades = [t for t in trades if t.get('date', '').startswith(f"{selected_year}-{selected_month:02d}")]
        
        if month_trades:
            col1, col2, col3, col4 = st.columns(4)
            
            total_pnl = sum(t.get('pnl_net', 0) for t in month_trades)
            wins = sum(1 for t in month_trades if t.get('pnl_net', 0) > 0)
            win_rate = (wins / len(month_trades) * 100) if month_trades else 0
            
            trading_days = len(set(t.get('date', '')[:10] for t in month_trades))
            green_days = sum(1 for d, p in daily_pnl.items() 
                           if d.startswith(f"{selected_year}-{selected_month:02d}") and p > 0)
            
            col1.metric("Total P&L", f"${total_pnl:,.2f}")
            col2.metric("Trades", len(month_trades))
            col3.metric("Win Rate", f"{win_rate:.1f}%")
            col4.metric("Green Days", f"{green_days}/{trading_days}")
        else:
            st.info("No trades this month")
        
        # Day detail viewer
        st.markdown("---")
        st.subheader("Day Details")
        
        selected_date = st.date_input("Select Date", value=date.today())
        date_str = selected_date.isoformat()
        
        day_trades = [t for t in trades if t.get('date', '')[:10] == date_str]
        day_entry = next((e for e in daily_entries if e.get('date') == date_str), None)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Plan:**")
            if day_entry and day_entry.get('plan'):
                st.write(day_entry['plan'])
            else:
                st.caption("No plan recorded")
        
        with col2:
            st.write("**Review:**")
            if day_entry and day_entry.get('review'):
                st.write(day_entry['review'])
            else:
                st.caption("No review recorded")
        
        if day_trades:
            st.write("**Trades:**")
            for t in day_trades:
                grade = t.get('grade', '-')
                grade_emoji = {"A": "🟢", "B": "🟡", "C": "🟠", "F": "🔴"}.get(grade, "⚪")
                pnl = t.get('pnl_net', 0)
                st.write(f"{grade_emoji} {t.get('symbol', '?')} {t.get('direction', '?')} - ${pnl:+,.2f}")
    
    def daily_plan_review(self):
        st.subheader("🎯 Daily Plan & Review")
        
        daily_entries = self.data_storage.load_daily_entries()
        
        # Date selector
        selected_date = st.date_input("Date", value=date.today(), key="plan_date")
        date_str = selected_date.isoformat()
        
        # Find existing entry
        existing = next((e for e in daily_entries if e.get('date') == date_str), None)
        existing_idx = next((i for i, e in enumerate(daily_entries) if e.get('date') == date_str), None)
        
        # Pre-market section
        st.markdown("---")
        st.markdown("### 🌅 Pre-Market Plan")
        
        col1, col2 = st.columns(2)
        
        with col1:
            sleep_quality = st.slider("Sleep Quality", 1, 10, 
                                     value=existing.get('sleep_quality', 7) if existing else 7,
                                     key="sleep")
            stress_level = st.slider("Stress Level", 1, 10,
                                    value=existing.get('stress_level', 5) if existing else 5,
                                    key="stress")
            home_stress = st.slider("Home Stress", 1, 10,
                                   value=existing.get('home_stress', 5) if existing else 5,
                                   key="home")
        
        with col2:
            alcohol = st.checkbox("Alcohol in last 24h",
                                 value=existing.get('alcohol', False) if existing else False,
                                 key="alcohol")
            exercise = st.checkbox("Exercise today/yesterday",
                                  value=existing.get('exercise', False) if existing else False,
                                  key="exercise")
            
            # Risk assessment
            high_risk = stress_level > 7 or home_stress > 7 or alcohol or sleep_quality < 5
            if high_risk:
                st.error("🚨 HIGH RISK - Consider not trading")
            else:
                st.success("✅ CLEARED")
        
        plan = st.text_area("Today's Plan",
                           value=existing.get('plan', '') if existing else '',
                           placeholder="What setups am I looking for? Key levels? Goals?",
                           height=100,
                           key="plan")
        
        # End of day review
        st.markdown("---")
        st.markdown("### 🌙 End of Day Review")
        
        review = st.text_area("Daily Review",
                             value=existing.get('review', '') if existing else '',
                             placeholder="What worked? What didn't? Lessons learned?",
                             height=100,
                             key="review")
        
        col1, col2 = st.columns(2)
        with col1:
            followed_plan = st.checkbox("Followed my plan",
                                       value=existing.get('followed_plan', False) if existing else False,
                                       key="followed")
        with col2:
            emotional_control = st.slider("Emotional Control", 1, 10,
                                         value=existing.get('emotional_control', 5) if existing else 5,
                                         key="emotional")
        
        mistakes = st.text_area("Mistakes Made",
                               value=existing.get('mistakes', '') if existing else '',
                               placeholder="Any rule breaks? Emotional decisions?",
                               height=80,
                               key="mistakes")
        
        tomorrow = st.text_area("Tomorrow's Focus",
                               value=existing.get('tomorrow', '') if existing else '',
                               placeholder="What to improve tomorrow?",
                               height=80,
                               key="tomorrow")
        
        # Save button
        if st.button("💾 Save Entry", type="primary"):
            entry_data = {
                "date": date_str,
                "sleep_quality": sleep_quality,
                "stress_level": stress_level,
                "home_stress": home_stress,
                "alcohol": alcohol,
                "exercise": exercise,
                "plan": plan,
                "review": review,
                "followed_plan": followed_plan,
                "emotional_control": emotional_control,
                "mistakes": mistakes,
                "tomorrow": tomorrow,
                "updated_at": datetime.now().isoformat()
            }
            
            if existing_idx is not None:
                daily_entries[existing_idx] = entry_data
            else:
                entry_data['id'] = len(daily_entries) + 1
                entry_data['created_at'] = datetime.now().isoformat()
                daily_entries.append(entry_data)
            
            self.data_storage.save_daily_entries(daily_entries)
            st.success("Saved!")
            st.rerun()
        
        # Show today's trades
        trades = self.data_storage.load_trades()
        day_trades = [t for t in trades if t.get('date', '')[:10] == date_str]
        
        if day_trades:
            st.markdown("---")
            st.markdown("### 📊 Today's Trades")
            
            total_pnl = sum(t.get('pnl_net', 0) for t in day_trades)
            st.metric("Day P&L", f"${total_pnl:+,.2f}")
            
            for t in day_trades:
                grade = t.get('grade', '-')
                grade_emoji = {"A": "🟢", "B": "🟡", "C": "🟠", "F": "🔴"}.get(grade, "⚪")
                st.write(f"{grade_emoji} {t.get('symbol')} {t.get('direction')} | ${t.get('pnl_net', 0):+,.2f} | Emotional: {t.get('emotional_state', '-')}")
    
    def show_trade_history(self):
        st.subheader("Trade History")
        st.info("💡 Use **Live Trade Grader** in sidebar to log new trades")
        
        trades = self.data_storage.load_trades()
        
        if not trades:
            st.write("No trades yet")
            return
        
        # Summary
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Trades", len(trades))
        col2.metric("Win Rate", f"{sum(1 for t in trades if t.get('pnl_net', 0) > 0) / len(trades) * 100:.1f}%")
        col3.metric("Total P&L", f"${sum(t.get('pnl_net', 0) for t in trades):,.2f}")
        col4.metric("Avg P&L", f"${sum(t.get('pnl_net', 0) for t in trades) / len(trades):,.2f}")
        
        # Trade list
        for t in sorted(trades, key=lambda x: x.get('date', ''), reverse=True)[:20]:
            grade = t.get('grade', '-')
            grade_emoji = {"A": "🟢", "B": "🟡", "C": "🟠", "F": "🔴"}.get(grade, "⚪")
            pnl = t.get('pnl_net', 0)
            
            with st.expander(f"{t.get('date', 'N/A')} | {grade_emoji} | {t.get('symbol', '?')} {t.get('direction', '?')} | ${pnl:+,.2f}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Entry:** {t.get('entry_price', '-')} @ {t.get('entry_time', '-')}")
                    st.write(f"**Stop:** {t.get('stop_loss', '-')} | **TP:** {t.get('take_profit', '-')}")
                    st.write(f"**Contracts:** {t.get('position_size', 1)}")
                with col2:
                    st.write(f"**Emotional:** {t.get('emotional_state', '-')}/10")
                    st.write(f"**Would repeat:** {'✓' if t.get('would_repeat') else '✗'}")
                    if t.get('screenshot_url'):
                        st.write(f"[Screenshot]({t['screenshot_url']})")
                if t.get('notes'):
                    st.write(f"**Notes:** {t['notes']}")
    
    def edit_trades(self):
        st.subheader("Edit & Delete Trades")
        
        trades = self.data_storage.load_trades()
        
        if not trades:
            st.write("No trades to edit")
            return
        
        for i, t in enumerate(sorted(trades, key=lambda x: x.get('date', ''), reverse=True)[:15]):
            original_idx = next((j for j, tr in enumerate(trades) if tr.get('id') == t.get('id')), i)
            
            grade = t.get('grade', '-')
            grade_emoji = {"A": "🟢", "B": "🟡", "C": "🟠", "F": "🔴"}.get(grade, "⚪")
            
            with st.expander(f"✏️ {t.get('date', 'N/A')} | {grade_emoji} | ${t.get('pnl_net', 0):+,.2f}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_pnl = st.number_input("Net P&L", value=float(t.get('pnl_net', 0)), key=f"pnl_{original_idx}")
                    new_emotion = st.slider("Emotional", 1, 10, int(t.get('emotional_state', 5)), key=f"emo_{original_idx}")
                
                with col2:
                    new_notes = st.text_area("Notes", value=t.get('notes', ''), key=f"notes_{original_idx}")
                
                col1, col2 = st.columns(2)
                if col1.button("💾 Save", key=f"save_{original_idx}"):
                    old_pnl = t.get('pnl_net', 0)
                    trades[original_idx]['pnl_net'] = new_pnl
                    trades[original_idx]['pnl_gross'] = new_pnl + t.get('commission', 0)
                    trades[original_idx]['emotional_state'] = new_emotion
                    trades[original_idx]['notes'] = new_notes
                    trades[original_idx]['updated_at'] = datetime.now().isoformat()
                    self.data_storage.save_trades(trades)
                    
                    # Update account balance
                    if new_pnl != old_pnl:
                        accounts = self.data_storage.load_accounts()
                        for j, acc in enumerate(accounts):
                            if acc.get('account_number') == t.get('account_id'):
                                accounts[j]['current_balance'] = acc.get('current_balance', 0) + (new_pnl - old_pnl)
                                self.data_storage.save_accounts(accounts)
                                break
                    
                    st.success("Saved!")
                    st.rerun()
                
                if col2.button("🗑️ Delete", key=f"del_{original_idx}"):
                    # Reverse P&L
                    accounts = self.data_storage.load_accounts()
                    for j, acc in enumerate(accounts):
                        if acc.get('account_number') == t.get('account_id'):
                            accounts[j]['current_balance'] = acc.get('current_balance', 0) - t.get('pnl_net', 0)
                            self.data_storage.save_accounts(accounts)
                            break
                    
                    trades.pop(original_idx)
                    self.data_storage.save_trades(trades)
                    st.success("Deleted!")
                    st.rerun()
