from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, Time, Table
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import time

# Base class for all our database models
Base = declarative_base()

# -------------------------------------------------------------------
# ASSOCIATION TABLES (For Many-to-Many Relationships)
# -------------------------------------------------------------------

# A teacher can teach multiple subjects, and a subject can be taught by multiple teachers
teacher_subject_association = Table(
    'teacher_subject', Base.metadata,
    Column('teacher_id', Integer, ForeignKey('teachers.id'), primary_key=True),
    Column('subject_id', Integer, ForeignKey('subjects.id'), primary_key=True)
)

# A batch/section takes specific subjects in a semester
batch_subject_association = Table(
    'batch_subject', Base.metadata,
    Column('batch_id', Integer, ForeignKey('batches.id'), primary_key=True),
    Column('subject_id', Integer, ForeignKey('subjects.id'), primary_key=True)
)

# -------------------------------------------------------------------
# CORE ENTITY MODELS
# -------------------------------------------------------------------

class GlobalSetting(Base):
    """Stores the dynamic dashboard rules like Uni timings and Jumma breaks."""
    __tablename__ = 'global_settings'
    
    id = Column(Integer, primary_key=True)
    uni_open_time = Column(Time, default=time(8, 0))   # e.g., 08:00 AM
    uni_close_time = Column(Time, default=time(16, 0)) # e.g., 04:00 PM
    jumma_break_start = Column(Time, default=time(13, 0)) # 01:00 PM
    jumma_break_end = Column(Time, default=time(14, 30))  # 02:30 PM
    credit_hour_duration_mins = Column(Integer, default=60) # 1 Credit Hour = 60 mins
    sunday_off = Column(Boolean, default=True)

class Teacher(Base):
    """Profile and availability for teaching staff."""
    __tablename__ = 'teachers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    cnic = Column(String(20), unique=True, nullable=True)
    contact_number = Column(String(20), nullable=True)
    
    # Relationships
    subjects_can_teach = relationship('Subject', secondary=teacher_subject_association, back_populates='capable_teachers')

class Room(Base):
    __tablename__ = 'rooms'
    id = Column(Integer, primary_key=True)
    room_name = Column(String, unique=True, nullable=False)
    capacity = Column(Integer, nullable=False)
    is_lab = Column(Boolean, default=False)
    # New Fields
    available_from = Column(Time, default=time(8, 0))
    available_to = Column(Time, default=time(16, 0))

class Subject(Base):
    """Curriculum details for the AI department."""
    __tablename__ = 'subjects'
    
    id = Column(Integer, primary_key=True)
    course_code = Column(String(20), nullable=False, unique=True) # e.g., "AIF-301"
    subject_name = Column(String(100), nullable=False)
    total_credit_hours = Column(Integer, nullable=False)
    requires_lab = Column(Boolean, default=False)
    
    # Relationships
    capable_teachers = relationship('Teacher', secondary=teacher_subject_association, back_populates='subjects_can_teach')
    batches_taking = relationship('BatchSection', secondary=batch_subject_association, back_populates='curriculum_subjects')

class BatchSection(Base):
    """Represents a specific group of students (e.g., Semester 3, Section A)."""
    __tablename__ = 'batches'
    
    id = Column(Integer, primary_key=True)
    semester_level = Column(Integer, nullable=False) # e.g., 1 through 8
    section_name = Column(String(10), nullable=False) # e.g., "A", "B"
    student_strength = Column(Integer, nullable=False)
    
    # Relationships
    curriculum_subjects = relationship('Subject', secondary=batch_subject_association, back_populates='batches_taking')


# -------------------------------------------------------------------
# DATABASE SETUP FUNCTION
# -------------------------------------------------------------------
def init_db(database_url="sqlite:///timetable.db"):
    """Initializes the database and creates tables if they don't exist."""
    # ADDED: connect_args={'check_same_thread': False} to prevent Streamlit threading crashes
    engine = create_engine(database_url, echo=False, connect_args={'check_same_thread': False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

# If run directly, it will create the SQLite database file in the root folder.
if __name__ == "__main__":
    db_session = init_db()
    print("✅ Database schema initialized successfully. 'timetable.db' created.")
