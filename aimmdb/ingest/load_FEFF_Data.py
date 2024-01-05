import copy
import pathlib

import numpy as np
import pandas as pd

from tiled.client import from_uri
from tiled.examples.xdi import read_xdi
from tiled.queries import Key

import pandas as pd
from pathlib import Path

def load_feff_data(data_path, verbose=True):
    """
    Parameters
    ----------
    data_path : os.PathLike
        path to the feff.inp, feff.out, and xmu.dat file.
    verbose : bool, optional
        Prints debug information if True.

    Returns
    -------
    feff_data : pandas.Dataframe
        dataframe containing the xmu.dat data
    metadata : dict
        dictionary containing the feff.inp, feff.out, and xmu.dat metadata
    """

    data_path = Path(data_path)

    feff_inp = data_path / "feff.inp"
    feff_out = data_path / "feff.out"
    xmu_dat = data_path / "xmu.dat"

    data = pd.read_csv(
        xmu_dat,
        sep="\s+",
        header=None,
        names=["omega", "e", "k", "mu", "mu0", "chi"],
        comment="#",
    )

    metadata = {
        "feff.inp": feff_inp.read_text(),
        "feff.out": feff_out.read_text(),
    }

    dat = [
        line
        for line in xmu_dat.read_text().splitlines()
        if line.startswith("#")
    ]
    metadata["xmu.dat-comments"] = "\n".join(dat)

    if verbose:
        print("FEFF Input:", feff_inp)
        print("FEFF Output:", feff_out)
        print("FEFF Data:", xmu_dat)
        print(data)
        print(metadata)

    # returns data and metadata, a pd.DataFrame and dict, respectively.
    return data, metadata