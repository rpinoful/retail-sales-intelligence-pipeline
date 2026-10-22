import pandas as pd
from pathlib import Path


def save_parquet(dataframe_dictionary: dict[str, pd.DataFrame], output_directory: Path) -> str:

    #checking if the output_directory works good:
    output_directory.mkdir(parents=True, exist_ok=True)

    for dataframe_name, dataframe in dataframe_dictionary.items():
        #creating output route with name_file
        output_route = output_directory / f"{dataframe_name}.parquet"
        dataframe.to_parquet(output_route, index=False)

    return print(f"Parquet files saved successfully in {output_directory.name}")