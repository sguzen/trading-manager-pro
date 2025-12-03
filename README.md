# Trading Manager Pro

A comprehensive Streamlit application for prop firm traders to track accounts, journal trades, manage psychology, and monitor progress toward withdrawal goals.

## Features

- **Account Management**: Track multiple prop firm accounts (Tradeify, TopOne, TPT, APEX, etc.)
- **Trade Journal**: Log trades with rule compliance tracking and performance analysis
- **Psychology Monitoring**: Daily check-ins and emotional state tracking
- **Performance Analytics**: Comprehensive charts and statistics
- **Goal Tracking**: Monitor progress toward $5M withdrawal target
- **Data Persistence**: All data saved locally in JSON format

## Installation

1. **Clone or download the files**
   - Save all Python files in the same directory
   - Create a new folder for your trading app

2. **Install requirements**
   ```bash
   pip install streamlit pandas plotly numpy
   ```

3. **Run the application**
   ```bash
   streamlit run main.py
   ```

## File Structure

```
trading_app/
├── main.py                 # Main Streamlit app
├── data_storage.py         # Data persistence layer
├── config_manager.py       # Configuration management
├── trade_journal.py        # Trade logging and journal
├── dashboard.py           # Performance analysis and charts
├── requirements.txt       # Python dependencies
├── trading_data/          # Data directory (auto-created)
│   ├── accounts.json
│   ├── trades.json
│   ├── withdrawals.json
│   └── daily_checkins.json
└── README.md
```

## Getting Started

1. **First Run**
   - The app will create a `trading_data` folder automatically
   - Default prop firms (Tradeify, TopOne, TPT, APEX) are pre-configured

2. **Configuration**
   - Go to Configuration tab
   - Add your accounts under "Accounts" tab
   - Create trading playbooks with your rules

3. **Daily Routine**
   - Complete daily check-in before trading
   - Log each trade with rule compliance
   - Review performance in Dashboard

## Key Trading Manager Features

### Daily Check-in System
- Sleep quality assessment
- Stress level monitoring
- Alcohol consumption tracking
- Trading clearance based on psychological state

### Rule Compliance Tracking
- Custom playbook creation with specific rules
- Trade-by-trade rule adherence logging
- Performance correlation with rule following

### Account Scaling Path
- Track evaluation → funded → payout progression
- Monitor multiple prop firms simultaneously
- Withdrawal tracking with reinvestment planning

### Psychology Integration
- Emotional state impact on performance
- Stress correlation analysis
- Self-sabotage pattern detection

## Data Security

- All data stored locally in JSON files
- No cloud storage or external dependencies
- Easy backup/restore functionality built-in
- Export to CSV available for external analysis

## Trading Manager Protocol Integration

The app implements the trading manager protocol from your brief:

### Pre-Market Check-ins
- ✅ Sleep quality (1-10)
- ✅ Stress level (1-10)
- ✅ Alcohol consumption (Y/N)
- ✅ Exercise status
- ✅ Home stress level (1-10)
- ✅ Trading plan documentation

### Risk Management
- ✅ Daily loss limits per account
- ✅ Position sizing enforcement
- ✅ Trade count limitations
- ✅ Emotional state thresholds

### Pattern Recognition
- ✅ Rule violation tracking
- ✅ Emotional trading detection
- ✅ Success/self-sabotage cycle monitoring
- ✅ Performance correlation analysis

## Customization

The app is designed to be easily customizable:

- **Add new prop firms**: Modify the default firms in `data_storage.py`
- **Custom rules**: Create unlimited playbooks with specific rule sets
- **New metrics**: Add fields to trade logging in `trade_journal.py`
- **Different goals**: Change the $5M target in dashboard calculations

## Backup and Recovery

- Use the built-in backup functionality in the app
- Backup files are timestamped JSON files
- Copy the entire `trading_data` folder for manual backups
- Restore from any backup file through the interface

## Troubleshooting

**App won't start:**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that all Python files are in the same directory
- Run with: `streamlit run main.py`

**Data not saving:**
- Check write permissions in the app directory
- Ensure `trading_data` folder can be created
- Look for error messages in the Streamlit console

**Performance issues:**
- Large trade datasets may slow the app
- Consider exporting old data and starting fresh periodically
- Use date filters in analysis to limit data processing

## Support

This is your personal trading manager application. Modify it as needed for your specific requirements and trading style. The modular design makes it easy to add new features or customize existing ones.

Remember: The goal is consistent profitability and psychological discipline, not just tracking. Use this tool to identify and break self-sabotage patterns while scaling toward your $1M annual payout target.