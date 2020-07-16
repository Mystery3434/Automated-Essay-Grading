import textstat

class readabilitymetrics:
    def __init__(self):
        self.flesch_reading_ease = None
        self.flesch_kincaid_grade_level = None
        self.smog = None
        self.coleman_liau = None
        self.ari = None

    def generatescore(self,text): 
        self.flesch_reading_ease = textstat.flesch_reading_ease(text)
        self.flesch_kincaid_grade_level = textstat.flesch_kincaid_grade(text)
        self.smog = textstat.smog_index(text)
        self.coleman_liau = textstat.coleman_liau_index(text)
        self.ari = textstat.automated_readability_index(text)
        pass
