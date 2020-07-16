import language_check
import collections
import sys
import re
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords

class grammarmetrics:
    def __init__(self):
        self.errorrate = None

    def generatescore(self,text,tokenized_text, tool):
        matches = tool.check(text)
        errorcount = self.thereforetherefore(text)
        self.errorrate = (len(matches)+errorcount)/len(tokenized_text)
        pass

    def thereforetherefore(self,text,threshold=3):
        stop_words = set(stopwords.words('english'))
        current_sentence = set()
        setlist = []
        wordcounts = collections.defaultdict()

        #split text into list of sentences
        sentencesplit = sent_tokenize(text)
        for sentence in sentencesplit:
            #split sentence into words
            words = sentence.split()
            for word in words:
                #remove commas
                if "," in word:
                    word.replace(",",'')
                if "." in word:
                    word.replace(".",'')
                #check if word is a stop word, remove stop words
                if word not in stop_words:
                    #append to current_sentence set if NOT a stop word
                    current_sentence.add(word)
            setlist.append(current_sentence)
            current_sentence = set()
        errorcount = 0 
        for i in range (0, len(setlist)-2):
            intersection = setlist[i].intersection(setlist[i+1],setlist[i+2])
            if len(intersection) == 0:
                continue
            else:
                errorcount+=1
        return errorcount
        pass


