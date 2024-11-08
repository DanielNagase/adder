#!/usr/bin/env python
import argparse, os

class FileSet:
	'''Class for a set of files'''
	# The unit for size is bytes
	bytesPerMegabyte = 1024 * 1024
	maximumSize = 300 * bytesPerMegabyte
	maximumFileCount = 500
	size = 0
	paths = []

	def canAdd(self, path, size):
		newCount = len(self.paths) + 1
		newSize = self.size + size

		return newCount <= self.maximumFileCount and newSize <= self.maximumSize

	def add(self, path, size):
		if not self.canAdd(path, size):
			return False

		self.paths.append(path)
		self.size = self.size + size

		return True

	def hasFiles(self):
		return self.size > 0 and len(self.paths) > 0

	def getSize(self):
		return self.size / self.bytesPerMegabyte

	def getCount(self):
		return len(self.paths)

	def reset(self):
		self.size = 0
		self.paths = []

def visitFile(entry):
	print(entry.path)

def visitPath(path):
	entries = sorted(os.scandir(path), key=lambda entry: entry.name)

	for entry in entries:
		if entry.is_dir():
			visitPath(entry)
		elif entry.is_file():
			visitFile(entry)

def main():
	parser = argparse.ArgumentParser(
		description='A tool for adding files to git in chunks'
	)
	parser.add_argument('path', help='Path to add')
	parser.add_argument('-s', '--size', help='Maximum size of a chunk (in MB)')
	parser.add_argument('-c', '--count', help='Maximum number of files in a chunk')

	args = parser.parse_args()
	visitPath(args.path)

if __name__ == "__main__":
	main()
