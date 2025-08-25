import requests
import json

def get_tokens(auth_code):
    url = 'https://api.box.com/oauth2/token'
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'client_id': 'hpqcaj9sk34n3ubp38jeekmuk194cqwr',   # Your Box app client_id
        'client_secret': 'HB0lyehwMfXOkxQTwGFtB9MlUairjqLD', # Your Box app client_secret
        'redirect_uri': 'https://example.com',                # The same redirect URI you used
    }

    response = requests.post(url, data=data)
    tokens = response.json()

    # Save tokens to a file for later use
    with open('/home/pi/box_tokens.json', 'w') as f:
        json.dump(tokens, f, indent=4)
    print("Tokens saved to /home/pi/box_tokens.json")
    print(tokens)

if __name__ == "__main__":
    auth_code = 'uPPYxIiZmuqvcbZseSG3F3ZYA0NPPifV'  # your authorization code here
    get_tokens(auth_code)
