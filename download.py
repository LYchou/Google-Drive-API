import os
import drive_api_tools

class Download:
    '''
    A class to handle file download operations from Google Drive.

    Methods:
        download_file(cloud_file_id: str, save_file: str) -> None:
            Downloads a single file from Google Drive to the local filesystem.
        
        download_files(files: list, save_folder: str) -> None:
            Downloads multiple files from Google Drive to a specified local folder.
        
        listdir_cloud_folder(cloud_folder_id: str) -> list:
            Lists all files in a specified Google Drive folder.
    '''

    def __init__(self) -> None:
        '''
        Initializes the Download class by setting up the Google Drive API service.
        '''
        # Initialize the Google Drive API service
        self.service = drive_api_tools.get_api_service()

    def download_file(self, cloud_file_id: str, save_file: str) -> None:
        '''
        Download a single file from Google Drive to the local filesystem.

        Args:
            cloud_file_id (str): The ID of the file in Google Drive.
            save_file (str): The local path where the file should be saved.

        Returns:
            None
        '''
        print(f'-- Downloading file with ID={cloud_file_id} to {save_file}')
        if not os.path.isfile(save_file):
            # Download the file if it does not already exist
            drive_api_tools.download_metadata(self.service, fileId=cloud_file_id, save_file=save_file)
            print('-- Download successful')
        else:
            print('-- Download failed: File already exists')

    def download_files(self, files: list, save_folder: str) -> None:
        '''
        Download multiple files from Google Drive to a specified local folder.

        Args:
            files (list): A list of dictionaries where each dictionary contains:
                - 'id': The ID of the file in Google Drive.
                - 'name': The name of the file including its extension.
            save_folder (str): The local folder path where files should be saved.

        Returns:
            None
        '''
        for file in files:
            basename, fileId = file['name'], file['id']
            save_file = os.path.join(save_folder, basename)
            self.download_file(fileId, save_file)

    def listdir_cloud_folder(self, cloud_folder_id: str) -> list:
        '''
        List all files in a specified Google Drive folder.

        Args:
            cloud_folder_id (str): The ID of the Google Drive folder.

        Returns:
            list: A list of dictionaries, each containing:
                - 'id': The ID of the file in Google Drive.
                - 'name': The name of the file including its extension.
        '''
        # Query to list files within the specified folder
        query = f"'{cloud_folder_id}' in parents"
        files = drive_api_tools.query_metadata(service=self.service, fields='id, name', query=query)
        return files

if __name__ == '__main__':
    # Example usage
    download = Download()
    # List files in a specific Google Drive folder
    files = download.listdir_cloud_folder('1UvWYeI8SEazWZeU05icAYBY38xRXSS7w')
    for file in files:
        print(file)
