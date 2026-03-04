from database.schema import init_db
from database.crud import add_room, add_subject, add_teacher, add_batch_section, update_global_settings
from datetime import time

def inject_test_data():
    print("⏳ Connecting to database...")
    db_session = init_db()

    print("⚙️ Setting Global Rules...")
    update_global_settings(
        session=db_session,
        open_time=time(8, 0),   # 8:00 AM
        close_time=time(16, 0), # 4:00 PM
        jumma_start=time(13, 0),
        jumma_end=time(14, 30),
        credit_mins=60,
        sun_off=True
    )

    print("🏫 Injecting Rooms & Labs...")
    add_room(db_session, "AI Lab 1", 50, True)
    add_room(db_session, "AI Lab 2", 40, True)
    add_room(db_session, "Room 301 (Theory)", 60, False)
    add_room(db_session, "Room 302 (Theory)", 60, False)

    print("📚 Injecting AI Curriculum...")
    add_subject(db_session, "AIF-301", "Programming Fundamentals", 4, True) # Includes Lab
    add_subject(db_session, "AIF-302", "Calculus and Analytical Geometry", 3, False)
    add_subject(db_session, "AIF-303", "Intro to Info and Comm Technologies", 3, True)
    add_subject(db_session, "AIF-401", "Data Structures & Algorithms", 4, True)
    add_subject(db_session, "AIF-402", "Artificial Intelligence", 3, False)

    print("👨‍🏫 Injecting Faculty...")
    # Fetch subjects to assign them
    from database.schema import Subject
    all_subs = db_session.query(Subject).all()
    sub_map = {s.course_code: s.id for s in all_subs}

    add_teacher(db_session, "Dr. Ali Raza", "31202-0000001-1", "0300-1111111", [sub_map["AIF-402"], sub_map["AIF-301"]])
    add_teacher(db_session, "Prof. Usman", "31202-0000002-1", "0300-2222222", [sub_map["AIF-302"]])
    add_teacher(db_session, "Lec. Fatima", "31202-0000003-1", "0300-3333333", [sub_map["AIF-401"], sub_map["AIF-303"]])

    print("🎓 Injecting Batches & Sections...")
    # 3rd Semester taking intro AI courses
    add_batch_section(db_session, 3, "A", 45, [sub_map["AIF-301"], sub_map["AIF-302"], sub_map["AIF-303"]])
    # 5th Semester taking advanced courses
    add_batch_section(db_session, 5, "A", 35, [sub_map["AIF-401"], sub_map["AIF-402"]])

    print("✅ Dummy data injection complete! You can now run 'streamlit run app.py' to see the data.")

if __name__ == "__main__":
    inject_test_data()
