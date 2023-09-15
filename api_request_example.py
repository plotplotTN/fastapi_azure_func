import requests

# URL of the API endpoint
url = 'https://fastapitraducter.azurewebsites.net/htm_to_json/'

# Open the .htm file in binary mode
with open('C:\\Users\\romai\\Downloads\\bordereauxcsv-20230911T144458Z-001\\bordereauxcsv\\Bmmnpve1_fichiers\\toprint.htm', 'rb') as file:
    # Define the files dictionary with the file data
    files = {'file': ('filename.htm', file)}
    
    # Make the POST request
    response = requests.post(url, files=files)

# Print the response from the server
print(response.text)