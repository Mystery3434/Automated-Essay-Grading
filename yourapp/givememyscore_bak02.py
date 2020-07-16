import sys
#import language_check
import string
from nltk.tokenize import word_tokenize
from yourapp.lexicalmetrics import lexicalmetrics
#from grammarmetrics import grammarmetrics
from yourapp.readabilitymetrics import readabilitymetrics
from yourapp.extended_criterion import extended_criterion
import nltk
#nltk.download('wordnet')
class givememyscore:
    def __init__(self):
        self.lex = lexicalmetrics()
        #self.grammar = grammarmetrics()
        self.readability = readabilitymetrics()
        self.extended = extended_criterion()

    def startevaluation(self, text):
        #tool = language_check.LanguageTool('en-US')
        #Get Mode of English from User Input
        # validinput = False
        # while validinput == False:
        #     language = input("Please select type of English:\n1. American  \n2. British  \n3. Canadian  \n4. Australian  \n5. New Zealand  \n6. South African\n")
        #     if language == '1' or 'American':
        #         tool = language_check.LanguageTool('en-US')
        #         validinput = True
        #     elif language == '2' or 'British':
        #         tool = language_check.LanguageTool('en-UK')
        #         validinput = True
        #     elif language == '3' or 'Canadian':
        #         tool = language_check.LanguageTool('en-CA')
        #         validinput = True
        #     elif language == '4' or 'Australian':
        #         tool = language_check.LanguageTool('en-AU')
        #         validinput = True
        #     elif language == '5' or 'New Zealand':
        #         tool = language_check.LanguageTool('en-NZ')
        #         validinput = True
        #     elif language == '6' or 'South African':
        #         tool = language_check.LanguageTool('en-SA')
        #         vaidinput = True
        #     else:
        #         print("Your input is not an option.")

        #Get Input Filename from User Input
        #filename = input("Please input the name of your file: ")

        # #Open File for Reading
        # try:
        #     f = open(filename, 'r')
        # except IOError:
        #     print("File Could Not Be Opened.")
        #     exit()
        #
        # #Read from Input File
        # try:
        #     text = f.read()
        # except IOError:
        #     print("Unable to Read File.")
        #     exit()
        #
        # #Close Input File
        # try:
        #     f.close()
        # except IOError:
        #     print("File Could Not Be Closed.")
        #     exit()

        nopunc_text = text.translate(str.maketrans('','',string.punctuation))
        tokenized_text = word_tokenize(nopunc_text)

        self.lex.generatescore(tokenized_text)
        #self.grammar.generatescore(text,tokenized_text,tool)
        self.readability.generatescore(text)
        self.extended.generatescore(tokenized_text)
        metrics = dict()
        metrics['wordfrequency_all'] = self.lex.wordfrequency_all
        metrics['wordfrequency_content'] = self.lex.wordfrequency_content
        metrics['wordfrequency_function'] = self.lex.wordfrequency_function
        metrics['wordrangescore'] = self.lex.wordrangescore
        metrics['academicwordscore'] = self.lex.academicwordscore
        metrics['sublist1score'] = self.lex.sublist1score
        metrics['sublist2score'] = self.lex.sublist2score
        metrics['sublist3score'] = self.lex.sublist3score
        metrics['sublist4score'] = self.lex.sublist4score
        metrics['sublist5score'] = self.lex.sublist5score
        metrics['sublist6score'] = self.lex.sublist6score
        metrics['sublist7score'] = self.lex.sublist7score
        metrics['sublist8score'] = self.lex.sublist8score
        metrics['sublist9score'] = self.lex.sublist9score
        metrics['sublist10score'] = self.lex.sublist10score
        metrics['familiarityscore'] = self.lex.familiarityscore
        metrics['concretenessscore'] = self.lex.concretenessscore
        metrics['imagabilityscore'] = self.lex.imagabilityscore
        metrics['meaningfulnesscscore'] = self.lex.meaningfulnesscscore
        metrics['meaningfulnesspscore'] = self.lex.meaningfulnesspscore
        metrics['ageofacquisitionscore'] = self.lex.ageofacquisitionscore
        #metrics['errorrate'] = self.grammar.errorrate
        metrics['flesch_reading_ease'] = self.readability.flesch_reading_ease
        metrics['flesch_kincaid_grade_level'] = self.readability.flesch_kincaid_grade_level
        metrics['smog'] = self.readability.smog
        metrics['coleman_liau'] = self.readability.coleman_liau
        metrics['ari'] = self.readability.ari
        metrics['semanticoverlap'] = self.extended.semanticoverlap
        metrics['typetokenratio'] = self.extended.typetokenratio
        return metrics


        print(self.lex.wordfrequency_all)
        print(self.lex.wordfrequency_content)
        print(self.lex.wordfrequency_function)
        print(self.lex.wordrangescore)
        print(self.lex.academicwordscore)
        print(self.lex.sublist1score)
        print(self.lex.sublist2score)
        print(self.lex.sublist3score)
        print(self.lex.sublist4score)
        print(self.lex.sublist5score)
        print(self.lex.sublist6score)
        print(self.lex.sublist7score)
        print(self.lex.sublist8score)
        print(self.lex.sublist9score)
        print(self.lex.sublist10score)
        print(self.lex.familiarityscore)
        print(self.lex.concretenessscore)
        print(self.lex.imagabilityscore)
        print(self.lex.meaningfulnesscscore)
        print(self.lex.meaningfulnesspscore)
        print(self.lex.ageofacquisitionscore)
        #print(self.grammar.errorrate)
        print(self.readability.flesch_reading_ease)
        print(self.readability.flesch_kincaid_grade_level)
        print(self.readability.smog)
        print(self.readability.coleman_liau)
        print(self.readability.ari)
        print(self.extended.semanticoverlap)
        print(self.extended.typetokenratio)

if __name__ == "__main__":
    givememyscore = givememyscore()
    a = "Tom hit Jerry. Jerry hit him back. tom was mad. Jerry is happy. Tom and Jerry not firends. This demonstrates that Tom and Jerry are not friends. Our hypothesis was wrong."

    x = givememyscore.startevaluation(a)
    print(x)
