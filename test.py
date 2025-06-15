# test.py

import streamlit as st
from streamlit_ace import st_ace
import pandas as pd
import backend
import database
from streamlit_google_oauth import google_oauth # Import the new library

# --- Page and Database Setup ---
st.set_page_config(page_title="ConjectureQ", layout="wide")
database.init_db()

# --- OAuth Configuration (Hardcoded Credentials) ---
CLIENT_ID = "877328479737-s8d7566e5otp0omrll36qk9t6vpopm6k.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "http://localhost:8501" # This must match your Google Cloud setup

# --- Session State Management ---
if 'user_info' not in st.session_state:
    st.session_state.user_info = None

# --- Login Flow using the new library ---
# The google_oauth function returns the user's email if logged in, otherwise None
user_email, user_info = google_oauth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    login_button_text="Login with Google",
    logout_button_text="Logout",
)

# If the user is logged in, store their info in the session state
if user_email and user_info:
    st.session_state.user_info = user_info
    # Add email to the user_info dict for consistency, as some older library versions did this
    st.session_state.user_info['email'] = user_email
elif not user_email and not user_info: # This condition triggers on logout
    st.session_state.user_info = None


# --- Main Application UI ---
if st.session_state.user_info:
    st.sidebar.title(f"Welcome, {st.session_state.user_info.get('name', 'User')}!")
    st.sidebar.image(st.session_state.user_info.get('picture'), width=100)
    st.sidebar.write(f"**Email:** {st.session_state.user_info.get('email')}")

st.title("ConjectureQ: Interactive Coding Challenges for Open Conjectures")

# Conditionally add "My Submissions" tab if logged in
tab_list = ["Problem Statement", "Background", "Solver", "Tester", "Discussion", "Leaderboards"]
if st.session_state.user_info:
    tab_list.insert(3, "My Submissions")

tabs = st.tabs(tab_list)

# ... (Problem Statement and Background tabs are the same)
with tabs[0]:
    st.header("Problem Statement")
    st.markdown("**Conjecture (true form):** Describe the conjecture here.")
    st.markdown("**Coding challenge:** Provide instructions for the coding task.")
with tabs[1]:
    st.header("Background")
    st.markdown("- Relevant papers: List and links to papers.")
    st.markdown("- Axioms and definitions: Provide key definitions.")

# --- Solver Tab ---
with tabs[2]:
    st.header("Solver Portal")
    if st.session_state.user_info:
        st.markdown(f"Submit your solution below, **{st.session_state.user_info.get('name')}**.")
        code = st_ace(placeholder="# Your function must be named 'solve'", language="python", theme="monokai", key="solver_editor")
        if st.button("Run Solution"):
            user_email = st.session_state.user_info.get('email')
            results = backend.run_solution_and_get_results(user_email, code)
            st.subheader("Results")
            st.write(results)
            st.success("Your submission has been saved! Check the 'My Submissions' tab.")
    else:
        st.warning("Please log in with Google to submit a solution.")

# --- My Submissions Tab (New and Conditional) ---
if st.session_state.user_info:
    with tabs[3]:
        st.header("My Past Submissions")
        user_email = st.session_state.user_info.get('email')
        my_submissions = database.get_user_submissions(user_email)
        if not my_submissions:
            st.info("You haven't submitted any solutions yet.")
        else:
            for i, sub in enumerate(my_submissions):
                with st.expander(f"Submission #{i+1}", expanded=i==0):
                    st.code(sub['code'], language='python')
                    st.write(f"Tests Passed: {sub.get('tests_passed', 0)}")

# --- The rest of the tabs are shifted ---
tab_offset = 1 if st.session_state.user_info else 0

# --- Tester Tab ---
with tabs[3 + tab_offset]:
    st.header("Tester Portal")
    if st.session_state.user_info:
        user_email = st.session_state.user_info.get('email')
        test_input = st.text_area("Test Input (e.g., [2, 3, 5])")
        if st.button("Submit Test Case"):
            feedback = backend.run_tester_and_get_feedback(user_email, test_input)
            st.subheader("Feedback")
            st.write(feedback)
    else:
        st.warning("Please log in to submit a test case.")

# --- Discussion Tab ---
with tabs[4 + tab_offset]:
    st.header("Discussion")
    if st.session_state.user_info:
        user_name = st.session_state.user_info.get('name')
        discussion_text = st.text_area("Add your comment or question:")
        if st.button("Post"):
            database.add_comment(user_name, discussion_text)
            st.success("Your comment has been posted.")
    else:
        st.warning("Please log in to join the discussion.")

    st.subheader("Community Discussion")
    comments = database.get_comments()
    for comment in reversed(comments):
        st.markdown(f"**{comment['name']}** ({comment['timestamp']}):")
        st.markdown(f"> {comment['text']}")

# --- Leaderboards Tab ---
with tabs[5 + tab_offset]:
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
