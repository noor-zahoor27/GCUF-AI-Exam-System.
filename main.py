import os
import random
import pandas as pd
from fastapi import FastAPI, Request, Form, Depends, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

import models
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def run_allocation_ai(db: Session):
    db.query(models.SeatingAssignment).delete()
    students = db.query(models.Student).all()
    halls = db.query(models.Hall).all()
    if not students or not halls:
        return
    random.shuffle(students)
    student_idx = 0
    for hall in halls:
        for r in range(hall.rows):
            for c in range(hall.cols):
                if student_idx < len(students):
                    s = students[student_idx]
                    assignment = models.SeatingAssignment(
                        student_name=s.name,
                        student_dept=s.dept,
                        hall_name=hall.hall_name,
                        seat_label=f"Row {r+1}, Col {c+1}"
                    )
                    db.add(assignment)
                    student_idx += 1
    db.commit()

@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    plan = db.query(models.SeatingAssignment).all()
    s_count = db.query(models.Student).count()
    h_count = db.query(models.Hall).count()
    
    return templates.TemplateResponse(
        request=request,
        name="index.html", 
        context={
            "request": request, 
            "plan": plan, 
            "s_count": s_count, 
            "h_count": h_count
        }
    )

@app.post("/add-hall")
async def add_hall(name: str = Form(...), r: int = Form(...), c: int = Form(...), db: Session = Depends(get_db)):
    new_hall = models.Hall(hall_name=name, rows=r, cols=c)
    db.add(new_hall)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.post("/upload-students")
async def upload(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        df = pd.read_csv(file.file)
        for _, row in df.iterrows():
            db.add(models.Student(roll_no=str(row['roll_no']), name=row['name'], dept=row['dept']))
        db.commit()
    except Exception as e:
        print(f"Error: {e}")
    return RedirectResponse(url="/", status_code=303)

@app.get("/generate")
def generate(db: Session = Depends(get_db)):
    run_allocation_ai(db)
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
