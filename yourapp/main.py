#!/bin/bash python
import argparse
import json
import time
import logging

st = time.time()

def process_text(body):
    # time.sleep(30)
    return "This is the result by yourapp with: {}".format(body)

def main(uid="", body=""):
    processed_body = process_text(body)
    ajson = {
        "uid": uid,
        "body": body,
        "processed_body": processed_body
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
