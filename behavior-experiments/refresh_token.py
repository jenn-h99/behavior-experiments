#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Get new token from user
token = input("Enter new Box token: ")

# Write to config file using older Python syntax
try:
    with open('box_config.py', 'w') as f:
        f.write('BOX_ACCESS_TOKEN = "{}"\n'.format(token))
    print("Token updated successfully!")
except IOError as e:
    print("Error writing config file: {}".format(e))
except Exception as e:
    print("Unexpected error: {}".format(e))

# Verify the file was created
try:
    with open('box_config.py', 'r') as f:
        content = f.read()
        print("Config file contents:")
        print(content)
except IOError:
    print("Could not read the config file")
    
