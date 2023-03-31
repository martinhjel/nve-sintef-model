import pytest
from pathlib import Path
import pandas as pd
import tempfile
import os
from nve_sintef_model.io.enmd.get_fastkontrakter import get_fastkontrakter


def test_invalid_file_path():
    non_existent_file = Path("non_existent_file.txt")
    with pytest.raises(FileNotFoundError):
        get_fastkontrakter(non_existent_file)