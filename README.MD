
# TO RUN THE API
    python -m uvicorn main:app --reload

    ou 

    if __name__ == '__main__':
        import uvicorn
        uvicorn.run(app,host="127.0.0.1",port=8000)

# for access the docs interface
http://127.0.0.1:8000/docs

#for access the logs interface
