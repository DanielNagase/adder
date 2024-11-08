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

	def __init__(self, size, count):
		self.fileSet = FileSet(size, count)

	def processChunk(self):
		if not self.fileSet.hasFiles():
			return

		sizeInMB = self.fileSet.getSize()
		count = self.fileSet.getCount()
		print("Processing Chunk: {0} files, {1:.2f} MB".format(count, sizeInMB))

		for path in self.fileSet.paths:
			print(" " + path)

		self.fileSet.reset()

	def processPath(self, path):
		# first, visit paths recursively
		self.visitPath(path)
		# after visiting paths recursively, process the
		# last chunk to handle any remaining files
		self.processChunk()

	def visitPath(self, path):
		entries = sorted(os.scandir(path), key=lambda entry: entry.name)

		for entry in entries:
			if entry.is_dir():
				self.visitPath(entry)
			elif entry.is_file():
				self.visitFile(entry)

	def visitFile(self, entry):
		statResult = entry.stat()
		didAdd = self.fileSet.add(entry.path, statResult.st_size)

		if not didAdd:
			self.processChunk()

def main():
	parser = argparse.ArgumentParser(
		description='A tool for adding files to git in chunks'
	)
	parser.add_argument('path', help='Path to add')
	parser.add_argument('-s', '--size', help='Maximum size of a chunk (in MB)', default=300)
	parser.add_argument('-c', '--count', help='Maximum number of files in a chunk', default=500)

	args = parser.parse_args()
	processor = Processor(args.size, args.count)
	processor.processPath(args.path)

if __name__ == "__main__":
	main()
