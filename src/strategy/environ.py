#!/usr/bin/env python

import os
import yaml
import subprocess

class Environ(object):

	def get(self, name):

		return os.environ.get(name)

	def print_set_env(self):
		dir_path = os.path.dirname(os.path.realpath(__file__))
		print(dir_path)
		os.chdir(dir_path)
		f = open("env/env.yaml", "r+")
		data = yaml.load(f)
		for key, value in data.items():
			command = 'heroku config:set {}="{}" --app "oandapypro"'.format(
			    str(key),
			    str(value)
			)
			print(command)
def main():
	env = Environ()
	print(env.print_set_env())

if __name__ == "__main__":
	main()
