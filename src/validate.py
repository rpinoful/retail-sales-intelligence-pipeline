import pandas as pd



def validate_required_columns(table_name:str,dataframe: dict[str, pd.DataFrame],required_columns:dict[str,list[str]]):
    """
    check all the columns validate from dataframes readed
    """
    # 1 - Taking all the require columns 
    columns_rules = set(required_columns[table_name])


    # 2 - Taking all values columns from current dataframe
    columns_dataframe = set(dataframe.columns)


    # 3 - Checking columns between columns rules and columns dataframe
    missing_columns = columns_rules - columns_dataframe

    if missing_columns:
        raise ValueError(
            f" The dataframe {table_name} have this missing columns {missing_columns} ❌"
        )

    
    




    


def validate_all_columns(dataframe_dictionary:dict[str,pd.DataFrame],required_columns:dict[str,list[str]])->None:
    """
    parameters : Dataframe dictionary , list dictionary (required_columns)
    - 1 Ierate dictionary dataframe
    - 2 pass key and dataframe to required columns function
    - 3  validate_required_columns checking : required_columns dictionary rules with current dataframe columns 
    """
    for dictionary_key,dataframe in dataframe_dictionary.items():
        validate_required_columns(dictionary_key,dataframe,required_columns)

    return "All dataframe columns were validated successfully ✅"


    