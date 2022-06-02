from Vetted_Feature_2 import sentence_link_NLI_analysis
import os
from multiprocessing import Pool
import time
import multiprocessing
from functools import partial
from Vetted_Feature_1 import parse_elements, sentence_list
from Vetted_Feature_2 import NLI_assessment
from test_sentences import sentences
import nltk
nltk.download('punkt')
import nltk.data
import logging
import torch as t
from transformers import BartForSequenceClassification, BartTokenizer


print("beginning test of parse elements")
print(parse_elements("https://globalnews.ca/news/8883112/bank-of-canada-june-1-decision/","p" ))

print("testing tokenizer download")
tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-mnli')
print("testing model download")
model = BartForSequenceClassification.from_pretrained('facebook/bart-large-mnli')

print("tests passed")
print("nli test")


#print(os.cpu_count())
#sentence_link_NLI_analysis('Canada’s greenhouse gas emissions have increased by 21.4 per cent from 1990 to 2019 and are driven mainly by oil and gas extraction and transport, according to the latest available data from the federal government.','https://www.canada.ca/en/environment-climate-change/services/environmental-indicators/greenhouse-gas-emissions.html')


sentence = "“With the economy in excess demand, and inflation persisting well above target and expected to move higher."
item = "he did not say hello world!"

link = "https://www.bankofcanada.ca/2022/06/fad-press-release-2022-06-01/"

print("beginning nli")

print(NLI_assessment(sentence, item, model, tokenizer))
print("nli test passed")

