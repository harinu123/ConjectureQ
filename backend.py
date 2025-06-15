import pandas as pd
import database
import ast
import time

def run_solution_and_get_results(solver_name: str, code: str):
    """
    Runs the solver's code against existing test cases and returns the results.
    """
    database.add_solver(solver_name, code)
    test_cases = database.get_test_cases()
    passed_count = 0
    failed_count = 0

    for test in test_cases:
        try:
            # A simple, unsafe eval. For a real application, use a sandboxed environment.
            exec(code, globals())
            # Assuming the solver's function is named 'solve'
            result = solve(test['input'])
            if result == test['expected_output']:
                passed_count += 1
            else:
                failed_count += 1
        except Exception as e:
            failed_count += 1

    database.update_solver_score(solver_name, passed_count)
    return {"status": "Completed", "passed": passed_count, "failed": failed_count}

def run_tester_and_get_feedback(tester_name: str, test_input: str):
    """
    Runs a new test case against all solver submissions and returns feedback.
    """
    try:
        # A simple, unsafe literal_eval.
        input_data = ast.literal_eval(test_input)
        # For this example, we'll assume a simple expected output.
        # A more robust system would require the tester to provide the expected output.
        expected_output = True # Placeholder
    except:
        return {"error": "Invalid input format. Please provide a list of integers."}

    database.add_test_case(tester_name, input_data, expected_output)
    solvers = database.get_solvers()
    broken_submissions = []
    breaks_found = 0

    for solver in solvers:
        try:
            exec(solver['code'], globals())
            result = solve(input_data)
            if result != expected_output:
                broken_submissions.append(f"{solver['name']}'s solution")
                breaks_found += 1
        except Exception:
            broken_submissions.append(f"{solver['name']}'s solution")
            breaks_found += 1

    database.update_tester_score(tester_name, breaks_found)
    return {"affected_submissions": len(broken_submissions), "broken": broken_submissions}

def get_solver_leaderboard():
    """
    Retrieves and formats the solver leaderboard.
    """
    solvers = database.get_solvers()
    if not solvers:
        return pd.DataFrame({"Rank": [], "User": [], "Tests Passed": []})

    df = pd.DataFrame(solvers)
    df = df.sort_values(by="tests_passed", ascending=False).reset_index(drop=True)
    df['Rank'] = df.index + 1
    return df[['Rank', 'name', 'tests_passed']].rename(columns={'name': 'User', 'tests_passed': 'Tests Passed'})

def get_tester_leaderboard():
    """
    Retrieves and formats the tester leaderboard.
    """
    testers = database.get_testers()
    if not testers:
        return pd.DataFrame({"Rank": [], "User": [], "Breaks Found": []})

    df = pd.DataFrame(testers)
    df = df.sort_values(by="breaks_found", ascending=False).reset_index(drop=True)
    df['Rank'] = df.index + 1
    return df[['Rank', 'name', 'breaks_found']].rename(columns={'name': 'User', 'breaks_found': 'Breaks Found'})

# Dummy solve function for the exec environment
def solve(numbers: list[int]) -> bool:
    # This is a placeholder and will be overwritten by the user's code
    return False
