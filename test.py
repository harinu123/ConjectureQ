# import streamlit as st
# from streamlit_ace import st_ace
# import pandas as pd

# # --- Local Imports ---
# import backend
# import database
# from authenticate import Authenticator

# # --- Initialize ---
# database.init_db()

# # --- Page Config (and landing-state) ---
# # st.set_page_config(page_title="ConjectureQ", layout="wide")

# # # ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
# # # ┃                           Landing Page Logic                            ┃
# # # ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
# # if "show_app" not in st.session_state:
# #     st.session_state.show_app = False

# # if not st.session_state.show_app:
# #     # Banner / Hero image (host your own or use this placeholder)
# #     st.image(
# #         "https://yourcdn.com/conjectureq_banner.png",
# #         use_column_width=True
# #     )

# #     st.markdown(
# #         """
# #         # Welcome to **ConjectureQ**  

# #         _Gamify theoretical research by turning open problems into interactive coding challenges._

# #         **🔍 What you’ll do:**  
# #         - As a **Tester**, craft “adversarial” MNIST-style batches that break your peers’ sampling policies.  
# #         - As a **Solver**, write a policy to queue training-data indices so your model stays robust.  

# #         **🏆 Leaderboards:**  
# #         Track top 🐉 Testers and 🧩 Solvers as you edge toward the frontier of ML puzzles.
# #         """
# #     )

# #     if st.button("▶️ Enter ConjectureQ"):
# #         st.session_state.show_app = True
# #         st.experimental_rerun()

# #     # Halt here until “Enter” is clicked
# #     st.stop()

# # ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
# # ┃                        Actual App Starts Below Here                      ┃
# # ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

# # --- App Title (after landing) ---
# st.title("Conjecture Q: CHALLENGE 1")

# # --- Authentication with hard-coded secrets ---
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

# # If user is NOT connected, show login and bail
# if not st.session_state.get("connected"):
#     st.image(
#         "https://www.googleapis.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png",
#         width=200,
#     )
#     st.header("Welcome!")
#     st.write("Please log in with your Google account to participate.")
#     authenticator.login_widget()
#     st.stop()

# # --- Sidebar with user info & logout ---
# st.sidebar.title(f"Welcome, {st.session_state['user_info'].get('name', 'User')}!")
# st.sidebar.image(
#     st.session_state['user_info'].get('picture'),
#     width=60,
#     use_container_width='auto'
# )
# st.sidebar.write(f"**Email:** {st.session_state['user_info'].get('email')}")
# if st.sidebar.button("Logout"):
#     authenticator.logout()

# # --- Tabs Setup ---
# tab_list = [
#     "Overview",
#     "Solver",
#     "Solver Submission",
#     "Tester",
#     "Tester Submission",
#     "My Submissions",  
#     "Discussion",
#     "Leaderboards",
# ]
# tabs = st.tabs(tab_list)

# # ----------------------- Problem Statement -------------------------------
# with tabs[0]:
#     st.header("Overview")
#     st.markdown(
#         """
#     This challenge is inspired by what has been called the **“Crazy Conjecture”**, proposed in a talk by Nathan Srebro at **ICLR 2025**
    
#     At its core, the conjecture asks:
    
#     > For any function $ f^*(x) $ representable by a neural network and any input distribution $ D_x $, does there exist a different distribution $ D_x' $ from which only polynomially many samples are enough to train a model—using gradient descent—to perform well on $ D_x $ itself?
    
#     In simpler terms:
    
#     If we can’t change the model architecture or optimizer, can we instead choose **where the training data comes from** to make learning vastly more efficient—even if the new data distribution looks nothing like the test distribution?
    
#     ---
    
#     ## Why This Matters
    
#     This is a fundamental open question in machine learning theory:
    
#     - It’s **not** about tuning hyperparameters or architectures.  
#     - It’s about **constructing training sets** that make learning provably easier.  
#     - If true, it could reshape how we think about **data selection**, **curriculum learning**, and **domain adaptation**.
    
#     ---
    
#     ## The Challenge Setup
    
#     - **Testers** design the hardest possible alternative training distributions $P_i$ (subject to certain constraints).  
#     - **Solvers** design **sampling policies** $ \pi(i) $ that adaptively pick examples to minimize a special scoring function.
    
#     ---
    
#     ## Your Goal
    
#     - **As a Solver** — You are effectively trying to **beat the Crazy Conjecture game**. Given any weird or adversarial distribution from a Tester, your policy should still extract the most useful training sequence to perform well on MNIST.
    
#     - **As a Tester** — You are trying to **break Solvers** by designing distributions that are far from MNIST yet still within the allowed constraints, making it hard for Solvers to succeed.
    
#     ---

#         """
#     )

# # ----------------------- Challenger --------------------------------------
# with tabs[1]:
#     st.header("Adaptive Sampling Policy")
#     st.markdown(
#     # r"""
#     # **Goal.** Implement a **stateful sampling policy** that chooses which indices to feed to SGD so the **average training loss over K steps** (AULC) is minimized.
    
#     # **Fixed training setup (hosted):** MNIST (flattened, normalized to $[-1,1]$), 2-layer MLP $784\!\to\!128\!\xrightarrow{\mathrm{ReLU}}\!10$, Cross-Entropy loss, SGD (lr=0.1), batch=256, seed=1337.
    
#     # **Telemetry you receive each step (for the batch you chose):**
#     # - `indices`: the indices you sampled
#     # - `per_sample_losses`: ndarray[batch] (CE per item)
#     # - *Optional (may be enabled in the portal later):* `probs` (softmax logits), `grad_norm_x` ($\|\nabla_x \ell\|_2$ per item)
    
#     # **Submission API (required):**
#     # - Provide a factory `build_policy(pool_size: int, seed: int) -> SolverPolicy`
#     # - The returned object must implement:
#     #   - `sample(batch_size: int) -> np.ndarray[int]`
#     #   - `update(indices, per_sample_losses, probs=None, grad_norm_x=None) -> None`
    
#     # **Score (lower is better):**
#     # \[
#     # \text{AULC}=\frac{1}{K}\sum_{t=1}^{K}\mathcal{L}_t
#     # \]
#     # Tie-breakers: final loss at step $K$, then wall-clock time.
#     #         """
#     r"""
    
#     ### Objective
#     Design a **sampling policy** that selects, at each training step $t$, a batch of indices from the current pool so as to **minimize** the following scoring function.
    
    
#     Let:
    
#     - $ N $ — total number of tester datasets.  
#     - $ P_i $ — dataset from the $ i $-th tester.  
#     - $ d(P_i, \text{MNIST}) $ — a divergence score measuring how far dataset $ D_i $ is from MNIST.  
    
    
#     $$
#     \text{Score} \;=\; 
#     \frac{\displaystyle \sum_{i=1}^N \; \text{Acc}\big( \text{MNIST} \;|\; \text{train on } P_i \big) \; \cdot \; d(P_i, \text{MNIST})}
#     {\displaystyle \sum_{i=1}^N \; d(P_i, \text{MNIST}) }
#     $$

#     where:

#     - $ \text{Acc}(\cdot) $ is the **test accuracy** on the MNIST test set after training on $ P_i $ with the solver’s sampling policy.
#     - The factor $ d(P_i, \text{MNIST}) $ weights performance more heavily on datasets **further from MNIST**.
    
#     ---
    
#     ### Training Environment (fixed)
#     - **Data:** MNIST train (28×28, grayscale) plus any tester-submitted images appended to the pool.  
#       Pixels are in $[0,1]$ (via `ToTensor()`); tester uploads are divided by $255$ then cast to float.
#     - **Model:** 2-layer MLP
#       $$
#       784 \;\xrightarrow{W_1}\; 256 \;\xrightarrow{\mathrm{ReLU}}\; 10 \;\xrightarrow{W_2}\; \text{(logits)}
#       $$
#     - **Loss:** cross-entropy on logits.
#     - **Optimizer:** SGD (no momentum), learning rate fixed by us.
#     - **Batch size:** $b$ (fixed by the host).  
#     - **Horizon:** $K$ steps (set in the portal).  
#     - **Seed:** fixed and applied to all host-side RNGs.
    
#     The **platform** runs the model/updates; the **solver** controls **which indices** are sampled each step.
    
#     ---
    
#     ### Telemetry (returned to you after each step)
#     For the **batch you chose** at step \(t\):
#     - `indices_t` — the indices you sampled (size \(b\)).
#     - `per_sample_losses_t \in \mathbb{R}^b` — cross-entropy per item (no reduction).
    
#     **Optional (may be enabled in the portal):**
#     - `probs_t \in \mathbb{R}^{b\times 10}` — softmax of logits.
#     - `grad_norm_x_t \in \mathbb{R}^b` — input-gradient norms
#       $$
#       \left\| \nabla_x \,\ell(f(x),y) \right\|_2
#       $$
#       a cheap proxy for importance sampling (higher norm ⇒ potentially higher variance contribution).
    
#     **Not exposed:** full weights, or per-sample gradients outside your batch.
    
#     ---
#     """
#     )

# with tabs[2]:
#     st.header("Submission Portal  🧩  (write your sampling policy)")
#     st.markdown(
#         """
#         **Template**

#         ```python
#         # Mandatory signature
#         def solve(n_samples: int) -> list[int]:
#             import random
#             random.seed(42)          # keep it deterministic
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

# # ----------------------- Tester -----------------------------

# with tabs[3]:
#     st.header("Tester")
#     st.markdown(
#     r"""
#     ## Submit a Dataset *Far* from MNIST
    
#     **Goal.** Upload a synthetic dataset $X_{\text{synth}} \in \mathbb{R}^{n \times 784}$ (flattened $28\times 28$) whose **pixel-value distribution** is maximally different from MNIST, measured by **symmetric KL divergence**.
    
#     ---
    
#     ### What to upload (CSV)
#     - **File:** CSV with **n rows × 784 columns** (one image per row, flattened).
#     - **Header:** optional (both with/without header are accepted).
#     - **Dtype:** numeric (float is fine).
#     - **Value range:** **[-1, 1]** (the platform clips values to this range before scoring).
#     - **Labels:** not used—**do not include any label column**.
    
#     > Tip: The portal provides a sample CSV for formatting reference.
    
#     ---
    
#     ### Scoring (higher is better)
#     Let $P_{\text{real}}$ be the MNIST pixel distribution and $P_{\text{synth}}$ be the distribution from the uploaded batch. We compute one **global pixel histogram** for each:
    
#     - **Histogram spec:** 50 bins over **[-1, 1]** (inclusive).
#     - **Smoothing:** add $\varepsilon=10^{-8}$ to every bin to avoid zeros.
#     """
#     )


#     st.latex(r"""
#     D_{\text{sym}}(P_{\text{real}}, P_{\text{synth}})
#     = D_{KL}(P_{\text{real}} \,\|\, P_{\text{synth}})
#     + D_{KL}(P_{\text{synth}} \,\|\, P_{\text{real}})
#     """)
    
#     st.markdown(
#         r"""
#     The leaderboard shows each tester’s **best** $D_{\text{sym}}$ to date.
    
#     ---
    
#     ### Fixed reference (for consistency)
#     - **Dataset:** MNIST train (60,000 images).
#     - **Preprocessing:** images flattened to 784 and normalized with mean $0.5$, std $0.5$ (so pixels lie roughly in **[-1, 1]**).
#     - The **reference histogram** $P_{\text{real}}$ is precomputed once from the above.
    
#     ---
    
#     ### Rules & constraints
#     - **Originality:** Do not upload MNIST samples or trivially perturbed MNIST—submissions must be synthetic or from an independent generator.
#     - **Validity checks:** CSV must be 2D (n×784). Non-numeric entries are rejected. Values outside [-1, 1] are **clipped**.
#     - **Size limits:** Recommended $n \le 1024$ per upload (larger files may be rejected for runtime/memory reasons).
#     - **Privacy:** The CSV should contain only pixel values (no personal data, no labels).
    
#     ---
    
#     ### Baseline intuition
#     - Uniform noise in [-1, 1] is a simple baseline.
#     - To increase $D_{\text{sym}}$, place probability mass in pixel-value regions rare in MNIST—while remembering symmetric KL penalizes empty bins on either side (smoothing mitigates this).
#     """
#     )
    

# # --------- Tester Submission portal ------------    

# # with tabs[4]:
# #     st.header("Submission Portal  🐉  (upload adversarial batch)")
# #     st.markdown(
# #         "Paste **Python-style** list of 784-long rows, e.g. `[[0,0,…,0],[…]]`"
# #     )
# #     test_input = st.text_area("Your batch here")
# #     if st.button("Submit Batch"):
# #         email    = st.session_state["user_info"]["email"]
# #         feedback = backend.run_tester_and_get_feedback(email, test_input)
# #         st.json(feedback)


# with tabs[4]:
#     st.header("Submission Portal  🐉 ")
#     st.markdown(
#         r"""
# Upload a **CSV** with **n rows × 784 columns** (one flattened $28\times28$ image per row).

# - Header row: optional.
# - Values: floats in **[-1, 1]** (we’ll clip to [-1,1] before scoring).
# - Score: **symmetric KL divergence** between your batch’s pixel histogram and MNIST’s (50 bins over [-1,1]).
#         """
#     )

#     uploaded = st.file_uploader("Choose CSV file", type=["csv"])

#     col1, col2 = st.columns(2)
#     with col1:
#         show_plots = st.checkbox("Show histogram plots", value=False)
#     with col2:
#         clip_vals = st.checkbox("Clip to [-1,1] before scoring", value=True)

#     if uploaded is not None and st.button("Submit Batch"):
#         email = st.session_state["user_info"]["email"]
#         out = backend.evaluate_tester_csv(
#             tester_name=email,
#             file_bytes=uploaded.read(),
#             clip=clip_vals,
#             show_plots=show_plots,
#         )
#         if out.get("status") == "Completed":
#             st.success(f"KL_sym = {out['kl_sym']:.6f}  |  n = {out['n_samples']}")
#             st.json({k: out[k] for k in ["kl_sym", "n_samples", "bins", "range"]})
#             if show_plots and "plots" in out:
#                 st.pyplot(out["plots"]["mnist"])
#                 st.pyplot(out["plots"]["synth"])
#         else:
#             st.error(out.get("error", "Upload failed"))

#     # Optional helper: sample CSV
#     import io, pandas as pd, numpy as np
#     if st.button("Download sample CSV"):
#         demo = np.random.uniform(-1, 1, size=(5, 784)).astype("float32")
#         buf = io.StringIO()
#         pd.DataFrame(demo).to_csv(buf, index=False, header=False)
#         st.download_button("sample.csv", data=buf.getvalue(), file_name="sample.csv", mime="text/csv")
        

# # ----------------------- My  Submissions -----------------------------
# with tabs[5]:
#     st.header("My Submissions")
#     email = st.session_state["user_info"]["email"]
#     subs  = database.get_user_submissions(email)
#     if not subs:
#         st.info("You haven't submitted any solutions yet.")
#     else:
#         for i, sub in enumerate(reversed(subs)):
#             with st.expander(f"Submission #{len(subs) - i}", expanded=(i == 0)):
#                 st.code(sub["code"], language="python")
#                 st.write(f"Pass: {sub.get('tests_passed', 0)}")


# # ----------------------- Discussion --------------------------------------
# with tabs[6]:
#     st.header("Discussion")
#     user_name = st.session_state["user_info"].get("name")
#     txt       = st.text_area("Add your comment or question:")
#     if st.button("Post"):
#         database.add_comment(user_name, txt)
#         st.success("Your comment has been posted.")
#     st.subheader("Community Discussion")
#     for c in reversed(database.get_comments()):
#         st.markdown(f"**{c['name']}** ({c.get('timestamp', '')}):")
#         st.markdown(f"> {c['text']}")

# # ----------------------- Leaderboards ------------------------------------
# with tabs[7]:
#     st.header("Leaderboards")
#     col1, col2 = st.columns(2)
#     with col1:
#         st.subheader("🏆 Solver Leaderboard")
#         st.dataframe(backend.get_solver_leaderboard(), use_container_width=True)
#     with col2:
#         st.subheader("🎯 Tester Leaderboard")
#         st.dataframe(backend.get_tester_leaderboard(), use_container_width=True)

#         st.dataframe(backend.get_tester_leaderboard(), use_container_width=True)


# test.py
# test_combined.py

import io
import numpy as np
import pandas as pd
import streamlit as st
from streamlit_ace import st_ace

# --- Local Imports ---
import backend
import database
from authenticate import Authenticator

# --- Initialize ---
database.init_db()

# --- Page Config (optional) ---
# st.set_page_config(page_title="ConjectureQ", layout="wide")

# ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃                        Actual App Starts Below Here                      ┃
# ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

# --- App Title (after landing) ---
st.title("Conjecture Q: CHALLENGE 1")

# --- Authentication with hard-coded secrets ---
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

authenticator.check_authentication()

# If user is NOT connected, show login and bail
if not st.session_state.get("connected"):
    st.image(
        "https://www.googleapis.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png",
        width=200,
    )
    st.header("Welcome!")
    st.write("Please log in with your Google account to participate.")
    authenticator.login_widget()
    st.stop()

# --- Sidebar with user info & logout ---
st.sidebar.title(f"Welcome, {st.session_state['user_info'].get('name', 'User')}!")
st.sidebar.image(
    st.session_state['user_info'].get('picture'),
    width=60,
    use_container_width='auto'
)
st.sidebar.write(f"**Email:** {st.session_state['user_info'].get('email')}")
if st.sidebar.button("Logout"):
    authenticator.logout()

# --- Tabs Setup ---
tab_list = [
    "Overview",
    "Solver",
    "Solver Submission",
    "Tester",
    "Tester Submission",
    "My Submissions",
    "Discussion",
    "Leaderboards",
]
tabs = st.tabs(tab_list)

# ----------------------- Problem Statement -------------------------------
with tabs[0]:
    st.header("Overview")
    st.markdown(
        r"""
This challenge is inspired by what has been called the **“Crazy Conjecture”**, proposed in a talk by Nathan Srebro at **ICLR 2025**.

At its core, the conjecture asks:

> For any function \( f^*(x) \) representable by a neural network and any input distribution \( D_x \), does there exist a different distribution \( D_x' \) from which only polynomially many samples are enough to train a model—using gradient descent—to perform well on \( D_x \) itself?

In simpler terms:

If we can’t change the model architecture or optimizer, can we instead choose **where the training data comes from** to make learning vastly more efficient—even if the new data distribution looks nothing like the test distribution?

---

## Why This Matters

This is a fundamental open question in machine learning theory:

- It’s **not** about tuning hyperparameters or architectures.  
- It’s about **constructing training sets** that make learning provably easier.  
- If true, it could reshape how we think about **data selection**, **curriculum learning**, and **domain adaptation**.

---

## The Challenge Setup

- **Testers** design the hardest possible alternative training distributions \(P_i\) (subject to certain constraints).  
- **Solvers** design **sampling policies** \( \pi(i) \) that adaptively pick examples to minimize a special scoring function (operationalized here as achieving high MNIST test accuracy while the training pool can include tester-submitted data that’s “far” from MNIST).

---

## Your Goal

- **As a Solver** — You are effectively trying to **beat the Crazy Conjecture game**. Given any weird or adversarial examples from Testers appended into the pool, your policy should still pick batches intelligently to train a robust model and perform well on MNIST test.  

- **As a Tester** — You are trying to **break Solvers** by designing inputs that are far from MNIST (by symmetric KL on pixel histograms) yet still satisfy the constraints, making it difficult for Solvers to succeed.
"""
    )

# ----------------------- Solver ------------------------------------------
with tabs[1]:
    st.header("Adaptive Sampling Policy")

    st.markdown(
        r"""
### Objective
Design a **sampling policy** that selects, at each training step \(t\), a batch of indices from the current pool so as to **improve MNIST test accuracy** while training is performed on a pool consisting of **MNIST train** plus any **Tester-submitted images** appended after MNIST.

Internally the platform also tracks an optimization-quality metric (AULC: the average batch loss over steps), but your displayed score is primarily **MNIST test accuracy**.

---

### Training Environment (fixed)
- **Data:** MNIST train (28×28, grayscale) plus any tester-submitted images appended to the pool.  
  Pixels are in \([0,1]\) (via `ToTensor()`); tester uploads are divided by \(255\) then cast to float internally.
- **Model:** 2-layer MLP  
  \[ 784 \xrightarrow{W_1} 256 \xrightarrow{\mathrm{ReLU}} 10 \xrightarrow{W_2} \text{(logits)} \]
- **Loss:** cross-entropy on logits.  
- **Optimizer:** SGD (no momentum), learning rate fixed by host.  
- **Batch size:** \(b\) (fixed by host).  
- **Steps:** a fixed number of optimization steps (derived from epochs and pool size unless configured otherwise).  
- **Seed:** fixed and applied to all host-side RNGs.

The **platform** runs the model/updates; the **solver** controls **which indices** are sampled **every batch**.

---

### Telemetry you receive *every step* (for the batch you chose)
- `indices` — the indices you sampled for this batch (size \(b\)).  
- `per_sample_losses ∈ ℝ^b` — cross-entropy loss per item (no reduction).

**Optional (host may enable):**
- `probs ∈ ℝ^{b×10}` — softmax class probabilities for each sample.  
- `grad_norm_x ∈ ℝ^b` — per-sample \( \|\nabla_x \,\ell(f(x),y)\|_2 \) (usually off).

**Not exposed:** full weights, global gradients, or per-sample grads outside your chosen batch.
"""
    )

    st.subheader("Policy Interface (what your code must implement)")

    st.markdown("**Preferred (new) API — batch-wise, stateful policy with telemetry**")
    st.code(
        """def build_policy(pool_size: int, seed: int):
    class MyPolicy:
        def __init__(self, n, s):
            import numpy as np, random
            self.n = int(n)
            random.seed(int(s))
            # Track EMA of per-sample losses
            self.loss_ema = np.zeros(self.n, dtype=float)
            self.beta = 0.9

        def sample(self, batch_size: int):
            import numpy as np
            # Hard-example sampling by EMA (fallback to uniform)
            if np.all(self.loss_ema == 0):
                return np.random.choice(self.n, size=batch_size, replace=True)
            order = np.argsort(-self.loss_ema)  # descending
            return order[:batch_size]

        def update(self, indices, per_sample_losses, probs=None, grad_norm_x=None):
            self.loss_ema[indices] = self.beta * self.loss_ema[indices] + (1 - self.beta) * per_sample_losses

    return MyPolicy(pool_size, seed)
""",
        language="python",
    )

    st.markdown("**Legacy (still supported) — epoch order only; no telemetry**")
    st.code(
        """def solve(n_samples: int) -> list[int]:
    import random
    random.seed(42)
    return random.sample(range(n_samples), k=n_samples)
""",
        language="python",
    )

    st.markdown(
        r"""
**Notes**
- You can keep state across steps.  
- Indices are clipped to \([0, N-1]\). If your batch is shorter/longer than \(b\), the host pads/truncates.  
- Duplicates in a batch are allowed (as configured by the host).
"""
    )

# ----------------------- Solver Submission --------------------------------
with tabs[2]:
    st.header("Submission Portal  🧩  (write your sampling policy)")
    code = st_ace(
        placeholder="# define build_policy(pool_size, seed) or legacy solve(n_samples) here…",
        language="python",
        theme="monokai",
        key="solver_editor",
        height=320,
    )
    if st.button("Submit Solver"):
        email = st.session_state["user_info"]["email"]
        out   = backend.run_solution_and_get_results(email, code)
        st.json(out)

# ----------------------- Tester ------------------------------------------
with tabs[3]:
    st.header("Tester")
    st.markdown(
        r"""
## Submit a Dataset *Far* from MNIST

**Goal.** Upload a synthetic dataset \(X_{\text{synth}} \in \mathbb{R}^{n \times 784}\) (flattened \(28\times 28\)) whose **pixel-value distribution** is maximally different from MNIST, measured by **symmetric KL divergence**.

---

### What to upload (CSV)
- **File:** CSV with **n rows × 784 columns** (one image per row, flattened).  
- **Header:** optional (both with/without header are accepted).  
- **Dtype:** numeric (float is fine).  
- **Value range:** **[-1, 1]** (the platform clips values to this range before scoring).  
- **Labels:** not used — **do not include any label column**.

> Tip: The portal provides a sample CSV for formatting reference.

---

### Scoring (higher is better)
Let \(P_{\text{real}}\) be the MNIST pixel distribution and \(P_{\text{synth}}\) be the distribution from the uploaded batch. We compute one **global pixel histogram** for each:

- **Histogram spec:** 50 bins over **[-1, 1]** (inclusive).  
- **Smoothing:** add \(\varepsilon=10^{-8}\) to every bin to avoid zeros.

\(
D_{\text{sym}}(P_{\text{real}}, P_{\text{synth}})
= D_{KL}(P_{\text{real}} \,\|\, P_{\text{synth}})
+ D_{KL}(P_{\text{synth}} \,\|\, P_{\text{real}})
\)
"""
    )

# ----------------------- Tester Submission --------------------------------
with tabs[4]:
    st.header("Tester Submission  🐉 ")
    st.markdown(
        r"""
Upload a **CSV** with **n rows × 784 columns** (one flattened \(28\times28\) image per row).

- Header row: optional.  
- Values: floats in **[-1, 1]** (we’ll clip to [-1,1] before scoring).  
- Score: **symmetric KL divergence** between your batch’s pixel histogram and MNIST’s (50 bins over [-1,1]).
"""
    )

    uploaded = st.file_uploader("Choose CSV file", type=["csv"])

    col1, col2 = st.columns(2)
    with col1:
        show_plots = st.checkbox("Show histogram plots", value=False)
    with col2:
        clip_vals = st.checkbox("Clip to [-1,1] before scoring", value=True)

    if uploaded is not None and st.button("Submit Batch"):
        email = st.session_state["user_info"]["email"]
        out = backend.evaluate_tester_csv(
            tester_name=email,
            file_bytes=uploaded.read(),
            clip=clip_vals,
            show_plots=show_plots,
        )
        if out.get("status") == "Completed":
            st.success(f"KL_sym = {out['kl_sym']:.6f}  |  n = {out['n_samples']}")
            st.json({k: out[k] for k in ["kl_sym", "n_samples", "bins", "range"]})
            if show_plots and isinstance(out.get("plots"), dict):
                if "mnist" in out["plots"]:
                    st.pyplot(out["plots"]["mnist"])
                if "synth" in out["plots"]:
                    st.pyplot(out["plots"]["synth"])
        else:
            st.error(out.get("error", "Upload failed"))

    # Optional helper: sample CSV
    if st.button("Download sample CSV"):
        demo = np.random.uniform(-1, 1, size=(5, 784)).astype("float32")
        buf = io.StringIO()
        pd.DataFrame(demo).to_csv(buf, index=False, header=False)
        st.download_button("sample.csv", data=buf.getvalue(), file_name="sample.csv", mime="text/csv")

# ----------------------- My  Submissions ---------------------------------
with tabs[5]:
    st.header("My Submissions")
    email = st.session_state["user_info"]["email"]
    subs  = database.get_user_submissions(email)
    if not subs:
        st.info("You haven't submitted any solutions yet.")
    else:
        for i, sub in enumerate(reversed(subs)):
            with st.expander(f"Submission #{len(subs) - i}", expanded=(i == 0)):
                st.code(sub["code"], language="python")
                st.write(f"Pass: {sub.get('tests_passed', 0)}")

# ----------------------- Discussion --------------------------------------
with tabs[6]:
    st.header("Discussion")
    user_name = st.session_state["user_info"].get("name")
    txt       = st.text_area("Add your comment or question:")
    if st.button("Post"):
        database.add_comment(user_name, txt)
        st.success("Your comment has been posted.")
    st.subheader("Community Discussion")
    for c in reversed(database.get_comments()):
        st.markdown(f"**{c['name']}** ({c.get('timestamp', '')}):")
        st.markdown(f"> {c['text']}")

# ----------------------- Leaderboards ------------------------------------
with tabs[7]:
    st.header("Leaderboards")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏆 Solver Leaderboard")
        st.dataframe(backend.get_solver_leaderboard(), use_container_width=True)
    with col2:
        st.subheader("🎯 Tester Leaderboard")
        st.dataframe(backend.get_tester_leaderboard(), use_container_width=True)
        # Preserve duplicate table if desired
        st.dataframe(backend.get_tester_leaderboard(), use_container_width=True)
