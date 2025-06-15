# import streamlit as st
# from streamlit_ace import st_ace
# import pandas as pd
# import backend  # Import the backend module
# import database # Import the database module

# # Initialize the database
# database.init_db()

# # --- Page Configuration ---
# st.set_page_config(
#     page_title="ConjectureQ",
#     layout="wide",
#     initial_sidebar_state="collapsed"
# )

# # --- Main Title ---
# st.title("ConjectureQ: Interactive Coding Challenges for Open Conjectures")

# # --- Tabs for Different Sections ---
# tabs = st.tabs(["Problem Statement", "Background", "Solver", "Tester", "Discussion", "Leaderboards"])

# # --- 1. Problem Statement ---
# with tabs[0]:
#     st.header("Problem Statement")
#     st.markdown("""
#         **Conjecture (True Form):** For any given set of positive integers, there exists a sequence of operations (addition, subtraction, multiplication) that will result in a prime number.

#         **Coding Challenge:** Write a Python function `solve(numbers: list[int]) -> bool` that takes a list of positive integers and returns `True` if a prime number can be formed using the allowed operations, and `False` otherwise. Your solution should be both correct and efficient.
#     """)

# # --- 2. Background ---
# with tabs[1]:
#     st.header("Background")
#     st.markdown("""
#         - **Relevant Papers:**
#             - [An Introduction to Number Theory](https://www.ams.org/bookstore-getitem/item=ST-8)
#             - [Computational Aspects of Number Theory](https://www.springer.com/gp/book/9783540441215)
#         - **Axioms and Definitions:**
#             - **Positive Integer:** An integer greater than 0.
#             - **Prime Number:** A positive integer greater than 1 that has no positive divisors other than 1 and itself.
#     """)

# # --- 3. Solver ---
# with tabs[2]:
#     st.header("Solver Portal")
#     st.markdown("Submit your solution code below and run it to see real-time results:")

#     solver_name = st.text_input("Enter your name to appear on the leaderboard:", key="solver_name")

#     code = st_ace(
#         placeholder="""# Your function must be named 'solve'
# # Example:
# # def solve(numbers: list[int]) -> bool:
# #     # ... your logic here ...
# #     return True
# """,
#         language="python",
#         theme="monokai",
#         keybinding="vscode",
#         font_size=14,
#         tab_size=4,
#         show_gutter=True,
#         show_print_margin=False,
#         wrap=True,
#         auto_update=False,
#         key="solver_editor"
#     )

#     if st.button("Run Solution"):
#         if solver_name and code:
#             # CORRECTED: Call the function from the 'backend' module
#             results = backend.run_solution_and_get_results(solver_name, code)
#             st.subheader("Results")
#             st.write(results)
#         else:
#             st.warning("Please enter your name and provide a solution.")

# # --- 4. Tester ---
# with tabs[3]:
#     st.header("Tester Portal")
#     st.markdown("Submit test cases or edge cases to challenge the solvers' submissions:")

#     tester_name = st.text_input("Enter your name to appear on the leaderboard:", key="tester_name")
#     test_input = st.text_area("Test Input (enter a list of positive integers, e.g., [2, 3, 5])")

#     if st.button("Submit Test Case"):
#         if tester_name and test_input:
#             # CORRECTED: Call the function from the 'backend' module
#             feedback = backend.run_tester_and_get_feedback(tester_name, test_input)
#             st.subheader("Feedback")
#             st.write(feedback)
#         else:
#             st.warning("Please enter your name and a test case.")

# # --- 5. Discussion ---
# with tabs[4]:
#     st.header("Discussion")

#     commenter_name = st.text_input("Your Name:", key="commenter_name")
#     discussion_text = st.text_area("Add your comment or question:")

#     if st.button("Post"):
#         if commenter_name and discussion_text:
#             # CORRECTED: Call the function from the 'database' module
#             database.add_comment(commenter_name, discussion_text)
#             st.success("Your comment has been posted.")
#         else:
#             st.warning("Please enter your name and a comment.")

#     st.subheader("Community Discussion")
#     # CORRECTED: Call the function from the 'database' module
#     comments = database.get_comments()
#     for comment in reversed(comments):  # Show newest first
#         st.markdown(f"**{comment['name']}** ({comment['timestamp']}):")
#         st.markdown(f"> {comment['text']}")

# # --- 6. Leaderboards ---
# with tabs[5]:
#     st.header("Leaderboards")
#     col1, col2 = st.columns(2)

#     with col1:
#         st.subheader("🏆 Solver Leaderboard")
#         # CORRECTED: Call the function from the 'backend' module
#         solver_df = backend.get_solver_leaderboard()
#         st.dataframe(solver_df, use_container_width=True)

#     with col2:
#         st.subheader("🎯 Tester Leaderboard")
#         # CORRECTED: Call the function from the 'backend' module
#         tester_df = backend.get_tester_leaderboard()
#         st.dataframe(tester_df, use_container_width=True)



# test.py

import streamlit as st
from streamlit_ace import st_ace
import pandas as pd
import backend
import database

# Initialize the database (creates users.csv if it doesn't exist)
database.init_db()

# --- Initialize Session State ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""

# --- Sidebar for Login/Signup ---
st.sidebar.title("User Account")

if st.session_state.logged_in:
    st.sidebar.success(f"Logged in as **{st.session_state.username}**")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()
else:
    login_tab, signup_tab = st.sidebar.tabs(["Login", "Sign Up"])

    with login_tab:
        st.header("Login")
        login_user = st.text_input("Username", key="login_user")
        login_pass = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if database.verify_user(login_user, login_pass):
                st.session_state.logged_in = True
                st.session_state.username = login_user
                st.rerun()
            else:
                st.sidebar.error("Invalid username or password.")

    with signup_tab:
        st.header("Create Account")
        new_user = st.text_input("Choose a Username", key="new_user")
        new_pass = st.text_input("Choose a Password", type="password", key="new_pass")
        if st.button("Sign Up"):
            if database.add_user(new_user, new_pass):
                st.sidebar.success("Account created! Please login.")
            else:
                st.sidebar.error("Username already exists.")


# --- Page Configuration ---
st.set_page_config(
    page_title="ConjectureQ",
    layout="wide"
)

# --- Main Title ---
st.title("ConjectureQ: Interactive Coding Challenges for Open Conjectures")


# --- Tabs for Different Sections ---
# Conditionally add "My Submissions" tab if logged in
tab_list = ["Problem Statement", "Background", "Solver", "Tester", "Discussion", "Leaderboards"]
if st.session_state.logged_in:
    tab_list.insert(3, "My Submissions") # Insert after Solver

tabs = st.tabs(tab_list)

# --- Problem Statement Tab ---
with tabs[0]:
    st.header("Problem Statement")
    st.markdown("""
        **Conjecture (True Form):** For any given set of positive integers...
        **Coding Challenge:** Write a Python function `solve(numbers: list[int]) -> bool`...
    """)

# --- Background Tab ---
with tabs[1]:
    st.header("Background")
    st.markdown("""
        - **Relevant Papers:** ...
        - **Axioms and Definitions:** ...
    """)

# --- Solver Tab ---
with tabs[2]:
    st.header("Solver Portal")
    if st.session_state.logged_in:
        st.markdown(f"Welcome, **{st.session_state.username}**! Submit your solution below.")
        
        code = st_ace(
            placeholder="# Your function must be named 'solve'",
            language="python", theme="monokai", key="solver_editor"
        )

        if st.button("Run Solution"):
            # Automatically use the logged-in username
            results = backend.run_solution_and_get_results(st.session_state.username, code)
            st.subheader("Results")
            st.write(results)
            st.success("Your submission has been saved! Check the 'My Submissions' tab.")
    else:
        st.warning("Please log in to submit a solution.")

# --- My Submissions Tab (New and Conditional) ---
if st.session_state.logged_in:
    with tabs[3]:
        st.header("My Past Submissions")
        st.markdown("Here is a history of your submitted code.")
        
        my_submissions = database.get_user_submissions(st.session_state.username)
        
        if not my_submissions:
            st.info("You haven't submitted any solutions yet.")
        else:
            for i, sub in enumerate(my_submissions):
                with st.expander(f"Submission from {sub.get('timestamp', 'older')}", expanded=i==0):
                    st.code(sub['code'], language='python')
                    st.write(f"Tests Passed: {sub['tests_passed']}")

# --- The rest of the tabs are shifted by 1 if logged in ---
tester_tab_index = 4 if st.session_state.logged_in else 3
discussion_tab_index = 5 if st.session_state.logged_in else 4
leaderboard_tab_index = 6 if st.session_state.logged_in else 5

# --- Tester Tab ---
with tabs[tester_tab_index]:
    st.header("Tester Portal")
    if st.session_state.logged_in:
        st.markdown("Submit test cases or edge cases to challenge the solvers' submissions:")
        test_input = st.text_area("Test Input (e.g., [2, 3, 5])")
        if st.button("Submit Test Case"):
            feedback = backend.run_tester_and_get_feedback(st.session_state.username, test_input)
            st.subheader("Feedback")
            st.write(feedback)
    else:
        st.warning("Please log in to submit a test case.")

# --- Discussion Tab ---
with tabs[discussion_tab_index]:
    st.header("Discussion")
    if st.session_state.logged_in:
        discussion_text = st.text_area("Add your comment or question:")
        if st.button("Post"):
            database.add_comment(st.session_state.username, discussion_text)
            st.success("Your comment has been posted.")
    else:
        st.warning("Please log in to join the discussion.")

    st.subheader("Community Discussion")
    comments = database.get_comments()
    for comment in reversed(comments):
        st.markdown(f"**{comment['name']}** ({comment['timestamp']}):")
        st.markdown(f"> {comment['text']}")

# --- Leaderboards Tab ---
with tabs[leaderboard_tab_index]:
    st.header("Leaderboards")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏆 Solver Leaderboard")
        solver_df = backend.get_solver_leaderboard()
        st.dataframe(solver_df, use_container_width=True)
    with col2:
        st.subheader("🎯 Tester Leaderboard")
        tester_df = backend.get_tester_leaderboard()
        st.dataframe(tester_df, use_container_width=True)
