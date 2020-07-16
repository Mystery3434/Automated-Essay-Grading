import nltk
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import collections

class extended_criterion:
    def __init__(self):
        self.semanticoverlap = None
        self.typetokenratio = None

    def generatescore(self, tokenized_text):
        stop_words = set(stopwords.words('english'))
        nostopwords_tokenized_text = []
        for w in tokenized_text:
            if w not in stop_words:
                nostopwords_tokenized_text.append(w)
        self.semantic_overlap(nostopwords_tokenized_text)
        self.type_token_ratio(tokenized_text)
        pass

    #semantic overlap is defined as the overlap of synonyms across sentences or paragraphs
    #we use WordNet to check if any synonyms exist in the text
    def semantic_overlap(self,tokenized_text):
        synonym_set = set()
        for word in tokenized_text:
            for syn in wordnet.synsets(word):
                for l in syn.lemmas():
                    if l.name() not in synonym_set:
                        synonym_set.add(l.name())
        synonym_count = 0
        for word in tokenized_text:
            if word in synonym_set:
                synonym_count+=1
        self.semanticoverlap = synonym_count
        pass


    #type token ratio is a representation of word repetition
    #it is defined as the ratio of individual words to total nunber of words
    def type_token_ratio(self,tokenized_text):
        wordcount = len(tokenized_text)
        wordfreq_dict = collections.defaultdict()
        for word in tokenized_text:
            if word in wordfreq_dict:
                wordfreq_dict[word]+=1
            else:
                wordfreq_dict[word]=1
        self.typetokenratio = wordfreq_dict
        pass

