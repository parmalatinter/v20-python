#!/usr/bin/env python

import requests

class Line(object):

	line_notify_api = 'https://notify-api.line.me/api/notify'
	headers = {}

	def __init__(self):
		line_notify_token = 'xLlVj86pNjQAqpMl3QSg6DQMruNZSRNxKlUvMI8zehN'
		
		headers = {'Authorization': 'Bearer ' + line_notify_token}  # 発行したトークン

	def send(self, title, message):
		args = dict(title=title, message=message)
		send_str = '%(title)s\n%(message)s' % args

		payload = {'message': send_str}
		line_notify = requests.post(self.line_notify_api, data=payload, headers=self.headers)

def main():
    line = Line()
    line.send('title', 'message')

if __name__ == "__main__":
    main()
