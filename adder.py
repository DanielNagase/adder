#!/usr/bin/env python
import argparse

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

def main():
	parser = argparse.ArgumentParser(
		description='A tool for adding files to git in chunks'
	)
	parser.add_argument('-s', '--size', help='Maximum size of a chunk (in MB)')
	parser.add_argument('-c', '--count', help='Maximum number of files in a chunk')

	args = parser.parse_args()

if __name__ == "__main__":
	main()
