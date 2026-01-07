import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import json
from typing import Dict, Optional, List

class PsychologicalManager:
    """
    Manages daily psychological check-ins and trading clearance status.
    Prevents trading when psychological state is unsafe.
    """
    
    def __init__(self, data_storage):
        self.data_storage = data_storage
        self.risk_thresholds = {
            'sleep_min': 6,  # Minimum hours of sleep
            'stress_max': 7,  # Maximum stress level (1-10)
            'emotional_max': 7,  # Maximum emotional level (1-10)
            'home_stress_max': 7  # Maximum home stress (1-10)
        }
    
    def get_todays_checkin(self) -> Optional[Dict]:
        """Get today's psychological check-in if it exists."""
        checkins = self.data_storage.load_data('psychological_checkins')
        today = date.today().isoformat()
        return next((c for c in checkins if c['date'] == today), None)
    
    def save_checkin(self, checkin_data: Dict) -> bool:
        """Save a daily psychological check-in."""
        checkins = self.data_storage.load_data('psychological_checkins')
        today = date.today().isoformat()
        
        # Remove any existing check-in for today
        checkins = [c for c in checkins if c['date'] != today]
        
        # Add new check-in
        checkin_data['date'] = today
        checkin_data['timestamp'] = datetime.now().isoformat()
        checkins.append(checkin_data)
        
        return self.data_storage.save_data('psychological_checkins', checkins)
    
    def calculate_risk_level(self, checkin: Dict) -> str:
        """
        Calculate trading risk level based on psychological state.
        Returns: 'GREEN', 'YELLOW', or 'RED'
        """
        red_flags = []
        yellow_flags = []
        
        # Critical red flags (immediate trading ban)
        if checkin.get('alcohol_consumed', False):
            red_flags.append("Alcohol consumed in last 24hrs")
        
        if checkin.get('sleep_hours', 0) < self.risk_thresholds['sleep_min']:
            red_flags.append(f"Insufficient sleep ({checkin.get('sleep_hours', 0)}hrs < {self.risk_thresholds['sleep_min']}hrs)")
        
        if checkin.get('stress_level', 0) > self.risk_thresholds['stress_max']:
            red_flags.append(f"Stress level too high ({checkin.get('stress_level', 0)}/10)")
        
        if checkin.get('emotional_state', 0) > self.risk_thresholds['emotional_max']:
            red_flags.append(f"Emotional state too high ({checkin.get('emotional_state', 0)}/10)")
        
        # Yellow flags (proceed with extreme caution)
        if checkin.get('sleep_hours', 0) < 7:
            yellow_flags.append(f"Below optimal sleep ({checkin.get('sleep_hours', 0)}hrs)")
        
        if checkin.get('home_stress', 0) > self.risk_thresholds['home_stress_max']:
            yellow_flags.append(f"High home stress ({checkin.get('home_stress', 0)}/10)")
        
        if not checkin.get('exercise_done', False):
            yellow_flags.append("No exercise/movement today")
        
        if checkin.get('stress_level', 0) >= 5:
            yellow_flags.append(f"Moderate stress level ({checkin.get('stress_level', 0)}/10)")
        
        # Determine final risk level
        if red_flags:
            return 'RED', red_flags, yellow_flags
        elif len(yellow_flags) >= 2:
            return 'YELLOW', red_flags, yellow_flags
        else:
            return 'GREEN', red_flags, yellow_flags
    
    def get_trading_clearance(self) -> Dict:
        """
        Get current trading clearance status.
        Returns dict with status and reasoning.
        """
        checkin = self.get_todays_checkin()
        
        if not checkin:
            return {
                'cleared': False,
                'status': 'NO_CHECKIN',
                'message': '⚠️ No check-in completed today. Complete your daily check-in before trading.',
                'color': 'red',
                'red_flags': ['No daily check-in completed'],
                'yellow_flags': []
            }
        
        risk_level, red_flags, yellow_flags = self.calculate_risk_level(checkin)
        
        if risk_level == 'RED':
            return {
                'cleared': False,
                'status': 'RED',
                'message': '🚫 TRADING BLOCKED - Critical risk factors present',
                'color': 'red',
                'red_flags': red_flags,
                'yellow_flags': yellow_flags
            }
        elif risk_level == 'YELLOW':
            return {
                'cleared': True,
                'status': 'YELLOW',
                'message': '⚠️ PROCEED WITH CAUTION - Multiple risk factors present',
                'color': 'orange',
                'red_flags': red_flags,
                'yellow_flags': yellow_flags,
                'restrictions': ['Max 1 trade today', 'Reduce position sizes by 50%', 'No revenge trading']
            }
        else:
            return {
                'cleared': True,
                'status': 'GREEN',
                'message': '✅ CLEARED FOR TRADING - All systems go',
                'color': 'green',
                'red_flags': red_flags,
                'yellow_flags': yellow_flags
            }
    
    def get_recent_pattern_analysis(self, days: int = 7) -> Dict:
        """Analyze psychological patterns over recent days."""
        checkins = self.data_storage.load_data('psychological_checkins')
        
        # Get last N days
        cutoff_date = (date.today() - timedelta(days=days)).isoformat()
        recent = [c for c in checkins if c['date'] >= cutoff_date]
        recent.sort(key=lambda x: x['date'])
        
        if not recent:
            return {'days_analyzed': 0}
        
        # Calculate averages
        avg_sleep = sum(c.get('sleep_hours', 0) for c in recent) / len(recent)
        avg_stress = sum(c.get('stress_level', 0) for c in recent) / len(recent)
        avg_emotional = sum(c.get('emotional_state', 0) for c in recent) / len(recent)
        
        # Count flags
        red_days = sum(1 for c in recent if self.calculate_risk_level(c)[0] == 'RED')
        yellow_days = sum(1 for c in recent if self.calculate_risk_level(c)[0] == 'YELLOW')
        green_days = sum(1 for c in recent if self.calculate_risk_level(c)[0] == 'GREEN')
        
        alcohol_days = sum(1 for c in recent if c.get('alcohol_consumed', False))
        exercise_days = sum(1 for c in recent if c.get('exercise_done', False))
        
        return {
            'days_analyzed': len(recent),
            'avg_sleep': round(avg_sleep, 1),
            'avg_stress': round(avg_stress, 1),
            'avg_emotional': round(avg_emotional, 1),
            'red_days': red_days,
            'yellow_days': yellow_days,
            'green_days': green_days,
            'alcohol_days': alcohol_days,
            'exercise_days': exercise_days,
            'sleep_trend': 'improving' if len(recent) > 1 and recent[-1].get('sleep_hours', 0) > avg_sleep else 'declining'
        }
    
    def show_daily_checkin_form(self):
        """Display the daily psychological check-in form."""
        st.header("🧠 Daily Psychological Check-In")
        
        # Check if already completed today
        existing_checkin = self.get_todays_checkin()
        
        if existing_checkin:
            st.info(f"✅ Check-in already completed today at {existing_checkin.get('timestamp', 'unknown time')}")
            if st.button("Update Today's Check-In"):
                existing_checkin = None
        
        st.markdown("**Complete this BEFORE opening any trading platform**")
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Physical State")
            
            sleep_hours = st.slider(
                "Hours of Sleep",
                min_value=0.0,
                max_value=12.0,
                value=existing_checkin.get('sleep_hours', 7.0) if existing_checkin else 7.0,
                step=0.5,
                help="Minimum 6 hours required for trading clearance"
            )
            
            exercise_done = st.checkbox(
                "Exercise/Movement Done Today",
                value=existing_checkin.get('exercise_done', False) if existing_checkin else False,
                help="Any physical activity: gym, walk, stretching"
            )
            
            alcohol_consumed = st.checkbox(
                "Alcohol Consumed (Last 24hrs)",
                value=existing_checkin.get('alcohol_consumed', False) if existing_checkin else False,
                help="⚠️ ANY alcohol = automatic trading ban"
            )
        
        with col2:
            st.subheader("Mental State")
            
            stress_level = st.slider(
                "Stress Level",
                min_value=1,
                max_value=10,
                value=existing_checkin.get('stress_level', 5) if existing_checkin else 5,
                help="1=Zen, 10=Overwhelmed. Max 7 for trading."
            )
            
            emotional_state = st.slider(
                "Emotional State",
                min_value=1,
                max_value=10,
                value=existing_checkin.get('emotional_state', 5) if existing_checkin else 5,
                help="1=Calm, 10=Highly Emotional. Max 7 for trading."
            )
            
            home_stress = st.slider(
                "Home Stress Level",
                min_value=1,
                max_value=10,
                value=existing_checkin.get('home_stress', 5) if existing_checkin else 5,
                help="Marriage/family stress level"
            )
        
        st.markdown("---")
        
        trading_plan = st.text_area(
            "Trading Plan for Today",
            value=existing_checkin.get('trading_plan', '') if existing_checkin else '',
            placeholder="What setups are you looking for? What accounts will you trade? What's your max loss tolerance today?",
            height=100
        )
        
        notes = st.text_area(
            "Additional Notes/Concerns",
            value=existing_checkin.get('notes', '') if existing_checkin else '',
            placeholder="Anything on your mind? Concerns? Distractions?",
            height=80
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            if st.button("Submit Check-In", type="primary", use_container_width=True):
                checkin_data = {
                    'sleep_hours': sleep_hours,
                    'exercise_done': exercise_done,
                    'alcohol_consumed': alcohol_consumed,
                    'stress_level': stress_level,
                    'emotional_state': emotional_state,
                    'home_stress': home_stress,
                    'trading_plan': trading_plan,
                    'notes': notes
                }
                
                if self.save_checkin(checkin_data):
                    st.success("✅ Check-in saved successfully!")
                    st.rerun()
                else:
                    st.error("❌ Error saving check-in")
    
    def show_clearance_dashboard(self):
        """Display current trading clearance status."""
        st.header("🚦 Trading Clearance Status")
        
        clearance = self.get_trading_clearance()
        
        # Status card
        status_color = clearance['color']
        if status_color == 'green':
            bg_color = '#d1fae5'
            border_color = '#10b981'
        elif status_color == 'orange':
            bg_color = '#fef3c7'
            border_color = '#f59e0b'
        else:
            bg_color = '#fee2e2'
            border_color = '#ef4444'
        
        st.markdown(
            f"""
            <div style="
                background-color: {bg_color};
                border-left: 5px solid {border_color};
                padding: 20px;
                border-radius: 5px;
                margin-bottom: 20px;
            ">
                <h2 style="margin: 0; color: {border_color};">{clearance['message']}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Display flags
        col1, col2 = st.columns(2)
        
        with col1:
            if clearance['red_flags']:
                st.error("**🚫 Critical Issues (Trading Blocked)**")
                for flag in clearance['red_flags']:
                    st.markdown(f"- {flag}")
        
        with col2:
            if clearance['yellow_flags']:
                st.warning("**⚠️ Caution Flags**")
                for flag in clearance['yellow_flags']:
                    st.markdown(f"- {flag}")
        
        # Restrictions if yellow status
        if clearance['status'] == 'YELLOW' and 'restrictions' in clearance:
            st.info("**📋 Trading Restrictions for Today:**")
            for restriction in clearance['restrictions']:
                st.markdown(f"- {restriction}")
        
        # Pattern analysis
        st.markdown("---")
        st.subheader("📊 7-Day Pattern Analysis")
        
        patterns = self.get_recent_pattern_analysis(7)
        
        if patterns['days_analyzed'] > 0:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Avg Sleep", f"{patterns['avg_sleep']} hrs", 
                         delta="Good" if patterns['avg_sleep'] >= 7 else "Low")
            
            with col2:
                st.metric("Avg Stress", f"{patterns['avg_stress']}/10",
                         delta="High" if patterns['avg_stress'] > 6 else "OK")
            
            with col3:
                st.metric("Green Days", f"{patterns['green_days']}/{patterns['days_analyzed']}")
            
            with col4:
                st.metric("Red Days", f"{patterns['red_days']}/{patterns['days_analyzed']}",
                         delta="Warning" if patterns['red_days'] > 2 else None)
            
            # Additional insights
            st.markdown("**Weekly Summary:**")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"- Exercise days: {patterns['exercise_days']}/{patterns['days_analyzed']}")
                st.markdown(f"- Alcohol days: {patterns['alcohol_days']}/{patterns['days_analyzed']}")
            
            with col2:
                st.markdown(f"- Sleep trend: {patterns['sleep_trend'].upper()}")
                st.markdown(f"- Avg emotional state: {patterns['avg_emotional']}/10")
        else:
            st.info("No check-in data available yet. Complete daily check-ins to see patterns.")
    
    def show_history(self):
        """Show historical check-ins and patterns."""
        st.header("📅 Check-In History")
        
        checkins = self.data_storage.load_data('psychological_checkins')
        
        if not checkins:
            st.info("No check-in history yet.")
            return
        
        # Convert to dataframe
        df = pd.DataFrame(checkins)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date', ascending=False)
        
        # Add risk level column
        df['risk_level'] = df.apply(
            lambda row: self.calculate_risk_level(row.to_dict())[0],
            axis=1
        )
        
        # Display
        st.dataframe(
            df[['date', 'sleep_hours', 'stress_level', 'emotional_state', 
                'alcohol_consumed', 'exercise_done', 'risk_level']],
            use_container_width=True
        )
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Sleep Trend")
            st.line_chart(df.set_index('date')['sleep_hours'])
        
        with col2:
            st.subheader("Stress Level Trend")
            st.line_chart(df.set_index('date')['stress_level'])
