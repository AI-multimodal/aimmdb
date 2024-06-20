from tiled.adapters.dataframe import DataFrameAdapter


# dataframe adapter representing FEFF data
class FEFFAdapter(DataFrameAdapter):
    specs = ["FEFF"]
