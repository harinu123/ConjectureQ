# ----------------------- Solver Portal ------------------------------------
with tabs[2]:
    st.header("Solver Portal  🧩  (write your sampling policy)")
    st.markdown("""
    **Template**  

    ```python
    # Mandatory signature
    def solve(n_samples: int) -> list[int]:
        import random
        random.seed(42)          # keep it deterministic
        return random.sample(range(n_samples), k=n_samples)  # naive uniform shuffle
    ```
    """)
    code = st_ace(
        placeholder="# define solve(n_samples) here…",
        language="python",
        theme="monokai",
        key="solver_editor",
        height=300,
    )
    if st.button("Submit Solver"):
        email = st.session_state["user_info"]["email"]
        out = backend.run_solution_and_get_results(email, code)
        st.json(out)

# ----------------------- Tester Portal ------------------------------------
with tabs[4]:
    st.header("Tester Portal  🐉  (upload adversarial batch)")
    st.markdown("Paste **Python-style** list of 784-long rows, e.g. `[[0,0,…,0],[…]]`")
    test_input = st.text_area("Your batch here")
    if st.button("Submit Batch"):
        email = st.session_state["user_info"]["email"]
        feedback = backend.run_tester_and_get_feedback(email, test_input)
        st.json(feedback)
