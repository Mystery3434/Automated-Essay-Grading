#!/bin/bash python
import argparse
import json
import time
import logging
import os

#import run_model
import yourapp.run_model
import yourapp.run_model_with_context
import yourapp.fact_checking


st = time.time()

def process_text(body):
    # time.sleep(30)
    return "This is the result by yourapp with: {}".format(body)

def associative_rules(processed_body):
    feedback_text = ""


    # NOTE: Although a low value for grammar error rate indicate better writing, we decided to invert these values so that a higher score
    # indicates better writing, in order for it to be more interpretable to the user. On the actual graph shown to the user, this value is thus
    # renamed "Grammatical Accuracy". to indicate that higher values indicate better writing quality.
    # However, in the database, these values are still referred to as grammar_errorrate even though they store the inverted values. 
    # Hence, these names in the database must be changed so as to avoid errors.
    # Furthermore, values for smog readability, frequency, and familiarity were scaled to the range of 0 to 100 for better interpretability and
    # named as "University-Appropriate Readability", "Word Variety", and "Word Choice" respectively.


    if processed_body["grammar_errorrate"] < 0.2:
        feedback_text += 'The essay recorded a relatively high grammar error rate. We suggest perhaps proofreading the essay once more for grammatical errors and typos. '
    elif processed_body["grammar_errorrate"] >= 0.2 and processed_body["grammar_errorrate"] < 0.7:
        feedback_text += 'The essay recorded a moderately high error rate. We suggest perhaps proofreading the essay once more for grammatical errors and typos. '
    else:
        feedback_text += 'The essay recorded a low grammar error rate. Proofreading might help improve the essay, but not by much. '

    if processed_body["smog"] < 30:
        feedback_text += "The readability of the essay is considered equivalent to that of middle school level writing. The essay does not incorporates enough academic terminology and may not be considered appropriate as a piece of academic writing. "
    elif processed_body["smog"] >= 30 and processed_body["smog"] < 70 :
        feedback_text += "The readability of the essay is considered equivalent to that of high school level writing. The essay could incorporate more academic terminology to be considered more appropriate as a piece of academic writing. "
    else:
        feedback_text += "The readability of the essay is considered equivalent to that of university level writing. The essay incorporates several academic terminology and may be considered highly appropriate as a piece of academic writing. "

    if processed_body["wordfrequency_all"] > 70:
        feedback_text += "The word variety is good with usage of both common and uncommon words. A strong vocabulary is demonstrated in this response. "
    elif processed_body["wordfrequency_all"] > 30 and processed_body["wordfrequency_all"] <= 70:
        feedback_text += "The word variety may be considered limited with usage of many commonly used words in addition to some uncommon words. Variety can be improved through usage of more synonyms, and wider vocabulary. "
    else:
        feedback_text += "The word variety is very limited with usage of many commonly used words. Variety can be improved through usage of more synonyms, and wider vocabulary. "

    if processed_body["familiarityscore"] > 70:
        feedback_text += "The word choice of the essay excels in familiarity, suggesting that the essay excels in expression. "
    elif processed_body["familiarityscore"] > 30 and processed_body["familiarityscore"] <= 70:
        feedback_text += "The word choice of the essay might be a bit esoteric in terms of familiarity, suggesting that the word choice could be more grounded. "
    else:
        feedback_text += "The word choice of the essay is arcane, suggesting that the essay needs to be modified to make it more suitable for academic writing. "

    if processed_body["accuracy_score"] > 70:
        feedback_text += "The factual accuracy checked against the provided facts is high. Good job!"
    elif processed_body["accuracy_score"] > 30 and  processed_body["accuracy_score"] <= 70:
        feedback_text += "There appear to be some factual mistakes in your essay. We suggest going back to see if you have successfully supported all factual claims as required in the essay. "
    else:
        feedback_text += "The factual accuracy checked against the provided facts is deemed relatively low. We suggest going back to see if you have successfully supported all factual claims as required in the essay. "

    return feedback_text
    

def main(id="", uuid="", body="", prompt = "", facts = None):
    #processed_body = process_text(body)
    processed_body = ""
    try:
        if not prompt:
            processed_body = yourapp.run_model.main(body)
        else:
            processed_body = yourapp.run_model_with_context.main(body, prompt)
    except Exception as e:
        logging.warn(f'iProceess: \n{e}')

    fact_status = ""
    fact_count = 0
    try:
        if facts!=[""]:
            fact_status, fact_count = yourapp.fact_checking.main(body, facts)
        else:
            fact_status, fact_count = "", 0

    except Exception as e:
        logging.warn(f'iProceess: \n{e}')

    processed_body["fact_status"] = str(fact_status)
    processed_body["fact_count"] = fact_count
    processed_body["holistic_score"] *= 100
    if not facts:
        processed_body["accuracy_score"] = 100
    else:
        processed_body["accuracy_score"] = (processed_body["fact_count"] / len(facts) ) * 100

    feedback_text = associative_rules(processed_body)
    processed_body["feedback_text"] = feedback_text

    # processed_body = {"length_by_sentence": 1,
    #                     "length_by_distinct_token": 1,
    #                     "length_by_word" : 1,
    #                     "length_by_character" : 1,
    #                     "lexical_diversity" : 9.5,
    #                     "data_by_sentence" : "{}",
    #                     "data_by_fdist" : "{}",
    #                     "wordfrequency_all" : 0.541,
    #                     "wordfrequency_content" : 0.912,
    #                     "wordfrequency_function" : 0.173,
    #                     "wordrangescore" : 0.614,
    #                     "academicwordscore" : 0.215,
    #                     "academic_sublists_score" : 0.871,
    #                     "familiarityscore" : 0.992,
    #                     "concretenessscore" : 0.123,
    #                     "imagabilityscore" : 0.224,
    #                     "meaningfulnesscscore" : 0.746,
    #                     "meaningfulnesspscore" : 0.43,
    #                     "ageofacquisitionscore" : 0.345,
    #                     "grammar_errorrate" : 0.765,
    #                     "flesch_reading_ease" : 0.636,
    #                     "flesch_kincaid_grade_level" : 0.876,
    #                     "smog" : 0.146,
    #                     "coleman_liau" : 0.865,
    #                     "ari" : 0.688,
    #                     "semanticoverlap" : 0.69,
    #                     "typetokenratio" : 0.420,
    #                     "holistic_score" : 0.696
    #                     }

    logging.warn(f'eeeProcess: {processed_body}')
    ajson = {
        "id": id,
        "uuid": uuid,
        "body": body,
        "processed_body": processed_body,
        "val": 0.01,
    }
    return ajson

usage = """
    Minimal app

	Usage:

    # Use text buffer
    python3 main.py -i id_of_item -t "text buffer" -l
	"""

if __name__ == "__main__":
    # Handle arguments
    parser = argparse.ArgumentParser(
        description="Minimal app",
        epilog=usage,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-i", help="Item id", type=str, default="1")
    parser.add_argument("-t", help="Text to be processed", type=str, default="")
    args = parser.parse_args()

    uid = args.i
    body = args.t

    result = main(
        uuid=uid,
        body=body,
    )

    print(result)
    print("~~ finished in {0:.3f} sec ~~".format(time.time() - st))
