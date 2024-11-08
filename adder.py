#!/usr/bin/env python3
import argparse, os

class FileSet:
	'''Class for a set of files'''
	bytesPerMegabyte = 1024 * 1024

	def __init__(self, maximumSize, maximumFileCount):
		# The unit for size and maximumSize is bytes
		self.size = 0
		self.maximumSize = maximumSize * self.bytesPerMegabyte
		self.maximumFileCount = maximumFileCount
		self.paths = []

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

class Processor:
	'''Class for processing a FileSet'''

	def process(self, fileSet):
		if not fileSet.hasFiles():
			return

		sizeInMB = fileSet.getSize()
		count = fileSet.getCount()
		print("Processing Chunk: {0} files, {1:.2f} MB".format(count, sizeInMB))

		for path in fileSet.paths:
			print(" " + path)

		fileSet.reset()

def visitFile(entry, fileSet):
	statResult = entry.stat()
	didAdd = fileSet.add(entry.path, statResult.st_size)

	if not didAdd:
		printProcessor = Processor()
		printProcessor.process(fileSet)

def visitPath(path, fileSet):
	entries = sorted(os.scandir(path), key=lambda entry: entry.name)

	for entry in entries:
		if entry.is_dir():
			visitPath(entry, fileSet)
		elif entry.is_file():
			visitFile(entry, fileSet)

def main():
	parser = argparse.ArgumentParser(
		description='A tool for adding files to git in chunks'
	)
	parser.add_argument('path', help='Path to add')
	parser.add_argument('-s', '--size', help='Maximum size of a chunk (in MB)', default=300)
	parser.add_argument('-c', '--count', help='Maximum number of files in a chunk', default=500)

	args = parser.parse_args()
	fileSet = FileSet(args.size, args.count)
	visitPath(args.path, fileSet)

	if fileSet.hasFiles():
		printProcessor = Processor()
		printProcessor.process(fileSet)

if __name__ == "__main__":
	main()
