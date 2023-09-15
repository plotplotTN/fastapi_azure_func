
# TO RUN THE API
    python -m uvicorn main:app --reload

    ou 

    if __name__ == '__main__':
        import uvicorn
        uvicorn.run(app,host="127.0.0.1",port=8000)

# for access the docs interface
http://127.0.0.1:8000/docs

# tuto: with azure CLI and docker, create image and push 

## open docker desktop
## open terminal on your laptop with az installed
### 1: az acr login --name containerregistryfortraducterapi
### 2: docker build . -f ./Dockerfile -t containerregistryfortraducterapi.azurecr.io/acr-helloworld:v2
### 3: docker push containerregistryfortraducterapi.azurecr.io/acr-helloworld:v2 
### 4: image should be avaiable on azure container registry
### 5: create a web app from this new image

# In azure cli
## tuto
https://learn.microsoft.com/en-us/azure/container-registry/container-registry-tutorial-prepare-registry
https://learn.microsoft.com/en-us/azure/container-registry/container-registry-tutorial-deploy-app
## create a ressource groupe
az group create --name api_bordereau_traducter --location westeurope
## create a container registry 
az acr create --resource-group api_bordereau_traducter --name containerregistryfortraducterapi --sku basic 
