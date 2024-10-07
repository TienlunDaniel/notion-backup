from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
import os
import json

# Replace with your own credentials
SERVICE_ACCOUNT_INFO = json.loads(os.environ['GOOGLE_DRIVE_SERVICE_ACCOUNT_SECRET_JSON'])
GOOGLE_DRIVE_ROOT_FOLDER_ID = os.environ['GOOGLE_DRIVE_ROOT_FOLDER_ID']

SCOPES = ['https://www.googleapis.com/auth/drive']

creds = service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT_INFO, scopes=SCOPES)

service = build('drive', 'v3', credentials=creds)


def drive_upload_folder(folder, drive_path):
  """
  Uploads the contents of a folder (directory) to Google Drive recursively.

  Args:
    folder: The local folder to upload.
    drive_path: The destination folder on Google Drive (ID or path).
  """

  uploaded_files = []
  for item_name in os.listdir(folder):

    item_path = os.path.join(folder, item_name)
    if os.path.isfile(item_path):
      # Upload the file
      file_metadata = {'name': item_name, 'parents': [drive_path]}
      media = MediaFileUpload(item_path, mimetype='application/octet-stream')
      file = service.files().create(body=file_metadata,
                                    media_body=media,
                                    fields='id').execute()
      uploaded_files.append(file)
      print(F'File ID: {file.get("id")} ({item_name})')
    elif os.path.isdir(item_path):
      # Create a folder in Google Drive
      folder_metadata = {'name': item_name, 
                        'mimeType': 'application/vnd.google-apps.folder',
                        'parents': [drive_path]}
      fd = service.files().create(body=folder_metadata,
                                      fields='id').execute()
      print(F'Folder ID: {fd.get("id")} ({item_name})')

      # Recursively upload the subfolder
      uploaded_files.extend(drive_upload_folder(item_path, fd.get('id')))

  return uploaded_files

def get_directories(path):
  """Gets all directories within the specified path.

  Args:
    path: The path to search in.

  Returns:
    A list of directory names.
  """
  directories = []
  for item in os.listdir(path):
    item_path = os.path.join(path, item)
    if os.path.isdir(item_path):
      directories.append(item)
  return directories

def list_files_in_folder(creds, folder_id):
    """
    Lists files within a specific folder.

    Args:
        creds: The credentials object obtained from the Google Auth library.
        folder_id: The ID of the folder.

    Returns:
        A list of file IDs within the folder.
    """
    try:
        service = build('drive', 'v3', credentials=creds)

        results = service.files().list(
            q=f"'{folder_id}' in parents",
            spaces='drive',
            fields='nextPageToken, files(id, name)',
        ).execute()
        items = results.get('files', [])

        if not items:
            print('No files found in the folder.')
            return []

        file_ids = []
        for item in items:
            print(f'{item["name"]} ({item["id"]})')
            file_ids.append(item["id"])
        return file_ids

    except HttpError as error:
        print(f'An error occurred: {error}')
        return []

def delete_files(creds, file_ids):
    """
    Deletes a list of files.

    Args:
        creds: The credentials object obtained from the Google Auth library.
        file_ids: A list of file IDs to delete.
    """
    try:
        service = build('drive', 'v3', credentials=creds)

        for file_id in file_ids:
            service.files().delete(fileId=file_id).execute()
            print(f'File with ID {file_id} deleted.')

    except HttpError as error:
        print(f'An error occurred: {error}')

files_ids_to_delete = list_files_in_folder(creds, GOOGLE_DRIVE_ROOT_FOLDER_ID)

# Example usage for ./
directories_in_tmp = get_directories('./')

for dir_name in directories_in_tmp:
  if 'Export' not in dir_name:
    print(F'directory {dir_name}')
    continue
  print(F'name of the directory {dir_name}')
  drive_upload_folder(dir_name, GOOGLE_DRIVE_ROOT_FOLDER_ID)

print(F'start deleting files with IDs {files_ids_to_delete}')
delete_files(creds, files_ids_to_delete)

