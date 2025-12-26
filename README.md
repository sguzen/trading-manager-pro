# Trading Manager Pro 📈

Trading journal with **real-time trade grading** for prop firm traders.

## Features

- **Live Trade Grader** (sidebar) - Grade setups in real-time as conditions appear
- **Custom Grading Rules** - Define your own A/B/C/F criteria  
- **Position Sizing by Grade** - Automatic size recommendations
- **Multi-Account Tracking** - Manage multiple prop firm accounts
- **Daily Check-ins** - Pre-market psychological assessment
- **Performance Analytics** - P&L by grade, emotional state correlations
- **Debt/Goal Tracking** - Track payoff progress

## Quick Start

```bash
pip install -r requirements.txt
streamlit run main.py
```

## First Steps

1. **Settings > Grade Rules** - Create your setup checklist
2. **Settings > Position Sizing** - Define contracts per grade
3. **Configuration > Accounts** - Add your prop firm accounts
4. **Use the Live Trade Grader** in the sidebar when trading!

## Files

- `main.py` - Main app
- `live_trade.py` - Real-time grading sidebar
- `settings_manager.py` - Rules & sizing config
- `config_manager.py` - Accounts, firms, withdrawals
- `trade_journal.py` - History & daily check-ins
- `dashboard.py` - Performance analytics
- `data_storage.py` - JSON persistence

Data stored in `trading_data/` (gitignored).
