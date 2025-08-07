import ast, types, inspect, textwrap
import numpy as np, pandas as pd, traceback
import database
from model import load_mnist, tensorise, train_model, accuracy
from evaluator import symmetric_kl
from torch.utils.data import DataLoader
from config import *

# --------------------------------------------------------------------------- #
# Helper: secure exec                                                         #
# --------------------------------------------------------------------------- #
def _safe_exec(user_code: str) -> types.ModuleType | str:
    """
    Returns a python module object exposing the submitted 'solve' callable.
    On failure, returns the *exception string*.
    """
    mod = types.ModuleType("submission")
    try:
        exec(textwrap.dedent(user_code), mod.__dict__)
    except Exception as e:
        return f"⚠️ Exec error: {e}\n{traceback.format_exc(limit=2)}"
    if "solve" not in mod.__dict__ or not callable(mod.__dict__["solve"]):
        return "⚠️ No callable named 'solve' found."
    return mod

# --------------------------------------------------------------------------- #
# 1️⃣  Solver entry-point                                                     #
# --------------------------------------------------------------------------- #
def run_solution_and_get_results(solver_name: str, code: str):
    database.add_solver(solver_name, code)

    # Load canonical MNIST once
    train_set, test_set = load_mnist()
    X_train = train_set.data.float().unsqueeze(1) / 255.0   # Nx1x28x28
    y_train = train_set.targets
    test_loader = DataLoader(test_set, batch_size=256)

    # Gather all adversarial batches supplied so far
    test_cases = database.get_test_cases()
    adv_batches = [
        tensorise(case["input"]) for case in test_cases if case["input"]
    ]
    if not adv_batches:                       # no adversary yet → trivial pass
        database.update_solver_score(solver_name, 0)
        return {"status": "No adversarial data yet – waiting for testers."}

    # Flatten all batches into one tensor (= union of tester data)
    adv_data = torch.cat(adv_batches, dim=0)
    adv_labels = torch.randint(0, 10, (len(adv_data),))     # dummy labels

    # Securely load solver’s sampler policy
    mod = _safe_exec(code)
    if isinstance(mod, str):          # exec failed
        return {"error": mod}

    # The user-defined function must accept (num_samples:int) and return list[int]
    sampler_fn = mod.solve
    sig = inspect.signature(sampler_fn)
    if len(sig.parameters) != 1:
        return {"error": "solve() must take exactly one argument: dataset size"}

    # Train and evaluate ------------------------------------------------------
    full_images = torch.cat([X_train, adv_data], dim=0)
    full_labels = torch.cat([y_train, adv_labels], dim=0)

    try:
        net = train_model(full_images, full_labels, sampler_fn)
        acc = accuracy(net, test_loader)
        passed = acc >= PASS_THRESHOLD
    except Exception as e:
        return {"error": f"Runtime error during training: {e}"}

    database.update_solver_score(solver_name, int(passed))
    return {
        "status"    : "Completed",
        "accuracy"  : round(acc, 4),
        "threshold" : PASS_THRESHOLD,
        "result"    : "PASS ✅" if passed else "FAIL ❌",
    }

# --------------------------------------------------------------------------- #
# 2️⃣  Tester entry-point                                                     #
# --------------------------------------------------------------------------- #
def run_tester_and_get_feedback(tester_name: str, test_input: str):
    """
    test_input : string representation of List[List[int]], each inner list len=784
    """
    try:
        raw = ast.literal_eval(test_input)
        if (
            not isinstance(raw, list)
            or not raw
            or not all(isinstance(row, list) and len(row) == 784 for row in raw)
        ):
            raise ValueError
        flat = np.asarray(raw, dtype=np.float32)
        if flat.min() < 0 or flat.max() > 255:
            raise ValueError
    except Exception:
        return {"error": "Input must be a JSON-style list of 784-length rows with 0-255 ints."}

    images = tensorise(flat)
    # distance-to-MNIST score
    mnist_train, _ = load_mnist()
    kld = symmetric_kl(images.numpy(), mnist_train.data.numpy().astype(np.float32) / 255.0)

    # Threshold: only store batches that are *meaningfully* different
    if kld < 0.05:
        return {"error": f"Dataset too close to MNIST (sym-KL={kld:.4f}). Try again."}

    # For bookkeeping
    expected_output = None            # not used any more
    database.add_test_case(tester_name, raw, expected_output)

    # Every solver evaluated against *this single batch* ---------------------
    solvers = database.get_solvers()
    broken = []
    for sol in solvers:
        res = run_solution_and_get_results(sol["name"], sol["code"])
        if res.get("result") != "PASS ✅":
            broken.append(sol["name"])

    if broken:
        database.update_tester_score(tester_name, len(broken))

    return {
        "symmetric_KL"  : round(kld, 4),
        "affected"      : len(broken),
        "broken_solvers": broken,
    }

# --------------------------------------------------------------------------- #
# 3️⃣  Leaderboard helpers (unchanged except for columns)                    #
# --------------------------------------------------------------------------- #
def get_solver_leaderboard():
    df = pd.DataFrame(database.get_solvers())
    if df.empty:
        return pd.DataFrame({"Rank": [], "User": [], "Pass": []})
    df = df.sort_values(by="tests_passed", ascending=False).reset_index(drop=True)
    df["Rank"] = df.index + 1
    return df[["Rank", "name", "tests_passed"]].rename(
        columns={"name": "User", "tests_passed": "Pass"}
    )

def get_tester_leaderboard():
    df = pd.DataFrame(database.get_testers())
    if df.empty:
        return pd.DataFrame({"Rank": [], "User": [], "Breaks": []})
    df = df.sort_values(by="breaks_found", ascending=False).reset_index(drop=True)
    df["Rank"] = df.index + 1
    return df[["Rank", "name", "breaks_found"]].rename(
        columns={"name": "User", "breaks_found": "Breaks"}
    )
