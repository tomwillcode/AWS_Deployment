#consolidated programs for Feature 1 V1
#first import what is needed
#from requests_html import HTMLSession
import pandas as pd
from urllib.parse import urlparse
import numpy as np
import nltk.data
#this library offers tools for scraping and parsing URL's. I like a lot of the built in functions for requests_html
from requests_html import HTMLSession
#import logging
#logger = logging.getLogger(__name__)
#nltk.download('punkt')
#nltk.download('punkt_tab')



#this function takes in any URL in string form as the first argument
#for the second argument it takes any given element in string form
#the function then scrapes everyone of the specified elements out of the URL and returns them in a list
#All elements and attributes within each element in the list are retained and accessible.
#For the purposes of Feature 1 this will tend to be used to scrape out <p> elements from an article, by taking in the article URL
#this function will need some exception handling added that it doesn't currently have. There are funny URL's out there that can't be scraped.
def parse_elements(url,element):
#    logger.info('parse elements started')
    session = HTMLSession()
    r = session.get(url)
    #r.html.render()
    paragraphs = r.html.find(element)
    return paragraphs

#takes a paragraph as string and breaks it down into sentences
def sentence_list(paragraph_string):
#    logger.info('sentence list started')
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    list_of_sentences = tokenizer.tokenize(paragraph_string)
    return list_of_sentences


#need a function to convert the list of links to a list of the text strings covered by the link
#this will take the list of links obtained using the requests.html function for getting the ordered list out of the <p> element
def links_as_text(link_list):
#    logger.info('Links as text started')
    text_list = []
    #go into for loop going through all the <a> elements in the list
    for link in link_list:
        #grab the text contained within the <a> element and add it to the list seeing that they all remain in order
        text_list.append(link.text)
        #when done return the list
    return text_list

#this function will take the list of links in text form.
#this function will also take the list of sentences that make up the paragraph
#This function returns a list of the sentences in order such that a sentence is assigned to each link
#In some cases the same sentence will contain multiple links, so it will appear in consecutive order in the list for each link in the sentence
#While-loop I hope will avoid some pitfalls that could slow this algorithm down otherwise
def return_hyperlink_sentences(link_text_list, text_sentence_list):
#    logger.info('return hyperlink sentences started')
    #create the list that will eventually be returned
    linked_sentences_list = []
    #setup two separate variables to iterate through links and sentences in an efficient manner
    sentence_variable = 0
    link_variable = 0
    #go into while loop that goes through the full list of the hyperlinks as text
    while link_variable < (len(link_text_list)):
        #check if the sentence contains the link
        if link_text_list[link_variable] in text_sentence_list[sentence_variable]:
            #if so add that sentence to the list and update the link variable in order to check the next link
            linked_sentences_list.append(text_sentence_list[sentence_variable])
            link_variable = link_variable + 1
        else:
            #in the event that the sentence doesn't contain a link move to the next sentence
            sentence_variable = sentence_variable + 1
    return linked_sentences_list


#this function builds the dataframe and ensures that it is an appropriate size, with columns labelled appropriately
#it takes the list of <p> elements as input and then builds a properly labeled dataframe that will accomodate those elements
#this function makes sure that there are enough columns to store the max number of links seen in any given <p> element
#the key issue is what is the max number of hyperlinks in a given paragraph? This program counts them up and adds sufficient columns
#the column naming is of course standardized. Late on a hash or some kind of identifier ought to be added here, so that every dataframe for every article has a unique name or way to identify it
def build_data_frame(paragraphs):
#    logger.info('build data frame started')
    columns = ['Paragraph', 'Paragraph Text']
    max_links = 0
    for paragraph in paragraphs:
        paragraph_links = len(paragraph.find('a'))
        if paragraph_links > max_links:
            max_links = paragraph_links
        else:
            continue
    for i in range(max_links):
        columns.append('Link ' + str(i + 1))

    for i in range(max_links):
        columns.append('Link ' + str(i + 1) + ' text')

    for i in range(max_links):
        columns.append('Link ' + str(i + 1) + ' sentence')

    for i in range(max_links):
        columns.append('Link ' + str(i + 1) + ' source type')

    for i in range(max_links):
        columns.append('Link ' + str(i + 1) + ' domain type')

    for i in range(max_links):
        columns.append('Link ' + str(i + 1) + ' domain restrictions')

    for i in range(max_links):
        columns.append('Link ' + str(i + 1) + ' potential contradictions or missing context')

    for i in range(max_links):
        columns.append('Link ' + str(i + 1) + ' supporting statements')

    paragraphs_data_frame = pd.DataFrame(index=range(len(paragraphs)),
                                   columns=columns)
    return paragraphs_data_frame


#this function fills the dataframe with appropriate data that has been scraped from the article URL
#this function ensures that the right <a> elements get scraped out and paired with the right <p> elements in the dataframe
#this function finds all the <a> elements in each <p> element and adds them to the row for that <p> element
#It takes the extracted <p> elements and the dataframe created by previous function as arguments.

def fill_data_frame(paragraphs, paragraphs_data_frame):
#    logger.info('fill data frame started')
    # 0 Set row number to 0
    working_row = 0
    # 1 for-loop for paragraph in paragraphs to iterate through them all
    for paragraph in paragraphs:
        # 2 update column 1 with <p> element
        paragraphs_data_frame.loc[working_row, ['Paragraph']] = [paragraph]
        # 3 update column 2 with <p> element as text
        paragraphs_data_frame.loc[working_row, ['Paragraph Text']] = [paragraph.text]
        # 4 place all <a> elements from current <p> element in an object "Links."
        try:
            working_links = ((paragraphs[working_row]).find('a'))
            #4.a) now place each sentence associated with each <a> element in a list where they are ordered from first <a> to last <a>
            text_sentences = sentence_list(paragraph.text)
            print(text_sentences)
            working_links_text = links_as_text(working_links)
            print("here is the current list of text with links attached")
            print(working_links_text)
            working_links_sentences = return_hyperlink_sentences(working_links_text,text_sentences)
            # 5 set column variable to column 3 to start adding <a> elements to that column
            column_variable = 1
            working_column = 'Link ' + (str(column_variable))
            # 6 set additional column variable to fill in the text version of the links
            working_text_column = 'Link ' + (str(column_variable)) + ' text'
            #6.a) set additional column variable to fill in the sentence that contains each link
            working_sentence_column = 'Link ' + (str(column_variable)) + ' sentence'
        except Exception:
            pass
        # 7 iterate through "Links" with a for loop: for link in links

        for link in working_links:
            try:
                # 8 update the cell with hyperlink
                paragraphs_data_frame.loc[working_row, [working_column]] = [link]
                # 9 update the cell with hyperlink in text version
                paragraphs_data_frame.loc[working_row, [working_text_column]] = [link.text]
                #9.a update the cell with the sentence that contains the current hyperlink
                paragraphs_data_frame.loc[working_row, [working_sentence_column]] = [working_links_sentences[(column_variable-1)]]
                # 10 update column variable.
                column_variable = (column_variable + 1)
                working_column = 'Link ' + (str(column_variable))
                # 11 update text column variable
                working_text_column = 'Link ' + (str(column_variable)) + ' text'
                # 11.a) update sentence column variable
                working_sentence_column = 'Link ' + (str(column_variable)) + ' sentence'
            except Exception:
                pass
        # now update working row
        working_row = (working_row + 1)
    return paragraphs_data_frame

#Classify URL's in DF by their parameters
#URL_Classify_Dataframe = pd.read_csv(r'C:\Users\musar\PycharmProjects\Sharpminds2021DW\Sources database.csv')
URL_Classify_Dataframe = pd.read_csv(r'Sources database.csv')

# need a function to take string version of href as input, iterate through URL_Classify_Dataframe, and classify domains and urls from the current article appropriately
def classify_href(href, classify_what, by):
#    logger.info('classify href started')
    for row in range(0, (URL_Classify_Dataframe.shape[0])):
        if str(URL_Classify_Dataframe.iloc[row][classify_what]) in href:
            return URL_Classify_Dataframe.iloc[row][by]
        else:
            continue


#the DF storing all data for the article the user is reading goes into this function, and the DF is updated with info pertaining to the hyperlinks in the article
def classify_all_links(DF1):
#    logger.info('classify all links started')
    #first establish the first column to iterate through
    column_variable = 1
    working_column = 'Link ' + (str(column_variable))
    #Have for loop that goes through all the columns
    for column in range(0,(DF1.shape[1])):
    #check if the column exists, if not then it is safe to return DF1 in its current state
        if working_column in DF1:
    #THEN go into for loop going down through all rows in that column
            for row in range(0, (DF1.shape[0])):
    #check if the cell has contents:
                #if pd.isnull(DF1.loc[row,[working_column]])==False:
                if (type(DF1.iloc[row][working_column]))!=float:
                #grab href from the cell as string
                    href = str((DF1.iloc[row][working_column]).links)
                    #now recruit function that sees if that string has a match in the URL_Classify_Dataframe
                    #this function classifies the url and domain if it can, and updates the appropriate columns in DF1
                    DF1.loc[row, [working_column + ' source type']]= classify_href(href,'URL','Source Type')
                    DF1.loc[row, [working_column + ' domain type']] = classify_href(href, 'Domain', 'Domain Type')
                    DF1.loc[row, [working_column + ' domain restrictions']] = classify_href(href, 'Domain', 'Domain Restrictions')
                #if the cell has no contents it is safe to continue looping through the rows in the current working column
                else:
                    continue
            #now after making it through that for loop update the current working_column to keep moving through them until every single column containing an <a> has been checked
            column_variable = (column_variable+1)
            working_column = 'Link ' + (str(column_variable))
        #after going through all columsn that contain links, the data_frame will be returned with all links classified appropriately
        else:
            return DF1


def Feature_1_analysis(url):
#    logger.info('feature 1 analysis started')
    paragraphs = parse_elements(url, 'p')
    dataframe = build_data_frame(paragraphs)
    dataframe = fill_data_frame(paragraphs, dataframe)
    dataframe = classify_all_links(dataframe)
    return dataframe

#dataframe = Feature_1_analysis('https://www.theatlantic.com/ideas/archive/2021/12/nba-nfl-surrendered-vaccine-refusers-kyrie-irving/621142/')

#print(dataframe)

#dataframe.to_csv('newomicrontestIII.csv')
#from Feature_2_trial import deep_dive_all_links

#dataframe = deep_dive_all_links(dataframe)




#dataframe.to_csv('newglobaltestIV.csv')

#from Vetted_DB_Access_Methods import add_info_to_db
#add_info_to_db(dataframe, 'https://www.theatlantic.com/ideas/archive/2021/12/nba-nfl-surrendered-vaccine-refusers-kyrie-irving/621142/')
