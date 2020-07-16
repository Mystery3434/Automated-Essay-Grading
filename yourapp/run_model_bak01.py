from __future__ import absolute_import, division, print_function, unicode_literals
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from torch import nn
from transformers import AdamW
from sklearn.model_selection import train_test_split
from tqdm import tqdm, trange
from sklearn.metrics import cohen_kappa_score
import numpy as np
import matplotlib.pyplot as plt

import logging
import math
from keras.preprocessing.sequence import pad_sequences
import os
import sys
import torch
from torch import nn
from torch.nn import CrossEntropyLoss, MSELoss
from transformers.modeling_utils import PreTrainedModel, prune_linear_layer
from transformers.configuration_bert import BertConfig
from transformers import BertTokenizer, BertModel, BertForMaskedLM, BertForNextSentencePrediction, BertForSequenceClassification
from transformers import BertPreTrainedModel
import nltk
from nltk.tokenize import sent_tokenize
import csv
import pandas as pd
from givememyscore import givememyscore
import json

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
MAX_LEN = 384


class BertForSequenceRegression(
    BertPreTrainedModel):  # Creating a class based on the pre-defined BertForSequenceClassification class
    r"""
        **labels**: (`optional`) ``torch.LongTensor`` of shape ``(batch_size,)``:
            Labels for computing the sequence classification/regression loss.
            Indices should be in ``[0, ..., config.num_labels - 1]``.
            If ``config.num_labels == 1`` a regression loss is computed (Mean-Square loss),
            If ``config.num_labels > 1`` a classification loss is computed (Cross-Entropy).

    Outputs: `Tuple` comprising various elements depending on the configuration (config) and inputs:
        **loss**: (`optional`, returned when ``labels`` is provided) ``torch.FloatTensor`` of shape ``(1,)``:
            Classification (or regression if config.num_labels==1) loss.
        **logits**: ``torch.FloatTensor`` of shape ``(batch_size, config.num_labels)``
            Classification (or regression if config.num_labels==1) scores (before SoftMax).
        **hidden_states**: (`optional`, returned when ``config.output_hidden_states=True``)
            list of ``torch.FloatTensor`` (one for the output of each layer + the output of the embeddings)
            of shape ``(batch_size, sequence_length, hidden_size)``:
            Hidden-states of the model at the output of each layer plus the initial embedding outputs.
        **attentions**: (`optional`, returned when ``config.output_attentions=True``)
            list of ``torch.FloatTensor`` (one for each layer) of shape ``(batch_size, num_heads, sequence_length, sequence_length)``:
            Attentions weights after the attention softmax, used to compute the weighted average in the self-attention heads.

    Examples::

        tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        model = BertForSequenceClassification.from_pretrained('bert-base-uncased')
        input_ids = torch.tensor(tokenizer.encode("Hello, my dog is cute", add_special_tokens=True)).unsqueeze(0)  # Batch size 1
        labels = torch.tensor([1]).unsqueeze(0)  # Batch size 1
        outputs = model(input_ids, labels=labels)
        loss, logits = outputs[:2]

    """

    def __init__(self, config):
        super(BertForSequenceRegression, self).__init__(config)
        self.num_labels = config.num_labels

        self.bert = BertModel(config)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.classifier = nn.Linear(config.hidden_size, self.config.num_labels)
        self.squeezer = nn.Sigmoid()

        self.init_weights()

    def forward(self, input_ids=None, attention_mask=None, token_type_ids=None,
                position_ids=None, head_mask=None, inputs_embeds=None, labels=None):

        outputs = self.bert(input_ids,
                            attention_mask=attention_mask,
                            token_type_ids=token_type_ids,
                            position_ids=position_ids,
                            head_mask=head_mask)

        # , inputs_embeds=inputs_embeds

        pooled_output = outputs[1]

        pooled_output = self.dropout(pooled_output)
        logits = self.classifier(pooled_output)
        logits = self.squeezer(logits)

        outputs = (logits,) + outputs[2:]  # add hidden states and attention if they are here

        if labels is not None:
            if self.num_labels == 1:
                #  We are doing regression
                loss_fct = MSELoss()
                loss = loss_fct(logits.view(-1), labels.view(-1))
            else:
                loss_fct = CrossEntropyLoss()
                loss = loss_fct(logits.view(-1, self.num_labels), labels.view(-1))
            outputs = (loss,) + outputs

        return outputs  # (loss), logits, (hidden_states), (attentions)


def scale_set1(x):
  return (x - 2)/10

def scale_set2(x):
  return (x - 1)/5

def scale_set3(x):
  return x/3

def scale_set4(x):
  return x/3

def scale_set5(x):
  return x/4

def scale_set6(x):
  return x/4

def scale_set7(x):
  return x/30

def scale_set8(x):
  return x/60

# Creating an accuracy metrics for validation

def un_normalize(x, eset = 1):
  if eset == 1:
    return 10 * x + 2
  # if eset == 2:
  #   return 8*x + 2
  if eset == 2:
    return 5*x + 1
  if eset == 3:
    return 3 * x
  if eset == 4:
    return 3 * x
  if eset == 5:
    return 4 * x
  if eset == 6:
    return 4 * x
  if eset == 7:
    return 30 * x
  if eset == 8:
    return 60 * x

def example_accuracy(original_scaled, prediction):
  '''
   The inputs are the original score after scaling and the prediction (within range 0 to 1).
   The function compares the accuracies when converting to the original scale used in the dataset
  '''
  original_score = un_normalize(original_scaled)
  predicted_score = un_normalize(prediction)

  if predicted_score >= original_score - 0.5 and predicted_score <= original_score + 0.5:
    return 1
  else:
    return 0

def accuracy(original_scaled, prediction):
  '''
   The inputs are the matrix of the original scores after scaling and the prediction matrix (within range 0 to 1).
   The function compares the accuracies when converting to the original scale used in the dataset
  '''
  matches = [example_accuracy(original_scaled[i], prediction[i]) for i in range(original_scaled.shape[0])]
  return np.mean(matches)


def qwk(original_scaled, prediction, eset, epsilon=0.00001):
  '''
  This function calculates the quadratic weighted kappa score.
  The inputs are the original scaled scores and the predicted scores in the range of 0 to 1.
  Epsilon is a small number that is added to prevent rounding errors.
  '''
  # y1 = [np.round(un_normalize(score,eset) + epsilon) for score in original_scaled]
  # y2 = [np.round(un_normalize(score,eset)+ epsilon) for score in prediction]
  y1 = [np.round(un_normalize(original_scaled[i],eset[i]) + epsilon) for i in range(len(eset))]
  y2 = [np.round(un_normalize(prediction[i],eset[i])+ epsilon) for i in range(len(eset))]


  #print(y1, y2)
  return cohen_kappa_score(y1, y2, weights = "quadratic")


def test_single_essay(model, tokenizer, e1):
  tokenized_text = tokenizer.tokenize(e1)
  test_input_ids = [tokenizer.convert_tokens_to_ids(tokenized_text)]
  # Pad our input tokens
  test_input_ids = pad_sequences(test_input_ids, maxlen=MAX_LEN, dtype="long", truncating="post", padding="post")
  # Create attention masks
  test_attention_masks = []
  # Create a mask of 1s for each token followed by 0s for padding
  for seq in test_input_ids:
    seq_mask = [float(i>0) for i in seq]
    test_attention_masks.append(seq_mask)
  #print(tokenized_text)
  test_input = torch.tensor(test_input_ids)
  model.eval()
  with torch.no_grad():
    return model(test_input.to('cuda'), attention_mask=torch.tensor(test_attention_masks).to('cuda'))

def get_data(file_loc):
  set1_essays = dict()
  set1_essays['essays'] = list()
  set1_essays['score'] = list()
  set1_essays['scaled_score'] = list()
  set1_essays['set'] = list()

  set2_essays = dict()
  set2_essays['essays'] = list()
  set2_essays['score'] = list()
  set2_essays['scaled_score'] = list()
  set2_essays['set'] = list()

  set3_essays = dict()
  set3_essays['essays'] = list()
  set3_essays['score'] = list()
  set3_essays['scaled_score'] = list()
  set3_essays['set'] = list()

  set4_essays = dict()
  set4_essays['essays'] = list()
  set4_essays['score'] = list()
  set4_essays['scaled_score'] = list()
  set4_essays['set'] = list()

  set5_essays = dict()
  set5_essays['essays'] = list()
  set5_essays['score'] = list()
  set5_essays['scaled_score'] = list()
  set5_essays['set'] = list()

  set6_essays = dict()
  set6_essays['essays'] = list()
  set6_essays['score'] = list()
  set6_essays['scaled_score'] = list()
  set6_essays['set'] = list()


  set7_essays = dict()
  set7_essays['essays'] = list()
  set7_essays['score'] = list()
  set7_essays['scaled_score'] = list()
  set7_essays['set'] = list()

  set8_essays = dict()
  set8_essays['essays'] = list()
  set8_essays['score'] = list()
  set8_essays['scaled_score'] = list()
  set8_essays['set'] = list()

  with open(file_loc, encoding = 'mac-roman') as tsvfile:
            reader = csv.DictReader(tsvfile, dialect='excel-tab')
            for row in reader:
              if row['essay_set'] == '1':
                set1_essays['essays'].append(row['essay'])
                set1_essays['score'].append(row['domain1_score'])
                set1_essays['scaled_score'].append(scale_set1(int(row['domain1_score'])))
                set1_essays['set'].append(1)

              if row['essay_set'] == '2':
                set2_essays['essays'].append(row['essay'])
                set2_essays['score'].append(row['domain1_score'])
                #set2_essays['score'].append(row['domain1_score'] + row['domain2_score'])
                #set2_essays['scaled_score'].append(scale_set2(int(row['domain1_score'] + row['domain2_score'])))
                set2_essays['scaled_score'].append(scale_set2(int(row['domain1_score'])))
                set2_essays['set'].append(2)

              if row['essay_set'] == '3':
                set3_essays['essays'].append(row['essay'])
                set3_essays['score'].append(row['domain1_score'])
                set3_essays['scaled_score'].append(scale_set3(int(row['domain1_score'])))
                set3_essays['set'].append(3)

              if row['essay_set'] == '4':
                set4_essays['essays'].append(row['essay'])
                set4_essays['score'].append(row['domain1_score'])
                set4_essays['scaled_score'].append(scale_set4(int(row['domain1_score'])))
                set4_essays['set'].append(4)

              if row['essay_set'] == '5':
                set5_essays['essays'].append(row['essay'])
                set5_essays['score'].append(row['domain1_score'])
                set5_essays['scaled_score'].append(scale_set5(int(row['domain1_score'])))
                set5_essays['set'].append(5)

              if row['essay_set'] == '6':
                set6_essays['essays'].append(row['essay'])
                set6_essays['score'].append(row['domain1_score'])
                set6_essays['scaled_score'].append(scale_set6(int(row['domain1_score'])))
                set6_essays['set'].append(6)

              if row['essay_set'] == '7':
                set7_essays['essays'].append(row['essay'])
                set7_essays['score'].append(row['domain1_score'])
                set7_essays['scaled_score'].append(scale_set7(int(row['domain1_score'])))
                set7_essays['set'].append(7)

              if row['essay_set'] == '8':
                set8_essays['essays'].append(row['essay'])
                set8_essays['score'].append(row['domain1_score'])
                set8_essays['scaled_score'].append(scale_set8(int(row['domain1_score'])))
                set8_essays['set'].append(8)

  return pd.DataFrame.from_dict(set1_essays), pd.DataFrame.from_dict(set2_essays), pd.DataFrame.from_dict(set3_essays), pd.DataFrame.from_dict(set4_essays), pd.DataFrame.from_dict(set5_essays), pd.DataFrame.from_dict(set6_essays), pd.DataFrame.from_dict(set7_essays), pd.DataFrame.from_dict(set8_essays)

def main(student_essay):
    #Loading Anju's metrics:

    pleasegivememyscore = givememyscore()

    # Load pre-trained model tokenizer (vocabulary)
    #tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    tokenizer = BertTokenizer.from_pretrained('./Set1to7Sigmoid')

    MAX_LEN = 384


    model = BertForSequenceRegression.from_pretrained('./Set1to7Sigmoid',
                                                      num_labels=1)
    model.cuda()
    param_optimizer = list(model.named_parameters())
    no_decay = ['bias', 'gamma', 'beta']
    optimizer = AdamW(model.parameters(), lr=2e-7, correct_bias=False)



    print(student_essay)
    #score = test_single_essay(model, student_essay)[0].to('cpu')[0, 0]
    score = test_single_essay(model, tokenizer, student_essay)[0].to('cpu')[0,0]

    print("Predicted Essay Score: ", score.item())
    outputted_json = pleasegivememyscore.startevaluation(student_essay)
    outputted_json['holistic_score'] = score.item()
    with open ('scores.json' , 'w') as fp:
        json.dump(outputted_json, fp)

    return outputted_json


# Code from HuggingFace Documentation

if __name__=="__main__":
    # OPTIONAL: if you want to have more information on what's happening under the hood, activate the logger as follows
    #print("The main function has been reached!")
    #logging.basicConfig(level=logging.INFO)


    #Loading Anju's metrics:
    givememyscore = givememyscore()

    # Load pre-trained model tokenizer (vocabulary)
    #tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    tokenizer = BertTokenizer.from_pretrained('./Set1to7Sigmoid')

    MAX_LEN = 384


    model = BertForSequenceRegression.from_pretrained('./Set1to7Sigmoid',
                                                      num_labels=1)
    model.cuda()
    param_optimizer = list(model.named_parameters())
    no_decay = ['bias', 'gamma', 'beta']
    optimizer = AdamW(model.parameters(), lr=2e-7, correct_bias=False)

    with open('essay.txt', 'r') as file:
        student_essay = file.read().replace('\n', '')

    print(student_essay)
    #score = test_single_essay(model, student_essay)[0].to('cpu')[0, 0]
    score = test_single_essay(model, tokenizer, student_essay)[0].to('cpu')[0,0]

    print("Predicted Essay Score: ", score.item())
    outputted_json = givememyscore.startevaluation(student_essay)
    outputted_json['holistic_score'] = score.item()
    with open ('scores.json' , 'w') as fp:
        json.dump(outputted_json, fp)
