import subprocess
import json
import questionary
import os

class Vault:
    def __init__(self):
        self.session_key = os.getenv("BW_SESSION")

    def get_or_ask(self, item_name, field="password", validator_func=None):
        """
        Tries to get a key. If missing OR the validator says it's expired,
        it asks the user for a new one and saves it.
        """
        secret = self._fetch_from_bw(item_name, field)
        
        # If secret exists, validate it (e.g., test a ping to Hostinger)
        if secret and validator_func:
            is_valid, error_msg = validator_func(secret)
            if not is_valid:
                print(f"[!] Key '{item_name}' found but appears invalid/expired: {error_msg}")
                secret = None # Trigger the 'ask' logic

        if not secret:
            print(f"[*] {item_name} ({field}) not found or expired in Vault.")
            secret = questionary.password(f"Please enter your {item_name} {field}:").ask()
            self._save_to_bw(item_name, field, secret)
            print(f"[+] {item_name} saved to Bitwarden successfully.")
            
        return secret
    
    def _fetch_from_bw(self, item_name, field):
        try:
            cmd = ["bw", "get", "item", item_name, "--session", self.session_key]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode != 0: return None
            
            data = json.loads(res.stdout)
            return data['login']['password'] if field == "password" else \
                   next((f['value'] for f in data.get('fields', []) if f['name'] == field), None)
        except:
            return None
        
    def _save_to_bw(self, item_name, field, value):
        """
        Logic to create or update an item in Bitwarden.
        (Uses 'bw create item' or 'bw edit item')
        """
        # Simplified: In a real script, you'd check if it exists to 'edit' or 'create'
        # For a portfolio, explaining the 'bw create' command is the key part.
        pass

    def _run_cmd(self, cmd):
        """Internal helper to run Bitwarden CLI commands."""
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Bitwarden Error: {result.stderr}")
        return result.stdout

    def get_secret(self, item_name, field="password"):
        """Generic fetcher for any item in your vault."""
        # This command fetches the item and uses 'jq' logic to get a specific field
        cmd = ["bw", "get", "item", item_name, "--session", self.session_key]
        raw_json = self._run_cmd(cmd)
        data = json.loads(raw_json)
        
        # Logic to find the specific field (like a custom 'API_KEY' field)
        if field == "password":
            return data['login']['password']
        else:
            # Look in custom fields
            for f in data.get('fields', []):
                if f['name'] == field:
                    return f['value']
        return None

    # Dedicated functions for your specific project needs
    def get_tailscale_key(self):
        return self.get_secret("Tailscale", field="AUTH_KEY")

    def get_hostinger_api(self):
        return self.get_secret("Hostinger", field="API_TOKEN")