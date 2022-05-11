from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
from google.oauth2.service_account import Credentials

GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = f'{os.getcwd()}/inventory/client_secrets.json'


SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = f'{os.getcwd()}/inventory/cavl-database-a6363a1fef07.json'


gauth = GoogleAuth()
gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, SCOPES)
drive = GoogleDrive(gauth)


folderName = 'database_backup'  # Please set the folder name.
folders = drive.ListFile({'q': "trashed=false"}).GetList()


def gdrive_db_backup():
	if folders:
		for folder in folders:
			print(folder['title'])
			if folder['title'] == folderName:
				print('\n\n RAN \n\n')
				f = drive.CreateFile({
					'title': 'inventory.db',
					'parents': [{
					'kind': 'drive#fileLink',
					'id': folder['id']
					}]
				})
				

		f.SetContentFile(f'{os.getcwd()}/inventory/uploads/inventory.db')
		f.Upload(param={'supportsTeamDrives': True})
		


