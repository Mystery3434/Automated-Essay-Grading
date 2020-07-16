import givememyscore
import pandas as pd
import csv

def modify_dataset():
    file_loc = "validation_testing_1.tsv"
    data = dict()
    data['essay_set'] = list()
    data['essay'] = list()
    data['domain1_score'] = list()

    data['wordfrequency_all'] = list()
    data['wordfrequency_content'] = list()
    data['wordfrequency_function'] = list()
    data['wordrangescore'] = list()
    data['academicwordscore'] = list()
    data['sublist1score'] = list()
    data['sublist2score'] = list()
    data['sublist3score'] = list()
    data['sublist4score'] = list()
    data['sublist5score'] = list()
    data['sublist6score'] = list()
    data['sublist7score'] = list()
    data['sublist8score'] = list()
    data['sublist9score'] = list()
    data['sublist10score'] = list()
    data['familiarityscore'] = list()
    data['concretenessscore'] = list()
    data['imagabilityscore'] = list()
    data['meaningfulnesscscore'] = list()
    data['meaningfulnesspscore'] = list()
    data['ageofacquisitionscore'] = list()
    data['errorrate'] = list()
    data['flesch_reading_ease'] = list()
    data['flesch_kincaid_grade_level'] = list()
    data['smog'] = list()
    data['coleman_liau'] = list()
    data['ari'] = list()
    data['semanticoverlap'] = list()
    #data['typetokenratio'] = list()



    get_doc_stats = givememyscore.givememyscore()
    i = 0
    with open(file_loc, encoding='latin1') as tsvfile:
        reader = csv.DictReader(tsvfile, dialect='excel-tab')

        for row in reader:

            i+=1
            data['essay_set'].append(row['essay_set'])
            data['essay'].append(row['essay'])
            data['domain1_score'].append(row['domain1_score'])
            docstats = get_doc_stats.startevaluation(row['essay'])
            data['wordfrequency_all'].append(docstats['wordfrequency_all'])
            data['wordfrequency_content'].append(docstats['wordfrequency_content'])
            data['wordfrequency_function'].append(docstats['wordfrequency_function'])
            data['wordrangescore'].append(docstats['wordrangescore'])
            data['academicwordscore'].append(docstats['academicwordscore'])
            data['sublist1score'].append(docstats['sublist1score'])
            data['sublist2score'].append(docstats['sublist2score'])
            data['sublist3score'].append(docstats['sublist3score'])
            data['sublist4score'].append(docstats['sublist4score'])
            data['sublist5score'].append(docstats['sublist5score'])
            data['sublist6score'].append(docstats['sublist6score'])
            data['sublist7score'].append(docstats['sublist7score'])
            data['sublist8score'].append(docstats['sublist8score'])
            data['sublist9score'].append(docstats['sublist9score'])
            data['sublist10score'].append(docstats['sublist10score'])
            data['familiarityscore'].append(docstats['familiarityscore'])
            data['concretenessscore'].append(docstats['concretenessscore'])
            data['imagabilityscore'].append(docstats['imagabilityscore'])
            data['meaningfulnesscscore'].append(docstats['meaningfulnesscscore'])
            data['meaningfulnesspscore'].append(docstats['meaningfulnesspscore'])
            data['ageofacquisitionscore'].append(docstats['ageofacquisitionscore'])
            data['errorrate'].append(docstats['errorrate'])
            data['flesch_reading_ease'].append(docstats['flesch_reading_ease'])
            data['flesch_kincaid_grade_level'].append(docstats['flesch_kincaid_grade_level'])
            data['smog'].append(docstats['smog'])
            data['coleman_liau'].append(docstats['coleman_liau'])
            data['ari'].append(docstats['ari'])
            data['semanticoverlap'].append(docstats['semanticoverlap'])
            if i % 10 == 0:
                print("Finished " + str(i) + " entries.")
        #data['typetokenratio'].append(docstats['typetokenratio'])


    # print(type(reader))
    df = pd.DataFrame.from_dict(data)
    df.to_csv("validation_testing_with_grammar3.tsv", sep='\t',index=False)
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    #     print(df)

if __name__ == "__main__":
    modify_dataset()