#!/usr/bin/env python

import os

class Environ(object):

    def get(self, name):

        return os.environ.get(name)


def main():
    
    env = Environ()
    print(env.get('ENV'))

if __name__ == "__main__":
    main()
