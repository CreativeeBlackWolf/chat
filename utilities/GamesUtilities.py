def CheckWords(words: list, lastWord: str, word: str) -> bool:
	# user may write more than 1 word in message (it IS filtering on server side but anyway)
	if len(word.split()) > 1:
		word = word.split()[0]

	if word == lastWord or word in words or not EndswithCheck(lastWord, word):
		return False
	return True

def EndswithCheck(lastWord: str, word: str):
	# converting words to lower case
	word = word.lower()
	lastWord = lastWord.lower()
	if lastWord.endswith(("ъ", "ь", "й")):
	# if the word ends with ^^^^^^^^^^^ those symbols then take the penultimate char
		if lastWord[-2] == word[0]:
			return True
		return False
	if lastWord[-1] == word[0]:
		return True
	return False

if __name__ == '__main__':
	pass