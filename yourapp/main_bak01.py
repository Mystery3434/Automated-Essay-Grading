#!/bin/bash python
import argparse
import json
import time
import logging

st = time.time()

def process_text(body):
    # time.sleep(30)
    return "This is the result by yourapp with: {}".format(body)

def main(id="", uuid="", body=""):
    #processed_body = process_text(body)
    processed_body = {"length_by_sentence": 1,
                        "length_by_distinct_token": 1,
                        "length_by_word" : 1,
                        "length_by_character" : 1,
                        "lexical_diversity" : 9.5,
                        "data_by_sentence" : "{}",
                        "data_by_fdist" : "{}",
                        "wordfrequency_all" : 0.541,
                        "wordfrequency_content" : 0.912,
                        "wordfrequency_function" : 0.173,
                        "wordrangescore" : 0.614,
                        "academicwordscore" : 0.215,
                        "academic_sublists_score" : 0.871,
                        "familiarityscore" : 0.992,
                        "concretenessscore" : 0.123,
                        "imagabilityscore" : 0.224,
                        "meaningfulnesscscore" : 0.746,
                        "meaningfulnesspscore" : 0.43,
                        "ageofacquisitionscore" : 0.345,
                        "grammar_errorrate" : 0.765,
                        "flesch_reading_ease" : 0.636,
                        "flesch_kincaid_grade_level" : 0.876,
                        "smog" : 0.146,
                        "coleman_liau" : 0.865,
                        "ari" : 0.688,
                        "semanticoverlap" : 0.69,
                        "typetokenratio" : 0.420,
                        "holistic_score" : 0.696
                        }

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
        uid=uid,
        body=body,
    )

    print(result)
    print("~~ finished in {0:.3f} sec ~~".format(time.time() - st))
