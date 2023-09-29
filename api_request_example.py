

if __name__ == "__main__":
    from azure.identity import InteractiveBrowserCredential
    from azure.storage.blob import BlobServiceClient
    from azure.identity import DefaultAzureCredential
    from azure.storage.blob import BlobServiceClient

    # Set the Blob Service URL
    BLOB_SERVICE_URL = "https://aaasnowrequeteur.blob.core.windows.net"


    try:
        #credential = DefaultAzureCredential()

        credential = InteractiveBrowserCredential(additionally_allowed_tenants=["d3f969e5-42a3-4d6c-a617-7b969dd92ea1"])
        #credential = InteractiveBrowserCredential()

        blob_service_client = BlobServiceClient(account_url=BLOB_SERVICE_URL, credential=credential)
        container_name = "snow-requeteur"
        container_client = blob_service_client.get_container_client(container_name)
        blob_list = container_client.list_blobs()
        l = [a.name for a in blob_list]
    except Exception as e:
        l = str(e)

    # The current credential is not configured to acquire tokens for tenant d3f969e5-42a3-4d6c-a617-7b969dd92ea1.

    print({"blob":l})