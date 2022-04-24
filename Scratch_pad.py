from Vetted_Feature_2 import sentence_link_NLI_analysis
import os
from multiprocessing import Pool
import time
import multiprocessing
from functools import partial
from Vetted_Feature_1 import parse_elements, sentence_list
from Vetted_Feature_2 import NLI_assessment
from test_sentences import sentences
import nltk.data
import logging
import torch as t
from transformers import BartForSequenceClassification, BartTokenizer


#print(os.cpu_count())
#sentence_link_NLI_analysis('Canada’s greenhouse gas emissions have increased by 21.4 per cent from 1990 to 2019 and are driven mainly by oil and gas extraction and transport, according to the latest available data from the federal government.','https://www.canada.ca/en/environment-climate-change/services/environmental-indicators/greenhouse-gas-emissions.html')

string_list = ['sasdff', 'success', 'sdfsdfsdfsdf','sdfsdfsd','sdfsdfsdf,','sdfsdfsd','sdfsdfsd','sdfsdfsd','success', 'sdfsdfsd','sdfsdfsd','sdfsdfsd','sdfsdfsd','sdfsdfsd','sdfsdfsd','sdfsdfsd','sdfsdfsd','success']

def if_item_matches(checked, against):
    if checked == against:
        time.sleep(2)
        print('success')
    else:
        time.sleep(2)
        print("not")

import multiprocessing
from multiprocessing import Array

from functools import partial

data_list = [1, 2, 3, 4]



def prod_xy(x,y, z):

    return x * y *z

some_number = 8

another_number = 9

def parallel_runs(data_list, some_variable, another_variable):
    manager = multiprocessing.Manager()
    pool = multiprocessing.Pool(processes=2)
    test_list = manager.list()
    prod_x=partial(prod_xy, y=some_variable, z=another_variable) # prod_x has only one argument x (y is fixed to 10)
    #stopper = manager.join()
    result_list = pool.map(prod_x, data_list)
    #stopper(result_list)
    return (result_list)


def execute_parralel_runs():
    if __name__ == '__main__':
        returned = []
        returned = parallel_runs(data_list, some_number, another_number)
        return returned


'''
if __name__ == '__main__':
    #arr = Array('i', [6,8,10,23])
    something = parallel_runs(data_list, some_number, another_number)
    print(something)
    #manage = multiprocessing.Manager()
    arr = []
    #arr = manage.Array()
    arr.append(something)

print(arr)

'''

variable_one = 8

variable_two = 9





current_prod_xy = partial(prod_xy, y=variable_one, z=variable_two)

'''
if __name__ == "__main__":
    pool = Pool(processes=4)
    returned = pool.map(current_prod_xy, data_list)
    pool.close()
    pool.join()
    outside = returned
'''
#below is where it's at and you finally figured it out!!
'''
def cube(x):
    print(f"start process {x}")
    result = x * x * x
    time.sleep(1)
    print(f"end process {x}")
    return result

returned = []

if __name__ == "__main__":
    pool = Pool(processes=4)
    returned = pool.map(cube, range(5))
    pool.close()
    pool.join()
    print(returned)

print(returned)

'''
'''
paragraphs = parse_elements('https://www.inc.com/magazine/202111/scott-eden/al-kahn-pokemon-yu-gi-oh-cabbage-patch-kids.html','p')

test_sentences = []

for paragraph in paragraphs:
    current_sentences = sentence_list(paragraph.text)
    test_sentences.append(current_sentences)
    print(test_sentences)
print(test_sentences)
'''

#below is the code that proved that multiprocessing offers no advantage over serial processing

'''
getting_models_start = time.time()
nli_tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-mnli')
nli_model = BartForSequenceClassification.from_pretrained('facebook/bart-large-mnli')
getting_models_end = time.time()

tested_against = 'I tried to implement fizz-buzz. It is an ongoing process and it seems not to have worked this time. I will continue testing to see if it works.'

#serial runs test
returned_serial_list = []
serial_processing_start = time.time()
for item in sentences:
    current_analysis = NLI_assessment(item,tested_against,nli_model,nli_tokenizer)
    returned_serial_list.append(current_analysis)
print(returned_serial_list)
serial_processing_end = time.time()
print(f'serial processing took {serial_processing_end-serial_processing_start}')







#parralell runs test

#first you need to rig a version of NLI_Assessment that is fixed for the model, tested_against, and the tokenizer
parrallel_NLI = partial(NLI_assessment,string_2=tested_against,model=nli_model,tokenizer=nli_tokenizer)


returned_analysis = []
parralel_processing_start = time.time()
if __name__ == "__main__":
    pool = Pool(processes=3)
    returned_analysis = pool.map(parrallel_NLI, sentences)
    pool.close()
    pool.join()
    print(returned_analysis)
parralel_processing_end = time.time()

print(f'getting set up with the AI tools took {getting_models_end-getting_models_start}')
print(f'serial processing took {serial_processing_end-serial_processing_start}')
print(f'parralel processing took {parralel_processing_end-parralel_processing_start}')
'''



