"""
This scripts contians all the ingestion methods that have been used to add datasets to aimmdb.


"""

from tiled.client import from_uri
from tiled.queries import Key

import pathlib
import re
import json
import pandas as pd

from heald_labview import mangle_dup_names


# NOTE this hardcodes BM prefix
def parse_filename(name):
    if "622" in name:
        sample = "BM_NCM622"
    elif "NCMA" in name:
        sample = "BM_NCMA"
    elif "712_Al_free" in name:
        sample = "BM_NCM712"
    elif "712" in name:
        sample = "BM_NCM712-Al"
    elif "811" in name:
        sample = "BM_NCM811"
    else:
        raise KeyError(f"unable to parse sample from {name}")

    if sample == "Ni_metal":
        charge = None
    elif "Pristine" in name:
        charge = (0, 0.0, "DC")
    else:
        if "1st" in name:
            cycle = 1
        elif "2nd" in name:
            cycle = 2
        elif "10th" in name:
            cycle = 10
        else:
            raise KeyError(f"unable to parse cycle from {name}")

        voltage_str = re.search("(\d*)V", name)[0]
        if voltage_str == "43V":
            voltage = 4.3
            state = "C"
        elif voltage_str == "48V":
            voltage = 4.8
            state = "C"
        elif voltage_str == "3V":
            voltage = 3.0
            state = "DC"
        else:
            raise KeyError(f"unable to parse voltage from {voltage_str}")

        charge = (cycle, voltage, state)

    if charge:
        keys = ["cycle", "voltage", "state"]
        charge = dict(zip(keys, charge))
    return sample, charge


def parse_filename_gihyeok(name):
    if "622" in name:
        sample = "BM_NCM622"
    elif "NCMA" in name:
        sample = "BM_NCMA"
    elif "712_Al-doped" in name:
        sample = "BM_NCM712-Al"
    elif "712" in name:
        sample = "BM_NCM712"
    elif "811" in name:
        sample = "BM_NCM811"
    else:
        raise KeyError(f"unable to parse sample from {name}")

    if "Co" in name:
        symbol = "Co"
    elif "Mn" in name:
        symbol = "Mn"
    elif "Ni" in name:
        symbol = "Ni"
    elif "O" in name:
        symbol = "O"
    else:
        raise KeyError(f"unable to parse symbol from {name}")

    return sample, symbol


def parse_filename_nslsii(name):
    if "622" in name:
        sample = "BM_NCM622"
    elif "NCMA" in name or "NMCA" in name:
        sample = "BM_NCMA"
    elif "712" in name or "721" in name:
        sample = "BM_NCM712-Al"
    else:
        raise KeyError(f"unable to parse sample from {name}")

    if "pristine" in name:
        charge = (0, 0.0, "DC")
    else:
        if "1st" in name:
            cycle = 1
        elif "2nd" in name:
            cycle = 2
        elif "10th" in name:
            cycle = 10
        else:
            # raise KeyError(f"unable to parse cycle from {name}")
            cycle = 1  # In Eli's dataset, files with no cycle value in the filename
            # are assumed to be cycle = 1

        if "4_3" in name:
            voltage = 4.3
            state = "C"
        elif "4_8" in name:
            voltage = 4.8
            state = "C"
        elif "3V" in name or "3_0" in name:
            voltage = 3.0
            state = "DC"
        else:
            raise KeyError(f"unable to parse voltage from {name}")

        charge = (cycle, voltage, state)

    if charge:
        keys = ["cycle", "voltage", "state"]
        charge = dict(zip(keys, charge))
    return sample, charge


def get_experiment_params(name):

    experiment_to_params_map = {
        "1-1": {
            "sample": "BM_NCMA",
            "charge": {"cycle": 1, "voltage": 3.0, "state": "DC"},
        },
        "1-2": {
            "sample": "BM_NCMA",
            "charge": {"cycle": 10, "voltage": 4.8, "state": "C"},
        },
        "1-3": {
            "sample": "BM_NCM712-Al",
            "charge": {"cycle": 1, "voltage": 3.0, "state": "DC"},
        },
        "1-4": {
            "sample": "BM_NCM712-Al",
            "charge": {"cycle": 10, "voltage": 3.0, "state": "DC"},
        },
        "2-1": {
            "sample": "BM_NCMA",
            "charge": {"cycle": 2, "voltage": 4.8, "state": "C"},
        },
        "2-2": {
            "sample": "BM_NCM712-Al",
            "charge": {"cycle": 1, "voltage": 4.8, "state": "C"},
        },
        "2-3": {
            "sample": "BM_NCM712-Al",
            "charge": {"cycle": 10, "voltage": 4.8, "state": "C"},
        },
        "2-4": {
            "sample": "BM_NCM811",
            "charge": {"cycle": 1, "voltage": 3.0, "state": "DC"},
        },
        "3-1": {
            "sample": "BM_NCM712-Al",
            "charge": {"cycle": 0, "voltage": 0.0, "state": "DC"},
        },
        "3-2": {
            "sample": "BM_NCM712-Al",
            "charge": {"cycle": 2, "voltage": 4.8, "state": "C"},
        },
        "3-3": {
            "sample": "BM_NCM622",
            "charge": {"cycle": 2, "voltage": 4.8, "state": "C"},
        },
        "3-4": {
            "sample": "BM_NCM811",
            "charge": {"cycle": 2, "voltage": 4.8, "state": "C"},
        },
        "4-1": {
            "sample": "BM_NCM811",
            "charge": {"cycle": 2, "voltage": 4.3, "state": "C"},
        },
        "4-2": {
            "sample": "BM_NCM622",
            "charge": {"cycle": 1, "voltage": 4.8, "state": "C"},
        },
        "4-3": {
            "sample": "BM_NCM811",
            "charge": {"cycle": 10, "voltage": 3.0, "state": "DC"},
        },
        "4-4": {
            "sample": "BM_NCMA",
            "charge": {"cycle": 1, "voltage": 4.8, "state": "C"},
        },
        "5-1": {
            "sample": "BM_NCM712-Al",
            "charge": {"cycle": 1, "voltage": 4.3, "state": "C"},
        },
        "5-2": {
            "sample": "BM_NCM622",
            "charge": {"cycle": 2, "voltage": 4.3, "state": "C"},
        },
        "5-3": {
            "sample": "BM_NCM811",
            "charge": {"cycle": 1, "voltage": 4.8, "state": "C"},
        },
        "5-4": {
            "sample": "BM_NCM622",
            "charge": {"cycle": 10, "voltage": 3.0, "state": "DC"},
        },
        "6-1": {
            "sample": "BM_NCM622",
            "charge": {"cycle": 1, "voltage": 3.0, "state": "DC"},
        },
        "6-2": {
            "sample": "BM_NCM712-Al",
            "charge": {"cycle": 2, "voltage": 4.8, "state": "C"},
        },
        "6-3": {
            "sample": "BM_NCM811",
            "charge": {"cycle": 10, "voltage": 4.8, "state": "C"},
        },
        "6-4": {
            "sample": "BM_NCMA",
            "charge": {"cycle": 0, "voltage": 0.0, "state": "DC"},
        },
        "7-1": {
            "sample": "BM_NCMA",
            "charge": {"cycle": 2, "voltage": 4.3, "state": "C"},
        },
        "7-2": {
            "sample": "BM_NCM622",
            "charge": {"cycle": 1, "voltage": 4.3, "state": "C"},
        },
        "7-3": {
            "sample": "BM_NCM811",
            "charge": {"cycle": 0, "voltage": 0.0, "state": "DC"},
        },
        "7-4": {
            "sample": "BM_NCMA",
            "charge": {"cycle": 1, "voltage": 4.3, "state": "C"},
        },
        "8-1": {
            "sample": "BM_NCM622",
            "charge": {"cycle": 0, "voltage": 0.0, "state": "DC"},
        },
        "8-2": {
            "sample": "BM_NCM811",
            "charge": {"cycle": 1, "voltage": 4.3, "state": "C"},
        },
        "8-3": {
            "sample": "BM_NCMA",
            "charge": {"cycle": 10, "voltage": 4.8, "state": "C"},
        },
        "8-4": {
            "sample": "BM_NCM622",
            "charge": {"cycle": 10, "voltage": 4.8, "state": "C"},
        },
    }

    split_name = name.split()
    experiment_number = split_name[0]
    experiment_params = experiment_to_params_map[experiment_number]

    return experiment_params["sample"], experiment_params["charge"]


def read_header(f):
    header = ""
    for line in f:
        if line.startswith("Time (s)"):
            line = line.rstrip()
            header = line.split("\t")
            return header


def read_wanli(f):
    names = read_header(f)
    names = mangle_dup_names(names)
    df = pd.read_csv(f, sep="\t", names=names)

    translation = {
        "Mono Energy": "energy",
        "Counter 0": "i0",
        "Counter 1": "tey",
        "Counter 2": "tfy",
        # "Counter 3": "i0",
    }
    df = df.rename(columns=translation)[list(translation.values())]

    df["mu_tfy"] = df["tfy"] / df["i0"]
    df["mu_tey"] = df["tey"] / df["i0"]

    return df


def read_eli_txt(f):

    lines = f.readlines()

    metadata = {}

    for line in lines:
        line = line.rstrip()

        if line[0] == "#":
            # Metadata
            meta_raw = line[2:]
            if "Column" in meta_raw:
                break  # No more relevant information after this line
            else:
                if ": " in meta_raw:
                    # Builds metadata
                    meta_split = meta_raw.split(": ", 1)
                    keys = meta_split[0].split(".")
                    if keys[0].lower() not in metadata:
                        metadata[keys[0].lower()] = {}

                    metadata[keys[0].lower()][keys[1].lower()] = meta_split[1]

    return metadata


def read_eli_dat(f):
    df = pd.read_csv(f, sep=",", index_col=0)
    df.columns = ["energy", "mutrans", "mufluor", "murefer"]
    return df


def ingest_aimm_ncm_wanli(c, sample_ids, data_path):
    c_uid = c["uid"]
    files = list(data_path.glob("*.txt"))

    for file in files:
        fname = file.name
        print(fname)

        try:
            sample_name, charge = parse_filename(fname)
        except KeyError as e:
            print(f"failed to extract sample from {fname}")
            continue

        sample_id = sample_ids[sample_name]

        with open(file, "r") as f:
            df = read_wanli(f)

        metadata = {
            "dataset": "nmc",
            "fname": fname,
            "charge": charge,
            "facility": {"name": "ALS"},
            "beamline": {"name": "8.0.1"},
            "element": {"symbol": "Ni", "edge": "L3"},
            "sample_id": sample_id,
        }

        results = c_uid.search(Key("fname") == fname)
        if len(results) != 0:
            uid = results.values().first().item["id"]
            del c_uid[uid]
            c_uid.write_dataframe(
                df, metadata, specs=["XAS_TEY", "XAS_TFY", "HasBatteryChargeData"]
            )
        else:
            print(f"{fname} is not part of the database")


def ingest_aimm_ncm_eli(c, sample_ids, data_path):
    c_uid = c["uid"]
    files = list(data_path.glob("*.txt"))

    for file in files:
        fname = file.stem  # source of data comes from two different files .dat and .txt
        print(fname)

        try:
            # sample_name, charge = parse_filename_nslsii(fname)
            sample_name, charge = get_experiment_params(fname)
        except KeyError as e:
            print(f"failed to extract sample from {fname}")
            continue

        sample_id = sample_ids[sample_name]

        with open(file, "r") as f:
            meta = read_eli_txt(f)
            meta["beamline"]["name"] = "ISS"
            meta["sample"]["name"] = sample_name

        metadata = {
            "dataset": "nmc",
            "fname": fname,
            "charge": charge,
            "sample_id": sample_id,
        }

        metadata.update(meta)

        dat_file = data_path / (fname + ".dat")
        with open(dat_file, "r") as f:
            df = read_eli_dat(f)

        # print(df.head())
        # print(sample_name, sample_id, metadata["element"])
        c_uid.write_dataframe(df, metadata, specs=["XAS", "HasBatteryChargeData"])


def ingest_aimm_ncm_gihyeok(c, sample_ids, data_path):
    c_uid = c["uid"]
    files = list(data_path.glob("*.txt"))

    for file in files:
        fname = file.name
        print(fname)

        try:
            sample_name, symbol = parse_filename_gihyeok(fname)
        except KeyError as e:
            print(f"failed to extract sample from {fname}")
            continue

        sample_id = sample_ids[sample_name]

        with open(file, "r") as f:
            df = pd.read_csv(f, sep="\t")

        new_columns = ["energy", "normfluor"]

        metadata = {
            "dataset": "nmc",
            "fname": fname,
            "facility": {"name": "ALS"},
            "beamline": {"name": "8.0.1"},
            "element": {"symbol": symbol, "edge": "L3"},
            "sample_id": sample_id,
        }

        for column in df.columns:
            if column != "Energy":
                sub_df = df[["Energy", column]].copy()
                sub_df.columns = new_columns

                if "Pristine" in column:
                    charge = (0, 0.0, "DC")
                else:
                    if "1st" in column:
                        cycle = 1
                    elif "2nd" in column:
                        cycle = 2
                    elif "10th" in column:
                        cycle = 10
                    else:
                        raise KeyError(f"unable to parse cycle from {column}")

                    if "3.0" in column:
                        voltage = 3.0
                        state = "DC"
                    elif "4.8" in column:
                        voltage = 4.8
                        state = "C"
                    else:
                        raise KeyError(f"unable to parse voltage from {column}")

                    charge = (cycle, voltage, state)

                keys = ["cycle", "voltage", "state"]
                charge = dict(zip(keys, charge))
                metadata["charge"] = charge

                c_uid.write_dataframe(
                    sub_df, metadata, specs=["XAS", "HasBatteryChargeData"]
                )


def get_sample_charge(name):

    file_to_sample_map = {
        "BM_NCM622": [
            "Sigscan71987",
            "Sigscan71991",
            "Sigscan71996",
            "Sigscan72001",
            "Sigscan72005",
            "Sigscan72009",
            "Sigscan71970",
            "Sigscan71974",
        ],
        "BM_NCMA": [
            "Sigscan71986",
            "Sigscan71990",
            "Sigscan71995",
            "Sigscan71999",
            "Sigscan72004",
            "Sigscan72008",
            "Sigscan71969",
            "Sigscan71973",
        ],
        "BM_NCM811": [],
        "BM_NCM712-Al": [
            "Sigscan71983",
            "Sigscan71988",
            "Sigscan71993",
            "Sigscan71997",
            "Sigscan72002",
            "Sigscan72006",
            "Sigscan72010",
            "Sigscan71971",
        ],
        "BM_NCM712": [
            "Sigscan71294",
            "Sigscan71295",
            "Sigscan71296",
            "Sigscan71297",
            "Sigscan71312",
            "Sigscan71313",
            "Sigscan71314",
            "Sigscan71315",
            "Sigscan71985",
            "Sigscan71989",
            "Sigscan71994",
            "Sigscan71998",
            "Sigscan72003",
            "Sigscan72007",
            "Sigscan71968",
            "Sigscan71972",
        ],
    }

    file_to_charge_map = {
        "Pristine": [
            "Sigscan71294",
            "Sigscan72001",
            "Sigscan72002",
            "Sigscan72003",
            "Sigscan72004",
        ],
        "1st_43V": [
            "Sigscan71295",
            "Sigscan72005",
            "Sigscan72006",
            "Sigscan72007",
            "Sigscan72008",
        ],
        "1st_48V": [
            "Sigscan71296",
            "Sigscan72009",
            "Sigscan72010",
            "Sigscan71968",
            "Sigscan71969",
        ],
        "1st_3V": [
            "Sigscan71297",
            "Sigscan71970",
            "Sigscan71971",
            "Sigscan71972",
            "Sigscan71973",
        ],
        "2nd_43V": [
            "Sigscan71312",
            "Sigscan71983",
            "Sigscan71985",
            "Sigscan71986",
            "Sigscan71974",
        ],
        "2nd_48V": [
            "Sigscan71313",
            "Sigscan71987",
            "Sigscan71988",
            "Sigscan71989",
            "Sigscan71990",
        ],
        "10th_48V": [
            "Sigscan71314",
            "Sigscan71991",
            "Sigscan71993",
            "Sigscan71994",
            "Sigscan71995",
        ],
        "10th_3V": [
            "Sigscan71315",
            "Sigscan71996",
            "Sigscan71997",
            "Sigscan71998",
            "Sigscan71999",
        ],
    }

    str_sample = None
    str_charge = None

    fname = name.split("-")[0].capitalize()

    for key, value in file_to_sample_map.items():
        if fname in value:
            str_sample = key
            break

    for key, value in file_to_charge_map.items():
        if fname in value:
            str_charge = key
            break

    if str_sample is not None and str_charge is not None:
        return str_sample + "_" + str_charge


def ingest_aimm_ncm_gihyeok_sigscan(c, sample_ids, data_path):

    c_uid = c["uid"]
    files = list(data_path.glob("*.txt"))

    for file in files:
        fname = file.name
        print(fname)

        file_params = get_sample_charge(file.stem)
        print(file_params)

        try:
            sample_name, charge = parse_filename(file_params)
        except KeyError as e:
            print(f"failed to extract sample from {fname}")
            continue

        sample_id = sample_ids[sample_name]
        print(sample_name, sample_id)

        with open(file, "r") as f:
            df = read_wanli(f)

        metadata = {
            "dataset": "nmc",
            "fname": fname,
            "charge": charge,
            "facility": {"name": "ALS"},
            "beamline": {"name": "8.0.1"},
            "element": {"symbol": "Co", "edge": "L3"},
            "sample_id": sample_id,
        }

        # print(df.head())
        # print(metadata)

        c_uid.write_dataframe(
            df, metadata, specs=["XAS_TEY", "XAS_TFY", "HasBatteryChargeData"]
        )


def ingest_aimm_ncm_gihyeok_oxygen(c, sample_ids, data_path):

    c_uid = c["uid"]
    files = list(data_path.glob("*.txt"))

    for file in files:
        fname = file.name
        print(fname)

        try:
            sample_name, symbol = parse_filename_gihyeok(fname)
        except KeyError as e:
            print(f"failed to extract sample from {fname}")
            continue

        sample_id = sample_ids[sample_name]

        with open(file, "r") as f:
            df = pd.read_csv(f, sep="\t")

        new_columns = ["energy", "normfluor"]

        metadata = {
            "dataset": "nmc",
            "fname": fname,
            "facility": {"name": "ALS"},
            "beamline": {"name": "8.0.1"},
            "element": {"symbol": symbol, "edge": "K"},
            "sample_id": sample_id,
        }

        for i in range(0, len(df.columns), 2):
            sub_df = df[[df.columns[i], df.columns[i + 1]]].copy()
            sub_df.columns = new_columns
            sub_df = sub_df.dropna()

            column = df.columns[i + 1]
            if "Pristine" in column:
                charge = (0, 0.0, "DC")
            else:
                if "1st" in column:
                    cycle = 1
                elif "2nd" in column:
                    cycle = 2
                elif "10th" in column:
                    cycle = 10
                else:
                    raise KeyError(f"unable to parse cycle from {column}")

                if "3.0" in column:
                    voltage = 3.0
                    state = "DC"
                elif "4.3" in column:
                    voltage = 4.3
                    state = "C"
                elif "4.8" in column:
                    voltage = 4.8
                    state = "C"
                else:
                    raise KeyError(f"unable to parse voltage from {column}")

                charge = (cycle, voltage, state)

            keys = ["cycle", "voltage", "state"]
            charge = dict(zip(keys, charge))
            metadata["charge"] = charge

            # print(sub_df.head())
            # print(metadata)

            c_uid.write_dataframe(
                sub_df, metadata, specs=["XAS", "HasBatteryChargeData"]
            )


def ingest_aimm_ncm_vasp(data_path):
    file = data_path / "xas_nmc_vasp.json"
    if file.is_file():
        with open(file, "r") as f:
            file_data = json.load(f)
            d = {}
            meta = {}
            if file_data["energy"].keys() == file_data["intensity"].keys():
                for key, values in file_data["energy"].items():
                    d[key] = {"energy": values, "mutrans": file_data["intensity"][key]}
                    ###
                    meta[key] = {
                        "dataset": "sim_nmc",
                        "fname": file.name,
                        "facility": {"name": "CNM"},
                        "beamline": {"name": "Simulation"},
                    }
            return file_data


def ingest_aimm_ncm_feff(c, data_path):
    c_uid = c["uid"]
    file = data_path / "xas_nmc_feff_v2.json"
    if file.is_file():
        with open(file, "r") as f:
            file_data = json.load(f)

            spectrum = {}
            meta = {}
            for key, values in file_data["spectrum"].items():
                # if file_data['composition'][key] in  samples:
                spectra = {
                    "energy": values["energies"],
                    "mutrans": values["mu"],
                    "k": values["wavenumber"],
                    "chi": values["chi"],
                }
                df = pd.DataFrame(spectra)
                spectrum[key] = df

                meta[key] = {
                    "dataset": "nmc_simulation",
                    "file": {"fname": file.name, "id": key},
                    "facility": {"name": "CNM"},
                    "beamline": {"name": "Simulation"},
                    "element": {
                        "symbol": file_data["absorbing_atom"][key],
                        "edge": file_data["EDGE"][key],
                    },
                    "sample": {"name": file_data["composition"][key].upper()},
                    # "sample_id": sample_id,
                }

                try:
                    structure_id = (
                        c_uid.search(Key("file.id") == key).keys().first()
                    )  # Get unique id generated in the server for the structure
                    meta["structure_id"] = structure_id
                except KeyError as e:
                    print(f"failed to extract structure from id: {key}")

                # meta.append(metadata)
                c_uid.write_dataframe(spectrum[key], meta[key], specs=["simulation"])
                print(file.name, key, structure_id)

            # return file_data
            # return spectrum, meta


def ingest_aimm_feff_structures(c, data_path):
    c_uid = c["uid"]
    file = data_path / "xas_nmc_feff_v2.json"
    if file.is_file():
        with open(file, "r") as f:
            file_data = json.load(f)

            structures = {}
            df = pd.DataFrame()
            for key, values in file_data["input"].items():
                structures[key] = {}
                structures[key]["structure"] = values["structure"]
                structures[key]["dataset"] = "nmc_sim_structure"
                structures[key]["file"] = {"fname": file.name, "id": key}

                c_uid.write_dataframe(df, structures[key], specs=["structure"])
                print(file.name, key)

    # return structures, file_data


def ingest_aimm_ncm_sim_xanes(c, data_path, start):
    # c_uid = c["uid"]
    file = data_path / "HJ_NMC_XANES.json"
    if file.is_file():
        with open(file, "r") as f:
            file_data = json.load(f)

            spectrum = {}
            meta = {}
            for i in range(start, len(file_data)):

                try:
                    structure_id = (
                        c["dataset"]["nmc_sim_structure"]["uid"]
                        .search(Key("file.id") == str(file_data[i]["structure_id"]))
                        .keys()
                        .first()
                    )  # Get unique id generated in the server for the structure
                    print(
                        f"{i} - {len(file_data)} - {file_data[i]['structure_id']} - {structure_id}"
                    )
                    # meta["structure_id"] = structure_id
                except KeyError as e:
                    print(f"failed to extract structure from id: {i}")

                if structure_id is None:
                    print(f"None: {i} - {file_data[i]['structure_id']}")
                else:
                    if len(structure_id) == 0:
                        print(f"Empty: {i} - {file_data[i]['structure_id']}")

            return file_data


def update_alignment_ncm_wanli(c):

    alignments = {
        "FVHEqkxTqz8": {"name": "BM_NCM622", "offset": -0.278},
        "SNH7Dg7PR9h": {"name": "BM_NCM712-Al", "offset": -0.278},
        "f6pVatZS3D9": {"name": "BM_NCMA", "offset": -0.278},
        "4FToXZNyQBr": {"name": "BM_NCM712", "offset": -1.135},
    }

    for key, value in alignments.items():
        spectra = c["dataset"]["nmc"]["element"]["Ni"]["edge"]["L3"]["sample"][key][
            "uid"
        ].search(Key("facility.name") == "ALS")
        for spectra_key, spectra_value in spectra.items():
            metadata = dict(spectra_value.metadata)
            if "energy_offset" not in metadata:
                # Remove auto-generated entries in metadata of old node. Server will create new entries for new node
                metadata.pop("_tiled")
                metadata.pop("sample")

                metadata["energy_offset"] = value["offset"]

                df = spectra_value.read()
                df = df + value["offset"]

                if "tey" in df.columns:
                    specs = ["XAS_TEY", "XAS_TFY", "HasBatteryChargeData"]
                else:
                    specs = ["XAS", "HasBatteryChargeData"]

                old_uid = spectra_value.uid

                del c["uid"][spectra_key]

                c["uid"].write_dataframe(df, metadata, specs=specs)

                new_node = (
                    c["uid"].search(Key("fname") == metadata["fname"]).values().first()
                )

                print(f"Node updated from {old_uid} to {new_node.uid}")
            else:
                print(f"Skipped: alignment has been updated previously - {spectra_key}")


def validate_files(c, data_path):
    c_uid = c["uid"]
    files = list(data_path.glob("*.txt"))

    counter = 0
    for file in files:
        fname = file.name
        print(fname)

        results = c_uid.search(Key("fname") == fname)
        if len(results) != 0:
            counter += 1
            print(results.values().first().item["id"])
        else:
            print("Not found")
    print(f"total files found: {counter}")
