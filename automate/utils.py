import requests
import json

# from cryptography.fernet import Fernet


class Crypt:
    """This is a class that handles the encryption and decryption of access token"""

    def __init__(self, value):
        self.value = value

    def encrypt(self):
        """This encrypts value using the provided key"""
        # Todo: (mark) write encryption function with cryptography
        pass

    def decrypt(self):
        """This decrypts value using the provided key"""
        # Todo: (mark) write decryption function with cryptography
        pass


def add_hook_to_repo(repo, host, owner, auth_token):
    endpoint = f"https://api.github.com/repos/{owner}/{repo}/hooks"
    payload = {
        "name": "web",
        "active": True,
        "events": ["push", "pull_request"],
        "config": {
            "url": f"https://{host}/hooks/{repo}/",
            "content_type": "json",
            "insecure_ssl": "0",
        },
    }
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {auth_token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    try:
        response = requests.post(endpoint, data=json.dumps(payload), headers=headers)
    except Exception as e:
        raise Exception(e)
    if response.status_code == 201:
        return True
    return False


def gen_hook_url(username, repo_name):
    return f"https://domain.com/{username}/repo/hooks/{repo_name}/"
