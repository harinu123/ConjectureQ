import json
from datetime import datetime

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
        try:
            with open(file, 'r') as f:
                pass
        except FileNotFoundError:
            with open(file, 'w') as f:
                json.dump([], f)

def add_solver(name: str, code: str):
    with open(DB_FILES["solvers"], 'r+') as f:
        solvers = json.load(f)
        # Update existing solver or add a new one
        for solver in solvers:
            if solver['name'] == name:
                solver['code'] = code
                break
        else:
            solvers.append({"name": name, "code": code, "tests_passed": 0})
        f.seek(0)
        json.dump(solvers, f, indent=4)

def get_solvers():
    with open(DB_FILES["solvers"], 'r') as f:
        return json.load(f)

def update_solver_score(name: str, score: int):
    with open(DB_FILES["solvers"], 'r+') as f:
        solvers = json.load(f)
        for solver in solvers:
            if solver['name'] == name:
                solver['tests_passed'] = score
                break
        f.seek(0)
        json.dump(solvers, f, indent=4)

def add_tester(name: str):
    with open(DB_FILES["testers"], 'r+') as f:
        testers = json.load(f)
        if not any(t['name'] == name for t in testers):
            testers.append({"name": name, "breaks_found": 0})
            f.seek(0)
            json.dump(testers, f, indent=4)

def get_testers():
    with open(DB_FILES["testers"], 'r') as f:
        return json.load(f)

def update_tester_score(name: str, breaks: int):
    with open(DB_FILES["testers"], 'r+') as f:
        testers = json.load(f)
        # Add tester if they don't exist
        if not any(t['name'] == name for t in testers):
            testers.append({"name": name, "breaks_found": 0})

        for tester in testers:
            if tester['name'] == name:
                tester['breaks_found'] += breaks
                break
        f.seek(0)
        json.dump(testers, f, indent=4)


def add_test_case(tester_name: str, input_data: list, expected_output: bool):
    with open(DB_FILES["test_cases"], 'r+') as f:
        test_cases = json.load(f)
        test_cases.append({"tester": tester_name, "input": input_data, "expected_output": expected_output})
        f.seek(0)
        json.dump(test_cases, f, indent=4)

def get_test_cases():
    with open(DB_FILES["test_cases"], 'r') as f:
        return json.load(f)

def add_comment(name: str, text: str):
    with open(DB_FILES["comments"], 'r+') as f:
        comments = json.load(f)
        comments.append({"name": name, "text": text, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        f.seek(0)
        json.dump(comments, f, indent=4)

def get_comments():
    with open(DB_FILES["comments"], 'r') as f:
        return json.load(f)
