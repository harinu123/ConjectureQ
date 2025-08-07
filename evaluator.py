import numpy as np
from scipy.special import rel_entr
from config import *

def _histogram(images: np.ndarray):
    """
    images : Nx1x28x28 float32 in [0,1]
    Returns density vector of length KLD_BINS.
    """
    flat = images.ravel()
    hist, _ = np.histogram(flat, bins=KLD_BINS, range=(0.0, 1.0), density=True)
    hist += 1e-9                        # avoid log(0)
    hist /= hist.sum()                  # normalise
    return hist

def symmetric_kl(p_images, q_images):
    p = _histogram(p_images)
    q = _histogram(q_images)
    kl_pq = np.sum(rel_entr(p, q))      # KL(p‖q)
    kl_qp = np.sum(rel_entr(q, p))
    return 0.5 * (kl_pq + kl_qp)
