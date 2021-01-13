import itertools
import shutil
import json
import mmap
import os
from datetime import datetime
from pytz import timezone

# // thanks for this code to https://stackoverflow.com/a/34029605 //

def _SkipBackLines(mm, numlines, startidx):
	'''Factored out to simplify handling of n and offset'''
	for _ in itertools.repeat(None, numlines):
		startidx = mm.rfind(b'\n', 0, startidx)
		if startidx < 0:
			break
	return startidx

def tail(f, n = 20, offset = 0):
	# Reopen file in binary mode
	with open(f.name, 'rb') as binf, mmap.mmap(binf.fileno(), 0, access=mmap.ACCESS_READ) as mm:
		# len(mm) - 1 handles files ending w/newline by getting the prior line
		startofline = _SkipBackLines(mm, offset, len(mm) - 1)
		if startofline < 0:
			return []  # Offset lines consumed whole file, nothing to return
			# If using a generator function (yield-ing, see below),
			# this should be a plain return, no empty list

		endoflines = startofline + 1  # Slice end to omit offset lines

		# Find start of lines to capture (add 1 to move from newline to beginning of following line)
		startofline = _SkipBackLines(mm, n, startofline) + 1

		# Passing True to splitlines makes it return the list of lines without
		# removing the trailing newline (if any), so list mimics f.readlines()
		return mm[startofline:endoflines].splitlines()
		# If Windows style \r\n newlines need to be normalized to \n, and input
		# is ASCII compatible, can normalize newlines with:
		# return mm[startofline:endoflines].replace(os.linesep.encode('ascii'), b'\n').splitlines(True)

# // thanks for this code to https://stackoverflow.com/a/34029605 //

def GetTerminalSize():
	return shutil.get_terminal_size()

def GetTime(formatting: str = "%d/%m/%y | %H:%M:%S"):
	now = datetime.now(timezone("Europe/Moscow"))
	return now.strftime(formatting)

def WriteChatLogFile(logPath, channelName, channelPort, chatLog: list) -> str:
	"""
		writing and returning path to chat log file
	"""
	if not os.path.exists(logPath):
		os.mkdir(logPath)
	path = f"{logPath}/{GetTime(formatting = '%H%M%S-%d%m%y')}-{channelName}-{channelPort}.txt"
	with open(path, "w", encoding = "utf-8") as f:
		f.write("\n".join(chatLog))
	return path
