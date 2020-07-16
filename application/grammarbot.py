import sys
from grammarbot import GrammarBotClient
import string
import collections

filename = input("Please input the name of your file: ")
try:
    f1 = open(filename, 'r')
    text = f1.read()
    f1.close()
except IOError:
    print("File Could Not Be Opened.")
    exit()

client = GrammarBotClient(api_key='KS9C5N3Y')
res = client.check(text)
print(res.matches)

#for i in res.matches:
#    for j in matches:
#        if j.ruleId == i.rule and j.replacements == i.replacements:
#            matches.remove(j)
#numberoferrors = len(matches)
#+ len(res.matches)
