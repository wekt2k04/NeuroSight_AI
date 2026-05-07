from typing import List, Tuple

from torch.utils.data import DataLoader

from .impl import prepare_data as _prepare_data


def prepare_data(csv_path: str, images_dir: str, batch_size: int = 64, val_split: float = 0.2) -> Tuple[DataLoader, DataLoader, List[str]]:
    """Public ETL entry point used by scripts, notebooks, and future APIs."""
    return _prepare_data(csv_path, images_dir, batch_size, val_split)
