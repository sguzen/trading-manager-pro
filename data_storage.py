import json
import os
import pandas as pd
from datetime import datetime, date
from typing import Dict, List, Optional

class DataStorage:
    """Handles all data persistence using JSON files"""
    
    def __init__(self, data_dir: str = "trading_data"):
        self.data_dir = data_dir
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def _get_filepath(self, filename: str) -> str:
        """Get full filepath for a data file"""
        return os.path.join(self.data_dir, filename)
    
    def _save_json(self, filename: str, data: any):
        """Save data to a JSON file"""
        filepath = self._get_filepath(filename)
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving {filename}: {e}")
    
    def _load_json(self, filename: str, default: any = None) -> any:
        """Load data from a JSON file"""
        filepath = self._get_filepath(filename)
        if not os.path.exists(filepath):
            return default if default is not None else []
        
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return default if default is not None else []
    
    # Prop Firms
    def load_prop_firms(self) -> List[Dict]:
        return self._load_json("prop_firms.json", [])
    
    def save_prop_firms(self, firms: List[Dict]):
        self._save_json("prop_firms.json", firms)
    
    def add_prop_firm(self, firm: Dict):
        firms = self.load_prop_firms()
        firm['id'] = len(firms) + 1
        firm['created_at'] = datetime.now().isoformat()
        firms.append(firm)
        self.save_prop_firms(firms)
        return firm
    
    # Accounts
    def load_accounts(self) -> List[Dict]:
        return self._load_json("accounts.json", [])
    
    def save_accounts(self, accounts: List[Dict]):
        self._save_json("accounts.json", accounts)
    
    def add_account(self, account: Dict):
        accounts = self.load_accounts()
        account['id'] = len(accounts) + 1
        account['created_at'] = datetime.now().isoformat()
        account['updated_at'] = datetime.now().isoformat()
        accounts.append(account)
        self.save_accounts(accounts)
        return account
    
    def update_account_balance(self, account_name: str, new_balance: float):
        accounts = self.load_accounts()
        for acc in accounts:
            if acc['name'] == account_name:
                acc['balance'] = new_balance
                acc['updated_at'] = datetime.now().isoformat()
                break
        self.save_accounts(accounts)
    
    # Playbooks
    def load_playbooks(self) -> List[Dict]:
        return self._load_json("playbooks.json", [])
    
    def save_playbooks(self, playbooks: List[Dict]):
        self._save_json("playbooks.json", playbooks)
    
    def add_playbook(self, playbook: Dict):
        playbooks = self.load_playbooks()
        playbook['id'] = len(playbooks) + 1
        playbook['created_at'] = datetime.now().isoformat()
        playbooks.append(playbook)
        self.save_playbooks(playbooks)
        return playbook
    
    # Trades
    def load_trades(self) -> List[Dict]:
        return self._load_json("trades.json", [])
    
    def save_trades(self, trades: List[Dict]):
        self._save_json("trades.json", trades)
    
    def add_trade(self, trade: Dict):
        trades = self.load_trades()
        trade['id'] = len(trades) + 1
        trade['timestamp'] = datetime.now().isoformat()
        trades.append(trade)
        self.save_trades(trades)
        return trade
    
    def get_trades_by_account(self, account_name: str) -> List[Dict]:
        trades = self.load_trades()
        return [t for t in trades if t.get('account') == account_name]
    
    def get_trades_by_playbook(self, playbook_name: str) -> List[Dict]:
        trades = self.load_trades()
        return [t for t in trades if t.get('playbook') == playbook_name]
    
    def get_trades_by_grade(self, grade: str) -> List[Dict]:
        trades = self.load_trades()
        return [t for t in trades if t.get('grade') == grade]
    
    def get_trades_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        trades = self.load_trades()
        return [t for t in trades if start_date <= t.get('date', '') <= end_date]
    
    # Withdrawals
    def load_withdrawals(self) -> List[Dict]:
        return self._load_json("withdrawals.json", [])
    
    def save_withdrawals(self, withdrawals: List[Dict]):
        self._save_json("withdrawals.json", withdrawals)
    
    def add_withdrawal(self, withdrawal: Dict):
        withdrawals = self.load_withdrawals()
        withdrawal['id'] = len(withdrawals) + 1
        withdrawal['timestamp'] = datetime.now().isoformat()
        withdrawals.append(withdrawal)
        self.save_withdrawals(withdrawals)
        return withdrawal
    
    # Daily Check-ins
    def load_checkins(self) -> List[Dict]:
        return self._load_json("daily_checkins.json", [])
    
    def save_checkins(self, checkins: List[Dict]):
        self._save_json("daily_checkins.json", checkins)
    
    def add_checkin(self, checkin: Dict):
        checkins = self.load_checkins()
        checkin['id'] = len(checkins) + 1
        checkin['timestamp'] = datetime.now().isoformat()
        checkins.append(checkin)
        self.save_checkins(checkins)
        return checkin
    
    def get_today_checkin(self) -> Optional[Dict]:
        checkins = self.load_checkins()
        today = date.today().isoformat()
        for c in checkins:
            if c.get('date') == today:
                return c
        return None
    
    # Analytics helpers
    def get_performance_summary(self) -> Dict:
        """Get overall performance metrics"""
        trades = self.load_trades()
        withdrawals = self.load_withdrawals()
        
        if not trades:
            return {
                "total_trades": 0,
                "total_pnl": 0,
                "win_rate": 0,
                "avg_win": 0,
                "avg_loss": 0,
                "total_withdrawn": 0
            }
        
        winning = [t for t in trades if t.get('pnl', 0) > 0]
        losing = [t for t in trades if t.get('pnl', 0) < 0]
        
        return {
            "total_trades": len(trades),
            "total_pnl": sum(t.get('pnl', 0) for t in trades),
            "win_rate": len(winning) / len(trades) * 100 if trades else 0,
            "avg_win": sum(t.get('pnl', 0) for t in winning) / len(winning) if winning else 0,
            "avg_loss": sum(t.get('pnl', 0) for t in losing) / len(losing) if losing else 0,
            "total_withdrawn": sum(w.get('amount', 0) for w in withdrawals),
            "grade_a_trades": len([t for t in trades if t.get('grade') == 'A']),
            "grade_b_trades": len([t for t in trades if t.get('grade') == 'B']),
            "grade_c_trades": len([t for t in trades if t.get('grade') == 'C']),
            "rule_violations": len([t for t in trades if t.get('grade') == 'F'])
        }
    
    def get_grade_performance(self) -> Dict:
        """Get performance broken down by trade grade"""
        trades = self.load_trades()
        
        result = {}
        for grade in ['A', 'B', 'C', 'F']:
            grade_trades = [t for t in trades if t.get('grade') == grade]
            if grade_trades:
                wins = [t for t in grade_trades if t.get('pnl', 0) > 0]
                result[grade] = {
                    "count": len(grade_trades),
                    "total_pnl": sum(t.get('pnl', 0) for t in grade_trades),
                    "win_rate": len(wins) / len(grade_trades) * 100,
                    "avg_pnl": sum(t.get('pnl', 0) for t in grade_trades) / len(grade_trades)
                }
            else:
                result[grade] = {"count": 0, "total_pnl": 0, "win_rate": 0, "avg_pnl": 0}
        
        return result
    
    # Export functionality
    def export_to_csv(self, data_type: str) -> pd.DataFrame:
        """Export data to CSV format"""
        data_map = {
            "trades": self.load_trades,
            "accounts": self.load_accounts,
            "withdrawals": self.load_withdrawals,
            "checkins": self.load_checkins,
            "playbooks": self.load_playbooks,
            "prop_firms": self.load_prop_firms
        }
        
        if data_type not in data_map:
            return pd.DataFrame()
        
        data = data_map[data_type]()
        return pd.DataFrame(data)
    
    # Backup functionality
    def create_backup(self) -> str:
        """Create a backup of all data"""
        backup_data = {
            "prop_firms": self.load_prop_firms(),
            "accounts": self.load_accounts(),
            "playbooks": self.load_playbooks(),
            "trades": self.load_trades(),
            "withdrawals": self.load_withdrawals(),
            "daily_checkins": self.load_checkins(),
            "backup_timestamp": datetime.now().isoformat()
        }
        
        backup_filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self._save_json(backup_filename, backup_data)
        return backup_filename
    
    def restore_backup(self, backup_filename: str) -> bool:
        """Restore data from a backup file"""
        try:
            backup_data = self._load_json(backup_filename)
            if not backup_data:
                return False
            
            if "prop_firms" in backup_data:
                self.save_prop_firms(backup_data["prop_firms"])
            if "accounts" in backup_data:
                self.save_accounts(backup_data["accounts"])
            if "playbooks" in backup_data:
                self.save_playbooks(backup_data["playbooks"])
            if "trades" in backup_data:
                self.save_trades(backup_data["trades"])
            if "withdrawals" in backup_data:
                self.save_withdrawals(backup_data["withdrawals"])
            if "daily_checkins" in backup_data:
                self.save_checkins(backup_data["daily_checkins"])
            
            return True
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False
