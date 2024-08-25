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
def addingDataItem(base_model: BaseModel, item: str, data_type: str, default, description: str) -> BaseModel:
    # 取得現有 BaseModel 的欄位和類型標註
    fields = {
        field_name: (field_info, base_model.model_fields[field_name])
        for field_name, field_info in base_model.__annotations__.items()
    }

    # 新增一個新的欄位
    new_field = (eval(data_type), Field(default=default, description=description))

    # 將新欄位加入到欄位字典中
    fields[item] = new_field

    # 使用更新後的欄位來創建一個新的 BaseModel
    UpdatedModel = create_model('UpdatedModel', **fields)

    return UpdatedModel

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

def updateData(base: BaseModel) -> dict:
    # csvfile = f"{data_folder}/test_user.csv"
    #
    # # Read the existing CSV file
    # old_data = pd.read_csv(csvfile)
    #
    # # Convert the BaseModel instance to a dictionary
    # new_data = base.model_dump()
    #
    # # Find the matching item and update the 'default' field
    # for item in new_data:
    #     if item in old_data['item'].values:
    #         # Update the 'default' field for the matching item
    #         old_data.loc[old_data['item'] == item, 'default'] = new_data[item]
    #
    # # Save the updated DataFrame back to the CSV file
    # old_data.to_csv(csvfile, index=False)

    return base.model_dump()

# get unknown information
def getUnknownInfo(d: dict) -> str:
    unknown_info = [field for field, value in d.items() if value in {'unknown', 0}]

    return (
        "All information known"
        if not unknown_info
        else "The unknown information are: " + ", ".join(unknown_info)
    )

PersonalInfoBase = convertToBaseModel(f'{data_folder}/test_user.csv')
PersonalInfoBase = addingDataItem(PersonalInfoBase, "summary", "str", "unknown", "Running detail summary of conversation. Update this with new input")