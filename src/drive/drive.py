 
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os, json

class Drive():

	drive_obj = None
	folder_id = None
	file_list = None

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
		self.reset_file_list()

	def reset_file_list(self):
		self.file_list = self.drive_obj.ListFile({'q': "'{}' in parents and trashed=false".format(self.folder_id)}).GetList()

	def upload(self, filename, title):
		file = self.drive_obj.CreateFile({'title' : filename, "parents": [{"kind": "drive#fileLink", "id": self.folder_id}]})
		file.SetContentString(title)
		file.Upload()
		self.reset_file_list()
		print('uploaded: %s, id: %s' % (file['title'], file['id']))
		return file

	def delete_by_filename(self, filename):
		file = self.get_content_by_filename(filename)

		if not file:
			return
			
		file.Delete()
		print('deleted: %s, id: %s' % (file['title'], file['id']))
		self.reset_file_list()

	def get_file_list(self):
		return self.file_list

	def delete_all(self):
		for file1 in self.file_list:
			file1.Delete()
			print('deleted: %s, id: %s' % (file1['title'], file1['id']))
		self.reset_file_list()

	def delete_all_by_filename(self, filename):
		if not self.file_list: 
			return None
		for file1 in self.file_list:
			if file1['title'] == filename:
				file1.Delete()
				print('deleted: %s, id: %s' % (file1['title'], file1['id']))
		self.reset_file_list()

	def get_content_by_filename(self, filename):
		if not self.file_list: 
			return None
		file_list = [d.get('originalFilename') for d in self.file_list]

		try:
			index = file_list.index(filename)
		except ValueError as e:
			print(e)
			return None
    		
		if self.file_list[index]: 
			return self.file_list[index]
		else:
			return []

	def filter_dict(f, d):
		return {k:v for k,v in d.items() if f(k,v)}


if __name__ == '__main__':
    drive = Drive("1A3k4a4u4nxskD-hApxQG-kNhlM35clSa")
    drive.delete_all()
    file = drive.upload('filename.txt', 'title')
    res = drive.get_content_by_filename('filename.txt')
    if res: 	
    	print(res.GetContentString())
    
