# import io
# import torch  # used only for quick tensor ops below
# import ast, types, inspect, textwrap
# import numpy as np, pandas as pd, traceback
# import database
# from model import load_mnist, tensorise, train_model, accuracy
# from evaluator import symmetric_kl
# from torch.utils.data import DataLoader
# from config import *

# # Helpers for tester portal
# # --- Divergence config for Tester scoring ---
# MNIST_BINS  = 50
# MNIST_RANGE = (-1.0, 1.0)
# EPS = 1e-8

# _mnist_hist_cache = None  # (hist, edges)

# def _get_mnist_hist():
#     """
#     Returns (h_real, edges) built from the MNIST train set after mapping pixels to [-1,1]
#     via x_norm = (x/255 - 0.5)/0.5.
#     Cached after first call.
#     """
#     global _mnist_hist_cache
#     if _mnist_hist_cache is not None:
#         return _mnist_hist_cache

#     train_set, _ = load_mnist()  # your existing function
#     # train_set.data: uint8 [0..255], shape [60000, 28, 28]
#     X = train_set.data.numpy().astype(np.float32) / 255.0
#     X = (X - 0.5) / 0.5  # -> roughly [-1, 1]
#     flat = X.reshape(-1)
#     h_real, edges = np.histogram(flat, bins=MNIST_BINS, range=MNIST_RANGE, density=False)
#     _mnist_hist_cache = (h_real.astype(np.float64), edges)
#     return _mnist_hist_cache


# def _kl(p: np.ndarray, q: np.ndarray) -> float:
#     p = p.astype(np.float64) + EPS
#     q = q.astype(np.float64) + EPS
#     p = p / p.sum()
#     q = q / q.sum()
#     return float(np.sum(p * (np.log(p) - np.log(q))))


# def _sym_kl(h_real: np.ndarray, h_synth: np.ndarray) -> float:
#     return _kl(h_real, h_synth) + _kl(h_synth, h_real)

# # --------------------------------------------------------------------------- #
# # Helper: secure exec                                                         #
# # --------------------------------------------------------------------------- #
# def _safe_exec(user_code: str) -> types.ModuleType | str:
#     """
#     Returns a python module object exposing the submitted 'solve' callable.
#     On failure, returns the *exception string*.
#     """
#     mod = types.ModuleType("submission")
#     try:
#         exec(textwrap.dedent(user_code), mod.__dict__)
#     except Exception as e:
#         return f"⚠️ Exec error: {e}\n{traceback.format_exc(limit=2)}"
#     if "solve" not in mod.__dict__ or not callable(mod.__dict__["solve"]):
#         return "⚠️ No callable named 'solve' found."
#     return mod

# # --------------------------------------------------------------------------- #
# # 1️⃣  Solver entry-point                                                     #
# # --------------------------------------------------------------------------- #
# def run_solution_and_get_results(solver_name: str, code: str):
#     database.add_solver(solver_name, code)

#     # Load canonical MNIST once
#     train_set, test_set = load_mnist()
#     X_train = train_set.data.float().unsqueeze(1) / 255.0   # Nx1x28x28
#     y_train = train_set.targets
#     test_loader = DataLoader(test_set, batch_size=256)

#     # Gather all adversarial batches supplied so far
#     test_cases = database.get_test_cases()
#     adv_batches = [
#         tensorise(case["input"]) for case in test_cases if case["input"]
#     ]
#     if not adv_batches:                       # no adversary yet → trivial pass
#         database.update_solver_score(solver_name, 0)
#         return {"status": "No adversarial data yet – waiting for testers."}

#     # Flatten all batches into one tensor (= union of tester data)
#     adv_data = torch.cat(adv_batches, dim=0)
#     adv_labels = torch.randint(0, 10, (len(adv_data),))     # dummy labels

#     # Securely load solver’s sampler policy
#     mod = _safe_exec(code)
#     if isinstance(mod, str):          # exec failed
#         return {"error": mod}

#     # The user-defined function must accept (num_samples:int) and return list[int]
#     sampler_fn = mod.solve
#     sig = inspect.signature(sampler_fn)
#     if len(sig.parameters) != 1:
#         return {"error": "solve() must take exactly one argument: dataset size"}

#     # Train and evaluate ------------------------------------------------------
#     full_images = torch.cat([X_train, adv_data], dim=0)
#     full_labels = torch.cat([y_train, adv_labels], dim=0)

#     try:
#         net = train_model(full_images, full_labels, sampler_fn)
#         acc = accuracy(net, test_loader)
#         passed = acc >= PASS_THRESHOLD
#     except Exception as e:
#         return {"error": f"Runtime error during training: {e}"}

#     database.update_solver_score(solver_name, int(passed))
#     return {
#         "status"    : "Completed",
#         "accuracy"  : round(acc, 4),
#         "threshold" : PASS_THRESHOLD,
#         "result"    : "PASS ✅" if passed else "FAIL ❌",
#     }

# # --------------------------------------------------------------------------- #
# # 2️⃣  Tester entry-point                                                     #
# # --------------------------------------------------------------------------- #
# # def run_tester_and_get_feedback(tester_name: str, test_input: str):
# #     """
# #     test_input : string representation of List[List[int]], each inner list len=784
# #     """
# #     try:
# #         raw = ast.literal_eval(test_input)
# #         if (
# #             not isinstance(raw, list)
# #             or not raw
# #             or not all(isinstance(row, list) and len(row) == 784 for row in raw)
# #         ):
# #             raise ValueError
# #         flat = np.asarray(raw, dtype=np.float32)
# #         if flat.min() < 0 or flat.max() > 255:
# #             raise ValueError
# #     except Exception:
# #         return {"error": "Input must be a JSON-style list of 784-length rows with 0-255 ints."}

# #     images = tensorise(flat)
# #     # distance-to-MNIST score
# #     mnist_train, _ = load_mnist()
# #     kld = symmetric_kl(images.numpy(), mnist_train.data.numpy().astype(np.float32) / 255.0)

# #     # Threshold: only store batches that are *meaningfully* different
# #     if kld < 0.05:
# #         return {"error": f"Dataset too close to MNIST (sym-KL={kld:.4f}). Try again."}

# #     # For bookkeeping
# #     expected_output = None            # not used any more
# #     database.add_test_case(tester_name, raw, expected_output)

# #     # Every solver evaluated against *this single batch* ---------------------
# #     solvers = database.get_solvers()
# #     broken = []
# #     for sol in solvers:
# #         res = run_solution_and_get_results(sol["name"], sol["code"])
# #         if res.get("result") != "PASS ✅":
# #             broken.append(sol["name"])

# #     if broken:
# #         database.update_tester_score(tester_name, len(broken))

# #     return {
# #         "symmetric_KL"  : round(kld, 4),
# #         "affected"      : len(broken),
# #         "broken_solvers": broken,
# #     }

# def evaluate_tester_csv(
#     tester_name: str,
#     file_bytes: bytes,
#     clip: bool = True,
#     show_plots: bool = False,
# ):
#     """
#     Evaluate a tester-submitted CSV (n x 784).
#     - Clips values to [-1,1] if clip=True.
#     - Computes symmetric KL vs. MNIST histogram (50 bins over [-1,1]).
#     - Optionally returns matplotlib figs for hist comparisons (for Streamlit).
#     """
#     # 1) Parse CSV -> ndarray (n, 784)
#     try:
#         buf = io.BytesIO(file_bytes)
#         try:
#             df = pd.read_csv(buf, header=None)
#         except Exception:
#             buf.seek(0)
#             df = pd.read_csv(buf)  # tolerate header
#         X = df.values
#     except Exception as e:
#         return {"status": "Error", "error": f"Failed to parse CSV: {e}"}

#     if X.ndim != 2:
#         return {"status": "Error", "error": "CSV must be 2D: n rows × 784 columns."}
#     n, d = X.shape
#     if d != 784:
#         return {"status": "Error", "error": f"Expected 784 columns, got {d}."}
#     if n < 1:
#         return {"status": "Error", "error": "CSV has no rows."}

#     X = X.astype(np.float32, copy=False)
#     if clip:
#         X = np.clip(X, MNIST_RANGE[0], MNIST_RANGE[1])

#     # 2) Build histograms and compute symmetric KL
#     (h_real, edges) = _get_mnist_hist()
#     synth_pixels = X.reshape(-1)
#     h_synth, _ = np.histogram(synth_pixels, bins=MNIST_BINS, range=MNIST_RANGE, density=False)
#     kl_sym = _sym_kl(h_real, h_synth)

#     # 3) Persist best divergence for leaderboard (if helper exists)
#     try:
#         database.update_tester_divergence(tester_name, float(kl_sym))  # add this in database.py (see below)
#     except Exception:
#         # fallback: keep legacy counter if desired, or ignore
#         pass

#     # 4) Optional plots
#     # plots = None
#     # if show_plots:
#     #     plots = {}
#     #     centers = (edges[:-1] + edges[1:]) / 2
#     #     width = (edges[1] - edges[0])

#     #     fig1 = plt.figure()
#     #     plt.bar(centers, h_real / h_real.sum(), width=width)
#     #     plt.title("MNIST pixel histogram (normalized)")
#     #     plots["mnist"] = fig1

#     #     fig2 = plt.figure()
#     #     plt.bar(centers, h_synth / h_synth.sum(), width=width)
#     #     plt.title("Your batch histogram (normalized)")
#     #     plots["synth"] = fig2

#     return {
#         "status": "Completed",
#         "n_samples": int(n),
#         "kl_sym": float(kl_sym),
#         "bins": int(MNIST_BINS),
#         "range": MNIST_RANGE,
#         "plots": plots,
#     }

# # --------------------------------------------------------------------------- #
# # 3️⃣  Leaderboard helpers (unchanged except for columns)                    #
# # --------------------------------------------------------------------------- #
# def get_solver_leaderboard():
#     df = pd.DataFrame(database.get_solvers())
#     if df.empty:
#         return pd.DataFrame({"Rank": [], "User": [], "Pass": []})
#     df = df.sort_values(by="tests_passed", ascending=False).reset_index(drop=True)
#     df["Rank"] = df.index + 1
#     return df[["Rank", "name", "tests_passed"]].rename(
#         columns={"name": "User", "tests_passed": "Pass"}
#     )

# def get_tester_leaderboard():
#     df = pd.DataFrame(database.get_testers())
#     if df.empty:
#         return pd.DataFrame({"Rank": [], "User": [], "Breaks": []})
#     df = df.sort_values(by="breaks_found", ascending=False).reset_index(drop=True)
#     df["Rank"] = df.index + 1
#     return df[["Rank", "name", "breaks_found"]].rename(
#         columns={"name": "User", "breaks_found": "Breaks"}
#     )
import io
import torch  # used only for quick tensor ops below
import ast, types, inspect, textwrap
import numpy as np, pandas as pd, traceback
import database
from model import load_mnist, tensorise, train_model, accuracy
from evaluator import symmetric_kl
from torch.utils.data import DataLoader
from config import *
import math

# Helpers for tester portal
# --- Divergence config for Tester scoring ---
MNIST_BINS  = 50
MNIST_RANGE = (-1.0, 1.0)
EPS = 1e-8

_mnist_hist_cache = None  # (hist, edges)

def _get_mnist_hist():
    """
    Returns (h_real, edges) built from the MNIST train set after mapping pixels to [-1,1]
    via x_norm = (x/255 - 0.5)/0.5.
    Cached after first call.
    """
    global _mnist_hist_cache
    if _mnist_hist_cache is not None:
        return _mnist_hist_cache

    train_set, _ = load_mnist()  # your existing function
    # train_set.data: uint8 [0..255], shape [60000, 28, 28]
    X = train_set.data.numpy().astype(np.float32) / 255.0
    X = (X - 0.5) / 0.5  # -> roughly [-1, 1]
    flat = X.reshape(-1)
    h_real, edges = np.histogram(flat, bins=MNIST_BINS, range=MNIST_RANGE, density=False)
    _mnist_hist_cache = (h_real.astype(np.float64), edges)
    return _mnist_hist_cache


def _kl(p: np.ndarray, q: np.ndarray) -> float:
    p = p.astype(np.float64) + EPS
    q = q.astype(np.float64) + EPS
    p = p / p.sum()
    q = q / q.sum()
    return float(np.sum(p * (np.log(p) - np.log(q))))


def _sym_kl(h_real: np.ndarray, h_synth: np.ndarray) -> float:
    return _kl(h_real, h_synth) + _kl(h_synth, h_real)

# --------------------------------------------------------------------------- #
# Helper: secure exec                                                         #
# --------------------------------------------------------------------------- #
def _safe_exec(user_code: str) -> types.ModuleType | str:
    """
    Returns a python module object exposing a solver policy.
    On failure, returns the *exception string*.
    """
    mod = types.ModuleType("submission")
    try:
        exec(textwrap.dedent(user_code), mod.__dict__)
    except Exception as e:
        return f"⚠️ Exec error: {e}\n{traceback.format_exc(limit=2)}"
    return mod

# --- Legacy adapter for solve(n_samples) ------------------------------------
class _LegacyPolicy:
    def __init__(self, N, seed, solve_fn):
        self.N = int(N)
        self.seed = int(seed)
        self.solve_fn = solve_fn
        self._order = []
        self._pos = 0
        random = __import__("random")
        random.seed(self.seed)

    def _refresh_order(self):
        order = self.solve_fn(self.N)
        if not hasattr(order, "__len__"):
            order = list(range(self.N))
        self._order = list(order)
        self._pos = 0

    def sample(self, batch_size: int):
        if self._pos + batch_size > len(self._order):
            self._refresh_order()
        batch = self._order[self._pos:self._pos + batch_size]
        self._pos += batch_size
        return np.asarray(batch, dtype=np.int64)

    def update(self, *args, **kwargs):
        # legacy policies do not consume telemetry
        return

def _get_policy_builder(mod: types.ModuleType):
    """
    Returns a callable builder(pool_size:int, seed:int)->policy with sample/update.
    Accepts:
      - modern: build_policy(pool_size, seed)
      - legacy: solve(n_samples) -> list[int]
    """
    build = getattr(mod, "build_policy", None)
    if callable(build):
        return build

    solve = getattr(mod, "solve", None)
    if callable(solve):
        def _builder(pool_size: int, seed: int):
            return _LegacyPolicy(pool_size, seed, solve)
        return _builder

    return None

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
    # Compose full pool
    if adv_batches:
        adv_data = torch.cat(adv_batches, dim=0)
        adv_labels = torch.randint(0, 10, (len(adv_data),))     # dummy labels
        full_images = torch.cat([X_train, adv_data], dim=0)
        full_labels = torch.cat([y_train, adv_labels], dim=0)
    else:
        # Still allow training on MNIST only; no-op adversary
        full_images = X_train
        full_labels = y_train

    # Securely load solver’s policy
    mod = _safe_exec(code)
    if isinstance(mod, str):          # exec failed
        return {"error": mod}

    policy_builder = _get_policy_builder(mod)
    if policy_builder is None:
        return {"error": "Submission must define build_policy(pool_size, seed) or legacy solve(n_samples)."}

    # Train and evaluate ------------------------------------------------------
    try:
        net, metrics = train_model(
            full_images, full_labels,
            policy_builder,
            steps=TRAIN_STEPS,
            seed=SEED
        )
        acc = accuracy(net, test_loader)
        passed = acc >= PASS_THRESHOLD
    except Exception as e:
        return {"error": f"Runtime error during training: {e}"}

    database.update_solver_score(solver_name, int(passed))
    out = {
        "status"    : "Completed",
        "accuracy"  : round(float(acc), 4),
        "threshold" : PASS_THRESHOLD,
        "result"    : "PASS ✅" if passed else "FAIL ❌",
        "aulc"      : round(float(metrics.get("aulc", float("nan"))), 6),
        "steps"     : int(metrics.get("steps", 0)),
    }
    return out

# --------------------------------------------------------------------------- #
# 2️⃣  Tester entry-point                                                     #
# --------------------------------------------------------------------------- #
def evaluate_tester_csv(
    tester_name: str,
    file_bytes: bytes,
    clip: bool = True,
    show_plots: bool = False,
):
    """
    Evaluate a tester-submitted CSV (n x 784).
    - Clips values to [-1,1] if clip=True.
    - Computes symmetric KL vs. MNIST histogram (50 bins over [-1,1]).
    - Optionally returns matplotlib figs for hist comparisons (for Streamlit).
    """
    # 1) Parse CSV -> ndarray (n, 784)
    try:
        buf = io.BytesIO(file_bytes)
        try:
            df = pd.read_csv(buf, header=None)
        except Exception:
            buf.seek(0)
            df = pd.read_csv(buf)  # tolerate header
        X = df.values
    except Exception as e:
        return {"status": "Error", "error": f"Failed to parse CSV: {e}"}

    if X.ndim != 2:
        return {"status": "Error", "error": "CSV must be 2D: n rows × 784 columns."}
    n, d = X.shape
    if d != 784:
        return {"status": "Error", "error": f"Expected 784 columns, got {d}."}
    if n < 1:
        return {"status": "Error", "error": "CSV has no rows."}

    X = X.astype(np.float32, copy=False)
    if clip:
        X = np.clip(X, MNIST_RANGE[0], MNIST_RANGE[1])

    # 2) Build histograms and compute symmetric KL
    (h_real, edges) = _get_mnist_hist()
    synth_pixels = X.reshape(-1)
    h_synth, _ = np.histogram(synth_pixels, bins=MNIST_BINS, range=MNIST_RANGE, density=False)
    kl_sym = _sym_kl(h_real, h_synth)

    # 3) Persist best divergence for leaderboard (optional; function may not exist)
    try:
        database.update_tester_divergence(tester_name, float(kl_sym))  # may be absent; best-effort
    except Exception:
        pass

    # 4) Optional plots
    plots = None
    # (omitted to keep runtime small; can add matplotlib here if desired)

    return {
        "status": "Completed",
        "n_samples": int(n),
        "kl_sym": float(kl_sym),
        "bins": int(MNIST_BINS),
        "range": MNIST_RANGE,
        "plots": plots,
    }

# --------------------------------------------------------------------------- #
# 3️⃣  Leaderboard helpers (unchanged except for columns)                    #
# --------------------------------------------------------------------------- #
# def get_solver_leaderboard():
#     df = pd.DataFrame(database.get_solvers())
#     if df.empty:
#         return pd.DataFrame({"Rank": [], "User": [], "Pass": []})
#     df = df.sort_values(by="tests_passed", ascending=False).reset_index(drop=True)
#     df["Rank"] = df.index + 1
#     return df[["Rank", "name", "tests_passed"]].rename(
#         columns={"name": "User", "tests_passed": "Pass"}
#     )

# def get_tester_leaderboard():
#     df = pd.DataFrame(database.get_testers())
#     if df.empty:
#         return pd.DataFrame({"Rank": [], "User": [], "Breaks": []})
#     df = df.sort_values(by="breaks_found", ascending=False).reset_index(drop=True)
#     df["Rank"] = df.index + 1
#     return df[["Rank", "name", "breaks_found"]].rename(
#         columns={"name": "User", "breaks_found": "Breaks"}
#     )

def _display_name(raw: str) -> str:
    # hide emails if any slipped in
    return raw.split("@")[0] if "@" in raw else raw

def get_solver_leaderboard():
    df = pd.DataFrame(database.get_solvers())
    if df.empty:
        return pd.DataFrame({"Rank": [], "User": [], "Score": []})

    # Back-compat: prefer 'score', else 'tests_passed'
    if "score" not in df.columns:
        df["score"] = df.get("tests_passed", pd.Series([0]*len(df)))

    df["User"] = df["name"].map(_display_name)
    df = df.sort_values(by="score", ascending=False).reset_index(drop=True)
    df["Rank"] = df.index + 1
    df = df[["Rank","User","score"]].rename(columns={"score":"Score"})
    return df.head(10)  # show top 10


def get_tester_leaderboard():
    df = pd.DataFrame(database.get_testers())
    if df.empty:
        return pd.DataFrame({"Rank": [], "User": [], "Score": []})

    # Back-compat: prefer 'score', else 'breaks_found'
    if "score" not in df.columns:
        df["score"] = df.get("breaks_found", pd.Series([0]*len(df)))

    df["User"] = df["name"].map(_display_name)
    df = df.sort_values(by="score", ascending=False).reset_index(drop=True)
    df["Rank"] = df.index + 1
    df = df[["Rank","User","score"]].rename(columns={"score":"Score"})
    return df.head(5)   # show top 5
