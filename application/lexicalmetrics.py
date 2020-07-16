import collections
from nltk.corpus import stopwords

class lexicalmetrics:
    def __init__(self):
        self.wordfrequency_all = None
        self.wordfrequency_context = None
        self.wordfrequency_function = None
        self.wordrangescore = None
        self.academicwordscore = None
        self.sublist1score = None
        self.sublist2score = None
        self.sublist3score = None
        self.sublist4score = None
        self.sublist5score = None
        self.sublist6score = None
        self.sublist7score = None
        self.sublist8score = None
        self.sublist9score = None
        self.sublist10score = None
        self.familiarityscore = None
        self.concretenessscore = None
        self.imagabilityscore = None
        self.meaningfulnesscscore = None
        self.meaningfulnesspscore = None
        self.ageofacquisitionscore = None

    def generatescore(self,tokenized_text):
            try:
                f = open("written.num","r", encoding="utf8")
                f1 = open("awl.txt","r", encoding="utf8")
                f2 = open("sublist1.txt","r", encoding="utf8")
                f3 = open("sublist2.txt","r", encoding="utf8")
                f4 = open("sublist3.txt","r", encoding="utf8")
                f5 = open("sublist4.txt","r", encoding="utf8")
                f6 = open("sublist5.txt","r", encoding="utf8")
                f7 = open("sublist6.txt","r", encoding="utf8")
                f8 = open("sublist7.txt","r", encoding="utf8")
                f9 = open("sublist8.txt","r", encoding="utf8")
                f10 = open("sublist9.txt","r", encoding="utf8")
                f11 = open("sublist10.txt","r", encoding="utf8")
                f12 = open("familiarity.txt","r", encoding="utf8")
                f13 = open("concreteness.txt","r", encoding="utf8")
                f14 = open("imagability.txt","r", encoding="utf8")
                f15 = open("meaningfulness_coloradonorms.txt","r", encoding="utf8")
                f16 = open("meaningfulness_paivionorms.txt","r", encoding="utf8")
                f17 = open("ageofacquisition.txt","r", encoding="utf8")
            except IOError:
                print("File Could Not Be Opened.")
                exit()

            try:
                bnc = f.read().splitlines()
                awl = f1.read().splitlines()
                awl_sublist1 = f2.read().splitlines()
                awl_sublist2 = f3.read().splitlines()
                awl_sublist3 = f4.read().splitlines()
                awl_sublist4 = f5.read().splitlines()
                awl_sublist5 = f6.read().splitlines()
                awl_sublist6 = f7.read().splitlines()
                awl_sublist7 = f8.read().splitlines()
                awl_sublist8 = f9.read().splitlines()
                awl_sublist9 = f10.read().splitlines()
                awl_sublist10 = f11.read().splitlines()
                mrc_familiarity = f12.read().splitlines()
                mrc_concreteness = f13.read().splitlines()
                mrc_imagability = f14.read().splitlines()
                mrc_meaningfulness_c = f15.read().splitlines()
                mrc_meaningfulness_p = f16.read().splitlines()
                mrc_ageofacquisition = f17.read().splitlines()
            except IOError:
                print("Could Not Read From File.")
                exit()

            freqlist = collections.defaultdict()
            occurlist = collections.defaultdict()
            contentlist = collections.defaultdict()
            functionlist = collections.defaultdict()
            familiaritylist = collections.defaultdict()
            concretenesslist = collections.defaultdict()
            imagabilitylist = collections.defaultdict()
            ageofacquisitionlist = collections.defaultdict()
            meaningfulness_c_list = collections.defaultdict()
            meaningfulness_p_list = collections.defaultdict()

            for i in range (1, len(bnc)):
                freq, word, pos, occurrence = bnc[i].split()
                freqlist[word] = int(freq)
                occurlist[word] = int(occurrence)
                if pos=="aj0-av0" or pos=="aj0-nn1" or pos=="aj0-vvd" or pos=="aj0-vvg" or pos=="aj0-vvn" or pos=="nn1-np0" or pos=="nn1-vvb" or pos=="nn1-vvg" or pos=="nn2-vvz" or pos=="vvd-vvn" or pos=="aj0" or pos=="ajc" or pos=="ajs" or pos=="av0" or pos=="nn0" or pos=="nn1" or pos=="nn2" or pos=="np0" or pos=="vvb" or pos=="vvg" or pos=="vvi" or pos=="vvn" or pos=="vvz":
                    contentlist[word] = int(freq)
                else:
                    if pos!="pul" and pos!="pun" and pos!="puq" and pos!="pur" and pos!="unc" and pos!="zz0" and pos!="itj":
                        functionlist[word] = int(freq)

            for i in range (1, len(mrc_familiarity)):
                mrc_familiarity[i] = mrc_familiarity[i].strip()
                word, score = mrc_familiarity[i].split()
                familiaritylist[word] = int(score)

            for i in range (1, len(mrc_concreteness)):
                word, score = mrc_concreteness[i].split()
                concretenesslist[word] = int(score)

            for i in range (1, len(mrc_imagability)):
                word, score = mrc_imagability[i].split()
                imagabilitylist[word] = int(score)

            for i in range (1, len(mrc_ageofacquisition)):
                word, score = mrc_ageofacquisition[i].split()
                ageofacquisitionlist[word] = int(score)

            for i in range (1, len(mrc_meaningfulness_c)):
                word, score = mrc_meaningfulness_c[i].split()
                meaningfulness_c_list[word] = int(score)

            for i in range (1, len(mrc_meaningfulness_p)):
                word, score = mrc_meaningfulness_p[i].split()
                meaningfulness_p_list[word] = int(score)
     
            try:
                f.close()
                f1.close()
                f2.close()
                f3.close()
                f4.close()
                f5.close()
                f6.close()
                f7.close()
                f8.close()
                f9.close()
                f10.close()
                f11.close()
                f12.close()
                f13.close()
                f14.close()
                f15.close()
                f16.close()
                f17.close()
            except IOError:
                print("Could Not Close File.")
                exit()

            stop_words = set(stopwords.words('english'))
            nostopwords_tokenized_text = []
            for w in tokenized_text:
                if w not in stop_words:
                    nostopwords_tokenized_text.append(w)
                    

            self.wordfrequencyall(tokenized_text, freqlist)
            self.wordfrequencycontent(tokenized_text, contentlist)
            self.wordfrequencyfunction(tokenized_text, functionlist)
            self.wordrange(tokenized_text, occurlist)
            self.academicwords(nostopwords_tokenized_text, awl, awl_sublist1, awl_sublist2, awl_sublist3, awl_sublist4, awl_sublist5, awl_sublist6, awl_sublist7, awl_sublist8, awl_sublist9, awl_sublist10)
            self.wordfamiliarity(nostopwords_tokenized_text, familiaritylist)
            self.wordconcreteness(nostopwords_tokenized_text, concretenesslist)
            self.wordimagability(nostopwords_tokenized_text, imagabilitylist)
            self.ageofacquisition(nostopwords_tokenized_text, ageofacquisitionlist)
            self.wordmeaningfulness_c(nostopwords_tokenized_text, meaningfulness_c_list)
            self.wordmeaningfulness_p(nostopwords_tokenized_text, meaningfulness_p_list)
            pass
        
    def wordfrequencyall(self, tokenized_text, freqlist):
        self.wordfrequency_all = 0
        count = 0
        freqsum = 0
        for w in tokenized_text:
            if w in freqlist:
                freqsum += freqlist[w]
                count +=1
        
        if count != 0:
            self.wordfrequency_all = freqsum/count
        pass

    def wordfrequencycontent(self, tokenized_text, contentlist):
        self.wordfrequency_content = 0
        count = 0
        freqsum = 0
        for w in tokenized_text:
            if w in contentlist:
                freqsum += contentlist[w]
                count +=1
        if count != 0:
            self.wordfrequency_content = freqsum/count
        pass

    def wordfrequencyfunction(self, tokenized_text, functionlist):
        self.wordfrequency_function = 0
        count = 0
        freqsum = 0
        for w in tokenized_text:
            if w in functionlist:
                freqsum += functionlist[w]
                count +=1
        if count != 0:
            self.wordfrequency_function = freqsum/count
        pass
    
    def wordrange(self, tokenized_text, occurlist):
        self.wordrangescore = 0
        count = 0
        occursum = 0
        for w in tokenized_text:
            if w in occurlist:
                occursum += occurlist[w]
                count += 1
        if count != 0:
            self.wordrangescore = occursum/count
        pass

    def academicwords(self, tokenized_text, awl, sublist1, sublist2, sublist3, sublist4, sublist5, sublist6, sublist7, sublist8, sublist9, sublist10):
        awlcount = 0
        sublist1count = 0
        sublist2count = 0
        sublist3count = 0
        sublist4count = 0
        sublist5count = 0
        sublist6count = 0
        sublist7count = 0
        sublist8count = 0
        sublist9count = 0
        sublist10count = 0
        for w in tokenized_text:
            if w in awl:
                awlcount+=1
                if w in sublist1:
                    sublist1count+=1
                elif w in sublist2:
                    sublist2count+=1
                elif w in sublist3:
                    sublist3count+=1
                elif w in sublist4:
                    sublist4count+=1
                elif w in sublist5:
                    sublist5count+=1
                elif w in sublist6:
                    sublist6count+=1
                elif w in sublist7:
                    sublist7count+=1
                elif w in sublist8:
                    sublist8count+=1
                elif w in sublist9:
                    sublist9count+=1
                elif w in sublist10:
                    sublist10count+=1
        if awlcount!=0:
            self.academicwordscore = awlcount/(len(tokenized_text))
            self.sublist1score = sublist1count/awlcount
            self.sublist2score = sublist2count/awlcount
            self.sublist3score = sublist3count/awlcount
            self.sublist4score = sublist4count/awlcount
            self.sublist5score = sublist5count/awlcount
            self.sublist6score = sublist6count/awlcount
            self.sublist7score = sublist7count/awlcount
            self.sublist8score = sublist8count/awlcount
            self.sublist9score = sublist9count/awlcount
            self.sublist10score = sublist10count/awlcount
        else:
            self.academicwordscore = 0
            self.sublist1score = 0
            self.sublist2score = 0
            self.sublist3score = 0
            self.sublist4score = 0
            self.sublist5score = 0
            self.sublist6score = 0
            self.sublist7score = 0
            self.sublist8score = 0
            self.sublist9score = 0
            self.sublist10score = 0
        pass

    def wordfamiliarity(self,tokenized_text, scorelist):
        count = 0
        scoresum = 0
        for w in tokenized_text:
            if w.upper() in scorelist:
                scoresum += scorelist[w.upper()]
                count += 1
        if count == 0:
            familiarity = "not applicable"
        else:
            familiarity = scoresum/count
        self.familiarityscore = familiarity
        pass

    def wordconcreteness(self,tokenized_text, scorelist):
        count = 0
        scoresum = 0
        for w in tokenized_text:
            if w.upper() in scorelist:
                scoresum += scorelist[w.upper()]
                count += 1
        if count == 0:
            concreteness = "not applicable"
        else:
            concreteness = scoresum/count
        self.concretenessscore = concreteness
        pass
                    
    def wordimagability(self,tokenized_text, scorelist):
        count = 0
        scoresum = 0
        for w in tokenized_text:
            if w.upper() in scorelist:
                scoresum += scorelist[w.upper()]
                count += 1
        if count == 0:
            imagability = "not applicable"
        else:
            imagability = scoresum/count
        self.imagabilityscore = imagability
        pass

    def wordmeaningfulness_c(self,tokenized_text, scorelist):
        count = 0
        scoresum = 0
        for w in tokenized_text:
            if w.upper() in scorelist:
                scoresum += scorelist[w.upper()]
                count += 1
        if count == 0:
            meaningfulness_c = "not applicable"
        else:
            meaningfulness_c = scoresum/count
        self.meaningfulnesscscore = meaningfulness_c
        pass

    def wordmeaningfulness_p(self,tokenized_text, scorelist):
        count = 0
        scoresum = 0
        for w in tokenized_text:
            if w.upper() in scorelist:
                scoresum += scorelist[w.upper()]
                count += 1
        if count == 0:
            meaningfulness_p = "not applicable"
        else:
            meaningfulness_p = scoresum/count
        self.meaningfulnesspscore = meaningfulness_p
        pass

    def ageofacquisition(self,tokenized_text, scorelist):
        count = 0
        scoresum = 0
        for w in tokenized_text:
            if w.upper() in scorelist:
                scoresum += scorelist[w.upper()]
                count += 1
        if count == 0:
            ageofacquisition = "not applicable"
        else:
            ageofacquisition = scoresum/count
        self.ageofacquisitionscore = ageofacquisition
        pass

