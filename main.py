
from fastapi import FastAPI
from fastapi import File, UploadFile
import os 
from bs4 import BeautifulSoup
from datetime import datetime
import re
from utils.htm_to_json.fonction_to_traduct import *
from utils.htm_to_json.traducter2 import Traducter
import uvicorn
import json 

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/htm_to_json/")
async def get_json_from_htm(file:UploadFile):
    my_traducter = Traducter(file=file.file)
    return my_traducter.json_output



if __name__ == '__main__':
    uvicorn.run(app,host="127.0.0.1",port=8000)