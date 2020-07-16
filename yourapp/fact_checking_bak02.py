from absl import logging
from allennlp.predictors.predictor import Predictor
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import seaborn as sns
from fuzzywuzzy import fuzz
import string
import copy
import nltk
from nltk.corpus import wordnet, stopwords
nltk.download("wordnet")
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))
tf.compat.v1.enable_eager_execution()

def embed(input):
    return model(input)


# Reduce logging output.
logging.set_verbosity(logging.ERROR)


def plot_similarity(labels, features, rotation):
    corr = np.inner(features, features)
    sns.set(font_scale=1.2)
    g = sns.heatmap(
        corr,
        xticklabels=labels,
        yticklabels=labels,
        vmin=0,
        vmax=1,
        cmap="YlOrRd")
    g.set_xticklabels(labels, rotation=rotation)
    g.set_title("Semantic Textual Similarity")


def run_and_plot(messages_):
    message_embeddings_ = embed(messages_)
    plot_similarity(messages_, message_embeddings_, 90)


def print_prediction(prediction):
    # Requires the prediction vector from the 'label_probs' part of the predictor object.
    print("Probabilities:\nEntailment:{0:.2f}%\nContradiction:{1:.2f}%\nNeutral:{2:.2f}%\n".format(prediction[0] * 100,
                                                                                                   prediction[1] * 100,
                                                                                                   prediction[2] * 100))


def generate_entailment_matrix(essay_sentences, facts, predictor):
    # essay_sentences is a list of sentences in the essay
    # facts is a list of instructor-provided facts
    mat = np.zeros((len(essay_sentences), len(facts)))
    for i in range(len(essay_sentences)):
        for j in range(len(facts)):
            current_prediction = predictor.predict(hypothesis=facts[j], premise=essay_sentences[i])['label_probs']
            mat[i][j] = current_prediction[0]
    return mat


def plot_similarity_distinct(labels1, labels2, features1, features2, rotation):
    corr = np.inner(features1, features2)
    sns.set(font_scale=1.2)
    g = sns.heatmap(
        corr,
        yticklabels=labels1,
        xticklabels=labels2,
        vmin=0,
        vmax=1,
        cmap="YlOrRd")
    g.set_xticklabels(labels2, rotation=rotation)
    g.set_title("Semantic Textual Similarity")


def run_and_plot_distinct(messages1, messages2):
    message_embeddings1 = embed(messages1)
    message_embeddings2 = embed(messages2)
    plot_similarity_distinct(messages1, messages2, message_embeddings1, message_embeddings2, 90)


def get_similarity_matrix(list1, list2):
    # the first list could be a list of sentences in the essay
    # the second list could be a list of instructor-provided facts
    list_embeddings1 = embed(list1)
    list_embeddings2 = embed(list2)

    corr = np.inner(list_embeddings1, list_embeddings2)
    return corr


def get_fuzzy_matrix(essay_sentences, facts):
    matrix = np.array(
        [[((fuzz.partial_ratio(sentence, fact) + fuzz.token_set_ratio(sentence, fact)) / 2) / 100 for fact in facts] for
         sentence in essay_sentences])
    return matrix


def print_similar_fact(similarity_matrix, essay_sentence_list, facts):
    for i in range(similarity_matrix.shape[1]):
        highest_index = np.argmax(similarity_matrix.T[i])
        if similarity_matrix[highest_index][i] > 0.45:
            print(facts[i], essay_sentence_list[highest_index])


def print_corresponding_fact(similarity_matrix, entailment_matrix, essay_sentence_list, facts):
    matrix = 0.75 * similarity_matrix + 0.25 * entailment_matrix
    count = 0
    for i in range(matrix.shape[1]):
        highest_index = np.argmax(matrix.T[i])
        if matrix[highest_index][i] > 0.45:
            count += 1
            print("The fact: ", facts[i], "is supported by the sentence: ", essay_sentence_list[highest_index])
    print(count, " out of ", len(facts), " facts are supported by the essay.")


def fact_check_no_fuzzy(essay, facts, predictor, print_corresponding_facts=True):
    essay_sents = essay.split(".")
    entailment_matrix = generate_entailment_matrix(essay_sents, facts, predictor)
    similarity_matrix = get_similarity_matrix(essay_sents, facts)
    matrix = 0.75 * similarity_matrix + 0.25 * entailment_matrix
    count = 0
    for i in range(matrix.shape[1]):
        highest_index = np.argmax(matrix.T[i])
        if matrix[highest_index][i] > 0.45:
            count += 1
            if print_corresponding_facts:
                print("The fact: ", facts[i], "is supported by the sentence: ", essay_sents[highest_index])
    print(count, " out of ", len(facts), " facts are supported by the essay.")


def fact_check(essay, facts, predictor, print_corresponding_facts=True):
    essay_sents = essay.split(".")
    entailment_matrix = generate_entailment_matrix(essay_sents, facts, predictor)
    similarity_matrix = get_similarity_matrix(essay_sents, facts)
    fuzzy_matrix = get_fuzzy_matrix(essay_sents, facts)
    matrix = 0.33 * fuzzy_matrix + 0.33 * similarity_matrix + 0.33 * entailment_matrix
    count = 0
    print(matrix)
    for i in range(matrix.shape[1]):
        highest_index = np.argmax(matrix.T[i])
        if matrix[highest_index][i] > 0.5:
            count += 1
            if print_corresponding_facts:
                print("The fact: ", facts[i], "is supported by the sentence: ", essay_sents[highest_index])
    print(count, " out of ", len(facts), " facts are supported by the essay.")


def fact_check_with_fuzzy_only(essay, facts, predictor, print_corresponding_facts=True):
    essay_sents = essay.split(".")
    fuzzy_matrix = get_fuzzy_matrix(essay_sents, facts)
    matrix = fuzzy_matrix
    count = 0
    print(matrix)
    for i in range(matrix.shape[1]):
        highest_index = np.argmax(matrix.T[i])
        if matrix[highest_index][i] > 0.5:
            count += 1
            if print_corresponding_facts:
                print("The fact: ", facts[i], "is supported by the sentence: ", essay_sents[highest_index])
    print(count, " out of ", len(facts), " facts are supported by the essay.")


def fact_check_with_semsim_only(essay, facts, predictor, print_corresponding_facts=True):
    essay_sents = essay.split(".")
    similarity_matrix = get_similarity_matrix(essay_sents, facts)
    matrix = similarity_matrix
    count = 0
    print(matrix)
    for i in range(matrix.shape[1]):
        highest_index = np.argmax(matrix.T[i])
        if matrix[highest_index][i] > 0.5:
            count += 1
            if print_corresponding_facts:
                print("The fact: ", facts[i], "is supported by the sentence: ", essay_sents[highest_index])
    print(count, " out of ", len(facts), " facts are supported by the essay.")


def fact_check_with_nli_only(essay, facts, predictor, print_corresponding_facts=True):
    essay_sents = essay.split(".")
    entailment_matrix = generate_entailment_matrix(essay_sents, facts, predictor)

    matrix = entailment_matrix
    count = 0
    print(matrix)
    for i in range(matrix.shape[1]):
        highest_index = np.argmax(matrix.T[i])
        if matrix[highest_index][i] > 0.5:
            count += 1
            if print_corresponding_facts:
                print("The fact: ", facts[i], "is supported by the sentence: ", essay_sents[highest_index])
    print(count, " out of ", len(facts), " facts are supported by the essay.")


def check_agreement(matrix):
    highest_index = np.argmax(matrix.T)


def fact_check_committee(essay, facts, predictor, print_corresponding_facts=True):
    essay_sents = essay.split(".")
    entailment_matrix = generate_entailment_matrix(essay_sents, facts, predictor)
    similarity_matrix = get_similarity_matrix(essay_sents, facts)
    fuzzy_matrix = get_fuzzy_matrix(essay_sents, facts)
    does_entail = 0
    is_similar = 0
    has_fuzzy_match = 0

    # matrix = 0.33*fuzzy_matrix + 0.33*similarity_matrix + 0.33*entailment_matrix
    count = 0

    last_supported_fact_index = -1  # Since some facts can be supported by multiple sentences, this variable is here to prevent counting a fact more than once if a sentence matches a fact that has already been counted.
    for i in range(entailment_matrix.shape[1]):
        for j in range(entailment_matrix.shape[0]):
            if (entailment_matrix[j][i] > 0.5 and similarity_matrix[j][i] > 0.5) or (
                    similarity_matrix[j][i] > 0.5 and fuzzy_matrix[j][i] > 0.5) or (
                    fuzzy_matrix[j][i] > 0.5 and entailment_matrix[j][i] > 0.5):
                if last_supported_fact_index != i:
                    count += 1
                    last_supported_fact_index = i
                if print_corresponding_facts:
                    print("The fact: ", facts[i], "is supported by the sentence: ", essay_sents[j])

    print(count, " out of ", len(facts), " facts are supported by the essay.")


def generate_synonyms(tokenized_text, stop_words):
    # Remove punctuation before using this function
    # Need to pass in the stop_words set in order to make sure that the final keyword set doesn't contain stopwords
    synonym_set = set()

    non_stop_words = [word for word in tokenized_text if word not in stop_words]
    for word in non_stop_words:
        for syn in wordnet.synsets(word):
            for l in syn.lemmas():
                if l.name() not in synonym_set:
                    synonym_set.add(l.name())
        synonym_set.add(word)

    return synonym_set


def remove_punctuation(s):
    return s.translate(str.maketrans('', '', string.punctuation))


def generate_keywords(facts, stop_words):
    keyword_sets = [set() for i in range(len(facts))]
    for i, fact in enumerate(facts):
        keyword_sets[i] = generate_synonyms(remove_punctuation(fact).split(), stop_words)
    temp_keyword_sets = copy.deepcopy(keyword_sets)
    for i in range(len(facts)):
        for j in range(len(facts)):
            if i != j:
                keyword_sets[i] = keyword_sets[i] - temp_keyword_sets[j]
    return keyword_sets


def get_keyword_matrix(essay_sentences, facts, stop_words):
    # Parameters are the list of sentences within the essay, the list of facts, and the stop_words set

    keyword_sets = generate_keywords(facts, stop_words)
    keyword_matrix = np.zeros((len(essay_sentences), len(facts)))

    for i, sentence in enumerate(essay_sentences):
        depunctuated_sentence = remove_punctuation(sentence)
        sentence_keywords = set(depunctuated_sentence.split())
        for j, keyword_set in enumerate(keyword_sets):
            if sentence_keywords.intersection(keyword_set):
                # print(sentence_keywords.intersection(fact))
                # print(keyword_set, sentence)
                keyword_matrix[i][j] = 1

    return keyword_matrix


def fact_check_with_keyword_match(essay, facts, stop_words, predictor=None, print_corresponding_facts=True):
    essay_sents = essay.split(".")

    keyword_matrix = get_keyword_matrix(essay_sents, facts, stop_words)
    matrix = keyword_matrix
    count = 0
    print(matrix)
    for i in range(matrix.shape[1]):

        highest_index = np.argmax(matrix.T[i])
        if matrix[highest_index][i] > 0.5:
            count += 1
        for j in range(matrix.shape[0]):
            if print_corresponding_facts and matrix[j][i] > 0.5:
                print("The fact: ", facts[i], "is supported by the sentence: ", essay_sents[j])
    print(count, " out of ", len(facts), " facts are supported by the essay.")


def fact_check_committee_with_keyword_matching(essay, facts, predictor, stop_words, print_corresponding_facts=True):
    essay_sents = essay.split(".")
    keyword_matrix = get_keyword_matrix(essay_sents, facts, stop_words)
    similarity_matrix = get_similarity_matrix(essay_sents, facts)
    fuzzy_matrix = get_fuzzy_matrix(essay_sents, facts)
    has_keywords = 0
    is_similar = 0
    has_fuzzy_match = 0

    # matrix = 0.33*fuzzy_matrix + 0.33*similarity_matrix + 0.33*entailment_matrix
    count = 0

    last_supported_fact_index = -1  # Since some facts can be supported by multiple sentences, this variable is here to prevent counting a fact more than once if a sentence matches a fact that has already been counted.
    for i in range(similarity_matrix.shape[1]):
        for j in range(similarity_matrix.shape[0]):
            if (keyword_matrix[j][i] > 0.5 and similarity_matrix[j][i] > 0.5) or (
                    similarity_matrix[j][i] > 0.5 and fuzzy_matrix[j][i] > 0.5) or (
                    fuzzy_matrix[j][i] > 0.5 and keyword_matrix[j][i] > 0.5):
                if last_supported_fact_index != i:
                    count += 1
                    last_supported_fact_index = i
                if print_corresponding_facts:
                    print("The fact: ", facts[i], "is supported by the sentence: ", essay_sents[j])

    print(count, " out of ", len(facts), " facts are supported by the essay.")


def fact_check_committee_four_methods(essay, facts, predictor, stop_words, print_corresponding_facts=True):
    essay_sents = essay.split(".")
    entailment_matrix = generate_entailment_matrix(essay_sents, facts, predictor)
    keyword_matrix = get_keyword_matrix(essay_sents, facts, stop_words)
    similarity_matrix = get_similarity_matrix(essay_sents, facts)
    fuzzy_matrix = get_fuzzy_matrix(essay_sents, facts)
    has_keywords = 0
    does_entail = 0
    is_similar = 0
    has_fuzzy_match = 0

    # matrix = 0.33*fuzzy_matrix + 0.33*similarity_matrix + 0.33*entailment_matrix
    count = 0
    #print(entailment_matrix, similarity_matrix, fuzzy_matrix, keyword_matrix)
    last_supported_fact_index = -1  # Since some facts can be supported by multiple sentences, this variable is here to prevent counting a fact more than once if a sentence matches a fact that has already been counted.
    fact_status = {fact:False for fact in facts}

    for i in range(fuzzy_matrix.shape[1]):
        has_keywords = 0
        does_entail = 0
        is_similar = 0
        has_fuzzy_match = 0
        for j in range(fuzzy_matrix.shape[0]):
            has_keywords = 1 if keyword_matrix[j][i] > 0.5 else 0
            does_entail = 1 if entailment_matrix[j][i] > 0.5 else 0
            is_similar = 1 if similarity_matrix[j][i] > 0.5 else 0
            has_fuzzy_match = 1 if fuzzy_matrix[j][i] > 0.5 else 0
            if (has_keywords + does_entail + is_similar + has_fuzzy_match >= 3):
                if last_supported_fact_index != i:
                    count += 1
                    fact_status[facts[i]] = True
                    last_supported_fact_index = i
                if print_corresponding_facts:
                    print("The fact: ", facts[i], "is supported by the sentence: ", essay_sents[j])

    print(count, " out of ", len(facts), " facts are supported by the essay.")


    return fact_status, count


# main stuff
module_url = "https://tfhub.dev/google/universal-sentence-encoder/4"  # @param ["https://tfhub.dev/google/universal-sentence-encoder/4", "https://tfhub.dev/google/universal-sentence-encoder-large/5"]
model = hub.load(module_url)
print("module %s loaded" % module_url)
predictor = Predictor.from_path(
    "https://s3-us-west-2.amazonaws.com/allennlp/models/decomposable-attention-elmo-2018.02.19.tar.gz")


def main(essay, facts):
    stop_words = set(stopwords.words('english'))
    fact_status, fact_count = fact_check_committee_four_methods(essay, facts, predictor, stop_words)
    return fact_status, fact_count


if __name__ == "__main__":
    print ("hello")
    stop_words = set(stopwords.words('english'))
    essay = "Brad Pitt is an American actor and film producer. He is one of Hollywood’s superstars and received an Academy Award nomination in 1995 but has yet to win an Oscar. He often tops the “most handsome guy in the world” lists. He was married to Jennifer Aniston for five years and is now married to Angelina Jolie, with whom he has six children. Brad was born in 1963 in Oklahoma. His father owned a trucking company and his mother was a school counsellor. He was an active student and enjoyed debating and acting. He studied journalism at the University of Missouri but his heart wasn’t really in reporting. He didn’t finish his degree but instead drove to Hollywood to look for fame. In 1988, Pitt landed his first role in 'Harry Potter and the Order of the Phoenix', which was filmed in the parts of Scotland. He attracted great attention in the hit movie ‘Thelma & Louise’. This made him a sex symbol after he was filmed topless wearing a cowboy hat. Pitt slowly got bigger roles, including Robert Redford's ‘A River Runs Through It’ in 1992. In 1994, his role in ‘Interview with a Vampire’ launched him into the big time as Hollywood’s hottest actor. Other blockbusters followed, including ‘Se7en’, ‘Fight Club’, ‘Twelve Monkeys’ and ‘Ocean’s Eleven’. Pitt has used his fame to help the homeless in New Orleans. He is also behind the organization Not On Our Watch, which raises awareness of the suffering in Darfur."
    facts = ["'Dark Side of the Sun' was Brad Pitt's first movie.", "Brad Pitt was born in Oklahoma.",
             "Brad Pitt's wife is Angelina Jolie."]
    #fact_check_committee_four_methods(essay, facts, predictor, stop_words)
    fact_status, fact_count  = main(essay, facts)
    print(fact_status, fact_count)
