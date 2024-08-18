import os
import pandas as pd
from pydantic import BaseModel, Field, create_model

# data folder
data_folder = "health_data"

# Function to create a new CSV for personal health data based on the template
def createCSV(username):
    # Path to the template CSV file
    template_csv = f'{data_folder}/data_template.csv'  # Replace with the correct path

    # Read the template CSV into a DataFrame
    template_df = pd.read_csv(template_csv)

    # Save a new CSV for the given username based on the template
    new_csv_file = f"{data_folder}/{username}.csv"
    template_df.to_csv(new_csv_file, index=False)


# Function to add a new data item to the DataFrame
def addingDataItem(item, dataType, default, description, dataBase):
    # Create a new row with the provided data
    new_row = pd.DataFrame({
        'item': [item],
        'dataType': [dataType],
        'default': [default],
        'description': [description]
    })

    # Use pd.concat to add the new row to the DataFrame
    dataBase = pd.concat([dataBase, new_row], ignore_index=True)
    return dataBase


# Function to convert CSV data to a Pydantic BaseModel
def convertToBaseModel(csvData):
    # Read CSV data into a DataFrame
    df = pd.read_csv(csvData)

    # Dynamically create attributes for the model
    fields = {
        row['item']: (eval(row['dataType']), Field(default=row['default'], description=row['description']))
        for _, row in df.iterrows()
    }

    # Create and return the new model using create_model
    DynamicModel = create_model('DynamicModel', **fields)
    return DynamicModel

# convert basemodel to dictionary
def getInfoDict(base: BaseModel) -> dict:
    # Convert a BaseModel instance to a dictionary containing all its fields and values.
    return base.model_dump()

# get unknown information
def getUnknownInfo(d: dict) -> str:
    # 過濾出值為 'unknown' 或 0 的字段
    unknown_info = [field for field, value in d.items() if value in {'unknown', 0}]

    # 根據是否存在未知信息返回結果
    return (
        "All information known"
        if not unknown_info
        else "The unknown information are: " + ", ".join(unknown_info)
    )

PersonalInfoBase = convertToBaseModel('health_data/test_user.csv')