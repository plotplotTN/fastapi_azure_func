
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
import traceback
import sys
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.keyvault.secrets import SecretClient

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/htm_to_json/")
async def get_json_from_htm(file:UploadFile):
    my_traducter = Traducter(file=file.file)
    return my_traducter.json_output



@app.get("/secret/")
def read_secret():


     # Set the Key Vault URL
    KEY_VAULT_URL = "https://aaakeyvault-prod.vault.azure.net/"  
    credential = DefaultAzureCredential()

    res1 = None
    try: 
        secret_client = SecretClient(vault_url=KEY_VAULT_URL, credential=credential)
        secret_name = "test-key"
        retrieved_secret = secret_client.get_secret(secret_name)
        retrieved_secret = retrieved_secret.value
        res1 = retrieved_secret
    except Exception as e:
        res1 = str(e) 

    return {"secretOsEnviron": res1}



@app.get("/test_lecture_blob/")
def test_lecture_blob():
    # Set the Blob Service URL
    BLOB_SERVICE_URL = "https://aaasnowrequeteur.blob.core.windows.net"
  
    try:
        credential = DefaultAzureCredential()
        blob_service_client = BlobServiceClient(account_url=BLOB_SERVICE_URL, credential=credential)
        container_name = "snow-requeteur"
        container_client = blob_service_client.get_container_client(container_name)
        blob_list = container_client.list_blobs()
        l = [a.name for a in blob_list]
    except Exception as e:
        l = [str(e)]
        l.append(str(traceback.format_exc()))

    return {"blob":l}


@app.get("/test_ecriture_blob/")
async def test_ecriture_blob():
    try:
        BLOB_SERVICE_URL = "https://aaasnowrequeteur.blob.core.windows.net"
        credential = DefaultAzureCredential()
        blob_service_client = BlobServiceClient(account_url=BLOB_SERVICE_URL, credential=credential)
        container_name = "snow-requeteur"
        container_client = blob_service_client.get_container_client(container_name)
        blob_name = "oui.txt"
        blob_content = "hello"
        container_client.upload_blob(blob_name, blob_content, overwrite=True)
        return {"blob":credential.get_token}
    except Exception as e:
        return {"blob":str(e)}

@app.get("/test_ip/")
def get_ip():
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(local_ip)
    return {"ip":local_ip}


if __name__ == '__main__':
    uvicorn.run(app,host="127.0.0.1",port=8000)
