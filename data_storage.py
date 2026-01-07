import json
import os
from typing import Dict, List, Any
from datetime import datetime

class DataStorage:
    """
    Handles all data persistence for the Trading Manager Pro application.
    Uses JSON files for simple, human-readable storage.
    """
    
    def __init__(self, data_dir: str = "trading_data"):
        self.data_dir = data_dir
        self.ensure_data_directory()
        
        # Define all data files
        self.data_files = {
            'prop_firms': 'prop_firms.json',
            'accounts': 'accounts.json',
            'playbooks': 'playbooks.json',
            'trades': 'trades.json',
            'withdrawals': 'withdrawals.json',
            'psychological_checkins': 'psychological_checkins.json',  # NEW
            'config': 'config.json'
        }
        
        self.ensure_data_files()
    
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def ensure_data_files(self):
        """Create empty data files if they don't exist."""
        for data_type, filename in self.data_files.items():
            filepath = os.path.join(self.data_dir, filename)
            if not os.path.exists(filepath):
                self.save_data(data_type, [])
    
    def get_filepath(self, data_type: str) -> str:
        """Get the full filepath for a data type."""
        if data_type not in self.data_files:
            raise ValueError(f"Unknown data type: {data_type}")
        return os.path.join(self.data_dir, self.data_files[data_type])
    
    def load_data(self, data_type: str) -> List[Dict]:
        """Load data from JSON file."""
        filepath = self.get_filepath(data_type)
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_data(self, data_type: str, data: List[Dict]) -> bool:
        """Save data to JSON file."""
        filepath = self.get_filepath(data_type)
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def backup_all_data(self, backup_dir: str = None) -> str:
        """
        Create a backup of all data files.
        Returns the backup directory path.
        """
        if backup_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join(self.data_dir, f"backup_{timestamp}")
        
        os.makedirs(backup_dir, exist_ok=True)
        
        for data_type, filename in self.data_files.items():
            source = self.get_filepath(data_type)
            dest = os.path.join(backup_dir, filename)
            
            if os.path.exists(source):
                with open(source, 'r') as src_file:
                    with open(dest, 'w') as dst_file:
                        dst_file.write(src_file.read())
        
        return backup_dir
    
    def restore_from_backup(self, backup_dir: str) -> bool:
        """Restore data from a backup directory."""
        try:
            for data_type, filename in self.data_files.items():
                backup_file = os.path.join(backup_dir, filename)
                if os.path.exists(backup_file):
                    dest = self.get_filepath(data_type)
                    with open(backup_file, 'r') as src:
                        with open(dest, 'w') as dst:
                            dst.write(src.read())
            return True
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False
    
    # Convenience methods for specific data types
    
    def load_prop_firms(self) -> List[Dict]:
        """Load prop firms configuration."""
        return self.load_data('prop_firms')
    
    def save_prop_firms(self, firms: List[Dict]) -> bool:
        """Save prop firms configuration."""
        return self.save_data('prop_firms', firms)
    
    def load_accounts(self) -> List[Dict]:
        """Load trading accounts."""
        return self.load_data('accounts')
    
    def save_accounts(self, accounts: List[Dict]) -> bool:
        """Save trading accounts."""
        return self.save_data('accounts', accounts)
    
    def load_playbooks(self) -> List[Dict]:
        """Load trading playbooks."""
        return self.load_data('playbooks')
    
    def save_playbooks(self, playbooks: List[Dict]) -> bool:
        """Save trading playbooks."""
        return self.save_data('playbooks', playbooks)
    
    def load_trades(self) -> List[Dict]:
        """Load trade journal entries."""
        return self.load_data('trades')
    
    def save_trades(self, trades: List[Dict]) -> bool:
        """Save trade journal entries."""
        return self.save_data('trades', trades)
    
    def load_withdrawals(self) -> List[Dict]:
        """Load withdrawal records."""
        return self.load_data('withdrawals')
    
    def save_withdrawals(self, withdrawals: List[Dict]) -> bool:
        """Save withdrawal records."""
        return self.save_data('withdrawals', withdrawals)
    
    def load_psychological_checkins(self) -> List[Dict]:
        """Load psychological check-in records."""
        return self.load_data('psychological_checkins')
    
    def save_psychological_checkins(self, checkins: List[Dict]) -> bool:
        """Save psychological check-in records."""
        return self.save_data('psychological_checkins', checkins)
    
    def get_account_by_id(self, account_id: str) -> Dict:
        """Get a specific account by ID."""
        accounts = self.load_accounts()
        return next((acc for acc in accounts if acc.get('id') == account_id), None)
    
    def update_account_balance(self, account_id: str, new_balance: float) -> bool:
        """Update the balance of a specific account."""
        accounts = self.load_accounts()
        for account in accounts:
            if account.get('id') == account_id:
                account['current_balance'] = new_balance
                account['last_updated'] = datetime.now().isoformat()
                return self.save_accounts(accounts)
        return False
    
    def add_trade(self, trade: Dict) -> bool:
        """Add a new trade to the journal."""
        trades = self.load_trades()
        trade['id'] = f"trade_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        trade['timestamp'] = datetime.now().isoformat()
        trades.append(trade)
        return self.save_trades(trades)
    
    def get_trades_by_account(self, account_id: str) -> List[Dict]:
        """Get all trades for a specific account."""
        trades = self.load_trades()
        return [t for t in trades if t.get('account_id') == account_id]
    
    def get_trades_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """Get trades within a date range."""
        trades = self.load_trades()
        return [t for t in trades if start_date <= t.get('date', '') <= end_date]
    
    def load_settings(self) -> Dict:
        """Load application settings."""
        settings_data = self.load_data('config')
        if settings_data and len(settings_data) > 0:
            return settings_data[0]
        return {}
    
    def save_settings(self, settings: Dict) -> bool:
        """Save application settings."""
        # Ensure all expected keys exist with defaults
        default_settings = {
            'default_view': 'Overview',
            'show_clearance_banner': True,
            'enforce_clearance': 'Soft (Warning Only)',
            'track_overrides': True,
            'remind_checkin': True,
            'end_of_day_summary': False,
            'last_updated': datetime.now().isoformat()
        }
        
        # Merge with existing settings (preserve extra fields like grade_rules, etc.)
        merged_settings = {**default_settings, **settings}
        merged_settings['last_updated'] = datetime.now().isoformat()
        
        return self.save_data('config', [merged_settings])
    
    def load_daily_checkins(self) -> List[Dict]:
        """Load daily check-ins (alias for psychological_checkins)."""
        return self.load_psychological_checkins()
    
    def export_all_data(self) -> Dict[str, List[Dict]]:
        """Export all data as a dictionary for backup/download."""
        return {
            'prop_firms': self.load_prop_firms(),
            'accounts': self.load_accounts(),
            'playbooks': self.load_playbooks(),
            'trades': self.load_trades(),
            'withdrawals': self.load_withdrawals(),
            'psychological_checkins': self.load_psychological_checkins(),
            'settings': [self.load_settings()],
            'export_date': datetime.now().isoformat()
        }
    
    def import_all_data(self, data: Dict[str, List[Dict]]) -> bool:
        """Import data from a dictionary (from backup/upload)."""
        try:
            if 'prop_firms' in data:
                self.save_prop_firms(data['prop_firms'])
            
            if 'accounts' in data:
                self.save_accounts(data['accounts'])
            
            if 'playbooks' in data:
                self.save_playbooks(data['playbooks'])
            
            if 'trades' in data:
                self.save_trades(data['trades'])
            
            if 'withdrawals' in data:
                self.save_withdrawals(data['withdrawals'])
            
            # Handle both old and new formats for psychological checkins
            if 'psychological_checkins' in data:
                self.save_psychological_checkins(data['psychological_checkins'])
            elif 'daily_checkins' in data:
                self.save_psychological_checkins(data['daily_checkins'])
            
            # Handle settings - can be dict or list
            if 'settings' in data:
                settings_data = data['settings']
                # If it's a dict, wrap it in a list
                if isinstance(settings_data, dict):
                    self.save_settings(settings_data)
                # If it's a list with items, take the first one
                elif isinstance(settings_data, list) and len(settings_data) > 0:
                    self.save_settings(settings_data[0])
            
            return True
        except Exception as e:
            print(f"Error importing data: {e}")
            import traceback
            traceback.print_exc()
            return False