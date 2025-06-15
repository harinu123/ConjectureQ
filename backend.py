import json
from datetime import datetime
import os

DB_FILES = {
    "solvers": "solvers.json",
    "testers": "testers.json",
    "test_cases": "test_cases.json",
    "comments": "comments.json"
}

def init_db():
    """
    Initializes the JSON database files if they don't exist.
    """
    for file in DB_FILES.values():
        if not os.path.exists(file):
            with open(file, 'w') as f:
                json.dump([], f)

def _read_db(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def _write_db(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def add_solver(name: str, code: str):
    solvers = _read_db(DB_FILES["solvers"])
    for solver in solvers:
        if solver['name'] == name:
            solver['code'] = code
            _write_db(DB_FILES["solvers"], solvers)
            return
    solvers.append({"name": name, "code": code, "tests_passed": 0})
    _write_db(DB_FILES["solvers"], solvers)

def get_solvers():
    return _read_db(DB_FILES["solvers"])

def update_solver_score(name: str, score: int):
    solvers = _read_db(DB_FILES["solvers"])
    for solver in solvers:
        if solver['name'] == name:
            solver['tests_passed'] = score
            break
    _write_db(DB_FILES["solvers"], solvers)

def update_tester_score(name: str, breaks_found: int):
    testers = _read_db(DB_FILES["testers"])
    for tester in testers:
        if tester['name'] == name:
            # Increment the score
            tester['breaks_found'] += breaks_found
            _write_db(DB_FILES["testers"], testers)
            return
    # If tester not found, add them
    testers.append({"name": name, "breaks_found": breaks_found})
    _write_db(DB_FILES["testers"], testers)


def get_testers():
    return _read_db(DB_FILES["testers"])

def add_test_case(tester_name: str, input_data: list, expected_output: bool):
    test_cases = _read_db(DB_FILES["test_cases"])
    # Avoid duplicate test cases
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
