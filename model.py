# import torch, torch.nn as nn, torch.nn.functional as F, numpy as np, random
# from torch.utils.data import DataLoader, TensorDataset
# from torchvision import datasets, transforms
# from sklearn.model_selection import train_test_split
# from config import *

# # --- Reproducibility ---------------------------------------------------------
# def set_seed(seed: int = SEED):
#     random.seed(seed)
#     np.random.seed(seed)
#     torch.manual_seed(seed)
#     if torch.cuda.is_available():
#         torch.cuda.manual_seed_all(seed)

# # --- Simple two-layer network ------------------------------------------------
# class SimpleNet(nn.Module):
#     def __init__(self):
#         super().__init__()
#         self.fc1 = nn.Linear(28 * 28, 256)
#         self.fc2 = nn.Linear(256, 10)

#     def forward(self, x):
#         x = x.view(-1, 28 * 28)
#         x = F.relu(self.fc1(x))
#         return self.fc2(x)

# # --- Dataset utilities -------------------------------------------------------
# def load_mnist():
#     tfm = transforms.Compose(
#         [transforms.ToTensor()]  # (0-1) float32 range already
#     )
#     train = datasets.MNIST(root="data", train=True, download=True, transform=tfm)
#     test  = datasets.MNIST(root="data", train=False, download=True, transform=tfm)
#     return train, test

# def tensorise(flat_list, dtype=torch.float32):
#     """List[List[int]] → torch.Tensor Nx1x28x28 in 0-1 float32."""
#     arr = np.asarray(flat_list, dtype=np.float32).reshape(-1, 1, 28, 28) / 255.0
#     return torch.tensor(arr, dtype=dtype)

# # --- Training loop -----------------------------------------------------------
# def train_model(train_images, train_labels, sampler_fn):
#     """
#     train_images : torch.Tensor  Nx1x28x28
#     train_labels : torch.Tensor  N
#     sampler_fn   : Callable[[int], List[int]]
#                    returns *ordered* index list for one epoch
#     """
#     set_seed()
#     net = SimpleNet().to(DEVICE)
#     opt = torch.optim.SGD(net.parameters(), lr=SGD_LR)
#     loss_fn = nn.CrossEntropyLoss()

#     N = len(train_images)

#     for _ in range(EPOCHS):
#         idx_order = sampler_fn(N)
#         loader = DataLoader(
#             TensorDataset(train_images[idx_order], train_labels[idx_order]),
#             batch_size=BATCH_SIZE,
#             shuffle=False,       # sampler determines order
#         )
#         for x, y in loader:
#             x, y = x.to(DEVICE), y.to(DEVICE)
#             opt.zero_grad()
#             loss_fn(net(x), y).backward()
#             opt.step()
#     return net

# # --- Evaluation --------------------------------------------------------------
# @torch.no_grad()
# def accuracy(model, test_loader):
#     correct = total = 0
#     for x, y in test_loader:
#         x, y = x.to(DEVICE), y.to(DEVICE)
#         pred = model(x).argmax(dim=1)
#         correct += (pred == y).sum().item()
#         total   += y.size(0)
#     return correct / total
import math
import torch, torch.nn as nn, torch.nn.functional as F, numpy as np, random
from torch.utils.data import DataLoader, TensorDataset
from torchvision import datasets, transforms
from config import *

# --- Reproducibility ---------------------------------------------------------
def set_seed(seed: int = SEED):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

# --- Simple two-layer network ------------------------------------------------
class SimpleNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(28 * 28, 256)
        self.fc2 = nn.Linear(256, 10)

    def forward(self, x):
        x = x.view(-1, 28 * 28)
        x = F.relu(self.fc1(x))
        return self.fc2(x)

# --- Dataset utilities -------------------------------------------------------
def load_mnist():
    tfm = transforms.Compose(
        [transforms.ToTensor()]  # (0-1) float32 range already
    )
    train = datasets.MNIST(root="data", train=True, download=True, transform=tfm)
    test  = datasets.MNIST(root="data", train=False, download=True, transform=tfm)
    return train, test

def tensorise(flat_list, dtype=torch.float32):
    """List[List[int]] → torch.Tensor Nx1x28x28 in 0-1 float32."""
    arr = np.asarray(flat_list, dtype=np.float32).reshape(-1, 1, 28, 28) / 255.0
    return torch.tensor(arr, dtype=dtype)

# --- Optional per-sample input-grad norms -----------------------------------
def _per_sample_grad_norm_x(model, x, y, loss_fn):
    """
    Returns np.ndarray [batch] of ||d loss_i / d x_i||_2 for each sample i.
    This does a backward per item (slow); gated by TELEMETRY_GRAD_NORM_X.
    """
    norms = []
    for i in range(x.size(0)):
        xi = x[i:i+1].detach().clone().requires_grad_(True)
        yi = y[i:i+1]
        logits_i = model(xi)
        loss_i = loss_fn(logits_i, yi)  # scalar
        model.zero_grad(set_to_none=True)
        if xi.grad is not None:
            xi.grad.zero_()
        loss_i.backward()
        norms.append(xi.grad.view(1, -1).norm(p=2, dim=1).item())
    return np.asarray(norms, dtype=np.float32)

# --- Training loop (batch-wise policy) --------------------------------------
def train_model(train_images, train_labels, policy_builder, *, steps=None, seed: int = SEED):
    """
    train_images : torch.Tensor  Nx1x28x28  (0..1)
    train_labels : torch.Tensor  N          (int64)
    policy_builder : Callable[[int, int], Policy] -> object with:
                     - sample(batch_size:int) -> np.ndarray[int]
                     - update(indices, per_sample_losses, probs=None, grad_norm_x=None) -> None
    steps       : int | None   (if None => EPOCHS * ceil(N / BATCH_SIZE))
    seed        : int
    Returns: (model, metrics_dict)
    """
    set_seed(seed)
    net = SimpleNet().to(DEVICE)
    opt = torch.optim.SGD(net.parameters(), lr=SGD_LR)
    loss_vec_fn = nn.CrossEntropyLoss(reduction="none")
    loss_mean_fn = nn.CrossEntropyLoss(reduction="mean")

    N = int(train_images.size(0))
    steps = steps if steps is not None else (EPOCHS * math.ceil(N / BATCH_SIZE))

    # Build policy
    policy = policy_builder(N, seed)

    # For AULC metric: average of batch-mean loss across steps
    aulc_accum = 0.0

    # Convenience tensors live on DEVICE
    train_images = train_images.to(DEVICE)
    train_labels = train_labels.to(DEVICE)

    for _ in range(steps):
        # 1) Ask policy for a batch of indices
        idx = np.asarray(policy.sample(BATCH_SIZE), dtype=np.int64)

        # Safety checks / normalization
        if CLIP_INDICES_TO_RANGE:
            np.clip(idx, 0, N - 1, out=idx)
        if ENFORCE_BATCH_LEN:
            if idx.size < BATCH_SIZE:
                # pad by repeating the last valid index (or zeros if none)
                pad_val = int(idx[-1]) if idx.size > 0 else 0
                idx = np.pad(idx, (0, BATCH_SIZE - idx.size), constant_values=pad_val)
            elif idx.size > BATCH_SIZE:
                idx = idx[:BATCH_SIZE]
        # Duplicates allowed per config
        # (no-op: we don't enforce uniqueness if ALLOW_DUPLICATES=True)

        idx_t = torch.from_numpy(idx).to(DEVICE)
        x = train_images.index_select(0, idx_t)
        y = train_labels.index_select(0, idx_t)

        # 2) Forward
        x.requires_grad_(TELEMETRY_GRAD_NORM_X)
        logits = net(x)
        per_sample_losses = loss_vec_fn(logits, y)  # [batch]
        batch_mean_loss = per_sample_losses.mean()

        # 3) Backward + step
        opt.zero_grad(set_to_none=True)
        batch_mean_loss.backward()
        opt.step()

        # 4) Telemetry prep
        aulc_accum += float(batch_mean_loss.detach().cpu().item())

        probs = None
        if TELEMETRY_PROBS:
            with torch.no_grad():
                probs = torch.softmax(logits, dim=1).detach().cpu().numpy()

        grad_norm_x = None
        if TELEMETRY_GRAD_NORM_X:
            # compute fresh to avoid interference with optimizer step
            grad_norm_x = _per_sample_grad_norm_x(net, x.detach(), y.detach(), loss_mean_fn)

        # Send numpy arrays to the policy
        policy.update(
            indices=idx.copy(),
            per_sample_losses=per_sample_losses.detach().cpu().numpy(),
            probs=probs,
            grad_norm_x=grad_norm_x,
        )

    metrics = {
        "aulc": aulc_accum / float(steps) if steps > 0 else float("nan"),
        "steps": int(steps),
    }
    return net, metrics

# --- Evaluation --------------------------------------------------------------
@torch.no_grad()
def accuracy(model, test_loader):
    model.eval()
    correct = total = 0
    for x, y in test_loader:
        x, y = x.to(DEVICE), y.to(DEVICE)
        pred = model(x).argmax(dim=1)
        correct += (pred == y).sum().item()
        total   += y.size(0)
    return correct / total
