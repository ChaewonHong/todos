from fastapi import FastAPI, Form, Request, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import uvicorn
from database import Base, engine, SessionLocal
from fastapi.responses import RedirectResponse
import models

app = FastAPI()

#DB 엔진 연결 
models.Base.metadata.create_all(bind=engine)

# html 문서를 위한 객체
templates = Jinja2Templates(directory="templates")

# 정적파일을 위한 설정
## 정적파일(static) 종류(image, css, js)
app.mount("/static", StaticFiles(directory="static"), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        # 마지막에 무조건 닫음
        db.close()

# localhost:8000/
@app.get("/")
async def home(request: Request, db_ss: Session = Depends(get_db)):
    todos = db_ss.query(models.Todo).order_by(models.Todo.id.desc())
    print(type(todos))

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "todos": todos}
        )

@app.post("/add")
async def add(request: Request, task: str = Form(...), 
              db_ss: Session = Depends(get_db)):
    # 클라이언트 textarea에서 입력 데이터 넘어온거 확인
    print(task)

    # db 테이블에 task 저장하고 
    # 클라이언트에서 넘어온 task를 Todo 객체로 성장
    todo = models.Todo(task=task)

    # 의존성 주입에서 처리함 Depends(get_db): 엔진객체생성, 세션연결
    # db 체이블에 task 저장하기
    db_ss.add(todo)
    # db에 실제 저장
    db_ss.commit()

    return RedirectResponse(url=app.url_path_for("home"), 
                            status_code=status.HTTP_303_SEE_OTHER)


@app.get("/delete/{todo_id}")
async def add(request: Request, todo_id: int, db_ss: Session = Depends(get_db)):
    todo = db_ss.query(models.Todo).filter(models.Todo.id == todo_id).first()
    db_ss.delete(todo)
    db_ss.commit()
    return RedirectResponse(url=app.url_path_for("home"), status_code=status.HTTP_303_SEE_OTHER)    

@app.get("/edit/{todo_id}")
async def edit(request: Request):
    todos = 0
    return templates.TemplateResponse("edit.html",
                                      {"request": request, "todos":todos})


# python main.py
if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)

# CLI명령 : uvicorn main:app --reload