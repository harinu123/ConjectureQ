import streamlit as st
from streamlit_ace import st_ace
import pandas as pd
import backend  # Import the backend module
import database # Import the database module

# Initialize the database
database.init_db()

# --- Page Configuration ---
st.set_page_config(
    page_title="ConjectureQ",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Main Title ---
st.title("ConjectureQ: Interactive Coding Challenges for Open Conjectures")

# --- Tabs for Different Sections ---
tabs = st.tabs(["Problem Statement", "Background", "Solver", "Tester", "Discussion", "Leaderboards"])

# --- 1. Problem Statement ---
with tabs[0]:
    st.header("Problem Statement")
    st.markdown("""
        **Conjecture (True Form):** For any given set of positive integers, there exists a sequence of operations (addition, subtraction, multiplication) that will result in a prime number.

        **Coding Challenge:** Write a Python function `solve(numbers: list[int]) -> bool` that takes a list of positive integers and returns `True` if a prime number can be formed using the allowed operations, and `False` otherwise. Your solution should be both correct and efficient.
    """)

# --- 2. Background ---
with tabs[1]:
    st.header("Background")
    st.markdown("""
        - **Relevant Papers:**
            - [An Introduction to Number Theory](https://www.ams.org/bookstore-getitem/item=ST-8)
            - [Computational Aspects of Number Theory](https://www.springer.com/gp/book/9783540441215)
        - **Axioms and Definitions:**
            - **Positive Integer:** An integer greater than 0.
            - **Prime Number:** A positive integer greater than 1 that has no positive divisors other than 1 and itself.
    """)

# --- 3. Solver ---
with tabs[2]:
    st.header("Solver Portal")
    st.markdown("Submit your solution code below and run it to see real-time results:")

    solver_name = st.text_input("Enter your name to appear on the leaderboard:", key="solver_name")

    code = st_ace(
        placeholder="""# Your function must be named 'solve'
# Example:
# def solve(numbers: list[int]) -> bool:
#     # ... your logic here ...
#     return True
""",
        language="python",
        theme="monokai",
        keybinding="vscode",
        font_size=14,
        tab_size=4,
        show_gutter=True,
        show_print_margin=False,
        wrap=True,
        auto_update=False,
        key="solver_editor"
    )

    if st.button("Run Solution"):
        if solver_name and code:
            # CORRECTED: Call the function from the 'backend' module
            results = backend.run_solution_and_get_results(solver_name, code)
            st.subheader("Results")
            st.write(results)
        else:
            st.warning("Please enter your name and provide a solution.")

# --- 4. Tester ---
with tabs[3]:
    st.header("Tester Portal")
    st.markdown("Submit test cases or edge cases to challenge the solvers' submissions:")

    tester_name = st.text_input("Enter your name to appear on the leaderboard:", key="tester_name")
    test_input = st.text_area("Test Input (enter a list of positive integers, e.g., [2, 3, 5])")

    if st.button("Submit Test Case"):
        if tester_name and test_input:
            # CORRECTED: Call the function from the 'backend' module
            feedback = backend.run_tester_and_get_feedback(tester_name, test_input)
            st.subheader("Feedback")
            st.write(feedback)
        else:
            st.warning("Please enter your name and a test case.")

# --- 5. Discussion ---
with tabs[4]:
    st.header("Discussion")

    commenter_name = st.text_input("Your Name:", key="commenter_name")
    discussion_text = st.text_area("Add your comment or question:")

    if st.button("Post"):
        if commenter_name and discussion_text:
            # CORRECTED: Call the function from the 'database' module
            database.add_comment(commenter_name, discussion_text)
            st.success("Your comment has been posted.")
        else:
            st.warning("Please enter your name and a comment.")

    st.subheader("Community Discussion")
    # CORRECTED: Call the function from the 'database' module
    comments = database.get_comments()
    for comment in reversed(comments):  # Show newest first
        st.markdown(f"**{comment['name']}** ({comment['timestamp']}):")
        st.markdown(f"> {comment['text']}")

# --- 6. Leaderboards ---
with tabs[5]:
    st.header("Leaderboards")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏆 Solver Leaderboard")
        # CORRECTED: Call the function from the 'backend' module
        solver_df = backend.get_solver_leaderboard()
        st.dataframe(solver_df, use_container_width=True)

    with col2:
        st.subheader("🎯 Tester Leaderboard")
        # CORRECTED: Call the function from the 'backend' module
        tester_df = backend.get_tester_leaderboard()
        st.dataframe(tester_df, use_container_width=True)
