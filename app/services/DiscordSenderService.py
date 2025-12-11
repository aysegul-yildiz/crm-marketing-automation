import requests
import json

class DiscordSenderService:
    @staticmethod
    def send_discord_post(webhook_url: str, content: str):
        """
        Sends a Discord webhook message.
        """
        payload = {"content": content}
        headers = {"Content-Type": "application/json"}
        response = requests.post(webhook_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Will raise HTTPError if status is not 2xx
        return response