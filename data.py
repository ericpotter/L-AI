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


# Example usage
username = 'test_user'
createCSV(username)

# Read the initial CSV file
csv_file = f"{data_folder}/{username}.csv"
df = pd.read_csv(csv_file)

# Add a new data item to the DataFrame
df = addingDataItem('age', 'int', 30, "User's age", df)
df.to_csv(csv_file, index=False)

# Convert CSV data to a Pydantic BaseModel
DynamicModel = convertToBaseModel(csv_file)

# Create an instance of the dynamically generated model
model_instance = DynamicModel(age=25)
print(model_instance)