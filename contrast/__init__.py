__version__ = "0.0.2"

from .train import loss as loss
from .train.trainer import ContrastTrainer
from .train.arguments import ContrastArguments
from .datasets import *
from .train.callback import *
from .modelling import *

def seed_everything(seed=42):
    import random
    import numpy as np
    import torch

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True