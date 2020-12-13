import re
import string

# global variable: the current line number in grimms.txt
line_num = 0

def lineIncrement():
    """ Modifies and returns the global var: line_num. """
    global line_num
    line_num = line_num + 1
    return line_num

def getStopwords():
    file = open("stopwords.txt", 'r')
    stopwords = []
    for line in file:
        line = line.strip();
        stopwords.append(line)
    file.close()
    return stopwords

def openGrimms():
    file = open("grimms.txt", 'r')
    for i in range(124):
        file.readline()
        lineIncrement()
    return file

def isTitle(string):
    match = re.search(r'^[A-Z\d][A-Z\s\,\.\[-]*[A-Z\]]$', string)
    if match == None:  # if doesn't match
        r = False
    else:
        r = True
    return r

def isEndStoryText(string):
    """ Return True if reach the end of stories. """
    match = re.search(r'^\*\*\*', string)
    if match == None:
        r = False
    else:
        r = True
    return r
    
def removePunctuations(word):
    word = word.strip(string.punctuation)
    # in the case of "king's"
    word = re.sub(r'[^a-zA-Z0-9 ]', '', word) # => 'kings'
    return word

def line2words(line):
    line = line.replace('-', ' ')
    words = line.split()
    wordlist = []
    for word in words:
        word = removePunctuations(word)
        word = word.lower()
        wordlist.append(word)
    return wordlist

def removeStopwords(wordlist, stopwords):
    output_wordlist = []
    for word in wordlist:
        if word not in stopwords:
            output_wordlist.append(word)
    return output_wordlist

def buildIndex():
    print("Loading stopwords...")
    stopwords = getStopwords()
    print(stopwords)

    print("\nBuilding index...")
    grimms = openGrimms()

    dictionary = dict()  # {word: {TITLE: [line_nums]}}
    titles = list()  # will store all TITLES
    for line in grimms:
        lineIncrement()
        line = line.strip()
        if not isEndStoryText(line):
            # if not hits the end
            if isTitle(line):
                title = line
                titles.append(title)
                print(len(titles), title)
            else:
                # process each line in the story content
                wordlist = line2words(line)
                wordlist = removeStopwords(wordlist, stopwords)
                
                for word in wordlist:
                    if word not in dictionary:
                        dictionary.setdefault(word, {title:[line_num]})
                    else:
                        dictionary.get(word).setdefault(title, []).append(line_num)
                
        else:
            # finished reading stories
            break
    
    grimms.close()
    return dictionary, titles

def queryAND(W2S, TITLES, querywords):
    """ Search for AND queries.
    Also eligible for 1-word, 2-word, ..., n-words queries. """
    d_results = dict()
    titleset = set(TITLES)
    for word in querywords:
        title_lines = W2S.get(word, {}) # {TITLE:[line_num})
        titleset = titleset.intersection(set(title_lines.keys()))
    if len(titleset) != 0:
        # creating dict with the structure {TITLE: {word: [line_num]}}
        for title in titleset:
            for word in querywords:
                d_results.setdefault(title,{}).setdefault(word, W2S.get(word,{}).get(title,[]))
    
    # else: titleset is empty, return the empty dict()
    return d_results

def getResults(W2S, TITLES, query):
    """ Query from the index and return results in a dictionary that's ready
    for output. d_results {TITLE: {word: [line_num]}} """

    d_results = dict()
    querylist = query.split()
    
    if len(querylist) == 3:
        if querylist[1] == 'or': # word1 or word2
            word1 = querylist[0]
            title_lines1 = W2S.get(word1, {})
            word2 = querylist[2]
            title_lines2 = W2S.get(word2, {})
            titleset = set(title_lines1.keys()).union(set(title_lines2.keys()))
            for title in titleset:
                # creating dict with the structure {TITLE: {word: [line_num]}}
                d_results.setdefault(title,{}).setdefault(word1,title_lines1.get(title,[]))
                d_results.setdefault(title,{}).setdefault(word2,title_lines2.get(title,[]))
        elif querylist[1] == 'morethan':
            if querylist[2].isnumeric():
                # "owl morethan 5"
                times = int(querylist[2])
                title_lines = W2S.get(querylist[0], {}) # {TITLE: [line_num]}
                for title, lines in title_lines.items():
                    if len(lines) > times:
                        d_results.setdefault(title, {}).setdefault(querylist[0], lines)
            else:
                # "owl morethan raven"
                querylist.remove('morethan')
                raw = queryAND(W2S, TITLES, querylist) # {TITLE: {word: [line_num]}}
                for title, wordlines in raw.items():
                    wordlines1 = wordlines.get(querylist[0], [])
                    wordlines2 = wordlines.get(querylist[1], [])
                    if len(wordlines1) > len(wordlines2):
                        d_results.setdefault(title, wordlines)           
        elif querylist[1] == 'near':
            # "owl near raven"
            querylist.remove('near')
            raw = queryAND(W2S, TITLES, querylist) # {TITLE: {word: [line_num]}}
            for title, wordlines in raw.items():
               wordlines1 = wordlines.get(querylist[0], [])
               wordlines2 = wordlines.get(querylist[1], [])
               pointer = 0
               for word1_line in wordlines1:
                   for word2_line in wordlines2:
                       if (word1_line == word2_line) or (word1_line - 1 == word2_line) or (word1_line + 1 == word2_line):
                           d_results.setdefault(title, {}).setdefault(querylist[0], []).append(word1_line)
                           d_results.setdefault(title, {}).setdefault(querylist[1], []).append(word2_line)
                       
        elif querylist[1] == 'and': #word1 and word2
            # remove 'and', then query "word1 word2"
            querylist.remove('and')
            d_results = queryAND(W2S, TITLES, querylist)
        else: # word1 word2 word3
            # query "word1 word2 word3"
            d_results = queryAND(W2S, TITLES, querylist)
    else: # word1 word2 word3 ... wordn (including 1-word and 2-word queries)
        d_results = queryAND(W2S, TITLES, querylist)
    
    return d_results

def textlines():
    file = open("grimms.txt", 'r')
    textlines = file.readlines()
    file.close()
    return textlines

def textformat(word, text):
    text = text.strip()
    replace = word.upper().center(len(word)+4, '*')
    text = text.replace(word, replace)
    return text    

######## MAIN goes here: ###########
W2S, TITLES = buildIndex()
text = textlines()

print("\nWelcom to the Grimms' Fairy Tales search system!")

query = input("\nPlease enter your query: ")

while query != "qquit":
    d_results = getResults(W2S, TITLES, query)

    # output d_results = {TITLE:{word:[line_num]}}
    print("\nquery =", query)
    if len(d_results) > 0:
        for t, wl in d_results.items():
            print("\t", t)
            for word in wl.keys():
                print("\t  ", word)
                if len(wl[word]) > 0:
                    for line_num in wl[word]:
                        printtext = textformat(word, text[line_num -1])
                        print("\t    ", line_num, printtext)
                else:
                    print("\t    ", "--")
    else:
        print("\t", "--")
                
    
    query = input("\nPlease enter your query: ")

####### END PROGRAM ##########
