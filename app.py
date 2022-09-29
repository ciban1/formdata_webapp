import uvicorn
from fastapi.encoders import jsonable_encoder
from fastapi import FastAPI, Request, Form, Depends, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from schemas import AwesomeForm  # uses schema file to bring in format of printing form data

import pymongo
cluster = pymongo.MongoClient("mongodb+srv://CIbanez:hRlNcZ0S8TsKRvHO@cluster0.eplptmw.mongodb.net/mydatabase?retryWrites=true&w=majority")
db = cluster["mydatabase"]
collection = db["test"]

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get('/basic', response_class=HTMLResponse)
def get_basic_form(request: Request):
    return templates.TemplateResponse("basic-form.html", {"request": request})  # renders HTML form and returns to user (lets us see the form)

@app.post('/basic', response_class=HTMLResponse)
# form parameters in same format as query parameters
# fastAPI pulls values from Form data from Request using names of parameters (also names on html inputs)
# use Form to declare form data input parameters
async def post_basic_form(request: Request, username: str = Form(...), password: str = Form(...), file: UploadFile = File(...)):
    print('username:', username)
    print('password:', password)

    # adding to MongoDB
    collection.insert_one({"name": username, "password": password})

    # await is for async function
    # this is for reading the uploaded file
    content = await file.read()
    print(content)
    return templates.TemplateResponse("basic-form.html", {"request": request})  # returns form


# second form made using schema
@app.get('/awesome', response_class=HTMLResponse)
def get_form(request: Request):
    return templates.TemplateResponse("awesome-form.html", {"request": request})  # renders HTML form and returns to user (lets us see the form)

@app.post('/awesome', response_class=HTMLResponse)
def post_form(request: Request, form_data: AwesomeForm = Depends(AwesomeForm.as_form)):  # as_form from schema
    print(form_data)
    # convert a data type (like a Pydantic model) to something compatible with JSON (like a dict, list, etc)
    form_data = jsonable_encoder(form_data)
    collection.insert_one(form_data)  # https://www.mongodb.com/developer/languages/python/python-quickstart-fastapi/



    return templates.TemplateResponse("awesome-form.html", {"request": request})

if __name__ == '__main__':
    uvicorn.run(app)