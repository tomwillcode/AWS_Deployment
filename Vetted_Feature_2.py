#import torch as t
#import time
#from transformers import BartForSequenceClassification, BartTokenizer
#tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-mnli')
#model = BartForSequenceClassification.from_pretrained('facebook/bart-large-mnli')
from requests_html import HTMLSession
import pandas as pd
from urllib.parse import urlparse
import numpy as np
#import nltk.data
import logging
from vetted_secrets import GOOGLE_API_KEY
import google.generativeai as genai
#logger = logging.getLogger(__name__)

#must use nltk.download('punkt')
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')


#as used in feature 1 gets all elements of a specified type from a URL
def parse_elements(url,element):
    #logger.info('parse elements started')

    session = HTMLSession()
    r = session.get(url)
    #r.html.render()
    paragraphs = r.html.find(element)
    return paragraphs

#breaks a paragraph as string down into a list of sentence/strings from paragraph


#takes a sentence and a url and compares the input sentence to every single sentence in the linked URL using NLI to see if they are in agreement or if there is missing context or misrepresentation.
def sentence_link_NLI_analysis(sentence, link):
    try:
        text = parse_elements(link, 'body')
        text = text[0].text
        try:
            contradictory_information = model.generate_content(
                'In the following task you will be given a paragraph and an article that the paragraph is citing. Your job is to find missing context in the article that has been left out of the paragraph. In your response you should just return sentences from the article that include that extra missing context, and if no such sentences are found you could return nothing. Here is the paragraph: > ' + sentence +

                ' and here is the article: > '

                + text)
            contradictory_information = [i for i in contradictory_information.text.split('**').pop().split('\n') if len(i) > 1]
        except Exception:
            contradictory_information = []
        try:
            supporting_information = model.generate_content(
                'In the following task you will be given a paragraph and an article that the paragraph is citing. Your job is to find supporting statements in the article that back up what the paragraph is saying. In your response you should just return sentences from the article that support the claims in the paragraph, and if no such sentences are found you could return nothing. Here is the paragraph: > ' + sentence +

                ' and here is the article: > '

                + text)
            supporting_information = [i for i in supporting_information.text.split('**').pop().split('\n') if len(i) > 1]
        except Exception:
            supporting_information = []
    except Exception:
        contradictory_information = []
        supporting_information = []
    returned_dictionary = {}
    returned_dictionary['contradictions'] = contradictory_information
    returned_dictionary['entailments'] = supporting_information
    return(returned_dictionary)




def deep_dive_all_links(DF1):
    #logger.info('deep dive all links started')

    #first establish the first column to iterate through
    column_variable = 1
    working_column = 'Link ' + (str(column_variable))
    working_sentence_column = 'Paragraph Text'
    #Have for loop that goes through all the columns
    for column in range(0,(DF1.shape[1])):
    #check if the column exists, if not then it is safe to return DF1 in its current state
        if working_column in DF1:
    #THEN go into for loop going down through all rows in that column
            for row in range(0, (DF1.shape[0])):
    #check if the cell has contents: (Because the NaN values are floats, and the <a> element will never be a float.)
                #if pd.isnull(DF1.loc[row,[working_column]])==False: <- another if test that throws an error.
                if (type(DF1.iloc[row][working_column]))!=float:
                #grab href from the cell as string
                    href = (list((DF1.iloc[row][working_column]).links).pop())
                    #logger.info(href)
                    #href = str((DF1.iloc[row][working_column]).links)
                    #grab sentence that contains that href also in string form
                    current_sentence = (DF1.iloc[row][working_sentence_column])
                    #NOW GO INTO Transformers
                    try:
                        #logger.info("new deep dive")
                        current_deep_dive = sentence_link_NLI_analysis(current_sentence, href)
                    except Exception:
                        #logger.info("exception handled for current deep dive")
                        current_deep_dive = {'contradictions':[],'entailments':[]}
                    #code built into the above function will cause it to skip any errors and return a dictionary with "None" types if errors happen inside that function
                    #down below cells will be updated with None types in the event that the NLI analysis runs into an error.
                    #an alternative strategy would be to go for error handling below, so that the cells aren't updated at all if the NLI analysis ran into an error and had to pass.
                    #such errors for the NLI analysis are generally due to things like string length.
                    DF1.at[row, working_column + ' potential contradictions or missing context'] = current_deep_dive['contradictions']
                    DF1.at[row, working_column + ' supporting statements'] = current_deep_dive['entailments']
                    #DF1.loc[row, [working_column + ' potential contradictions or missing context']]= current_deep_dive['contradictions']
                    #DF1.loc[row, [working_column + ' supporting statements']] = current_deep_dive['entailments']
                #if the cell has no <a> element it is safe to continue looping through the rows in the current working column
                else:
                    continue
            #now after making it through that for loop update the current working_column to keep moving through them until every single column containing an <a> has been checked
            column_variable = (column_variable+1)
            working_column = 'Link ' + (str(column_variable))
            #working_sentence_column = 'Link ' + (str(column_variable)) + ' sentence'
        #after going through all columns that contain links, the data_frame will be returned with all links classified appropriately
        else:
            return DF1





'''
import torch as t
import time
from transformers import BartForSequenceClassification, BartTokenizer
#tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-mnli')
#model = BartForSequenceClassification.from_pretrained('facebook/bart-large-mnli')
from requests_html import HTMLSession
import pandas as pd
from urllib.parse import urlparse
import numpy as np
import nltk.data
import logging
logger = logging.getLogger(__name__)

#must use nltk.download('punkt')
tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-mnli')
model = BartForSequenceClassification.from_pretrained('facebook/bart-large-mnli')



def NLI_assessment(string_1, string_2, model, tokenizer):
#    logger.info("Model Prediction Started")
    #nli_start_time = time.time()
    #start = time.time()
    #tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-mnli')
    #stop = time.time()
    #print("tokenizer definition takes")
    #print(start-stop)
    #start = time.time()
    #model = BartForSequenceClassification.from_pretrained('facebook/bart-large-mnli')
    #stop = time.time()
    #print("model definition takes")
    #print(start - stop)
    #start = time.time()
    device = "cuda:0" if t.cuda.is_available() else "cpu"
    model = model.to(device)
    #stop = time.time()
    #print("setting the device takes")
    #print(start - stop)
    #start = time.time()
    input_ids = tokenizer.encode(string_1, string_2, return_tensors='pt').to(device)
    #stop = time.time()
    #print("tokenizing the strings takes")
    #print(start - stop)
    #input_ids = tokenizer.encode(string_1, string_2, return_tensors='pt')
    try:
        #start = time.time()
        logits = model(input_ids)[0]
        #stop = time.time()
        #print("running the tokenized strings through the model takes")
        #print(start - stop)

        #start = time.time()
        probability_vector = logits.softmax(dim=1)
        #stop = time.time()
        #print("giving the probability vector to softmax to get proper probabilities takes")
        #print(start - stop)
        #nli_end_time = time.time()
        #print("total NLI_assessment time was")
        #print(nli_start_time-nli_end_time)
        NLI_probabilities = {}
        NLI_probabilities["contradiction"] = probability_vector[:,0].item()
        NLI_probabilities["neutral"] = probability_vector[:, 1].item()
        NLI_probabilities["entail"] = probability_vector[:, 2].item()
    except Exception:
        Null_dic = {"contradiction":None,"neutral":None,"entail":None}
        return Null_dic
    return NLI_probabilities


#as used in feature 1 gets all elements of a specified type from a URL
def parse_elements(url,element):
#    logger.info('parse elements started')

    session = HTMLSession()
    r = session.get(url)
    #r.html.render()
    paragraphs = r.html.find(element)
    return paragraphs

#breaks a paragraph as string down into a list of sentence/strings from paragraph
def sentence_list(paragraph_string):
#    logger.info('sentence list started')

    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    list_of_sentences = tokenizer.tokenize(paragraph_string)
    return list_of_sentences

#takes a list of <p> elements and returns a list of sentence/strings in order from first to last.
def p_as_sentence_list(paragraphs_list):
#    logger.info('p as sentence list started')

    returned_list = []
    for paragraph in paragraphs_list:
        paragraph_text = paragraph.text
        paragraph_tokenized = sentence_list(paragraph_text)
        returned_list.extend(paragraph_tokenized)
    return returned_list


#takes a sentence and a url and compares the input sentence to every single sentence in the linked URL using NLI to see if they are in agreement or if there is missing context or misrepresentation.
def sentence_link_NLI_analysis(sentence, link):
#    logger.info('sentence link NLI analysis')

    paragraphs = parse_elements(link,'p')
    sentences = p_as_sentence_list(paragraphs)
    contradictions_list =[]
    entailments_list =[]
    refined_contradictions_list =[]
    returned_dictionary = {}
    #tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-mnli')
    #model = BartForSequenceClassification.from_pretrained('facebook/bart-large-mnli')
    for item in sentences:
        #getting an error for an empty set the model doesn't want that. Hence len > 0
        if len(item) > 0:
            try:
                current_assessment = NLI_assessment(sentence, item, model, tokenizer)
                current_assessment['item'] = item
                #now two IF statements will see if the current "item" meets the threshold for contradiction or entailment with the citing sentence
                if current_assessment['contradiction'] >= (2/3):
                    contradictions_list.append(item)
                if current_assessment['entail'] >= (2/3):
                    entailments_list.append(item)
            except Exception:
                pass
        else:
            continue
    #next a for loop to deal with the high rate of type 1 errors re: false contradictions. Feeding the two strings to the model in reverse order should do a good job of eliminating false contradictions and keeping true contradictions
    for contradiction in contradictions_list:
        revised_assessment = NLI_assessment(contradiction, sentence, model,tokenizer)
        if revised_assessment['contradiction'] >= (2/3):
            refined_contradictions_list.append(contradiction)
    #all true contradictions should be appended to a "true contradictions" list
    returned_dictionary['contradictions'] = refined_contradictions_list
    returned_dictionary['entailments'] = entailments_list
    print(returned_dictionary)
#    logger.info(returned_dictionary)
    return(returned_dictionary)




def deep_dive_all_links(DF1):
#    logger.info('deep dive all links started')

    #first establish the first column to iterate through
    column_variable = 1
    working_column = 'Link ' + (str(column_variable))
    working_sentence_column = 'Link ' + (str(column_variable)) + ' sentence'
    #Have for loop that goes through all the columns
    for column in range(0,(DF1.shape[1])):
    #check if the column exists, if not then it is safe to return DF1 in its current state
        if working_column in DF1:
    #THEN go into for loop going down through all rows in that column
            for row in range(0, (DF1.shape[0])):
    #check if the cell has contents: (Because the NaN values are floats, and the <a> element will never be a float.)
                #if pd.isnull(DF1.loc[row,[working_column]])==False: <- another if test that throws an error.
                if (type(DF1.iloc[row][working_column]))!=float:
                #grab href from the cell as string
                    href = (list((DF1.iloc[row][working_column]).links).pop())
                   # logger.info(href)
                    #href = str((DF1.iloc[row][working_column]).links)
                    #grab sentence that contains that href also in string form
                    current_sentence = (DF1.iloc[row][working_sentence_column])
                    #NOW GO INTO Transformers
                    try:
                       # logger.info("new deep dive")
                        current_deep_dive = sentence_link_NLI_analysis(current_sentence, href)
                    except Exception:
                       # logger.info("exception handled for current deep dive")
                        current_deep_dive = {'contradictions':[],'entailments':[]}
                    #code built into the above function will cause it to skip any errors and return a dictionary with "None" types if errors happen inside that function
                    #down below cells will be updated with None types in the event that the NLI analysis runs into an error.
                    #an alternative strategy would be to go for error handling below, so that the cells aren't updated at all if the NLI analysis ran into an error and had to pass.
                    #such errors for the NLI analysis are generally due to things like string length.
                    DF1.at[row, working_column + ' potential contradictions or missing context'] = current_deep_dive['contradictions']
                    DF1.at[row, working_column + ' supporting statements'] = current_deep_dive['entailments']
                    #DF1.loc[row, [working_column + ' potential contradictions or missing context']]= current_deep_dive['contradictions']
                    #DF1.loc[row, [working_column + ' supporting statements']] = current_deep_dive['entailments']
                #if the cell has no <a> element it is safe to continue looping through the rows in the current working column
                else:
                    continue
            #now after making it through that for loop update the current working_column to keep moving through them until every single column containing an <a> has been checked
            column_variable = (column_variable+1)
            working_column = 'Link ' + (str(column_variable))
            working_sentence_column = 'Link ' + (str(column_variable)) + ' sentence'
        #after going through all columns that contain links, the data_frame will be returned with all links classified appropriately
        else:
            return DF1

''' 
