from fastapi import FastAPI,UploadFile,Form,Response,Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from typing import Annotated 
import sqlite3

con=sqlite3.connect('db.db',check_same_thread=False)
cur=con.cursor()

cur.execute(f"""
           CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            image BLOB,
            price INTEGER NOT NULL,
            description TEXT,
            place TEXT NOT NULL,
            instertAt INTEGER NOT NULL)
           """)



app = FastAPI()

SECRET = "super-coding"
manager = LoginManager(SECRET, '/login')

@manager.user_loader()
def query_user(data):
    WHERE_STATEMENT = f'id="{data}"'
    if type (data) == dict:
        WHERE_STATEMENT = f'''id="{data['id']}"'''
    con.row_factory=sqlite3.Row
    cur=con.cursor()
    user =cur.execute(f"""
                      SELECT * from users WHERE {WHERE_STATEMENT}
                      """).fetchone()
    return user

@app.post('/login')
def login(id:Annotated[str,Form()], 
           password:Annotated[str,Form()]):
    user = query_user(id)
    if not user:
        raise InvalidCredentialsException
    elif password != user['password']:
        raise InvalidCredentialsException
    
    access_token = manager.create_access_token(data={
      'sub': {  
        'id':user['id'],
        'name':user['name'],
        'email':user['email']
      }
    })
    
    # 자동으로 서버에서 200상태 코드 보내줌    
    return {'access_token':access_token}


@app.post('/signup')
def signup(id:Annotated[str,Form()], 
           password:Annotated[str,Form()],
           name:Annotated[str,Form()],
           email:Annotated[str,Form()]):
    cur.execute(f"""
                INSERT INTO items(id,name,email,password)
                VALUES('{id}', '{name}','{email}','{password}')
                """)
    con.commit()
    return '200'

@app.post('/items')
async def create_item (image:UploadFile, 
                title:Annotated[str, Form()], 
                price:Annotated[int, Form()],
                description:Annotated[str, Form()],
                place:Annotated[str, Form()],
                insertAt:Annotated[int, Form()],
                user=Depends(manager)
                ):
    image_bytes = await image.read()
    cur.execute(f"""
                INSERT INTO 
                items(title,image,price,description,place,insertAt)
                VALUES
                ('{title}','{image_bytes.hex()}',{price},'{description}','{place}',{insertAt})
                """)
    con.commit()
    return '200'

@app.get('/items')
async def get_items(user=Depends(manager)):
   #컬럼명같이 가지고 옴
    con.row_factory=sqlite3.Row
    cur = con.cursor()
    rows = cur.execute(f"""
                       SELECT * from items;
                       """).fetchall()
    return JSONResponse(jsonable_encoder(
        dict(rows) for row in rows
        ))

@app.get('/images/{item_id}')
async def get_image(item_id):
    cur=con.cursor()
    image_bytes=cur.execute(f"""
                            SELECT image from items WHERE id={item_id}
                            """).fetchone()[0]
    return Response(content=bytes.fromhex(image_bytes), media_type='image/*')




app.mount("/",  StaticFiles(directory="frontend", html=True), name="frontend")