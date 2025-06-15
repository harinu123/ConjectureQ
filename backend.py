import pandas as pd
import database
import ast
import time

# A basic set of initial test cases.
# In a real scenario, this would be more extensive.
INITIAL_TEST_CASES = [
    {'tester': 'system', 'input': [7], 'expected_output': True},
    {'tester': 'system', 'input': [10, 2], 'expected_output': True}, # 10-2 = 8, 10+2=12, 10*2=20
    {'tester': 'system', 'input': [6, 9], 'expected_output': False} # 3, 15, 54
]

def run_solution_and_get_results(solver_name: str, code: str):
    """
    Runs the solver's code against existing test cases and returns the results.
    """
    database.add_solver(solver_name, code)
    test_cases = database.get_test_cases()
    # Ensure initial test cases are present
    if not any(t['tester'] == 'system' for t in test_cases):
        for case in INITIAL_TEST_CASES:
            database.add_test_case(case['tester'], case['input'], case['expected_output'])
        test_cases = database.get_test_cases()

    passed_count = 0
    failed_count = 0
    
    # Create a dictionary to execute the code in
    exec_globals = {}

    for test in test_cases:
        try:
            # More secure execution: only expose the 'solve' function
            exec(code, exec_globals)
            solve_func = exec_globals.get('solve')
            if not callable(solve_func):
                 raise ValueError("No valid 'solve' function found in the submitted code.")
            
            result = solve_func(test['input'])
            if result == test['expected_output']:
                passed_count += 1
            else:
                failed_count += 1
        except Exception as e:
            failed_count += 1
            print(f"Error executing solver {solver_name} code: {e}")

    database.update_solver_score(solver_name, passed_count)
    return {"status": "Completed", "passed": passed_count, "failed": failed_count}

def run_tester_and_get_feedback(tester_name: str, test_input: str):
    """
    Runs a new test case against all solver submissions and returns feedback.
    """
    try:
        input_data = ast.literal_eval(test_input)
        if not isinstance(input_data, list) or not all(isinstance(x, int) and x > 0 for x in input_data):
            return {"error": "Invalid input. Please provide a list of positive integers."}
        # A real system would require the tester to provide the expected output.
        # For this example, we'll assume a simple placeholder.
        expected_output = False
    except (ValueError, SyntaxError):
        return {"error": "Invalid input format. Please provide a list of integers like [2, 3, 5]."}

    database.add_test_case(tester_name, input_data, expected_output)
    solvers = database.get_solvers()
    broken_submissions = []
    
    exec_globals = {}

    for solver in solvers:
        try:
            exec(solver['code'], exec_globals)
            solve_func = exec_globals.get('solve')
            if not callable(solve_func):
                continue # Skip if solver code is invalid

            result = solve_func(input_data)
            if result != expected_output:
                broken_submissions.append(f"{solver['name']}'s solution")
        except Exception:
            broken_submissions.append(f"{solver['name']}'s solution")
    
    if broken_submissions:
        database.update_tester_score(tester_name, len(broken_submissions))

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
