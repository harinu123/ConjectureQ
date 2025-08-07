# Global knobs in one place.

SEED              = 31415           # reproducibility for torch & numpy
BATCH_SIZE        = 64
SGD_LR            = 0.01
EPOCHS            = 5
PASS_THRESHOLD    = 0.92            # accuracy required for a solver to “pass”
KLD_BINS          = 32              # histogram resolution for symmetric-KL
DEVICE            = "cuda" if __import__("torch").cuda.is_available() else "cpu"
