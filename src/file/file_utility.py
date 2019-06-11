#!/usr/bin/env python

from datetime import datetime
import os 
from io import StringIO
import drive.drive

class File_utility():
	drive_id = ''
	header = ''
	content = ''
	filemame = ''
	googleDrive = None

	def __init__(self, filemame, drive_id):
		self.drive_id = drive_id
		self.filemame = filemame
		self.googleDrive = drive.drive.Drive(self.drive_id)

	def set_header(self, header = ''):
		self.header = header

	def set_contents(self, contents):

		for text in contents:
			self.content = self.content + text

	def export_drive(self):
		self.googleDrive.upload(self.filemame, self.header +self.content)

	def delete_drive(self):
		self.googleDrive.delete_by_filename(self.filemame)

	def get_string(self):
		self.googleDrive.reset_file_list()
		print(self.googleDrive.get_file_list())
		res = self.googleDrive.get_content_by_filename(self.filemame)
		if res: 	
			return StringIO(res.GetContentString())
		return ''
