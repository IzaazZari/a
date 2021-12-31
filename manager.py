
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from fastapi.staticfiles import StaticFiles
from pathlib import Path
import sqlite3

import re
import itertools as it

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

import secrets

app = FastAPI()

security=HTTPBasic()

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "test")
    correct_password = secrets.compare_digest(credentials.password, "test")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username




app.mount("/static",StaticFiles(directory=Path(__file__).parent.parent.absolute() / "static")
,name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/",response_class=HTMLResponse)
async def funcEnterInput(f1:Request,username:str=Depends(get_current_username)):
    return templates.TemplateResponse("1.html",{"request":f1})


@app.get("/search",response_class=HTMLResponse)
async def funcSearch(f1:Request,username:str=Depends(get_current_username)):
    return templates.TemplateResponse("search.html",{"request":f1})

@app.post("/delete",response_class=HTMLResponse)
async def funcDelete(f3:Request,username:str=Depends(get_current_username)):
    cn=sqlite3.connect("arena.db")
    cn.execute("delete FROM arena;")
    cn.commit()
    cn.close()
    return templates.TemplateResponse("delete.html",{"request":f3})


    

@app.post("/search",response_class=HTMLResponse)
async def funcSearchResults(f1:Request,num1: str= Form(...),num2:str=Form(...),num3:str=Form(...),username:str=Depends(get_current_username)):
    print(f1)
    print(num1)
    print(num2)
    print(num3)
    # x =  "insert into arena values" + " ("+str(num1)+","+str(num2)+","+str(num3)+");" 
    x = "select count(*) from arena where section="+num1+" and"+" row="+num2+" and" +" seat="+num3
    x2=sqlite3.connect("arena.db")
    cursor1 = x2.execute(x)
    answer1=cursor1.fetchone()
    x2.close()
    print(answer1[0])
    if answer1[0]==0:
        print("You entered this for section: ",num1)
        print("You entered this for row: ",num2)
        print("You entered this for seat range: ",num3)
        print("This seat does not require Covid testing.")
        dict1={'request':f1,'section':num1,'row':num2,'seat':num3}
        #return templates.TemplateResponse("testnotneeded.html",{"request":f1})
        return templates.TemplateResponse("testnotneeded.html",dict1)
    else:
        print("You entered this for section: ",num1)
        print("You entered this for row: ",num2)
        print("You entered this for seat range: ",num3)
        print("This seat requires Covid testing.")
        dict1={'request':f1,'section':num1,'row':num2,'seat':num3}
        return templates.TemplateResponse("testneeded.html",dict1)
        
def expand(parameter1):
    if "-" in parameter1:
        z1 = re.search("(\d{1}-{1}\d{1,2})",str(parameter1))
        # print(z1.group(1))

        z2=z1.group(1)
        ranges=list(map(int,re.findall(r'\d+',z2)))
        thelist= [i for i in range(ranges[0],ranges[1]+1)]
        # print("section",thelist)
    else:
        thelist=[int(parameter1)]
        # print("section",thelist)
    return thelist

    


#   return templates.TemplateResponse("search.html",{"request":f1})

@app.post("/",response_class=HTMLResponse)
async def funcSaveInput(f2:Request,num1: str= Form(...),num2:str=Form(...),num3:str=Form(...)):
    print(f2)
    print("abc")
    print(num1)
    print(num2) 
    print(num3)
    num1=num1.strip()
    num2=num2.strip()
    num3=num3.strip()

    thing1=[]
    s1=num1.split(',')
    for i in s1:
        k1 = expand(i)
        thing1.append(k1)
    thing1=list(it.chain(*thing1))
    print("thing1 ",thing1)

    thing2=[]
    s2=num2.split(',')
    for i in s2:
        k2 = expand(i)
        thing2.append(k2)
    thing2=list(it.chain(*thing2))
    print("thing2 ",thing2)

    thing3=[]
    s3=num3.split(',')
    for i in s3:
        k3 = expand(i)
        thing3.append(k3)
    thing3=list(it.chain(*thing3))
    print("thing3 ",thing3)

    list1=thing1
    list2=thing2
    list3=thing3

    # list1=expand(num1)

    # list2=expand(num2)

    # list3=expand(num3)

    product1= list(it.product(list1,list2,list3))
    print("product1 ",product1)
    recN=len(product1)
    dict1={'request':f2,'section':num1,'row':num2,'seat':num3,'numberofrecordsadded':recN}

    # x =  "insert into arena values" + " ("+str(num1)+","+str(num2)+","+str(num3)+");" 
    x =  "insert into arena values (?,?,?)"
    y =  "delete from arena" 
    print(x)
    x2=sqlite3.connect("arena.db")
    # x2.execute(x)
    x2.executemany(x,product1)
    x2.commit()
    # for x4 in x3:
    #     print(x4)
    x2.close()
    return templates.TemplateResponse("2.html",dict1)
    