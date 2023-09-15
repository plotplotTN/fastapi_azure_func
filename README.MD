
# TO RUN THE API
    python -m uvicorn main:app --reload

    ou 

    if __name__ == '__main__':
        import uvicorn
        uvicorn.run(app,host="127.0.0.1",port=8000)

# for access the docs interface
http://127.0.0.1:8000/docs



# In azure cli
## create a ressource groupe
az group create --name api_bordereau_traducter --location westeurope
## create a container registry 
az acr create --resource-group api_bordereau_traducter --name containerregistryfortraducterapi --sku basic 
