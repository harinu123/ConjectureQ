# import json
# from datetime import datetime

# DB_FILES = {
#     "solvers": "solvers.json",
#     "testers": "testers.json",
#     "test_cases": "test_cases.json",
#     "comments": "comments.json"
# }

# def init_db():
#     """
#     Initializes the JSON database files if they don't exist.
#     """
#     for file in DB_FILES.values():
#         try:
#             with open(file, 'r') as f:
#                 pass
#         except FileNotFoundError:
#             with open(file, 'w') as f:
#                 json.dump([], f)

# def add_solver(name: str, code: str):
#     with open(DB_FILES["solvers"], 'r+') as f:
#         solvers = json.load(f)
#         # Update existing solver or add a new one
#         for solver in solvers:
#             if solver['name'] == name:
#                 solver['code'] = code
#                 break
#         else:
#             solvers.append({"name": name, "code": code, "tests_passed": 0})
#         f.seek(0)
#         json.dump(solvers, f, indent=4)

# def get_solvers():
#     with open(DB_FILES["solvers"], 'r') as f:
#         return json.load(f)

# def update_solver_score(name: str, score: int):
#     with open(DB_FILES["solvers"], 'r+') as f:
#         solvers = json.load(f)
#         for solver in solvers:
#             if solver['name'] == name:
#                 solver['tests_passed'] = score
#                 break
#         f.seek(0)
#         json.dump(solvers, f, indent=4)

# def add_tester(name: str):
#     with open(DB_FILES["testers"], 'r+') as f:
#         testers = json.load(f)
#         if not any(t['name'] == name for t in testers):
#             testers.append({"name": name, "breaks_found": 0})
#             f.seek(0)
#             json.dump(testers, f, indent=4)

# def get_testers():
#     with open(DB_FILES["testers"], 'r') as f:
#         return json.load(f)

# def update_tester_score(name: str, breaks: int):
#     with open(DB_FILES["testers"], 'r+') as f:
#         testers = json.load(f)
#         # Add tester if they don't exist
#         if not any(t['name'] == name for t in testers):
#             testers.append({"name": name, "breaks_found": 0})

#         for tester in testers:
#             if tester['name'] == name:
#                 tester['breaks_found'] += breaks
#                 break
#         f.seek(0)
#         json.dump(testers, f, indent=4)


# def add_test_case(tester_name: str, input_data: list, expected_output: bool):
#     with open(DB_FILES["test_cases"], 'r+') as f:
#         test_cases = json.load(f)
#         test_cases.append({"tester": tester_name, "input": input_data, "expected_output": expected_output})
#         f.seek(0)
#         json.dump(test_cases, f, indent=4)

# def get_test_cases():
#     with open(DB_FILES["test_cases"], 'r') as f:
#         return json.load(f)

# def add_comment(name: str, text: str):
#     with open(DB_FILES["comments"], 'r+') as f:
#         comments = json.load(f)
#         comments.append({"name": name, "text": text, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
#         f.seek(0)
#         json.dump(comments, f, indent=4)

# def get_comments():
#     with open(DB_FILES["comments"], 'r') as f:
#         return json.load(f)


# database.py

import json
from datetime import datetime
import os
import pandas as pd
import bcrypt # For hashing passwords

# --- File Paths ---
DB_FILES = {
    "solvers": "solvers.json",
    "testers": "testers.json",
    "test_cases": "test_cases.json",
    "comments": "comments.json"
}
USERS_FILE = "users.csv"

# --- Initialization ---
def init_db():
    """Initializes the JSON and CSV database files if they don't exist."""
    for file in DB_FILES.values():
        if not os.path.exists(file):
            with open(file, 'w') as f:
                json.dump([], f)
    
    if not os.path.exists(USERS_FILE):
        df = pd.DataFrame(columns=["username", "hashed_password"])
        df.to_csv(USERS_FILE, index=False)

def seed_sample_leaderboards():
    # only seed if empty
    if not _read_db(DB_FILES["solvers"]):
        solvers = [
            {"name":"Aarav Sharma","code":"", "score":0.83},
            {"name":"Priya Iyer","code":"", "score":0.79},
            {"name":"Rohan Gupta","code":"", "score":0.76},
            {"name":"Neha Menon","code":"", "score":0.75},
            {"name":"Karthik Reddy","code":"", "score":0.73},
            {"name":"Li Wei","code":"", "score":0.82},
            {"name":"Zhang Min","code":"", "score":0.78},
            {"name":"Chen Hao","code":"", "score":0.77},
            {"name":"Liu Yang","code":"", "score":0.74},
            {"name":"Alex Carter","code":"", "score":0.71},  # one white name
        ]
        _write_db(DB_FILES["solvers"], solvers)

    if not _read_db(DB_FILES["testers"]):
        testers = [
            {"name":"Meera Joshi","score":2.35},
            {"name":"Arjun Nair","score":2.12},
            {"name":"Wang Jing","score":2.05},
            {"name":"Sun Qian","score":1.98},
            {"name":"Emily Clark","score":1.85},  # one white name
        ]
        _write_db(DB_FILES["testers"], testers)

# --- User Functions (New) ---
def add_user(username, password):
    """Adds a new user to the users.csv file with a hashed password."""
    if not os.path.exists(USERS_FILE):
        init_db()
        
    users_df = pd.read_csv(USERS_FILE)
    if username in users_df['username'].values:
        return False # User already exists

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    new_user = pd.DataFrame([[username, hashed_password.decode('utf-8')]], columns=["username", "hashed_password"])
    users_df = pd.concat([users_df, new_user], ignore_index=True)
    users_df.to_csv(USERS_FILE, index=False)
    return True

def verify_user(username, password):
    """Verifies a user's credentials against the stored hash."""
    if not os.path.exists(USERS_FILE):
        return False
        
    users_df = pd.read_csv(USERS_FILE)
    user_record = users_df[users_df['username'] == username]

    if not user_record.empty:
        stored_hash = user_record.iloc[0]['hashed_password'].encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            return True # Password matches
    return False

# --- Helper Read/Write Functions ---
def _read_db(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def _write_db(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

# --- Existing Functions (Modified to include username) ---
def add_solver(name: str, code: str):
    solvers = _read_db(DB_FILES["solvers"])
    for s in solvers:
        if s['name'] == name:
            s['code'] = code
            _write_db(DB_FILES["solvers"], solvers)
            return
    solvers.append({"name": name, "code": code, "score": 0})
    _write_db(DB_FILES["solvers"], solvers)

def get_user_submissions(username: str):
    """Retrieves all submissions for a specific user."""
    solvers = _read_db(DB_FILES["solvers"])
    return [s for s in solvers if s['name'] == username]
    
def get_solvers():
    return _read_db(DB_FILES["solvers"])

def update_solver_score(name: str, score: float):
    solvers = _read_db(DB_FILES["solvers"])
    for s in solvers:
        if s['name'] == name:
            s['score'] = float(score)
            break
    else:
        solvers.append({"name": name, "code": "", "score": float(score)})
    _write_db(DB_FILES["solvers"], solvers)

# --- Other functions remain the same ---
def update_tester_score(name: str, score: float):
    testers = _read_db(DB_FILES["testers"])
    for t in testers:
        if t['name'] == name:
            t['score'] = float(score)
            _write_db(DB_FILES["testers"], testers)
            return
    testers.append({"name": name, "score": float(score)})
    _write_db(DB_FILES["testers"], testers)

def get_testers():
    return _read_db(DB_FILES["testers"])

def add_test_case(tester_name: str, input_data: list, expected_output: bool):
    test_cases = _read_db(DB_FILES["test_cases"])
    if not any(case['input'] == input_data for case in test_cases):
        test_cases.append({"tester": tester_name, "input": input_data, "expected_output": expected_output})
        _write_db(DB_FILES["test_cases"], test_cases)

def get_test_cases():
    return _read_db(DB_FILES["test_cases"])

def add_comment(name: str, text: str):
    comments = _read_db(DB_FILES["comments"])
    comments.append({"name": name, "text": text, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    _write_db(DB_FILES["comments"], comments)

def get_comments():
    return _read_db(DB_FILES["comments"])
