# test.py

import streamlit as st
from streamlit_ace import st_ace
import pandas as pd
import backend
import database
from streamlit_oauth import OAuth2Component # Import the OAuth library

# --- Page and Database Setup ---
st.set_page_config(page_title="ConjectureQ", layout="wide")
database.init_db()

# --- OAuth Configuration (Hardcoded Credentials) ---
# WARNING: This is not a secure practice for production apps.
# Replace the placeholder text with your actual credentials from Google Cloud.
CLIENT_ID = 877328479737-s8d7566e5otp0omrll36qk9t6vpopm6k.apps.googleusercontent.com 
CLIENT_SECRET = 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
REDIRECT_URI = "http://localhost:8501" # This must match your Google Cloud setup

# Make sure you have filled in your credentials above.
if CLIENT_ID == "PASTE_YOUR_CLIENT_ID_HERE" or CLIENT_SECRET == "PASTE_YOUR_CLIENT_SECRET_HERE":
    st.error("OAuth credentials are not configured. Please edit test.py to add your Client ID and Client Secret.")
    st.stop()

# Create an OAuth2Component instance
oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET,
    authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
    token_url="https://oauth2.googleapis.com/token",
    refresh_token_url="https://oauth2.googleapis.com/token",
    revoke_token_url="https://oauth2.googleapis.com/revoke",
)

# --- Session State Management ---
if 'user_info' not in st.session_state:
    st.session_state.user_info = None

# --- Login Button and User Info Fetching ---
# The button is displayed in the main body of the app if the user is not logged in.
if not st.session_state.user_info:
    result = oauth2.authorize_button(
        name="Login with Google",
        icon="https://www.google.com.tw/favicon.ico",
        redirect_uri=REDIRECT_URI,
        scope="openid email profile",
        key="google",
        use_container_width=True,
        pkce='S256',
    )
    if result:
        st.session_state.user_info = result.get('userinfo')
        st.rerun()
else: # If user is logged in, show their info and a logout button in the sidebar.
    user = st.session_state.user_info
    st.sidebar.title(f"Welcome, {user.get('name', 'User')}!")
    st.sidebar.image(user.get('picture'), width=100)
    st.sidebar.write(f"**Email:** {user.get('email')}")
    if st.sidebar.button("Logout"):
        st.session_state.user_info = None
        st.rerun()

# --- Main Application UI ---
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
