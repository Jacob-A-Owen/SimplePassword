import json
import os
import random
import string
import hashlib
import msvcrt
from difflib import get_close_matches
from cryptography.fernet import Fernet

USERS_FILE = "users.json"


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def show_title():
    clear_screen()
    print(r"""
   _____ _                 _      _____                                     _ 
  / ____(_)               | |    |  __ \                                   | |
 | (___  _ _ __ ___  _ __ | | ___| |__) |_ _ ___ _____      _____  _ __  __| |
  \___ \| | '_ ` _ \| '_ \| |/ _ \  ___/ _` / __/ __\ \ /\ / / _ \| '__|/ _` |
  ____) | | | | | | | |_) | |  __/ |  | (_| \__ \__ \\ V  V / (_) | |  | (_| |
 |_____/|_|_| |_| |_| .__/|_|\___|_|   \__,_|___/___/ \_/\_/ \___/|_|   \__,_|
                    | |                                                        
                    |_|                                                        
""")
    print("                         (press enter to continue)")
    input()


def hash_text(text):
    return hashlib.sha256(text.encode()).hexdigest()


def text_input(prompt):
    print(prompt, end="", flush=True)
    value = ""

    while True:
        key = msvcrt.getch()

        if key in {b"\r", b"\n"}:
            print()
            return value

        if key == b"\x1b":   # ESC
            print()
            return None

        if key == b"\x08":   # BACKSPACE
            if value:
                value = value[:-1]
                print("\b \b", end="", flush=True)
            continue

        if key in {b"\x00", b"\xe0"}:   # arrows / function keys
            msvcrt.getch()
            continue

        try:
            char = key.decode()
            value += char
            print(char, end="", flush=True)
        except:
            pass


def hidden_password_input(prompt):
    print(prompt, end="", flush=True)
    password = ""

    while True:
        key = msvcrt.getch()

        if key in {b"\r", b"\n"}:
            print()
            return password

        if key == b"\x1b":   # ESC
            print()
            return None

        if key == b"\x08":   # BACKSPACE
            if password:
                password = password[:-1]
                print("\b \b", end="", flush=True)
            continue

        if key in {b"\x00", b"\xe0"}:
            msvcrt.getch()
            continue

        try:
            password += key.decode()
            print("*", end="", flush=True)
        except:
            pass


def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)


def user_files(username):
    safe_name = "".join(c for c in username if c.isalnum() or c in ("_", "-")).lower()
    key_file = f"{safe_name}_secret.key"
    data_file = f"{safe_name}_passwords.json"
    return key_file, data_file


def setup_or_check_user():
    users = load_users()

    username = text_input("\nUsername: ")
    if username is None or not username.strip():
        return None

    username = username.strip().lower()

    if username not in users:
        choice = text_input("No account found. Create new user? [y/n]: ")
        if choice is None or choice.strip().lower() != "y":
            return None

        while True:
            master = hidden_password_input("Create master password: ")
            if master is None:
                return None

            confirm = hidden_password_input("Confirm master password: ")
            if confirm is None:
                return None

            if master != confirm:
                print("Passwords do not match.")
                continue

            if len(master) < 6:
                print("Password must be 6+ chars.")
                continue

            users[username] = {"master_hash": hash_text(master)}
            save_users(users)
            print("User created.")
            return username

    while True:
        master = hidden_password_input("Enter master password: ")
        if master is None:
            return None

        if hash_text(master) == users[username]["master_hash"]:
            print("Access granted.")
            return username

        print("Wrong password.")


def get_key(file):
    if os.path.exists(file):
        with open(file, "rb") as f:
            return f.read()

    key = Fernet.generate_key()
    with open(file, "wb") as f:
        f.write(key)
    return key


def load_data(file):
    if not os.path.exists(file):
        return []
    with open(file, "r") as f:
        return json.load(f)


def save_data(data, file):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)


def encrypt_text(cipher, txt):
    return cipher.encrypt(txt.encode()).decode()


def decrypt_text(cipher, txt):
    return cipher.decrypt(txt.encode()).decode()


def strength_details(p):
    score = sum([
        len(p) >= 8,
        len(p) >= 12,
        any(c.islower() for c in p),
        any(c.isupper() for c in p),
        any(c.isdigit() for c in p),
        any(c in string.punctuation for c in p)
    ])

    if score <= 2:
        return "Weak", "[#--]"
    if score <= 4:
        return "Medium", "[##-]"
    return "Strong", "[###]"


def password_strength(p):
    return strength_details(p)[0]


def strength_display(p):
    name, bar = strength_details(p)
    return f"{name} {bar}"


def generate_password():
    print("\nPassword Generator\n")

    while True:
        length = text_input("Password length (8-50): ")
        if length is None:
            return None

        if not length.isdigit():
            print("Enter a number.")
            continue

        length = int(length)
        if length < 8 or length > 50:
            print("Length must be between 8 and 50.")
            continue
        break

    upper = text_input("Include uppercase letters? (y/n): ")
    if upper is None:
        return None
    lower = text_input("Include lowercase letters? (y/n): ")
    if lower is None:
        return None
    digits = text_input("Include numbers? (y/n): ")
    if digits is None:
        return None
    symbols = text_input("Include symbols? (y/n): ")
    if symbols is None:
        return None

    print()

    chars = ""
    if upper.strip().lower() == "y":
        chars += string.ascii_uppercase
    if lower.strip().lower() == "y":
        chars += string.ascii_lowercase
    if digits.strip().lower() == "y":
        chars += string.digits
    if symbols.strip().lower() == "y":
        chars += string.punctuation

    if not chars:
        print("You must select at least one character type.")
        return None

    return "".join(random.choice(chars) for _ in range(length))


def add_password(cipher, data, file):
    website = text_input("Website: ")
    if website is None:
        return

    user = text_input("Username: ")
    if user is None:
        return

    choice = text_input("Generate password? (yes/no): ")
    if choice is None:
        return

    if choice.strip().lower() == "yes":
        password = generate_password()
        if not password:
            return
        print("Generated:", password)
    else:
        password = hidden_password_input("Password: ")
        if password is None:
            return

    entry = {
        "website": website,
        "username": user,
        "password": encrypt_text(cipher, password),
        "strength": password_strength(password)
    }

    data.append(entry)
    save_data(data, file)
    print("Saved.")
    print("Strength:", strength_display(password))


def print_password_list(cipher, data):
    print("\nSaved Accounts")
    print("-" * 40)

    for i, x in enumerate(data, 1):
        real_pw = decrypt_text(cipher, x["password"])
        print(f"{i}. Website: {x['website']}")
        print("   Username:", x["username"])
        print("   Password:", real_pw)
        print("   Strength:", strength_display(real_pw))
        print("-" * 40)


def view_passwords(cipher, data, file):
    if not data:
        print("No passwords saved.")
        return

    while True:
        print_password_list(cipher, data)
        print("Enter a number to manage an entry")
        print("Or press B to go back")

        choice = text_input("Choice: ")
        if choice is None:
            return

        choice = choice.strip().lower()

        if choice == "b":
            return

        if not choice.isdigit():
            print("Invalid input.")
            continue

        index = int(choice) - 1
        if index < 0 or index >= len(data):
            print("Invalid selection.")
            continue

        while True:
            item = data[index]

            print(f"\nSelected: {item['website']}")
            print("1. Edit Username")
            print("2. Edit Password")
            print("3. Delete This Entry")
            print("4. Back")

            sub = text_input("Choose an option: ")
            if sub is None:
                break

            sub = sub.strip()

            if sub == "1":
                new_user = text_input("New username: ")
                if new_user is None:
                    continue
                if new_user.strip():
                    item["username"] = new_user.strip()
                    save_data(data, file)
                    print("Username updated.")
                else:
                    print("Username not changed.")

            elif sub == "2":
                new_pw = hidden_password_input("New password: ")
                if new_pw is None:
                    print("Password update cancelled.")
                else:
                    item["password"] = encrypt_text(cipher, new_pw)
                    item["strength"] = password_strength(new_pw)
                    save_data(data, file)
                    print("Password updated.")
                    print("Strength:", strength_display(new_pw))

            elif sub == "3":
                removed = data.pop(index)
                save_data(data, file)
                print(f"Deleted entry for {removed['website']}.")
                if not data:
                    print("No passwords saved.")
                    return
                break

            elif sub == "4":
                break

            else:
                print("Invalid option.")


def print_result(cipher, item, title):
    real_pw = decrypt_text(cipher, item["password"])
    print(f"\n{title}")
    print("-" * 30)
    print("Website:", item["website"])
    print("Username:", item["username"])
    print("Password:", real_pw)
    print("Strength:", strength_display(real_pw))


def search_password(cipher, data):
    if not data:
        print("No passwords.")
        return

    s = text_input("Search website: ")
    if s is None:
        return

    s = s.strip().lower()
    sites = [x["website"] for x in data]
    lower = [x.lower() for x in sites]

    if s in lower:
        item = data[lower.index(s)]
    else:
        match = get_close_matches(s, lower, 1, 0.4)
        if not match:
            print("No match.")
            return
        item = data[lower.index(match[0])]

    print_result(cipher, item, "Match Found")


def remove_password(data, file):
    if not data:
        print("No entries.")
        return

    for i, x in enumerate(data, 1):
        print(f"{i}. {x['website']}")

    c = text_input("Delete number: ")
    if c is None or not c.isdigit():
        return

    i = int(c) - 1
    if 0 <= i < len(data):
        removed = data.pop(i)
        save_data(data, file)
        print("Removed", removed["website"])


def delete_user_profile(user):
    users = load_users()

    if user not in users:
        return False

    confirm = text_input(f"Delete profile '{user}'? (yes/no): ")
    if confirm is None or confirm.strip().lower() != "yes":
        return False

    pw = hidden_password_input("Enter master password: ")
    if pw is None or hash_text(pw) != users[user]["master_hash"]:
        print("Wrong password.")
        return False

    key, data = user_files(user)

    users.pop(user)
    save_users(users)

    if os.path.exists(key):
        os.remove(key)
    if os.path.exists(data):
        os.remove(data)

    print("Profile deleted.")
    return True


def show_menu(user):
    print(f"\nLogged in as: {user}\n")
    print("1. Add Password               5. Remove Password")
    print("2. View All Passwords         6. Delete User Profile")
    print("3. Search by Website          7. Log Out")
    print("4. Generate Random Password   8. Exit")


def main():
    show_title()

    while True:
        user = setup_or_check_user()
        if not user:
            continue

        key_file, data_file = user_files(user)
        cipher = Fernet(get_key(key_file))
        data = load_data(data_file)

        while True:
            show_menu(user)
            print()

            choice = text_input("Choose an option: ")
            if choice is None:
                continue

            choice = choice.strip()

            if choice == "1":
                add_password(cipher, data, data_file)

            elif choice == "2":
                view_passwords(cipher, data, data_file)

            elif choice == "3":
                search_password(cipher, data)

            elif choice == "4":
                pw = generate_password()
                if pw:
                    print("Generated:", pw)
                    print("Strength:", strength_display(pw))

            elif choice == "5":
                remove_password(data, data_file)

            elif choice == "6":
                if delete_user_profile(user):
                    break

            elif choice == "7":
                print("Logging out...")
                break

            elif choice == "8":
                print("Exiting SimplePassword.")
                return

            else:
                print("Invalid option.")


if __name__ == "__main__":
    main()