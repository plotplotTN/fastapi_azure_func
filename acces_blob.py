from azure.storage.blob import BlobServiceClient
import urllib.parse


connection_string = "https://teststockagefastapi.blob.core.windows.net/borderaucontainer"
connection_string = "DefaultEndpointsProtocol=https;AccountName=teststockagefastapi;AccountKey=P4hCscg4j1a+B6aIlKMKJM0eBBVz1PsESRVPl8Lt7QyqD08ICDO8AnDGShrqWdC3ollMgf2hmcXO+AStRT4kag==;EndpointSuffix=core.windows.net"

# Create a BlobServiceClient using the connection string
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# Create a new container (or use an existing one)
container_name = "borderaucontainer"
#container_client = blob_service_client.create_container(container_name)
container_client= blob_service_client.get_container_client(container=container_name)

# Upload a file to the blob container
blob_name = "myblob.htm" # be careful with the name
with open('C:\\Users\\romai\\Downloads\\bordereauxcsv-20230911T144458Z-001\\bordereauxcsv\\Bmmnpve1_fichiers\\toprint.htm', "rb") as data:
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    blob_client.upload_blob(data)

print(f"File uploaded to {container_name}/{blob_name}")