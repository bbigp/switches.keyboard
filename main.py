import uvicorn

if __name__ == '__main__':
    uvicorn.run('app.application:app', host='0.0.0.0', port=8002, access_log=True)

