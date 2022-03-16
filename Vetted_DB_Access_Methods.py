import pandas as pd
import sqlite3
from flask import Flask, render_template, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from Vetted_DB_Config import secret_key, Vetted_DB_URI_Connection
from Vetted_Feature_1 import Feature_1_analysis
from Vetted_Feature_2 import deep_dive_all_links
from sqlalchemy.orm import relationship
#from flask.ext.sqlalchemy import SQLAlchemy
#will forms be needed? Difficult to say.
#from forms import RegistrationForm, LoginForm
app = Flask(__name__)
#app.debug = True
app.config['SECRET_KEY'] = secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = Vetted_DB_URI_Connection
#app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

'''
For the time being the Vetted chrome extension is powered by a fairly simple database. 
There are two tables. One for "Articles" and one for "Citations".
The idea is that a given "Article" that needs to be vetted has many "Citations" associated with it.
Thus every Citation has a foreign key linking it to the primary key of the parent "Article." 
'''



#model for the two main SQL tables for this apps DB are what follows.

class Articles(db.Model):
    __tablename__ = 'Articles'
    id = db.Column(db.Integer, primary_key=True)
    article_url = db.Column(db.Text, unique=False, nullable=False)
    citations = db.relationship('Citations', backref='article')
    def __repr__(self):
        return f"Links('{self.article_url}')"

    def __init__(self, article_url):
        self.article_url = article_url

#You can change the string type into a "text" type which will be more flexible for what it contains. That is string length.
class Citations(db.Model):
    __tablename__ = 'Citations'
    id = db.Column(db.Integer, primary_key=True)
    citation_url = db.Column(db.String(2000), unique=False, nullable=False)
    citation_text = db.Column(db.String(2000), unique=False, nullable=False)
    citation_source_type = db.Column(db.String(500), unique=False, nullable=False)
    citation_domain_type = db.Column(db.String(500), unique=False, nullable=False)
    citation_domain_restrictions = db.Column(db.String(500), unique=False, nullable=False)
    citation_contradictions = db.Column(db.Text, unique=False, nullable=False)
    citation_support = db.Column(db.Text, unique=False, nullable=False)
    article_url = db.Column(db.String(2000), unique=False, nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('Articles.id'), unique=False)

    def __repr__(self):
        return f"Links('{self.article_url}')"

    def __init__(self, citation_url, citation_text, citation_source_type, citation_domain_type, citation_domain_restrictions, citation_contradictions, citation_support, article_url, article):
        self.citation_url = citation_url
        self.citation_text = citation_text
        self.citation_source_type = citation_source_type
        self.citation_domain_type = citation_domain_type
        self.citation_domain_restrictions = citation_domain_restrictions
        self.citation_contradictions = citation_contradictions
        self.citation_support = citation_support
        self.article_url = article_url
        self.article = article



db.create_all()




#this function is used to add the URL for a given article to the articles table.
def add_article_to_db(url):
    current = Articles(article_url=url)
    db.session.add(current)
    db.session.commit()
'''
The following function takes all the information for a given citation in a given article and adds it to a new row in the citations-table.
The parent articles primary key is added as a foreign key for the citation/row. 
'''
def add_citations_to_db(url,text,source,domain,restrictions,contradictions,support,linked_article):
    current = Citations(citation_url= url, citation_text = text, citation_source_type = source, citation_domain_type = domain, citation_domain_restrictions = restrictions, citation_contradictions = contradictions, citation_support = support, article_url = linked_article, article = Articles.query.filter_by(article_url=linked_article).first())
    db.session.add(current)
    db.session.commit()

'''
The below functions are all used for getting information from either the articles or citations table. 
Some search by the URL others search using a key. Some get all results with the given key, some get the first.
'''

def query_articles_table(url):
    query = Articles.query.filter_by(article_url=url).first()
    return query

def query_citations_table(url):
    query = Citations.query.filter_by(article_url=url).first()
    return query

def get_all_citations(url):
    query = Citations.query.filter_by(article_url=url).all()
    return query

def query_articles_table_ID(ID):
    query = Articles.query.filter_by(id=ID).first()
    return query

def query_citations_table_ID(ID):
    query = Citations.query.filter_by(id=ID).first()
    return query


def check_db_connection():
    checks = 1
    while checks < 3:
        try:
            test = query_articles_table_ID(1)
            print("result of connection test")
            print(test)
        except Exception:
            checks = checks + 1



#This function that takes every string in a list and simply makes a massive string out of all those strings. The elements are now separated by a unique substring 35284777
#This is because some versions of SQL don't want a list stored in a cell. I feel it will be more robust to store the list as a string. Store it as "Text" to be exact.
#When the elements from the string need to be accessed again one can simply split the string up according to the unique substring "35284777" that separates them.
def add_list_as_string(current_cell):
    returned_string = " "
    if ((type(current_cell)) == list) and (len((current_cell)) > 0):
        current_list = (current_cell)
        for element in current_list:
            returned_string = returned_string + element + "35284777"
    else:
        returned_string = 'None Found'
    return returned_string

'''
The following function takes all the info from a fully vetted article. It takes the pandas dataframe that has the results of the feature 1 and feature 2 analysis.
This function iterates through the relevant information for each citation attached to the current parent article.
This function adds the information related to a given citation into the appropriate columns for each piece of information, and it does this row by row, (citation by citation).
Basically this gets recruited at the end of both F1 and F2 analyses to add all the resulting data to the database. 
'''

def add_info_to_db(DF1, article_url):
    #first determine how many columns you must iterate through
    column_variable = 1
    column_list = []
    #While loop determines how many columns
    while (('Link ' + (str(column_variable))) in DF1) == True:
        column_list.append(column_variable)
        column_variable = column_variable + 1
    #next part is for-loops to do the necessary work of adding data to DB

    #for loop going down through all rows will be necessary now + for loop for each column while @ each row
    for row in range(0, (DF1.shape[0])):
    #now go through columns
        for column in column_list:
            working_column = 'Link ' + (str(column))
                #basically the NaN's are floats, just make sure that is false, and then it is verified that cell contains a link
                #if pd.isnull(DF1.loc[row,[working_column]])==False:
            if (type(DF1.iloc[row][working_column]))!=float:
                #grab the citation URL/HREF
                    href = str(list((DF1.iloc[row][working_column]).links).pop())
                #grab text within the <a> element as a string
                    text = ((DF1.iloc[row][working_column]).text)
                    '''
                    the following functions take the list of contradictions and supporting statements for the current citation and convert the lists
                    to strings. These strings will be stored in the SQL table with each element from the original lists separated by a unique substring. This is more robust than storing as a list I believe.
                    '''
                    current_contradictions = DF1.iloc[row][working_column + ' potential contradictions or missing context']
                    contradictions = add_list_as_string(current_contradictions)
                    current_supporting = DF1.iloc[row][working_column + ' supporting statements']
                    supporting = add_list_as_string(current_supporting)

                    #The next set of algorithms simply see's how citations were classified according to feature 1's rules based system.
                    source_type = ""
                    if (type(DF1.iloc[row][working_column + ' source type'])) == str:
                        source_type = (DF1.iloc[row][working_column + ' source type'])
                    else:
                        source_type = "Could not classify."
                    domain_type = ""
                    if (type(DF1.iloc[row][working_column + ' domain type'])) == str:
                        domain_type = (DF1.iloc[row][working_column + ' domain type'])
                    else:
                        domain_type = "Could not classify."
                    domain_restrictions = ''
                    if (type(DF1.iloc[row][working_column + ' domain restrictions'])) == bool:
                        domain_restrictions = str(DF1.iloc[row][working_column + ' domain restrictions'])
                    else:
                        domain_restrictions = 'Could not determine.'

                    #here we shall recruit the function to update the database.
                    print("information to be added for the current citation:")
                    print(href)
                    checks = 1
                    while checks < 5:
                        try:
                            add_citations_to_db(href, text, source_type, domain_type, domain_restrictions, contradictions, supporting, article_url)
                            print("info added for proceeding citation")
                            checks = 6
                        except:
                            Exception
                            print("citations not added trying again")
                            checks = checks + 1
            #if the cell has no contents it is safe to continue looping through the rows in the current working column
            else:
                continue
            #now after making it through that for loop update the current working_column to keep moving through them until every single column containing an <a> has been checked

        #after going through all columsn that contain links, the data_frame will be returned with all links classified appropriately

           #If the column is not in the DB it's safe to end this process. The DB has been updated

'''
This next function grabs all the information for every citation/row for a given article that a user would like to Vett.
It grabs the information in the form a list that can be sent to the front-end as a JSON object.
'''


def get_array_from_citations(url):
    #first grab a list of the rows from the citations table pertaining to a specific article URL
    citations_list = get_all_citations(url)
    #this is the array that will be returned full of info related to the citations for a given article
    returned_list = []
    for element in citations_list:
        #now we build a dictionary for each citation that will be added to the returned list
        current_dict = {}
        current_dict['citation_url'] = element.citation_url
        current_dict['citation_text'] = element.citation_text
        current_dict['citation_source_type'] = element.citation_source_type
        current_dict['citation_domain_type'] = element.citation_domain_type
        current_dict['citation_domain_restrictions'] = element.citation_domain_restrictions
        #now the long string of contradictions will be extracted
        #crucially the unique string that separates all the contradictions will be used to split the contradictions into a list
        contra_string = element.citation_contradictions
        contradictions_list = contra_string.split("35284777")
        current_dict['citation_contradictions'] = contradictions_list
        #now the same will be done for the support string
        support_string = element.citation_support
        support_list = support_string.split("35284777")
        current_dict['citation_support'] = support_list
        returned_list.append(current_dict)
        print(returned_list)
    return returned_list


#from time to time the vetting process will fail due to glitches that are hard to diagnose mostly related to communcation
#between the server and the database. Also articles will end up in the database with no associated citations in the citations table simply because they had no hyperlinks attached
def check_for_unvetted_articles():
    index_variable = 3
    while query_articles_table_ID(index_variable) != None:
        current_article_link = (query_articles_table_ID(index_variable)).article_url
        #print(current_article_link)
        if query_citations_table(current_article_link) == None:
            print("The following article has no vetted citations associated with it. This means there were either no hyperlinks in the article or the Vetting process encountered an error.")
            print(current_article_link)
            index_variable = index_variable+1
        else:
            index_variable = index_variable+1

def vett_again():
    index_variable = 3
    while query_articles_table_ID(index_variable) != None:
        current_article_link = (query_articles_table_ID(index_variable)).article_url
        if query_citations_table(current_article_link) == None:
            print("The following article has no vetted citations associated with it. This means there were either no hyperlinks in the article or the Vetting process encountered an error.")
            print("commencing with the next vetting attempt")
            dataframe = Feature_1_analysis(current_article_link)
            dataframe = deep_dive_all_links(dataframe)
            check_db_connection()
            add_info_to_db(dataframe, current_article_link)
            index_variable = index_variable+1
        else:
            index_variable = index_variable+1

#print((get_array_from_citations('https://globalnews.ca/news/8476100/owen-power-goals-canada-world-junior-hockey/')))