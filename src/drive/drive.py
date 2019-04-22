 
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os, json

class Drive():

	drive_obj = None
	folder_id = None

	def __init__(self, folder_id):
		self.set_service(folder_id)

	def set_service(self, folder_id):
		os.chdir(os.path.dirname(os.path.abspath(__file__)))
		gauth = GoogleAuth()

		# Try to load saved client credentials
		gauth.LoadCredentialsFile("mycreds.txt")
		if gauth.credentials is None:
		    # Authenticate if they're not there
		    gauth.CommandLineAuth()
		elif gauth.access_token_expired:
		    # Refresh them if expired
		    gauth.Refresh()
		else:
		    # Initialize the saved creds
		    gauth.Authorize()
		# Save the current credentials to a file
		gauth.SaveCredentialsFile("mycreds.txt")

		drive = GoogleDrive(gauth)
		self.drive_obj = GoogleDrive(gauth)
		self.folder_id = folder_id

	def upload(self, filename, title):
		file = self.drive_obj.CreateFile({'title' : filename, "parents": [{"kind": "drive#fileLink", "id": self.folder_id}]})
		file.SetContentString(title)
		file.Upload()
		return file

	def delete(self, filename, title):
		file = self.drive_obj.CreateFile({'title' : filename, "parents": [{"kind": "drive#fileLink", "id": self.folder_id}]})
		file.SetContentString(title)
		file.Upload()

	def file_list(self):
		file_list = self.drive_obj.ListFile({'q': "'{}' in parents and trashed=false".format(self.folder_id)}).GetList()
		for file1 in file_list:
	  		print('title: %s, id: %s' % (file1['title'], file1['id']))

	def delete_all(self):
		file_list = self.drive_obj.ListFile({'q': "'{}' in parents and trashed=false".format(self.folder_id)}).GetList()
		for file1 in file_list:
			file1.Delete()
			print('deleted: %s, id: %s' % (file1['title'], file1['id']))

	def get_file_string(self, file):	
		got_file = self.drive_obj.CreateFile({'id': file['id']})
		return got_file.GetContentString()

if __name__ == '__main__':
    drive = Drive("1A3k4a4u4nxskD-hApxQG-kNhlM35clSa")
    file = drive.upload('filename.txt', 'title')
    drive.file_list()
    print(drive.get_file_string(file))
    drive.delete_all()
