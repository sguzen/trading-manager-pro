import json
import os
from datetime import datetime, date
from typing import Dict, List, Any

class DataStorage:
    def __init__(self, data_dir: str = "trading_data"):
        self.data_dir = data_dir
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def _get_path(self, filename: str) -> str:
        return os.path.join(self.data_dir, filename)
    
    def _load_json(self, filename: str) -> List[Dict]:
        path = self._get_path(filename)
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []
    
    def _save_json(self, filename: str, data: Any):
        path = self._get_path(filename)
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    # Settings
    def load_settings(self) -> Dict:
        path = self._get_path("settings.json")
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return self._default_settings()
        return self._default_settings()
    
    def _default_settings(self) -> Dict:
        return {
            "debt_amount": 5000.0,
            "debt_name": "Trading Loan",
            "goal_amount": 1000000.0,
            "must_have_rules": [],  # Rules that ALL must be checked (or F-grade)
            "bonus_rules": [],      # Rules that determine A/B/C grade
            "grade_thresholds": {
                "A": 80,   # % of bonus rules for A-grade
                "B": 50,   # % of bonus rules for B-grade
                "C": 0     # Below B = C-grade
            },
            "position_sizing": {
                "A": {"drawdown_pct": 50, "label": "Full Size"},
                "B": {"drawdown_pct": 30, "label": "Reduced"},
                "C": {"drawdown_pct": 15, "label": "Minimum"},
                "F": {"drawdown_pct": 0, "label": "NO TRADE"}
            }
        }
    
    def save_settings(self, settings: Dict):
        self._save_json("settings.json", settings)
    
    # Prop Firms
    def load_prop_firms(self) -> List[Dict]:
        return self._load_json("prop_firms.json")
    
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
        return self._load_json("accounts.json")
    
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
    
    # Playbooks
    def load_playbooks(self) -> List[Dict]:
        return self._load_json("playbooks.json")
    
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
        return self._load_json("trades.json")
    
    def save_trades(self, trades: List[Dict]):
        self._save_json("trades.json", trades)
    
    def add_trade(self, trade: Dict):
        trades = self.load_trades()
        trade['id'] = len(trades) + 1
        trade['timestamp'] = datetime.now().isoformat()
        trades.append(trade)
        self.save_trades(trades)
        return trade
    
    # Withdrawals
    def load_withdrawals(self) -> List[Dict]:
        return self._load_json("withdrawals.json")
    
    def save_withdrawals(self, withdrawals: List[Dict]):
        self._save_json("withdrawals.json", withdrawals)
    
    def add_withdrawal(self, withdrawal: Dict):
        withdrawals = self.load_withdrawals()
        withdrawal['id'] = len(withdrawals) + 1
        withdrawal['timestamp'] = datetime.now().isoformat()
        withdrawals.append(withdrawal)
        self.save_withdrawals(withdrawals)
        return withdrawal
    
    # Daily Check-ins (old - kept for compatibility)
    def load_daily_checkins(self) -> List[Dict]:
        return self._load_json("daily_checkins.json")
    
    def save_daily_checkins(self, checkins: List[Dict]):
        self._save_json("daily_checkins.json", checkins)
    
    def add_daily_checkin(self, checkin: Dict):
        checkins = self.load_daily_checkins()
        checkin['id'] = len(checkins) + 1
        checkin['date'] = date.today().isoformat()
        checkin['timestamp'] = datetime.now().isoformat()
        checkins.append(checkin)
        self.save_daily_checkins(checkins)
        return checkin
    
    # Daily Entries (new - plan & review)
    def load_daily_entries(self) -> List[Dict]:
        return self._load_json("daily_entries.json")
    
    def save_daily_entries(self, entries: List[Dict]):
        self._save_json("daily_entries.json", entries)
    
    # Export/Import
    def export_all_data(self) -> Dict:
        return {
            "settings": self.load_settings(),
            "prop_firms": self.load_prop_firms(),
            "accounts": self.load_accounts(),
            "playbooks": self.load_playbooks(),
            "trades": self.load_trades(),
            "withdrawals": self.load_withdrawals(),
            "daily_checkins": self.load_daily_checkins(),
            "exported_at": datetime.now().isoformat()
        }
    
    def import_data(self, data: Dict):
        if "settings" in data:
            self.save_settings(data["settings"])
        if "prop_firms" in data:
            self.save_prop_firms(data["prop_firms"])
        if "accounts" in data:
            self.save_accounts(data["accounts"])
        if "playbooks" in data:
            self.save_playbooks(data["playbooks"])
        if "trades" in data:
            self.save_trades(data["trades"])
        if "withdrawals" in data:
            self.save_withdrawals(data["withdrawals"])
        if "daily_checkins" in data:
            self.save_daily_checkins(data["daily_checkins"])
