#!/usr/bin/env python
import argparse, os

class FileSet:
	'''Class for a set of files'''
	# The unit for size is bytes
	maximumSize = 300 * 1024 * 1024 # 300 MB
	maximumFileCount = 500
	currentSize = 0
	currentFileCount = 0

	def __init__(self, diskSize, fileCount):
		if (diskSize <= 0) or (fileCount <= 0):
			raise ValueError('Disk size and file count must positive values!')

		self.fileCount = fileCount
		self.diskSize = diskSize

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
