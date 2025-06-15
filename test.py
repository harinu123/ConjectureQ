import streamlit as st
from streamlit_ace import st_ace
import pandas as pd

# Page config
st.set_page_config(
    page_title="Challenge Details",
    layout="wide",
)

# Title
st.title("Challenge Details")

# Tabs for sections
tabs = st.tabs(["Problem Statement", "Background", "Solver", "Tester", "Discussion", "Leaderboards"])

# 1. Problem Statement
with tabs[0]:
    st.header("Problem Statement")
    st.markdown("**Conjecture (true form):** Describe the conjecture here.")
    st.markdown("**Coding challenge:** Provide instructions for the coding task.")

# 2. Background
with tabs[1]:
    st.header("Background")
    st.markdown("- Relevant papers: List and links to papers.")
    st.markdown("- Axioms and definitions: Provide key definitions.")

# 3. Solver
with tabs[2]:
    st.header("Solver Portal")
    st.markdown("Submit your solution code below and run to see real-time results:")
    code = st_ace(
        placeholder="Write your solution here...",
        language="python",
        theme="chrome",
        keybinding="vscode",
        font_size=14,
        tab_size=4,
        show_gutter=True,
        show_print_margin=False,
        wrap=True,
        auto_update=True,
        key="solver_editor"
    )
    if st.button("Run Solution"):
        # TODO: send 'code' to backend for evaluation and display results
        results = run_solution_and_get_results(code)  # stub function
        st.subheader("Results")
        st.write(results)

# 4. Tester
with tabs[3]:
    st.header("Tester Portal")
    st.markdown("Submit test cases or edge cases:")
    test_input = st.text_area("Test Input (JSON or plain text)")
    if st.button("Submit Test Case"):
        # TODO: send test_input to backend, run against all solver submissions
        feedback = run_tester_and_get_feedback(test_input)  # stub function
        st.subheader("Feedback")
        st.write(feedback)

# 5. Discussion
with tabs[4]:
    st.header("Discussion")
    discussion = st.text_area("Add your comment or question:")
    if st.button("Post"):
        # TODO: save discussion comment to backend
        st.success("Your comment has been posted.")

# 6. Leaderboards
with tabs[5]:
    st.header("Leaderboards")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Solver Leaderboard")
        # TODO: fetch solver leaderboard as DataFrame
        solver_df = pd.DataFrame({
            "Rank": [1, 2, 3],
            "User": ["alice", "bob", "carol"],
            "Tests Passed": [50, 45, 40]
        })
        st.dataframe(solver_df)
    with col2:
        st.subheader("Tester Leaderboard")
        # TODO: fetch tester leaderboard as DataFrame
        tester_df = pd.DataFrame({
            "Rank": [1, 2, 3],
            "User": ["dave", "eve", "frank"],
            "Breaks Found": [10, 8, 5]
        })
        st.dataframe(tester_df)

# Placeholder backend functions

def run_solution_and_get_results(code: str):
    # Connect to evaluation service
    return {"status": "Success", "passed": 10, "failed": 0}


def run_tester_and_get_feedback(test_input: str):
    # Connect to tester service
    return {"affected_submissions": 3, "broken": ["alice_solution.py", "carol_solution.py"]}
