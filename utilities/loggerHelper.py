import configparser
import logging
import os
from utilities.utils import tail

FORMATTER = logging.Formatter("[%(asctime)s] -> [%(name)s(%(threadName)s) / %(levelname)s] in function %(funcName)s: %(message)s",
	"%d/%b/%y | %H:%M:%S")

# reading config file to get config file 
cfg = configparser.ConfigParser()
cfg.read("client.cfg")

# defining path to logging file
LOG_PATH = cfg.get("Paths", "logs_path", fallback = "./logs")
CLIENT_LOG_FILE = f"{LOG_PATH}/client.log"
SERVER_LOG_FILE = f"{LOG_PATH}/server.log"

def GetFileHandler(client = True):
	file = CLIENT_LOG_FILE if client else SERVER_LOG_FILE
	if not os.path.exists(file):
		os.mkdir(LOG_PATH)
		open(file, "w", encoding = "utf-8").close()
	fileHandler = logging.FileHandler(file, encoding = "utf-8")
	fileHandler.setFormatter(FORMATTER)
	return fileHandler

def GetConsoleHandler():
	consoleHandler = logging.ConsoleHandler()
	consoleHandler.setFormatter(FORMATTER)
	return consoleHandler

def GetLogger(loggerName, loggingLevel = logging.INFO, consoleHandler: bool = False):
	logger = logging.getLogger(loggerName)
	logger.setLevel(loggingLevel)
	logger.addHandler(GetFileHandler())
	if consoleHandler:
		logger.addHandler(GetConsoleHandler())
	logger.propagate = False
	return logger

def GetLog(lines, client = True) -> tuple:
	file = CLIENT_LOG_FILE if client else SERVER_LOG_FILE
	with open(file, "r", encoding = "utf-8") as f:
		if f.readline():
			return tuple(tail(f, lines))
		else:
			return ()

def ClearLogFile(client = True) -> bool:
	try:
		open(CLIENT_LOG_FILE if client else SERVER_LOG_FILE, "w").close()
	except Exception as e:
		return False
	return True

def GetLogAsString(lines, client = True) -> str:
	text = ""
	for l in GetLog(lines, client = client):
		text += l.decode("utf-8") + "\n"
	return text if text else "Log file is empty."
