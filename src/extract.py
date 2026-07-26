from pathlib import Path
import pandas as pd

#dictionary when to save all the table reading
dict_dataframes = {}





def read_excel(route: str) -> dict:
    folder = Path(route)

    if not folder.exists():
        raise FileNotFoundError(f"File not found: {folder}")


    try:
        dataframes = pd.read_excel(folder,sheet_name=None)
        print("Excel file readed with sucess ✅")


        
    except  PermissionError as e:
        print(f" File dont found{e}")

    except  ValueError as e:
            print(f" File dont found{e}")



    return dataframes