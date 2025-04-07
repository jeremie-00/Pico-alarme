import hashlib
import binascii
import json

def hash_password(password):
    hash = hashlib.sha256(password.encode()).digest()
    return binascii.hexlify(hash).decode('utf-8')

def save_hashed_password(username, password, json_file='users.json'):
    hashed_password = hash_password(password)
    try:
        with open(json_file, 'r') as file:
            users = json.load(file)
            print(users)
    except Exception as e:
        users = {}

    users[username] = hashed_password

    with open(json_file, 'w') as file:
        json.dump(users, file)

    print(f"Mot de passe pour l'utilisateur '{username}' a été haché et enregistré avec succès.")

# Exemple d'utilisation
save_hashed_password("name", "pswd")