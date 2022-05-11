from flask import Flask,render_template,request,send_file,Blueprint
from flask_login import login_required
from werkzeug.utils import secure_filename
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import google_auth_oauthlib.flow
from google.oauth2 import service_account
import os

# GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = f'{os.getcwd()}/inventory/client_secrets.json'



SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = f'{os.getcwd()}/inventory/cavl-database-a6363a1fef07'

credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

adminpage = Blueprint('admin',__name__)

@adminpage.route("/", methods=['GET', 'POST'])
@login_required
def admin():
	if request.form:
		if request.form["back_up_db"]:
				gauth = GoogleAuth()
				gauth.LocalWebserverAuth()

				drive = GoogleDrive(gauth)


				team_drive_id = '0ABaFl3VnIbEXUk9PVA'

				parent_folder_id = '1HNHMDhyW9YthjzCPrgB_oiWGmZ8BtrTA'

				f = drive.CreateFile({
				    'title': 'inventory.db',
				    'parents': [{
				        'kind': 'drive#fileLink',
				        'teamDriveId': team_drive_id,
				        'id': parent_folder_id
				    }]
				})


				f.SetContentFile(f'{os.getcwd()}/uploads/inventory.db')
				f.Upload(param={'supportsTeamDrives': True})
		
	return render_template('admin.html')

@adminpage.route("/download-db", methods=['GET', 'POST'])
@login_required
def download_db():
	return send_file(f'{os.getcwd()}/inventory/uploads/inventory.db', as_attachment=True)

@adminpage.route("/upload-db", methods=['GET', 'POST'])
@login_required
def upload_db():
	if request.method == 'POST': # check if the method is post
		f = request.files['file'] # get the file from the files object
		# Saving the file in the required destination
		f.save(os.path.join(f'{os.getcwd()}/inventory/uploads',secure_filename(f.filename))) # this will secure the file

		print(os.path.join(f'{os.getcwd()}/inventory/uploads',secure_filename(f.filename)))

		return 'file uploaded successfully' # Display thsi message after uploading


