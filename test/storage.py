import firebase_admin
from firebase_admin import credentials, initialize_app, storage
import firebase_admin.storage
from google.cloud import storage
from google.oauth2 import service_account

json_file = "key.json"

# Init firebase with your credentials
cred = credentials.Certificate(json_file)
initialize_app(cred, {'storageBucket': 'aetheria-7fcbf.appspot.com'})

# upload file
def upload_blob(bucket_name, source_file_name, destination_blob_name):
    credentials = service_account.Credentials.from_service_account_file(json_file)
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    print(f"File {source_file_name} uploaded to {destination_blob_name}.")

# upload_blob(firebase_admin.storage.bucket().name, 'temp.m4a', 'test/123.m4a')

# download file
def download_blob(bucket_name, source_blob_name, download_file_name):
    credentials = service_account.Credentials.from_service_account_file(json_file)
    storage.Client(credentials=credentials).bucket(bucket_name).blob(source_blob_name).download_to_filename(download_file_name)

# download_blob(firebase_admin.storage.bucket().name, 'test/123.m4a', 'download.m4a')

def delete_blob(bucket_name,  delete_file_name):
    credentials = service_account.Credentials.from_service_account_file(json_file)
    storage.Client(credentials=credentials).bucket(bucket_name).blob(delete_file_name).delete()

# delete_blob(firebase_admin.storage.bucket().name, 'temp.m4a')