import json
import os
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any

class DataStorage:
    def __init__(self, data_dir: str = "trading_data"):
        self.data_dir = data_dir
        self.ensure_data_directory()
        
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def save_json(self, filename: str, data: Any):
        """Save data to JSON file"""
        filepath = os.path.join(self.data_dir, f"{filename}.json")
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def load_json(self, filename: str, default: Any = None):
        """Load data from JSON file"""
        filepath = os.path.join(self.data_dir, f"{filename}.json")
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    content = f.read().strip()
                    if not content:  # Empty file
                        return default or []
                    return json.loads(content)
            except (json.JSONDecodeError, ValueError):
                # Corrupted file, return default and recreate
                return default or []
        return default or []
    
    # Prop Firms
    def save_prop_firms(self, prop_firms: List[Dict]):
        self.save_json("prop_firms", prop_firms)
    
    def load_prop_firms(self) -> List[Dict]:
        default_firms = [
            {
                "name": "Tradeify",
                "account_types": ["50K Growth", "100K Growth", "150K Growth"],
                "max_daily_loss": {"50K Growth": 2000, "100K Growth": 4000, "150K Growth": 6000},
                "max_total_loss": {"50K Growth": 3000, "100K Growth": 6000, "150K Growth": 9000},
                "profit_target": {"50K Growth": 3000, "100K Growth": 6000, "150K Growth": 9000},
                "payout_percentage": 80,
                "min_trading_days": 4
            },
            {
                "name": "TopOneFutures",
                "account_types": ["50K", "100K", "150K"],
                "max_daily_loss": {"50K": 2500, "100K": 5000, "150K": 7500},
                "max_total_loss": {"50K": 3000, "100K": 6000, "150K": 9000},
                "profit_target": {"50K": 3000, "100K": 6000, "150K": 9000},
                "payout_percentage": 80,
                "min_trading_days": 5
            },
            {
                "name": "TakeProfitTrader",
                "account_types": ["25K", "50K", "100K"],
                "max_daily_loss": {"25K": 1250, "50K": 2500, "100K": 5000},
                "max_total_loss": {"25K": 2000, "50K": 4000, "100K": 8000},
                "profit_target": {"25K": 1500, "50K": 3000, "100K": 6000},
                "payout_percentage": 80,
                "min_trading_days": 5,
                "special_features": ["Daily Payouts"]
            },
            {
                "name": "APEX",
                "account_types": ["300K"],
                "max_daily_loss": {"300K": 9000},
                "max_total_loss": {"300K": 15000},
                "profit_target": {"300K": 15000},
                "payout_percentage": 90,
                "min_trading_days": 10,
                "special_features": ["High Payout %", "Promo Discounts"]
            }
        ]
        return self.load_json("prop_firms", default_firms)
    
    # Accounts
    def save_accounts(self, accounts: List[Dict]):
        self.save_json("accounts", accounts)
    
    def load_accounts(self) -> List[Dict]:
        return self.load_json("accounts", [])
    
    # Playbooks
    def save_playbooks(self, playbooks: List[Dict]):
        self.save_json("playbooks", playbooks)
    
    def load_playbooks(self) -> List[Dict]:
        default_playbooks = [
            {
                "name": "Scalping Setup",
                "description": "High frequency scalping strategy",
                "rules": [
                    "Only trade during high volume hours (9:30-11:30, 1:30-3:30)",
                    "Maximum 3 trades per day",
                    "Risk/Reward minimum 1:1.5",
                    "Stop loss maximum 8 ticks",
                    "No trading if emotional state > 7/10"
                ],
                "max_position_size": {"first_trade": 200, "second_trade": 100, "third_trade": 100},
                "max_daily_loss": 400
            }
        ]
        return self.load_json("playbooks", default_playbooks)
    
    # Trades
    def save_trades(self, trades: List[Dict]):
        self.save_json("trades", trades)
    
    def load_trades(self) -> List[Dict]:
        return self.load_json("trades", [])
    
    def add_trade(self, trade: Dict):
        trades = self.load_trades()
        trade['id'] = len(trades) + 1
        trade['timestamp'] = datetime.now().isoformat()
        trades.append(trade)
        self.save_trades(trades)
    
    # Withdrawals
    def save_withdrawals(self, withdrawals: List[Dict]):
        self.save_json("withdrawals", withdrawals)
    
    def load_withdrawals(self) -> List[Dict]:
        return self.load_json("withdrawals", [])
    
    def add_withdrawal(self, withdrawal: Dict):
        withdrawals = self.load_withdrawals()
        withdrawal['id'] = len(withdrawals) + 1
        withdrawal['timestamp'] = datetime.now().isoformat()
        withdrawals.append(withdrawal)
        self.save_withdrawals(withdrawals)
    
    # Daily Check-ins (for trading psychology)
    def save_daily_checkins(self, checkins: List[Dict]):
        self.save_json("daily_checkins", checkins)
    
    def load_daily_checkins(self) -> List[Dict]:
        return self.load_json("daily_checkins", [])
    
    def add_daily_checkin(self, checkin: Dict):
        checkins = self.load_daily_checkins()
        checkin['id'] = len(checkins) + 1
        checkin['date'] = datetime.now().date().isoformat()
        checkin['timestamp'] = datetime.now().isoformat()
        checkins.append(checkin)
        self.save_daily_checkins(checkins)
    
    # Export data
    def export_to_csv(self, data_type: str) -> pd.DataFrame:
        """Export data to CSV format"""
        if data_type == "trades":
            data = self.load_trades()
        elif data_type == "accounts":
            data = self.load_accounts()
        elif data_type == "withdrawals":
            data = self.load_withdrawals()
        elif data_type == "checkins":
            data = self.load_daily_checkins()
        else:
            return pd.DataFrame()
        
        return pd.DataFrame(data)
    
    # Backup functionality
    def create_backup(self):
        """Create a backup of all data"""
        backup_data = {
            "prop_firms": self.load_prop_firms(),
            "accounts": self.load_accounts(),
            "playbooks": self.load_playbooks(),
            "trades": self.load_trades(),
            "withdrawals": self.load_withdrawals(),
            "daily_checkins": self.load_daily_checkins(),
            "backup_timestamp": datetime.now().isoformat()
        }
        
        backup_filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.save_json(backup_filename, backup_data)
        return backup_filename
    
    def restore_backup(self, backup_filename: str):
        """Restore data from backup"""
        backup_data = self.load_json(backup_filename.replace('.json', ''))
        if backup_data:
            self.save_prop_firms(backup_data.get("prop_firms", []))
            self.save_accounts(backup_data.get("accounts", []))
            self.save_playbooks(backup_data.get("playbooks", []))
            self.save_trades(backup_data.get("trades", []))
            self.save_withdrawals(backup_data.get("withdrawals", []))
            self.save_daily_checkins(backup_data.get("daily_checkins", []))
            return True
        return False