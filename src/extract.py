from pathlib import Path
import pandas as pd

#dictionary when to save all the table reading
dict_dataframes = {}





def read_excel(route: Path) -> dict:
    folder = Path(route)

    if not folder.exists():
        raise FileNotFoundError(f"File not found: {folder}")


    try:
        dataframes = pd.read_excel(folder,sheet_name=None)
        print("Excel file readed with sucess ✅")


        
    except  PermissionError as error:
        raise PermissionError(
        print(f" File dont found{error}")
        ) from error
    

    except  ValueError as error:
            raise ValueError(
                print(f" File dont found{error}")    
            ) from error
            

    return dataframes





def read_parquet_files(path_parquet:Path) -> dict:
     # search all the parquet files in the folder:
     dir_parquet = path_parquet.glob("*.parquet")
     dataframes_dictionary_bronze = {f.stem:pd.read_parquet(f) for f in dir_parquet}
     print(f" Was readed all the parquet files from path passed {dataframes_dictionary_bronze.keys()} ✅ \n")
     return dataframes_dictionary_bronze








