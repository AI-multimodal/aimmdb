import copy
import pandas as pd
from pathlib import Path

from aimmdb.ingest import load_feff_data


DATA_PATH = Path("aimmdb/_tests/data/feff/65272_C_007")


def test_load_feff_data():

    data, metadata = load_feff_data(DATA_PATH)

    assert isinstance(data, pd.DataFrame)
    assert isinstance(metadata, dict)
    assert isinstance(metadata["feff.inp"], str)
    assert isinstance(metadata["feff.out"], str)
    assert isinstance(metadata["xmu.dat-comments"], str)


def copy_feff_data():

    data, metadata = load_feff_data(DATA_PATH)

    data_copy = copy.deepcopy(data)

    assert data.equals(data_copy)

    metadata_copy = copy.deepcopy(metadata)

    assert metadata.equals(metadata_copy)

    assert isinstance(data_copy, pd.DataFrame)
    assert isinstance(metadata_copy, dict)
    assert isinstance(metadata_copy["feff.inp"], str)
    assert isinstance(metadata_copy["feff.out"], str)
    assert isinstance(metadata_copy["xmu.dat-comments"], str)
