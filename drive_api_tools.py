import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

import config


def get_api_service():
    '''
    Function to obtain an authenticated Google Drive API service object.
    
    This function handles authentication by checking for existing credentials,
    refreshing them if they are expired, or performing a new OAuth2 authorization flow
    if no valid credentials are found. The resulting service object is used to interact
    with the Google Drive API.

    Returns:
        service: googleapiclient.discovery.Resource, Google Drive API service object
    '''
    creds = None

    # Load existing credentials from the token file, if it exists
    if os.path.exists(config.TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(config.TOKEN_FILE, config.SCOPES)

    # If no valid credentials are available, initiate the authorization flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                config.CREDENTIALS_FILE, config.SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(config.TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    # Build the Drive API service object
    service = build(config.API_NAME, config.API_VERSION, credentials=creds)

    return service


def get_metadata(service, fileId):
    '''
    Retrieve metadata of a specific file from Google Drive.

    Args:
        service: googleapiclient.discovery.Resource, Google Drive API service object
        fileId: str, The ID of the file whose metadata is to be retrieved

    Returns:
        file: dict, Metadata of the file
    '''
    file = service.files().get(fileId=fileId).execute()
    return file


def query_metadata(service, query='', fields='id, name'):
    '''
    Query and retrieve a list of files from Google Drive based on a query.

    Args:
        service: googleapiclient.discovery.Resource, Google Drive API service object
        query: str, Query string to filter the results (e.g., "name contains 'report'")
        fields: str, Comma-separated list of fields to include in the response

    Returns:
        files: list, A list of dictionaries containing file metadata
    '''
    files = []
    page_token = None
    while True:
        response = service.files().list(
            q=query,
            spaces='drive',
            fields=f'nextPageToken, files({fields})',
            pageToken=page_token
        ).execute()
        
        files.extend(response.get('files', []))
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break

    return files


def create_folder(service, folder_name, parent_id):
    '''
    Create a new folder in Google Drive within the specified parent directory.

    Args:
        service: googleapiclient.discovery.Resource, Google Drive API service object
        folder_name: str, The name of the new folder
        parent_id: str, The ID of the parent folder where the new folder will be created

    Returns:
        file: dict, Metadata of the created folder
    '''
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }
    file = service.files().create(body=file_metadata).execute() 
    return file


def delete_metadata(service, fileId):
    '''
    Delete a file or folder from Google Drive.

    Args:
        service: googleapiclient.discovery.Resource, Google Drive API service object
        fileId: str, The ID of the file or folder to be deleted

    Returns:
        None
    '''
    service.files().delete(fileId=fileId).execute()


def upload_file(service, fileName, parent_id, local_file):
    '''
    Upload a local file to Google Drive.

    Args:
        service: googleapiclient.discovery.Resource, Google Drive API service object
        fileName: str, The name of the file to be created on Google Drive (including extension)
        parent_id: str, The ID of the parent folder where the file will be uploaded
        local_file: str, The path to the local file to be uploaded

    Returns:
        file: dict, Metadata of the uploaded file
    '''
    file_metadata = {
        "name": fileName,
        "parents": [parent_id]
    }
    media = MediaFileUpload(local_file)
    file = service.files().create(
        body=file_metadata,
        media_body=media
    ).execute()
    return file


def download_metadata(service, fileId, save_file):
    '''
    Download a file from Google Drive to the local filesystem.

    Args:
        service: googleapiclient.discovery.Resource, Google Drive API service object
        fileId: str, The ID of the file to be downloaded
        save_file: str, The local path where the file will be saved (including extension)

    Returns:
        None
    '''
    request = service.files().get_media(fileId=fileId)

    with open(save_file, 'wb') as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            # Uncomment the line below to print download progress
            # print("Download %d%%." % int(status.progress() * 100))

if __name__ == '__main__':
    service = get_api_service()
    print(service)
