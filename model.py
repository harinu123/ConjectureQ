import torch, torch.nn as nn, torch.nn.functional as F, numpy as np, random
from torch.utils.data import DataLoader, TensorDataset
from torchvision import datasets, transforms
from sklearn.model_selection import train_test_split
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

# --- Training loop -----------------------------------------------------------
def train_model(train_images, train_labels, sampler_fn):
    """
    train_images : torch.Tensor  Nx1x28x28
    train_labels : torch.Tensor  N
    sampler_fn   : Callable[[int], List[int]]
                   returns *ordered* index list for one epoch
    """
    set_seed()
    net = SimpleNet().to(DEVICE)
    opt = torch.optim.SGD(net.parameters(), lr=SGD_LR)
    loss_fn = nn.CrossEntropyLoss()

    N = len(train_images)

    for _ in range(EPOCHS):
        idx_order = sampler_fn(N)
        loader = DataLoader(
            TensorDataset(train_images[idx_order], train_labels[idx_order]),
            batch_size=BATCH_SIZE,
            shuffle=False,       # sampler determines order
        )
        for x, y in loader:
            x, y = x.to(DEVICE), y.to(DEVICE)
            opt.zero_grad()
            loss_fn(net(x), y).backward()
            opt.step()
    return net

# --- Evaluation --------------------------------------------------------------
@torch.no_grad()
def accuracy(model, test_loader):
    correct = total = 0
    for x, y in test_loader:
        x, y = x.to(DEVICE), y.to(DEVICE)
        pred = model(x).argmax(dim=1)
        correct += (pred == y).sum().item()
        total   += y.size(0)
    return correct / total
