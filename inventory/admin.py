from flask import Flask,render_template,request,send_file,Blueprint,flash
from flask_login import login_required
from werkzeug.utils import secure_filename
from inventory.driveupload import gdrive_db_backup
import os


adminpage = Blueprint('admin',__name__)


@adminpage.route("/", methods=['GET', 'POST'])
@login_required
def admin():
	if request.form:
		if request.form["back_up_db"]:
			try:
				gdrive_db_backup()
				flash('Database was successfully backed up to GDrive')

			except UnboundLocalError:
				flash('There was an error uploading the database to GDrive')
				
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


