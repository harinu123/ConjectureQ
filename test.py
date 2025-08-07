

# # import streamlit as st
# # from streamlit_ace import st_ace
# # import pandas as pd

# # # --- Local Imports ---
# # import backend
# # import database
# # from authenticate import Authenticator

# # # --- Initialize ---
# # database.init_db()

# # # --- App Title and Page Config ---
# # st.set_page_config(page_title="ConjectureQ", layout="wide")
# # st.title("Conjecture Bytes:")

# # # --- Authentication with hard-coded secrets (unchanged) ---
# # CLIENT_ID     = "877328479737-s8d7566e5otp0omrll36qk9t6vpopm6k.apps.googleusercontent.com"
# # CLIENT_SECRET = "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"
# # REDIRECT_URI  = "https://conjectureq.streamlit.app/"
# # TOKEN_KEY     = "my_super_secret_token_key_12345"

# # authenticator = Authenticator(
# #     client_id     = CLIENT_ID,
# #     client_secret = CLIENT_SECRET,
# #     redirect_uri  = REDIRECT_URI,
# #     token_key     = TOKEN_KEY,
# # )

# # # This checks cookies / OAuth code.
# # authenticator.check_authentication()

# # # If user is NOT connected ---------------------------------------------------
# # if not st.session_state.get("connected"):
# #     st.image(
# #         "https://www.googleapis.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png",
# #         width=200,
# #     )
# #     st.header("Welcome!")
# #     st.write("Please log in with your Google account to participate.")
# #     authenticator.login_widget()
# #     st.stop()

# # # Sidebar --------------------------------------------------------------------
# # st.sidebar.title(f"Welcome, {st.session_state['user_info'].get('name', 'User')}!")
# # st.sidebar.image(
# #     st.session_state['user_info'].get('picture'), width=100, use_column_width='auto'
# # )
# # st.sidebar.write(f"**Email:** {st.session_state['user_info'].get('email')}")
# # if st.sidebar.button("Logout"):
# #     authenticator.logout()

# # # ----------------------- Create the eight tabs ------------------------------
# # tab_list = [
# #     "Problem Statement",
# #     "Background",
# #     "Solver",
# #     "My Submissions",
# #     "Tester",
# #     "Discussion",
# #     "Leaderboards",
# # ]
# # tabs = st.tabs(tab_list)

# # # ----------------------- Problem Statement ----------------------------------
# # with tabs[0]:
# #     st.header("Problem Statement")
# #     st.markdown(
# #         """
# #         **Conjecture (True Form):**

# #         **Coding Challenge:**
# #         """
# #     )

# # # ----------------------- Background -----------------------------------------
# # with tabs[1]:
# #     st.header("Background")
# #     st.markdown(
# #         """
# #         - **Relevant Papers:** [An Introduction to Number Theory](https://www.ams.org/bookstore-getitem/item=ST-8)
# #         - **Axioms and Definitions:** A **prime number** is a positive integer greater than 1 that has no positive divisors other than 1 and itself.
# #         """
# #     )

# # # ----------------------- Solver Portal (NEW) --------------------------------
# # with tabs[2]:
# #     st.header("Solver Portal  🧩  (write your sampling policy)")
# #     st.markdown(
# #         """
# #         **Template**

# #         ```python
# #         # Mandatory signature
# #         def solve(n_samples: int) -> list[int]:
# #             import random
# #             random.seed(42)          # keep it deterministic
# #             return random.sample(range(n_samples), k=n_samples)  # naive uniform shuffle
# #         ```
# #         """
# #     )
# #     code = st_ace(
# #         placeholder="# define solve(n_samples) here…",
# #         language="python",
# #         theme="monokai",
# #         key="solver_editor",
# #         height=300,
# #     )
# #     if st.button("Submit Solver"):
# #         email = st.session_state["user_info"]["email"]
# #         out   = backend.run_solution_and_get_results(email, code)
# #         st.json(out)

# # # ----------------------- My Submissions -------------------------------------
# # with tabs[3]:
# #     st.header("My Past Submissions")
# #     email = st.session_state["user_info"]["email"]
# #     subs  = database.get_user_submissions(email)
# #     if not subs:
# #         st.info("You haven't submitted any solutions yet.")
# #     else:
# #         for i, sub in enumerate(reversed(subs)):
# #             with st.expander(f"Submission #{len(subs) - i}", expanded=(i == 0)):
# #                 st.code(sub["code"], language="python")
# #                 st.write(f"Pass: {sub.get('tests_passed', 0)}")

# # # ----------------------- Tester Portal (NEW) --------------------------------
# # with tabs[4]:
# #     st.header("Tester Portal  🐉  (upload adversarial batch)")
# #     st.markdown(
# #         "Paste **Python-style** list of 784-long rows, e.g. `[[0,0,…,0],[…]]`"
# #     )
# #     test_input = st.text_area("Your batch here")
# #     if st.button("Submit Batch"):
# #         email    = st.session_state["user_info"]["email"]
# #         feedback = backend.run_tester_and_get_feedback(email, test_input)
# #         st.json(feedback)

# # # ----------------------- Discussion -----------------------------------------
# # with tabs[5]:
# #     st.header("Discussion")
# #     user_name = st.session_state["user_info"].get("name")
# #     txt = st.text_area("Add your comment or question:")
# #     if st.button("Post"):
# #         database.add_comment(user_name, txt)
# #         st.success("Your comment has been posted.")
# #     st.subheader("Community Discussion")
# #     for c in reversed(database.get_comments()):
# #         st.markdown(f"**{c['name']}** ({c.get('timestamp', '')}):")
# #         st.markdown(f"> {c['text']}")

# # # ----------------------- Leaderboards ---------------------------------------
# # with tabs[6]:
# #     st.header("Leaderboards")
# #     c1, c2 = st.columns(2)
# #     with c1:
# #         st.subheader("🏆 Solver Leaderboard")
# #         st.dataframe(backend.get_solver_leaderboard(), use_container_width=True)
# #     with c2:
# #         st.subheader("🎯 Tester Leaderboard")
# #         st.dataframe(backend.get_tester_leaderboard(), use_container_width=True)


# import textwrap
# import streamlit as st
# from streamlit_ace import st_ace
# import pandas as pd

# # ─────────────────────────────────────────────────────────────────────────────
# #  Local Imports
# # ─────────────────────────────────────────────────────────────────────────────
# import backend
# import database
# from authenticate import Authenticator

# # ─────────────────────────────────────────────────────────────────────────────
# #  Initialise database & page
# # ─────────────────────────────────────────────────────────────────────────────
# database.init_db()
# st.set_page_config(page_title="ConjectureQ", layout="wide", page_icon="🧩")

# # ─────────────────────────────────────────────────────────────────────────────
# #  Global CSS (Google font, gradient background, button styling, …)
# # ─────────────────────────────────────────────────────────────────────────────
# st.markdown(
#     """
#     <style>
#       @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

#       html, body, [class*="stApp"]  {
#           font-family: 'Inter', sans-serif;
#           background: radial-gradient(circle at top left, #0f2027, #203a43, #2c5364);
#       }

#       /* Hide Streamlit default chrome */
#       #MainMenu {visibility: hidden;}
#       footer, header {visibility: hidden;}

#       /* ---------- Landing page styles ---------- */
#       .landing-wrapper {
#           display: flex;
#           flex-direction: column;
#           gap: .5rem;
#           padding: 4rem 2rem;
#           color: #fff;
#       }
#       .landing-wrapper h1   {font-size: 3.4rem; font-weight: 800; margin: 0 0 .25rem 0;}
#       .landing-wrapper .sub {font-size: 1.2rem; font-weight: 300; opacity: .9;}
#       .landing-wrapper ul   {font-size: 1.05rem; margin-left: 1.25rem; line-height: 1.5;}
#       .landing-wrapper li::marker {content: "• "; color: #db5cff;}

#       /* nice gradient button */
#       .stButton > button {
#           background: linear-gradient(135deg,#7f00ff 0%,#e100ff 100%);
#           color: #fff; border: none; padding: .75rem 1.5rem;
#           border-radius: .6rem; font-size: 1.05rem; font-weight: 600;
#           transition: transform .12s ease-in-out, box-shadow .12s;
#       }
#       .stButton > button:hover {
#           transform: scale(1.05);
#           box-shadow: 0 0 10px #e100ff80;
#       }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )

# # ─────────────────────────────────────────────────────────────────────────────
# #  Landing-page session flag
# # ─────────────────────────────────────────────────────────────────────────────
# if "show_app" not in st.session_state:
#     st.session_state.show_app = False

# if not st.session_state.show_app:
#     hero_html = textwrap.dedent(
#         """
#         <div class="landing-wrapper">
#           <h1>Welcome to ConjectureQ</h1>
#           <p class="sub">Gamify theoretical research by turning open problems into interactive coding challenges.</p>

#           <h4>🔍&nbsp;What you’ll do:</h4>
#           <ul>
#             <li><strong>Tester</strong> – craft <em>adversarial</em> MNIST batches that break your peers’ sampling policies.</li>
#             <li><strong>Solver</strong> – write a policy to queue training-data indices so your model stays robust.</li>
#           </ul>

#           <h4>🏆&nbsp;Leaderboards:</h4>
#           <p>Track top 🐉 Testers and 🧩 Solvers as you edge toward the frontier of ML puzzles.</p>
#         </div>
#         """
#     )
#     st.markdown(hero_html, unsafe_allow_html=True)

#     if st.button("▶️ Enter ConjectureQ"):
#         st.session_state.show_app = True
#         # Streamlit ≥1.29 renamed experimental_rerun → rerun
#         if hasattr(st, "rerun"):
#             st.rerun()
#         else:
#             st.experimental_rerun()

#     st.stop()                     # ← nothing below executes until “Enter” is hit

# # ╭──────────────────────────────────────────────────────────────────────────╮
# # │                       Main Application starts here                       │
# # ╰──────────────────────────────────────────────────────────────────────────╯

# st.title("Conjecture Bytes:")

# # --- Authentication secrets (unchanged) ---
# CLIENT_ID     = "877328479737-s8d7566e5otp0omrll36qk9t6vpopm6k.apps.googleusercontent.com"
# CLIENT_SECRET = "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"
# REDIRECT_URI  = "https://conjectureq.streamlit.app/"
# TOKEN_KEY     = "my_super_secret_token_key_12345"

# authenticator = Authenticator(
#     client_id     = CLIENT_ID,
#     client_secret = CLIENT_SECRET,
#     redirect_uri  = REDIRECT_URI,
#     token_key     = TOKEN_KEY,
# )
# authenticator.check_authentication()

# if not st.session_state.get("connected"):
#     st.image(
#         "https://www.googleapis.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png",
#         width=200,
#         use_container_width=True,
#     )
#     st.header("Welcome!")
#     st.write("Please log in with your Google account to participate.")
#     authenticator.login_widget()
#     st.stop()

# # ───────── Sidebar with user info & logout ─────────
# st.sidebar.title(f"Welcome, {st.session_state['user_info'].get('name', 'User')}!")
# st.sidebar.image(
#     st.session_state['user_info'].get('picture'),
#     width=100,
#     use_container_width=True,
# )
# st.sidebar.write(f"**Email:** {st.session_state['user_info'].get('email')}")
# if st.sidebar.button("Logout"):
#     authenticator.logout()

# # ───────── Main tabs ─────────
# tab_list = [
#     "Problem Statement",
#     "Background",
#     "Solver",
#     "My Submissions",
#     "Tester",
#     "Discussion",
#     "Leaderboards",
# ]
# tabs = st.tabs(tab_list)

# # ---------------- Problem Statement ----------------
# with tabs[0]:
#     st.header("Problem Statement")
#     st.markdown(
#         """
#         **Conjecture (True Form):**

#         **Coding Challenge:**
#         """
#     )

# # ---------------- Background -----------------------
# with tabs[1]:
#     st.header("Background")
#     st.markdown(
#         """
#         - **Relevant Papers:** [An Introduction to Number Theory](https://www.ams.org/bookstore-getitem/item=ST-8)
#         - **Axioms and Definitions:** A **prime number** is a positive integer greater than 1 that has no positive divisors other than 1 and itself.
#         """
#     )

# # ---------------- Solver Portal --------------------
# with tabs[2]:
#     st.header("Solver Portal  🧩  (write your sampling policy)")
#     st.markdown(
#         """
#         **Template**

#         ```python
#         # Mandatory signature
#         def solve(n_samples: int) -> list[int]:
#             import random
#             random.seed(42)
#             return random.sample(range(n_samples), k=n_samples)
#         ```
#         """
#     )
#     code = st_ace(
#         placeholder="# define solve(n_samples) here…",
#         language="python",
#         theme="monokai",
#         key="solver_editor",
#         height=300,
#     )
#     if st.button("Submit Solver"):
#         email = st.session_state["user_info"]["email"]
#         out   = backend.run_solution_and_get_results(email, code)
#         st.json(out)

# # ---------------- My Submissions -------------------
# with tabs[3]:
#     st.header("My Past Submissions")
#     email = st.session_state["user_info"]["email"]
#     subs  = database.get_user_submissions(email)
#     if not subs:
#         st.info("You haven't submitted any solutions yet.")
#     else:
#         for i, sub in enumerate(reversed(subs)):
#             with st.expander(f"Submission #{len(subs) - i}", expanded=(i == 0)):
#                 st.code(sub["code"], language="python")
#                 st.write(f"Pass: {sub.get('tests_passed', 0)}")

# # ---------------- Tester Portal --------------------
# with tabs[4]:
#     st.header("Tester Portal  🐉  (upload adversarial batch)")
#     st.markdown(
#         "Paste **Python-style** list of 784-length rows, e.g. `[[0,0,…,0],[…]]`"
#     )
#     test_input = st.text_area("Your batch here")
#     if st.button("Submit Batch"):
#         email    = st.session_state["user_info"]["email"]
#         feedback = backend.run_tester_and_get_feedback(email, test_input)
#         st.json(feedback)

# # ---------------- Discussion -----------------------
# with tabs[5]:
#     st.header("Discussion")
#     user_name = st.session_state["user_info"].get("name")
#     txt = st.text_area("Add your comment or question:")
#     if st.button("Post"):
#         database.add_comment(user_name, txt)
#         st.success("Your comment has been posted.")
#     st.subheader("Community Discussion")
#     for c in reversed(database.get_comments()):
#         st.markdown(f"**{c['name']}** ({c.get('timestamp', '')}):")
#         st.markdown(f"> {c['text']}")

# # ---------------- Leaderboards ---------------------
# with tabs[6]:
#     st.header("Leaderboards")
#     col1, col2 = st.columns(2)
#     with col1:
#         st.subheader("🏆 Solver Leaderboard")
#         st.dataframe(
#             backend.get_solver_leaderboard(),
#             use_container_width=True
#         )
#     with col2:
#         st.subheader("🎯 Tester Leaderboard")
#         st.dataframe(
#             backend.get_tester_leaderboard(),
#             use_container_width=True
#         )


import streamlit as st, textwrap
from streamlit_ace import st_ace
import pandas as pd

# ── local imports
import backend, database
from authenticate import Authenticator

# ── page
database.init_db()
st.set_page_config("ConjectureQ", "🧩", layout="wide")

# ── global CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Chewy&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');

html,body,[class*="stApp"]{font-family:'Inter',sans-serif;background:#fafafa;}
#MainMenu,header,footer{visibility:hidden;}

.landing-wrapper{display:flex;flex-direction:column;align-items:center;gap:1.2rem;margin-top:4rem;}
.cq-logo{width:180px;object-fit:contain;}
.cq-name{font-family:'Chewy',cursive;font-size:5rem;margin:0;color:#ff46b5;text-shadow:0 3px 6px #ffbae6;}
.tagline{font-size:1.25rem;color:#333;margin-top:-.35rem;}

.card-row{display:flex;gap:2rem;margin-top:2.8rem;}
.card{width:230px;padding:1.7rem 1rem;background:#fff;border:2px dotted #ff7ac4;border-radius:20px;text-align:center;
      transition:transform .15s,box-shadow .15s;cursor:pointer;}
.card:hover{transform:translateY(-6px);box-shadow:0 6px 12px #ffb2e440;}
.card h3{font-family:'Chewy',cursive;font-size:1.75rem;margin:0;color:#333;}
.card p{margin:.4rem 0 0;font-size:.9rem;font-style:italic;color:#777;}

.stButton>button{background:linear-gradient(135deg,#7f00ff 0%,#e100ff 100%);
                 color:#fff;border:none;padding:.8rem 1.7rem;border-radius:.7rem;font-weight:600;font-size:1.05rem;}
</style>
""", unsafe_allow_html=True)

# ── landing-page gate
if "show_app" not in st.session_state:
    st.session_state.show_app = False

if not st.session_state.show_app:
    hero_html = """
<div class="landing-wrapper">
  <!-- If the logo 404s, hide the img -->
  <img src="https://raw.githubusercontent.com/hariharanweb/hosted-assets/main/conjectureq_logo.png"
       alt="ConjectureQ logo" class="cq-logo"
       onerror="this.style.display='none'">
  <h1 class="cq-name">ConjectureQ</h1>
  <p class="tagline">launch your AI bots into live battles</p>

  <div class="card-row">
    <div class="card" onclick="window.location.hash='#solve'">
      <h3>solve</h3><p>for coders</p>
    </div>
    <div class="card" onclick="window.location.hash='#test'">
      <h3>test</h3><p>for breakers</p>
    </div>
  </div>
</div>
"""
    st.markdown(hero_html, unsafe_allow_html=True)

    if st.button("🚀  Enter ConjectureQ"):
        st.session_state.show_app = True
        (st.rerun if hasattr(st,"rerun") else st.experimental_rerun())
    st.stop()

# ── main app below (identical logic) ────────────────────────────────────────
st.title("Conjecture Bytes:")

CLIENT_ID="877328479737-s8d7566e5otp0omrll36qk9t6vpopm6k.apps.googleusercontent.com"
CLIENT_SECRET="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"
REDIRECT_URI="https://conjectureq.streamlit.app/"
TOKEN_KEY="my_super_secret_token_key_12345"

auth=Authenticator(client_id=CLIENT_ID,client_secret=CLIENT_SECRET,
                   redirect_uri=REDIRECT_URI,token_key=TOKEN_KEY)
auth.check_authentication()

if not st.session_state.get("connected"):
    auth.login_widget(); st.stop()

st.sidebar.title(f"Welcome, {st.session_state['user_info'].get('name','User')}!")
st.sidebar.image(st.session_state['user_info'].get('picture'), width=100, use_container_width=True)
st.sidebar.write(f"**Email:** {st.session_state['user_info']['email']}")
if st.sidebar.button("Logout"): auth.logout()

tabs=st.tabs(["Problem Statement","Background","Solver","My Submissions",
              "Tester","Discussion","Leaderboards"])

with tabs[0]:
    st.header("Problem Statement"); st.markdown("…")

with tabs[1]:
    st.header("Background"); st.markdown("…")

with tabs[2]:
    st.header("Solver Portal  🧩")
    st.markdown("""```python
def solve(n:int)->list[int]:
    import random; random.seed(42)
    return random.sample(range(n),k=n)
```""")
    code=st_ace(placeholder="# write solve(n)…",language="python",theme="monokai",
                key="solver_editor",height=280)
    if st.button("Submit Solver"):
        st.json(backend.run_solution_and_get_results(
            st.session_state["user_info"]["email"], code))

with tabs[3]:
    st.header("My Past Submissions")
    subs=database.get_user_submissions(st.session_state["user_info"]["email"])
    if not subs: st.info("None yet.")
    else:
        for i,s in enumerate(reversed(subs)):
            with st.expander(f"Submission #{len(subs)-i}",expanded=i==0):
                st.code(s["code"]); st.write(f"Pass: {s.get('tests_passed',0)}")

with tabs[4]:
    st.header("Tester Portal  🐉")
    txt=st.text_area("Paste 784-length row list")
    if st.button("Submit Batch"):
        st.json(backend.run_tester_and_get_feedback(
            st.session_state["user_info"]["email"], txt))

with tabs[5]:
    st.header("Discussion")
    m=st.text_area("Add comment")
    if st.button("Post"):
        database.add_comment(st.session_state["user_info"]["name"], m); st.success("Posted!")
    for c in reversed(database.get_comments()):
        st.markdown(f"**{c['name']}** ({c.get('timestamp','')}):\n> {c['text']}")

with tabs[6]:
    st.header("Leaderboards")
    c1,c2=st.columns(2)
    with c1: st.subheader("🏆 Solver"); st.dataframe(backend.get_solver_leaderboard(),use_container_width=True)
    with c2: st.subheader("🎯 Tester"); st.dataframe(backend.get_tester_leaderboard(),use_container_width=True)

