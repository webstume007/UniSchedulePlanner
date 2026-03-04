from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import time

# Import our existing database and engine logic
from database.schema import init_db
from database import crud
from engine.scheduler import TimetableEngine

app = FastAPI(title="IUB AI Department Timetable API")

# Enable CORS so the React frontend (running on a different port) can talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, change this to your React app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# DATABASE DEPENDENCY
# ---------------------------------------------------------
def get_db():
    db = init_db()
    try:
        yield db
    finally:
        db.close()

# ---------------------------------------------------------
# PYDANTIC MODELS (Validates incoming data from React)
# ---------------------------------------------------------
class SettingsUpdate(BaseModel):
    uni_open_time: str
    uni_close_time: str
    jumma_break_start: str
    jumma_break_end: str
    credit_hour_duration_mins: int
    sunday_off: bool

class RoomCreate(BaseModel):
    room_name: str
    capacity: int
    is_lab: bool

class SubjectCreate(BaseModel):
    course_code: str
    subject_name: str
    total_credit_hours: int
    requires_lab: bool

class TeacherCreate(BaseModel):
    name: str
    cnic: Optional[str] = None
    contact_number: Optional[str] = None
    subject_ids: List[int]

class BatchCreate(BaseModel):
    semester_level: int
    section_name: str
    student_strength: int
    subject_ids: List[int]

# ---------------------------------------------------------
# API ROUTES
# ---------------------------------------------------------

@app.get("/api/stats")
def get_dashboard_stats(db = Depends(get_db)):
    return {
        "totalRooms": len(crud.get_all_rooms(db)),
        "totalSubjects": len(crud.get_all_subjects(db)),
        "totalTeachers": len(crud.get_all_teachers(db)),
        "totalBatches": len(crud.get_all_batches(db))
    }

# --- Settings ---
@app.get("/api/settings")
def get_settings(db = Depends(get_db)):
    settings = crud.get_global_settings(db)
    return {
        "uni_open_time": settings.uni_open_time.strftime("%H:%M"),
        "uni_close_time": settings.uni_close_time.strftime("%H:%M"),
        "jumma_break_start": settings.jumma_break_start.strftime("%H:%M"),
        "jumma_break_end": settings.jumma_break_end.strftime("%H:%M"),
        "credit_hour_duration_mins": settings.credit_hour_duration_mins,
        "sunday_off": settings.sunday_off
    }

@app.put("/api/settings")
def update_settings(data: SettingsUpdate, db = Depends(get_db)):
    # Convert string times to datetime.time objects
    def parse_time(t_str):
        h, m = map(int, t_str.split(':'))
        return time(h, m)
        
    crud.update_global_settings(
        db, parse_time(data.uni_open_time), parse_time(data.uni_close_time),
        parse_time(data.jumma_break_start), parse_time(data.jumma_break_end),
        data.credit_hour_duration_mins, data.sunday_off
    )
    return {"message": "Settings updated"}

# --- Rooms ---
@app.get("/api/rooms")
def get_rooms(db = Depends(get_db)):
    return crud.get_all_rooms(db)

@app.post("/api/rooms")
def add_room(data: RoomCreate, db = Depends(get_db)):
    success, msg = crud.add_room(db, data.room_name, data.capacity, data.is_lab)
    if not success: raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}

@app.delete("/api/rooms/{room_id}")
def delete_room(room_id: int, db = Depends(get_db)):
    if not crud.delete_room(db, room_id): raise HTTPException(status_code=404, detail="Room not found")
    return {"message": "Deleted"}

# --- Subjects ---
@app.get("/api/subjects")
def get_subjects(db = Depends(get_db)):
    return crud.get_all_subjects(db)

@app.post("/api/subjects")
def add_subject(data: SubjectCreate, db = Depends(get_db)):
    success, msg = crud.add_subject(db, data.course_code, data.subject_name, data.total_credit_hours, data.requires_lab)
    if not success: raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}

@app.delete("/api/subjects/{subject_id}")
def delete_subject(subject_id: int, db = Depends(get_db)):
    from database.schema import Subject
    try:
        obj = db.query(Subject).filter(Subject.id == subject_id).first()
        db.delete(obj)
        db.commit()
        return {"message": "Deleted"}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Cannot delete subject assigned to teacher/batch.")

# --- Teachers ---
@app.get("/api/teachers")
def get_teachers(db = Depends(get_db)):
    teachers = crud.get_all_teachers(db)
    # Format relationships for React
    return [{
        "id": t.id, "name": t.name, "cnic": t.cnic, "contact_number": t.contact_number,
        "subjects_can_teach": [{"id": s.id, "course_code": s.course_code} for s in t.subjects_can_teach]
    } for t in teachers]

@app.post("/api/teachers")
def add_teacher(data: TeacherCreate, db = Depends(get_db)):
    success, msg = crud.add_teacher(db, data.name, data.cnic, data.contact_number, data.subject_ids)
    if not success: raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}

@app.delete("/api/teachers/{teacher_id}")
def delete_teacher(teacher_id: int, db = Depends(get_db)):
    from database.schema import Teacher
    obj = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    db.delete(obj)
    db.commit()
    return {"message": "Deleted"}

# --- Batches ---
@app.get("/api/batches")
def get_batches(db = Depends(get_db)):
    batches = crud.get_all_batches(db)
    return [{
        "id": b.id, "semester_level": b.semester_level, "section_name": b.section_name, "student_strength": b.student_strength,
        "curriculum_subjects": [{"id": s.id, "course_code": s.course_code} for s in b.curriculum_subjects]
    } for b in batches]

@app.post("/api/batches")
def add_batch(data: BatchCreate, db = Depends(get_db)):
    success, msg = crud.add_batch_section(db, data.semester_level, data.section_name, data.student_strength, data.subject_ids)
    if not success: raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}

@app.delete("/api/batches/{batch_id}")
def delete_batch(batch_id: int, db = Depends(get_db)):
    from database.schema import BatchSection
    obj = db.query(BatchSection).filter(BatchSection.id == batch_id).first()
    db.delete(obj)
    db.commit()
    return {"message": "Deleted"}

# --- ALGORITHM ENGINE ---
@app.post("/api/generate")
def generate_timetable(db = Depends(get_db)):
    engine = TimetableEngine(db)
    success, result = engine.generate()
    
    if success:
        # Map IDs back to readable names before sending to React
        teachers = {t.id: t.name for t in crud.get_all_teachers(db)}
        rooms = {r.id: r.room_name for r in crud.get_all_rooms(db)}
        subjects = {s.id: s.course_code for s in crud.get_all_subjects(db)}
        batches = {b.id: f"Sem {b.semester_level} - Sec {b.section_name}" for b in crud.get_all_batches(db)}
        
        formatted = []
        for r in result:
            formatted.append({
                "batch": batches[r["batch_id"]],
                "day": r["day"],
                "time": f"{r['start_time']} - {r['end_time']}",
                "subject": subjects[r["subject_id"]],
                "teacher": teachers[r["teacher_id"]],
                "room": rooms[r["room_id"]]
            })
        return formatted
    else:
        raise HTTPException(status_code=400, detail=result)
