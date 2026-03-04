from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .schema import Teacher, Room, Subject, BatchSection, GlobalSetting

# ==========================================
# GLOBAL SETTINGS OPERATIONS
# ==========================================

def get_global_settings(session: Session):
    """Fetches the global settings. Creates default settings if none exist."""
    settings = session.query(GlobalSetting).first()
    if not settings:
        settings = GlobalSetting() # Uses defaults from schema.py
        session.add(settings)
        session.commit()
    return settings

def update_global_settings(session: Session, open_time, close_time, jumma_start, jumma_end, credit_mins, sun_off):
    """Updates the master university rules."""
    settings = get_global_settings(session)
    settings.uni_open_time = open_time
    settings.uni_close_time = close_time
    settings.jumma_break_start = jumma_start
    settings.jumma_break_end = jumma_end
    settings.credit_hour_duration_mins = credit_mins
    settings.sunday_off = sun_off
    session.commit()
    return settings

# ==========================================
# ROOM OPERATIONS
# ==========================================

def add_room(session: Session, name: str, capacity: int, is_lab: bool):
    """Adds a new classroom or lab to the database."""
    try:
        new_room = Room(room_name=name, capacity=capacity, is_lab=is_lab)
        session.add(new_room)
        session.commit()
        return True, "Room added successfully."
    except IntegrityError:
        session.rollback()
        return False, f"Error: A room with the name '{name}' already exists."

def get_all_rooms(session: Session):
    return session.query(Room).all()

def delete_room(session: Session, room_id: int):
    room = session.query(Room).filter(Room.id == room_id).first()
    if room:
        session.delete(room)
        session.commit()
        return True
    return False

# ==========================================
# SUBJECT OPERATIONS
# ==========================================

def add_subject(session: Session, code: str, name: str, credit_hours: int, requires_lab: bool):
    """Adds a new course to the curriculum."""
    try:
        new_subject = Subject(
            course_code=code, 
            subject_name=name, 
            total_credit_hours=credit_hours, 
            requires_lab=requires_lab
        )
        session.add(new_subject)
        session.commit()
        return True, "Subject added successfully."
    except IntegrityError:
        session.rollback()
        return False, f"Error: Course code '{code}' already exists."

def get_all_subjects(session: Session):
    return session.query(Subject).all()

# ==========================================
# TEACHER OPERATIONS
# ==========================================

def add_teacher(session: Session, name: str, cnic: str, contact: str, subject_ids: list):
    """
    Adds a teacher and links them to the subjects they are capable of teaching.
    subject_ids is a list of Subject.id integers.
    """
    try:
        new_teacher = Teacher(name=name, cnic=cnic, contact_number=contact)
        
        # Link the selected subjects to this teacher
        if subject_ids:
            subjects = session.query(Subject).filter(Subject.id.in_(subject_ids)).all()
            new_teacher.subjects_can_teach.extend(subjects)
            
        session.add(new_teacher)
        session.commit()
        return True, "Teacher profile created successfully."
    except IntegrityError:
        session.rollback()
        return False, "Error: A teacher with this CNIC already exists."

def get_all_teachers(session: Session):
    return session.query(Teacher).all()

# ==========================================
# BATCH / SECTION OPERATIONS
# ==========================================

def add_batch_section(session: Session, semester: int, section: str, strength: int, subject_ids: list):
    """
    Creates a new class (e.g., Semester 3, Section A) and assigns their syllabus.
    """
    try:
        new_batch = BatchSection(semester_level=semester, section_name=section, student_strength=strength)
        
        # Link the required curriculum subjects to this batch
        if subject_ids:
            subjects = session.query(Subject).filter(Subject.id.in_(subject_ids)).all()
            new_batch.curriculum_subjects.extend(subjects)
            
        session.add(new_batch)
        session.commit()
        return True, "Batch and curriculum assigned successfully."
    except Exception as e:
        session.rollback()
        return False, f"Database Error: {str(e)}"

def get_all_batches(session: Session):
    return session.query(BatchSection).all()
