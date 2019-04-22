 
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os, json

class Drive():

	driveObj = None

	def __init__(self):
		self.set_service()

	def set_service(self):
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
		self.driveObj = GoogleDrive(gauth)

	def upload(self, filename, title):
		file = self.driveObj.CreateFile({'title' : filename})
		file.SetContentString(title)
		file.Upload()

if __name__ == '__main__':
    drive = Drive()
    drive.upload('filename.txt', 'title')
