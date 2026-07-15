import requests
from dotenv import load_dotenv
import os
import pdb
import argparse
import subprocess

target_in_docker = True
target_behind_proxy = False

load_dotenv(dotenv_path='../../../../.env')
highlighter_port = int(os.getenv("HIGHLIGHTER_PORT"))
base_url = os.getenv("MY_DNS_NAME")
user = os.getenv("PROXY_USER")
pw = os.getenv("PROXY_PASSWORD")

def get_highlighter_ip():
    if not target_in_docker:
        return f'http://0.0.0.0:{highlighter_port}'

    # Run a command and capture its stdout and stderr
    ip = subprocess.run(
        f"docker inspect --format='{{{{.NetworkSettings.Networks.homeserver.IPAddress}}}}' highlighter",
        capture_output=True,  # Capture stdout and stderr
        text=True,           # Decode output as text (UTF-8 by default)
        shell=True           # Raise CalledProcessError if the command returns a non-zero exit code
    ).stdout.replace('\n', '')

    return f'{ip}'

def run(text: str, verbose: bool):
    # The exact object structure expected by the API
    payload = {
        "text": text,
        "ranges": [
            {"start": 0, "length": 6},    # Highlights "Python"
            {"start": 11, "length": 6},   # Highlights "Docker"
            {"start": 32, "length": 13}   # Highlights "UI components"
        ]
    }

    if not target_behind_proxy:
        url = get_highlighter_ip()
        response = requests.post(
            f"http://{url}:{highlighter_port}/highlighter/api/highlight", 
            json=payload,
            auth=(user, pw)
        )
    else:
        response = requests.post(
            f"http://{base_url}:{highlighter_port}/highlighter/api/highlight", 
            json=payload,
            auth=(user, pw)
        )

    return response.json()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Feed text to highlighter UI.')
    parser.add_argument('-t', '--text', help='Text baseline to send to UI.')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output.')

    args = parser.parse_args()
    text = "Python and Docker make building UI components fast and simple. Yaay"

    content = run(text = text, verbose = args.verbose)
    print(content)
