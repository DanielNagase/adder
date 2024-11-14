#!/usr/bin/env python3
import argparse, os, subprocess

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

	def __init__(self, size, count, isDryRun):
		self.fileSet = FileSet(size, count)
		self.isDryRun = isDryRun
		self.shouldShowProgress = False
		self.resumePath = None

	def setShouldShowProgress(self, shouldShow):
		self.shouldShowProgress = shouldShow

	def setResumePath(self, path):
		if path is None:
			return

		self.resumePath = path

	def showChunkSummary(self):
		if not self.fileSet.hasFiles():
			return

		lastPath = os.path.dirname(self.fileSet.paths[-1])
		count = self.fileSet.getCount()
		size = self.fileSet.getSize()
		print("Processed: {} ({} files, {:.2f} MB)".format(lastPath, count, size))

	def processChunk(self):
		if not self.fileSet.hasFiles():
			return

		if self.shouldShowProgress:
			self.showChunkSummary()

		self.process()
		self.fileSet.reset()

	# Subclasses should override this method to process the
	# fileset. The default implementation just prints each path.
	def process(self):
		sizeInMB = self.fileSet.getSize()
		count = self.fileSet.getCount()
		print("Processing Chunk: {0} files, {1:.2f} MB".format(count, sizeInMB))

		for path in self.fileSet.paths:
			print(" " + path)

	def processPath(self, path):
		# first, visit paths recursively
		self.visitPath(path)
		# after visiting paths recursively, process the
		# last chunk to handle any remaining files
		self.processChunk()

	def visitPath(self, path):
		entries = sorted(os.scandir(path), key=lambda entry: entry.name)

		for entry in entries:
			if self.resumePath and (len(self.resumePath) >= len(entry.path)):
				if entry.is_dir() and entry.path.startswith(self.resumePath):
					self.resumePath = None

			if entry.is_dir():
				self.visitPath(entry)
			elif entry.is_file():
				if not self.resumePath:
					self.visitFile(entry)

	def visitFile(self, entry):
		statResult = entry.stat()
		didAdd = self.fileSet.add(entry.path, statResult.st_size)

		if not didAdd:
			self.processChunk()
			self.fileSet.add(entry.path, statResult.st_size)

class GitProcessor(Processor):
	'''Class for adding files to git by using the command line'''

	def __init__(self, size, count, isDryRun):
		super().__init__(size, count, isDryRun)

	def getAddCommandArgs(self):
		command = ['git', 'add', '-f']

		return command

	def buildCommitCommandArgs(self, message):
		command = ['git', 'commit', '-m']
		command.append(message)

		return command

	def runCommand(self, args):
		completedProcess = None

		if self.isDryRun:
			print(' '.join(args))

			return

		try:
			completedProcess = subprocess.run(args, check=True, capture_output=True)
		except subprocess.CalledProcessError as error:
			errorString = error.stderr.decode()
			print("Command failed:\n {}".format(errorString), end='')

	def process(self):
		addArgs = self.getAddCommandArgs()
		addArgsLength = len(' '.join(addArgs))
		# This is the maximum number of characters for a command in Windows 10.
		maximumLength = 8192
		currentBatchLength = addArgsLength
		currentBatch = []

		for index, path in enumerate(self.fileSet.paths):
			if self.shouldShowProgress and index % 10 == 0:
				print('.', end='', flush=True)

			pathLength = len(path)

			if (pathLength + currentBatchLength) <= maximumLength:
				currentBatchLength += pathLength
				currentBatch.append(path)
			else:
				self.runCommand([*addArgs, *currentBatch])
				currentBatchLength = addArgsLength + pathLength
				currentBatch = [path]

		if len(currentBatch) > 0:
			self.runCommand([*addArgs, *currentBatch])
			currentBatch = []

		if self.shouldShowProgress:
			print('', flush=True)

		self.runCommand(self.buildCommitCommandArgs('Add files'))

def main():
	parser = argparse.ArgumentParser(
		description='A tool for adding files to git in chunks'
	)
	parser.add_argument('path', help='Path to add')
	parser.add_argument('-s', '--size', help='Maximum size of a chunk (in MB)', type=int, default=500)
	parser.add_argument('-c', '--count', help='Maximum number of files in a chunk', type=int, default=1000)
	parser.add_argument('-n', '--dry-run', action='store_true', help='Print commands that would be run without running them')
	parser.add_argument('-p', '--progress', action='store_true', help='Print progress information as chunks are added')
	parser.add_argument('-r', '--resume-path', metavar='PATH', help='Resume from a given path, skipping paths before it')

	args = parser.parse_args()
	processor = GitProcessor(args.size, args.count, args.dry_run)
	processor.setShouldShowProgress(args.progress)
	processor.setResumePath(args.resume_path)
	processor.processPath(args.path)

if __name__ == "__main__":
	main()
