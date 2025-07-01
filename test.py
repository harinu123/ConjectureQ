# test.py

import streamlit as st
from streamlit_ace import st_ace
import pandas as pd

# --- Local Imports ---
import backend
import database
from authenticate import Authenticator

# --- Initialize ---
database.init_db()

# --- App Title and Page Config ---
st.set_page_config(page_title="ConjectureQ", layout="wide")
st.title("ConjectureQ: Interactive Coding Challenges for unsolved problems")

# --- Authentication with hardcoded secrets ---
CLIENT_ID = "877328479737-s8d7566e5otp0omrll36qk9t6vpopm6k.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "https://conjectureq-hari.streamlit.app/"
# This key is used to sign the session cookie. You can change it to any secret string.
TOKEN_KEY = "my_super_secret_token_key_12345"

authenticator = Authenticator(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    token_key=TOKEN_KEY,
)

# This function checks for cookies and URL auth codes.
authenticator.check_authentication()

# --- Main App Logic ---
# If user is not connected, show login button and stop.
if not st.session_state.get("connected"):
    # st.image("https://www.googleapis.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png", width=200)
    st.header("Welcome!")
    st.write("Please log in with your Google account to participate.")
    authenticator.login_widget()
    st.stop()

# --- If user IS connected, show the full application ---

# Sidebar with user info and logout button
st.sidebar.title(f"Welcome, {st.session_state['user_info'].get('name', 'User')}!")
st.sidebar.image(st.session_state['user_info'].get('picture'), width=100, use_column_width='auto')
st.sidebar.write(f"**Email:** {st.session_state['user_info'].get('email')}")
if st.sidebar.button("Logout"):
    authenticator.logout()

# --- Application Tabs ---
tab_list = ["Problem Statement", "Background", "Solver", "My Submissions", "Tester", "Discussion", "Leaderboards"]
tabs = st.tabs(tab_list)

with tabs[0]:
    st.header("Problem Statement")
    st.markdown("""
        **Conjecture (True Form):** For any given set of positive integers, there exists a sequence of operations (addition, subtraction, multiplication) that will result in a prime number.
        **Coding Challenge:** Write a Python function `solve(numbers: list[int]) -> bool` that takes a list of positive integers and returns `True` if a prime number can be formed, and `False` otherwise.
    """)

with tabs[1]:
    st.header("Background")
    st.markdown("""
        - **Relevant Papers:** [An Introduction to Number Theory](https://www.ams.org/bookstore-getitem/item=ST-8)
        - **Axioms and Definitions:** A **prime number** is a positive integer greater than 1 that has no positive divisors other than 1 and itself.
    """)

with tabs[2]:
    st.header("Solver Portal")
    code = st_ace(placeholder="# Your function must be named 'solve'", language="python", theme="monokai", key="solver_editor")
    if st.button("Run Solution"):
        user_email = st.session_state['user_info'].get('email')
        results = backend.run_solution_and_get_results(user_email, code)
        st.subheader("Results")
        st.write(results)
        st.success("Your submission has been saved! Check the 'My Submissions' tab.")

with tabs[3]:
    st.header("My Past Submissions")
    user_email = st.session_state['user_info'].get('email')
    my_submissions = database.get_user_submissions(user_email)
    if not my_submissions:
        st.info("You haven't submitted any solutions yet.")
    else:
        # Show the most recent submission first
        for i, sub in enumerate(reversed(my_submissions)):
            with st.expander(f"Submission #{len(my_submissions) - i}", expanded=(i==0)):
                st.code(sub['code'], language='python')
                st.write(f"Tests Passed: {sub.get('tests_passed', 0)}")

with tabs[4]:
    st.header("Tester Portal")
    test_input = st.text_area("Test Input (e.g., [2, 3, 5])")
    if st.button("Submit Test Case"):
        user_email = st.session_state['user_info'].get('email')
        feedback = backend.run_tester_and_get_feedback(user_email, test_input)
        st.subheader("Feedback")
        st.write(feedback)

with tabs[5]:
    st.header("Discussion")
    user_name = st.session_state['user_info'].get('name')
    discussion_text = st.text_area("Add your comment or question:")
    if st.button("Post"):
        database.add_comment(user_name, discussion_text)
        st.success("Your comment has been posted.")
    
    st.subheader("Community Discussion")
    comments = database.get_comments()
    for comment in reversed(comments):
        st.markdown(f"**{comment['name']}** ({comment.get('timestamp', '')}):")
        st.markdown(f"> {comment['text']}")

with tabs[6]:
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
