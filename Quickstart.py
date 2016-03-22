import httplib2
import os
import pprint
from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
from apiclient.http import MediaFileUpload

FILENAME = ''
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/drive.appdata https://www.googleapis.com/auth/drive.apps.readonly'

CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API Python Quickstart'
FOLDER_TYPE = 'application/vnd.google-apps.folder'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """ Creates a folder Backup in Google Drive and then proceeds to backup all files in a specified folder on the desktop"""
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    folder_metadata = {
      'name' : 'Backup',
      'mimeType' : 'application/vnd.google-apps.folder'
    }

    response = service.files().list(q ="mimeType = 'application/vnd.google-apps.folder' and trashed = false and name = 'Backup'", fields='nextPageToken, files(id,name)').execute()
    folders = response.get('files', [])
    backup_id = folders[0]['id']
    if not folders:
      print " No folders found "
      file = service.files().create(body=folder_metadata,
                                    fields='id, name').execute()
      print "Backup created !"

    else:
      for item in folders:
        print ('file id: {0} file name: {1}').format(item['id'], item['name'])

    ##########################################################################
    ##########################################################################
    #This will get all the files in the folder backup 
    #into a DS called "files"
    ##########################################################################
    topdir = "."
    files_at_home =[]
    for path, subFolders, filenames in os.walk(topdir):
      for names in filenames:
        files_at_home.append(os.path.join(path,names))
    ###########################################################################
    ###########################################################################

    filenames = [] #DS for gathering files already present in Backup 
    response = service.files().list(q = "'" + backup_id + "'" + " in parents and trashed=false", fields='files(id,name)').execute()
    files_in_backup = response.get('files', [])
    if not files_in_backup:
      print "No files found"
    else:
      for item in files_in_backup:
        filenames.append(item['name'])
    print filenames

    for FILENAME in files_at_home:
      if FILENAME in filenames:
        print "File Already Exists !" + "\n"

      else:
        file_metadata ={ 
          'name' : FILENAME,
          'parents': [ backup_id ] #[ ] is important 
        }

        print 
        media_body = MediaFileUpload(FILENAME, mimetype = 'text/plain', resumable= False)
        file = service.files().create(body=file_metadata, media_body=media_body).execute()
        print " File Successfully Uploaded"
 
    

    
    


if __name__ == '__main__':
    main()
