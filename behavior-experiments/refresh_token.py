token = input("Enter new Box token: ")
with open('box_config.py', 'w') as f:
    f.write(f'BOX_ACCESS_TOKEN = "{token}"')
print("Token updated!")
