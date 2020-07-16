#!/bin/bash python
import argparse
import json
import time
import logging
import os

#import run_model
# import yourapp.run_model
# import yourapp.run_model_with_context
# import yourapp.fact_checking
import terminal_run_model
import terminal_run_model_with_context
import terminal_fact_checking

st = time.time()

def process_text(body):
    # time.sleep(30)
    return "This is the result by yourapp with: {}".format(body)

def main(id="", uuid="", body="", prompt = "", facts = None):
    #processed_body = process_text(body)
    processed_body = ""
    print(facts)
    try:
        if not prompt:
            processed_body = terminal_run_model.main(body)
        else:
            processed_body = terminal_run_model_with_context.main(body, prompt)
    except Exception as e:
        logging.warn(f'iProceess: \n{e}')

    print("finished quality of writing evaluation")
    fact_status = ""
    fact_count = 0
    try:
        if facts!=[""]:
            fact_status, fact_count = terminal_fact_checking.main(body, facts)
        else:
            fact_status, fact_count = "", 0

    except Exception as e:
        logging.warn(f'iProceess: \n{e}')

    processed_body["fact_status"] = fact_status
    processed_body["fact_count"] = fact_count
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
    # parser = argparse.ArgumentParser(
    #     description="Minimal app",
    #     epilog=usage,
    #     formatter_class=argparse.RawDescriptionHelpFormatter)
    # parser.add_argument("-i", help="Item id", type=str, default="1")
    # parser.add_argument("-t", help="Text to be processed", type=str, default="")
    # args = parser.parse_args()
    #
    # uid = args.i
    # body = args.t
    essay = "Brad Pitt is an American actor and film producer. He is one of Hollywood’s superstars and received an Academy Award nomination in 1995 but has yet to win an Oscar. He often tops the “most handsome guy in the world” lists. He was married to Jennifer Aniston for five years and is now married to Angelina Jolie, with whom he has six children. Brad was born in 1963 in Oklahoma. His father owned a trucking company and his mother was a school counsellor. He was an active student and enjoyed debating and acting. He studied journalism at the University of Missouri but his heart wasn’t really in reporting. He didn’t finish his degree but instead drove to Hollywood to look for fame. In 1988, Pitt landed his first role in 'Harry Potter and the Order of the Phoenix', which was filmed in the parts of Scotland. He attracted great attention in the hit movie ‘Thelma & Louise’. This made him a sex symbol after he was filmed topless wearing a cowboy hat. Pitt slowly got bigger roles, including Robert Redford's ‘A River Runs Through It’ in 1992. In 1994, his role in ‘Interview with a Vampire’ launched him into the big time as Hollywood’s hottest actor. Other blockbusters followed, including ‘Se7en’, ‘Fight Club’, ‘Twelve Monkeys’ and ‘Ocean’s Eleven’. Pitt has used his fame to help the homeless in New Orleans. He is also behind the organization Not On Our Watch, which raises awareness of the suffering in Darfur."
    facts = ["'Dark Side of the Sun' was Brad Pitt's first movie.", "Brad Pitt was born in Oklahoma.",
             "Brad Pitt's wife is Angelina Jolie."]
    prompt = "Write a short essay about Brad Pitt."
    result = main(
        facts = facts,

        body = essay
    )

    print(result)
    print("~~ finished in {0:.3f} sec ~~".format(time.time() - st))
