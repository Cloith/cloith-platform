import requests

def get_latest_metrics(api_token):
    """Fetches raw data from Hostinger API."""
    headers = {"Authorization": f"Bearer {api_token}"}
    try:
        response = requests.get(headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        return {
            "success": True,
            "cpu": data.get("cpu_usage", 0),
            "memory": data.get("memory_usage", 0),
            "status": data.get("status", "unknown")
        }
    except Exception as e:
        return {"success": False, "error": str(e)}