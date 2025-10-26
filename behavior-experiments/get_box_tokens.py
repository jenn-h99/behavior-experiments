import requests
import json

def get_tokens(auth_code):
    url = 'https://api.box.com/oauth2/token'
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'client_id': 'hpqcaj9sk34n3ubp38jeekmuk194cqwr',  # Keep this
        'client_secret': 'HB0lyehwMfXOkxQTwGFtB9MlUairjqLD',  # Keep this
        'redirect_uri': 'https://example.com',
    }

    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        tokens = response.json()
        with open('/home/pi/box_tokens.json', 'w') as f:
            json.dump(tokens, f, indent=4)
        print("Tokens saved to /home/pi/box_tokens.json")
        print(tokens)
    else:
        print("Failed to get tokens")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    auth_code = '5mib7FFp6rrECMmFomFmt6MkgesMHv73'
    get_tokens(auth_code)
