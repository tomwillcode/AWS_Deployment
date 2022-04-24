from Vetted_DB_Access_Methods import add_article_to_db, add_info_to_db, add_citations_to_db, query_articles_table, query_citations_table, get_array_from_citations, check_db_connection
from fastapi import FastAPI, Path, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from pydantic import BaseModel
import json
from Vetted_Feature_1 import Feature_1_analysis
from Vetted_Feature_2 import deep_dive_all_links
import uvicorn
import logging

app = FastAPI(debug=True)
logger = logging.getLogger(__name__)
logging.basicConfig(filename='vettedserver.log',level=logging.DEBUG)

#very important code that comes next. This allows permissions of what addresses can make a request to this server.
# the "origins" allows the front-end chrome extension to make requests
origins = ['chrome-extension://ddedlokjjjcmoolaiomjjfdgkdkjjpnh']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#this creates an object the server can understand in terms of what data comes in from the front end for requests.
#It is indeed the URL for the article someone is reading that comes in.
class Article(BaseModel):
    url: str




@app.get("/")
def read_root():
    return {"YO": "YO"}


test_dictionary = {"Test":"It WORKED!", "Testing":"Yes"}


def add_hello_world(string):
    string = string + "hello world"
    return string

#This is a post end-point that recieves the URL for the article the user is currently reading
#This end-point activates code that sees if the article has already been vetted or a vett was attempted
#if so it just passes because the get request down-below is all that's needed.
#if not the article URL is passed to the functions for vetting, and then all the information is added to the database
@app.post("/post")
async def post_item(request: Article):
    logger.info("Post request made")
    current_url = json.loads(request.json())
    url = current_url['url']
    query = (query_articles_table(url))
    if query == None:
       add_article_to_db(url)
       dataframe = Feature_1_analysis(url)
       dataframe = deep_dive_all_links(dataframe)
       #check_db_connection()
       add_info_to_db(dataframe, url)
    else:
        pass
    #check if the article has been vetted
    if(query_citations_table(url) == None):
        return json.dumps({'status': False})
    else:
        return json.dumps({'status':True})

#this endpoint checks to see if data for an articles citations are already in the database, and if so it grabs that data and sends the appropriate JSON object back to the front-end
#In the event that the article has no data in the citations table in the database, this endpoint returns None so the algorithm on the front-end can keep checking.
#The algorithm on the front end is designed to keep checking this endpoint for article data in a loop because the vetting process takes time, processor permitting.
@app.get("/vett")
def read_item(key):
    url = key
    if query_citations_table(url) == None:
        return "None"

    else:
        array_for_client = get_array_from_citations(url)
        json_array_for_client = json.dumps(array_for_client)
        return json_array_for_client

if __name__ == "__main__":
    uvicorn.run("Vetted_Server:app", host="0.0.0.0", port=8000, log_level="debug", log_config="log.ini")
    #uvicorn.run("Vetted_Server:app", host="0.0.0.0", port=8000)