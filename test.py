# # ----------------------- Solver Portal ------------------------------------
# with tabs[2]:
#     st.header("Solver Portal  🧩  (write your sampling policy)")
#     st.markdown("""
#     **Template**  

#     ```python
#     # Mandatory signature
#     def solve(n_samples: int) -> list[int]:
#         import random
#         random.seed(42)          # keep it deterministic
#         return random.sample(range(n_samples), k=n_samples)  # naive uniform shuffle
#     ```
#     """)
#     code = st_ace(
#         placeholder="# define solve(n_samples) here…",
#         language="python",
#         theme="monokai",
#         key="solver_editor",
#         height=300,
#     )
#     if st.button("Submit Solver"):
#         email = st.session_state["user_info"]["email"]
#         out = backend.run_solution_and_get_results(email, code)
#         st.json(out)

# # ----------------------- Tester Portal ------------------------------------
# with tabs[4]:
#     st.header("Tester Portal  🐉  (upload adversarial batch)")
#     st.markdown("Paste **Python-style** list of 784-long rows, e.g. `[[0,0,…,0],[…]]`")
#     test_input = st.text_area("Your batch here")
#     if st.button("Submit Batch"):
#         email = st.session_state["user_info"]["email"]
#         feedback = backend.run_tester_and_get_feedback(email, test_input)
#         st.json(feedback)

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
st.title("Conjecture Bytes:")

# --- Authentication with hard-coded secrets (unchanged) ---
CLIENT_ID     = "877328479737-s8d7566e5otp0omrll36qk9t6vpopm6k.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI  = "https://conjectureq.streamlit.app/"
TOKEN_KEY     = "my_super_secret_token_key_12345"

authenticator = Authenticator(
    client_id     = CLIENT_ID,
    client_secret = CLIENT_SECRET,
    redirect_uri  = REDIRECT_URI,
    token_key     = TOKEN_KEY,
)

# This checks cookies / OAuth code.
authenticator.check_authentication()

# If user is NOT connected ---------------------------------------------------
if not st.session_state.get("connected"):
    st.image(
        "https://www.googleapis.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png",
        width=200,
    )
    st.header("Welcome!")
    st.write("Please log in with your Google account to participate.")
    authenticator.login_widget()
    st.stop()

# Sidebar --------------------------------------------------------------------
st.sidebar.title(f"Welcome, {st.session_state['user_info'].get('name', 'User')}!")
st.sidebar.image(
    st.session_state['user_info'].get('picture'), width=100, use_column_width='auto'
)
st.sidebar.write(f"**Email:** {st.session_state['user_info'].get('email')}")
if st.sidebar.button("Logout"):
    authenticator.logout()

# ----------------------- Create the eight tabs ------------------------------
tab_list = [
    "Problem Statement",
    "Background",
    "Solver",
    "My Submissions",
    "Tester",
    "Discussion",
    "Leaderboards",
]
tabs = st.tabs(tab_list)

# ----------------------- Problem Statement ----------------------------------
with tabs[0]:
    st.header("Problem Statement")
    st.markdown(
        """
        **Conjecture (True Form):**

        **Coding Challenge:**
        """
    )

# ----------------------- Background -----------------------------------------
with tabs[1]:
    st.header("Background")
    st.markdown(
        """
        - **Relevant Papers:** [An Introduction to Number Theory](https://www.ams.org/bookstore-getitem/item=ST-8)
        - **Axioms and Definitions:** A **prime number** is a positive integer greater than 1 that has no positive divisors other than 1 and itself.
        """
    )

# ----------------------- Solver Portal (NEW) --------------------------------
with tabs[2]:
    st.header("Solver Portal  🧩  (write your sampling policy)")
    st.markdown(
        """
        **Template**

        ```python
        # Mandatory signature
        def solve(n_samples: int) -> list[int]:
            import random
            random.seed(42)          # keep it deterministic
            return random.sample(range(n_samples), k=n_samples)  # naive uniform shuffle
        ```
        """
    )
    code = st_ace(
        placeholder="# define solve(n_samples) here…",
        language="python",
        theme="monokai",
        key="solver_editor",
        height=300,
    )
    if st.button("Submit Solver"):
        email = st.session_state["user_info"]["email"]
        out   = backend.run_solution_and_get_results(email, code)
        st.json(out)

# ----------------------- My Submissions -------------------------------------
with tabs[3]:
    st.header("My Past Submissions")
    email = st.session_state["user_info"]["email"]
    subs  = database.get_user_submissions(email)
    if not subs:
        st.info("You haven't submitted any solutions yet.")
    else:
        for i, sub in enumerate(reversed(subs)):
            with st.expander(f"Submission #{len(subs) - i}", expanded=(i == 0)):
                st.code(sub["code"], language="python")
                st.write(f"Pass: {sub.get('tests_passed', 0)}")

# ----------------------- Tester Portal (NEW) --------------------------------
with tabs[4]:
    st.header("Tester Portal  🐉  (upload adversarial batch)")
    st.markdown(
        "Paste **Python-style** list of 784-long rows, e.g. `[[0,0,…,0],[…]]`"
    )
    test_input = st.text_area("Your batch here")
    if st.button("Submit Batch"):
        email    = st.session_state["user_info"]["email"]
        feedback = backend.run_tester_and_get_feedback(email, test_input)
        st.json(feedback)

# ----------------------- Discussion -----------------------------------------
with tabs[5]:
    st.header("Discussion")
    user_name = st.session_state["user_info"].get("name")
    txt = st.text_area("Add your comment or question:")
    if st.button("Post"):
        database.add_comment(user_name, txt)
        st.success("Your comment has been posted.")
    st.subheader("Community Discussion")
    for c in reversed(database.get_comments()):
        st.markdown(f"**{c['name']}** ({c.get('timestamp', '')}):")
        st.markdown(f"> {c['text']}")

# ----------------------- Leaderboards ---------------------------------------
with tabs[6]:
    st.header("Leaderboards")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🏆 Solver Leaderboard")
        st.dataframe(backend.get_solver_leaderboard(), use_container_width=True)
    with c2:
        st.subheader("🎯 Tester Leaderboard")
        st.dataframe(backend.get_tester_leaderboard(), use_container_width=True)
