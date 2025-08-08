# # Global knobs in one place.

# SEED              = 31415           # reproducibility for torch & numpy
# BATCH_SIZE        = 64
# SGD_LR            = 0.01
# EPOCHS            = 5
# PASS_THRESHOLD    = 0.92            # accuracy required for a solver to “pass”
# KLD_BINS          = 32              # histogram resolution for symmetric-KL
# DEVICE            = "cuda" if __import__("torch").cuda.is_available() else "cpu"

# Global knobs in one place.

SEED              = 31415           # reproducibility for torch & numpy
BATCH_SIZE        = 64
SGD_LR            = 0.01
EPOCHS            = 5               # used when TRAIN_STEPS=None (default = EPOCHS * ceil(N/BATCH_SIZE))
PASS_THRESHOLD    = 0.92            # accuracy required for a solver to “pass”
KLD_BINS          = 32              # histogram resolution for symmetric-KL
DEVICE            = "cuda" if __import__("torch").cuda.is_available() else "cpu"

# --- NEW: training/telemetry switches ---
TRAIN_STEPS           = None  # if None: EPOCHS * ceil(N/BATCH_SIZE); else use this many steps
TELEMETRY_PROBS       = True  # pass softmax probabilities to policy.update
TELEMETRY_GRAD_NORM_X = False # pass per-sample ||d loss/dx||_2 (costly if True)

# --- NEW: sampling safety checks ---
ENFORCE_BATCH_LEN     = True  # force batches to be exactly BATCH_SIZE
CLIP_INDICES_TO_RANGE = True  # clip any index to [0, N-1] before use
ALLOW_DUPLICATES      = True  # allow repeated indices within a batch
