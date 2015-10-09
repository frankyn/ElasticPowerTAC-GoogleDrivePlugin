from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from apiclient.http import MediaFileUpload
from apiclient.http import MediaIoBaseDownload
import oauth2client
from oauth2client import client
from oauth2client import tools

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

class GoogleDriveAPIWrapper():
    def __init__(self,client_secret_file,session_file):
        self._application_name = 'ElasticPowerTAC'
        self._client_secret_file = client_secret_file
        self._session_file = session_file
        self._scopes = ['https://www.googleapis.com/auth/drive']
        self._service = None
        self.auth_credentials()


    def download_file(self,file_id, file_name):
        """Download a Drive file's content to the local filesystem.

            Args:
            service: Drive API Service instance.
            file_id: ID of the Drive file that will downloaded.
            file_name: used as name for to write content in.
        """
        fd = open(file_name,'w+')
        request = self._service.files().get_media(fileId=file_id)
        media_request = MediaIoBaseDownload(fd, request)

        while True:
            try:
                download_progress, done = media_request.next_chunk()
            except:
                print('An error occurred')
                fd.close()
                return
            if download_progress:
                print('Download Progress: %d%%' % int(download_progress.progress() * 100))
            if done:
                print('Download Complete')
                fd.close()
                return



    def insert_file(self, title, description, parent_id, mime_type, filename):
        """Insert new file.

        Args:
        service: Drive API service instance.
        title: Title of the file to insert, including the extension.
        description: Description of the file to insert.
        parent_id: Parent folder's ID.
        mime_type: MIME type of the file to insert.
        filename: Filename of the file to insert.
        Returns:
        Inserted file metadata if successful, None otherwise.
        """


        # Setup Upload
        media_body = MediaFileUpload(filename, mimetype=mime_type, resumable=True)
        body = {
            'title': title,
            'description': description,
            'mimeType': mime_type
        }
        # Set the parent folder.
        if parent_id:
            body['parents'] = [{'id': parent_id}]

        try:
            file = self._service.files().insert(
            body=body,
            media_body=media_body).execute()

            # Uncomment the following line to print the File ID
            # print 'File ID: %s' % file['id']

            return file
        except:
            print('An error occured')
        return None

    def auth_credentials(self):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        credential_dir = './'
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       self._session_file)

        store = oauth2client.file.Storage(credential_path)
        self._credentials = store.get()
        if not self._credentials or self._credentials.invalid:
            flow = client.flow_from_clientsecrets(self._client_secret_file, self._scopes)
            flow.user_agent = self._application_name
            flow.params['access_type'] = 'offline'
            if flags:
                self._credentials = tools.run_flow(flow, store, flags)
            else: # Needed only for compatability with Python 2.6
                self._credentials = tools.run(flow, store)

        # Authorize with HTTP
        self._http = self._credentials.authorize(httplib2.Http())

        # Setup Service in order to upload file
        self._service = discovery.build('drive', 'v2', http=self._http)


def main():
    """
        Driver Program for the GoogleDriveUpload ElasticPowerTAC Plugin
    """
    googledrive = GoogleDriveAPIWrapper('client_secrets.json','session.json')


    test_file = googledrive.insert_file(title="hello",
                            description="world",
                            parent_id=None,
                            mime_type="image/jpeg",
                            filename="Small_Portrait.jpg")
    if test_file:
        googledrive.download_file(file_id=test_file['id'],file_name="hello.jpg")
 
if __name__ == '__main__':
    main()
