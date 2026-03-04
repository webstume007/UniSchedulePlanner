from sqlalchemy.orm import Session
from database.schema import Room, Subject, Teacher, BatchSection, GlobalSettings
from datetime import time

# --- GLOBAL SETTINGS ---
def get_global_settings(db: Session):
    settings = db.query(GlobalSettings).first()
    if not settings:
        settings = GlobalSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

def update_global_settings(db: Session, open_t, close_t, j_start, j_end, duration, sun_off):
    settings = get_global_settings(db)
    settings.uni_open_time = open_t
    settings.uni_close_time = close_t
    settings.jumma_break_start = j_start
    settings.jumma_break_end = j_end
    settings.credit_hour_duration_mins = duration
    settings.sunday_off = sun_off
    db.commit()
    return True

# --- ROOMS ---
def get_all_rooms(db: Session):
    return db.query(Room).all()

def add_room(db: Session, name, capacity, is_lab, available_from, available_to):
    try:
        new_room = Room(
            room_name=name, 
            capacity=capacity, 
            is_lab=is_lab,
            available_from=available_from,
            available_to=available_to
        )
        db.add(new_room)
        db.commit()
        return True, "Room added successfully!"
    except Exception as e:
        db.rollback()
        return False, str(e)

def delete_room(db: Session, room_id: int):
    room = db.query(Room).filter(Room.id == room_id).first()
    if room:
        db.delete(room)
        db.commit()
        return True
    return False

# --- SUBJECTS ---
def get_all_subjects(db: Session):
    return db.query(Subject).all()

def add_subject(db: Session, code, name, credit_hours, is_lab):
    try:
        new_subject = Subject(
            course_code=code, 
            subject_name=name, 
            total_credit_hours=credit_hours, 
            requires_lab=is_lab
        )
        db.add(new_subject)
        db.commit()
        return True, "Subject added!"
    except Exception as e:
        db.rollback()
        return False, str(e)

# --- TEACHERS ---
def get_all_teachers(db: Session):
    return db.query(Teacher).all()

def add_teacher(db: Session, name, cnic, contact, subject_ids):
    try:
        new_teacher = Teacher(name=name, cnic=cnic, contact_number=contact)
        if subject_ids:
            subs = db.query(Subject).filter(Subject.id.in_(subject_ids)).all()
            new_teacher.subjects_can_teach = subs
        db.add(new_teacher)
        db.commit()
        return True, "Teacher added!"
    except Exception as e:
        db.rollback()
        return False, str(e)

# --- BATCHES ---
def get_all_batches(db: Session):
    return db.query(BatchSection).all()

def add_batch_section(db: Session, semester, section, strength, subject_ids):
    try:
        new_batch = BatchSection(semester_level=semester, section_name=section, student_strength=strength)
        if subject_ids:
            subs = db.query(Subject).filter(Subject.id.in_(subject_ids)).all()
            new_batch.curriculum_subjects = subs
        db.add(new_batch)
        db.commit()
        return True, "Batch created!"
    except Exception as e:
        db.rollback()
        return False, str(e)
