# Trading Manager Pro

A Streamlit-based trading journal and performance tracker for prop firm traders.

## Features

- **Multi-Account Management**: Track multiple prop firm accounts (Tradeify, TPT, TopOne, APEX, etc.)
- **Playbook System with A/B/C Grading**: Define setups with hierarchical quality grades
- **Trade Journal**: Log trades with automatic grade calculation
- **Psychology Tracking**: Daily pre-market check-ins with trading approval system
- **Performance Analytics**: Equity curves, grade performance, emotional analysis
- **Withdrawal Tracking**: Track progress toward $1M goal with loan repayment

## Setup Grading System

Each playbook uses a hierarchical grading system with mandatory/optional rules:

### Rule Types

- **🔒 Mandatory**: Affects the grade calculation. Missing a mandatory rule impacts your grade.
- **📝 Optional**: Tracked for analysis but doesn't affect the grade. Use for refining your edge over time.

### Grade Tiers

### 🔴 C Setup (Minimum)
The absolute must-have criteria. If ANY **mandatory** C rule is missing, the trade is marked as **F (Failed)**.

Example C rules:
- 🔒 Market structure break confirmed (mandatory)
- 🔒 Fair value gap present (mandatory)
- 📝 Clean candle close (optional - tracking for refinement)

### 🟡 B Setup (Better)
All mandatory C rules met PLUS all mandatory B criteria.

Example B rules:
- 🔒 Clean 50% retracement (mandatory)
- 🔒 Liquidity swept before entry (mandatory)
- 📝 Volume confirmation (optional)

### 🟢 A Setup (Best)
All mandatory C + B rules met PLUS all mandatory A criteria.

Example A rules:
- 🔒 HTF confluence (4H or Daily) (mandatory)
- 📝 Previous session high/low taken (optional - testing if it adds edge)

### Grade Calculation

| Grade | Requirements |
|-------|-------------|
| **A** | All mandatory C + B + A rules met |
| **B** | All mandatory C + B rules met |
| **C** | All mandatory C rules met |
| **F** | Any mandatory C rule NOT met (rule violation) |

**Note:** Optional rules are always tracked and stored, allowing you to later analyze if certain optional criteria correlate with higher win rates. This helps refine your playbook over time without affecting current grades.

## Installation

```bash
pip install -r requirements.txt
streamlit run main.py
```

## File Structure

```
trading_manager_pro/
├── main.py              # App entry point
├── data_storage.py      # JSON persistence
├── config_manager.py    # Prop firms, accounts, playbooks
├── trade_journal.py     # Trade logging, check-ins
├── dashboard.py         # Performance analytics
├── requirements.txt     # Dependencies
└── trading_data/        # Auto-created data folder
```

## Usage

1. **Configuration → Prop Firms**: Add your prop firms and their rules
2. **Configuration → Accounts**: Add your trading accounts
3. **Configuration → Playbooks**: Create playbooks with A/B/C graded rules
4. **Trade Journal → Daily Check-in**: Complete pre-market assessment
5. **Trade Journal → Log Trade**: Journal trades with rule compliance
6. **Performance Analysis**: Review grade-based performance

## Pre-Market Check-in Rules

Trading is blocked if:
- Alcohol consumed in last 24 hours
- Stress level ≥ 7
- Sleep quality ≤ 4

## Path to $1M

1. Prove consistency with current 50K Tradeify account
2. Extract first payouts and repay $5K loan
3. Scale to 150K accounts (Tradeify/TopOne)
4. Add TPT for daily payout capability
5. Accumulate 20x 300K APEX accounts during 90% promos

## License

MIT
