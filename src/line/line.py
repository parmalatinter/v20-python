#!/usr/bin/env python

import requests
import strategy.environ

class Line(object):

	line_notify_api = 'https://notify-api.line.me/api/notify'
	# テスト
	line_notify_token = 'H2dgkYyK6FYQo4GZo21MLR50ObjZmkv9dkxYEZc78lk' 
	env = 'TEST'
	headers = {}

	def __init__(self):
		environ = strategy.environ.Environ()
		self.env = environ.get('ENV') if environ.get('ENV') else self.env
		if not self.env == 'PRO':
			# 本番
			self.line_notify_token = 'CBmYadvZxpKXCWZ7hFuFn1BwkPkClacjlWujm5y9ulQ'
		
		self.headers = {'Authorization': 'Bearer ' + self.line_notify_token}  # 発行したトークン

	def send(self, title, message, imageFile=None):
		args = dict(title=title, message=message)
		message = '%(title)s\n%(message)s' % args

		print(message)
		files = None
		if imageFile:
			files = {'imageFile': imageFile}
		payload = {'message': message}
		line_notify = requests.post(self.line_notify_api, data=payload, headers=self.headers,files=files)
		
def main():
    line = Line()
    line.send('title', 'message')

if __name__ == "__main__":
    main()
