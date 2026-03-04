import streamlit as st
import pandas as pd
from database.crud import add_room, add_subject, add_teacher, add_batch_section
from datetime import time

def render_import_page(db_session):
    st.markdown("""
        <style>
        .import-header { color: #006837; font-weight: bold; }
        .upload-card { 
            background-color: #f0f9f4; 
            padding: 20px; 
            border-radius: 10px; 
            border: 1px dashed #006837; 
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 class='import-header'>📥 Bulk Data Import</h1>", unsafe_allow_html=True)
    st.info("Upload CSV files to quickly populate your database. Ensure your CSV headers match the required formats listed below.")

    # Create 4 tabs for different data types
    tab1, tab2, tab3, tab4 = st.tabs(["🏫 Rooms", "📚 Subjects", "👨‍🏫 Teachers", "🎓 Batches"])

    # --- TAB 1: ROOMS ---
    with tab1:
        st.subheader("Import Rooms")
        st.markdown("""
        **Required Headers:** `room_name`, `capacity`, `is_lab`, `available_from`, `available_to`  
        *Example Time Format: 08:00, 16:00*
        """)
        room_file = st.file_uploader("Upload Rooms CSV", type=['csv'], key="room_up")
        if room_file:
            df = pd.read_csv(room_file)
            st.dataframe(df.head())
            if st.button("Process Rooms Import"):
                count = 0
                for _, row in df.iterrows():
                    # Convert string time to time object
                    start_h = int(str(row['available_from']).split(':')[0])
                    end_h = int(str(row['available_to']).split(':')[0])
                    success, _ = add_room(db_session, row['room_name'], row['capacity'], 
                                        row['is_lab'], time(start_h, 0), time(end_h, 0))
                    if success: count += 1
                st.success(f"Successfully imported {count} rooms!")

    # --- TAB 2: SUBJECTS ---
    with tab2:
        st.subheader("Import Subjects")
        st.markdown("**Required Headers:** `course_code`, `subject_name`, `credit_hours`, `requires_lab`")
        sub_file = st.file_uploader("Upload Subjects CSV", type=['csv'], key="sub_up")
        if sub_file:
            df = pd.read_csv(sub_file)
            st.dataframe(df.head())
            if st.button("Process Subjects Import"):
                count = 0
                for _, row in df.iterrows():
                    success, _ = add_subject(db_session, row['course_code'], row['subject_name'], 
                                           row['credit_hours'], row['requires_lab'])
                    if success: count += 1
                st.success(f"Successfully imported {count} subjects!")

    # --- TAB 3: TEACHERS ---
    with tab3:
        st.subheader("Import Teachers")
        st.markdown("**Required Headers:** `name`, `cnic`, `contact`, `subject_codes` (comma separated)")
        tea_file = st.file_uploader("Upload Teachers CSV", type=['csv'], key="tea_up")
        if tea_file:
            from database.schema import Subject
            df = pd.read_csv(tea_file)
            st.dataframe(df.head())
            if st.button("Process Teachers Import"):
                count = 0
                for _, row in df.iterrows():
                    # Logic to find IDs from Course Codes
                    codes = str(row['subject_codes']).split(',')
                    sub_ids = [s.id for s in db_session.query(Subject).filter(Subject.course_code.in_(codes)).all()]
                    success, _ = add_teacher(db_session, row['name'], row['cnic'], row['contact'], sub_ids)
                    if success: count += 1
                st.success(f"Successfully imported {count} teachers!")

    # --- TAB 4: BATCHES ---
    with tab4:
        st.subheader("Import Batches")
        st.markdown("**Required Headers:** `semester`, `section`, `strength`, `subject_codes` (comma separated)")
        bat_file = st.file_uploader("Upload Batches CSV", type=['csv'], key="bat_up")
        if bat_file:
            from database.schema import Subject
            df = pd.read_csv(bat_file)
            st.dataframe(df.head())
            if st.button("Process Batches Import"):
                count = 0
                for _, row in df.iterrows():
                    codes = str(row['subject_codes']).split(',')
                    sub_ids = [s.id for s in db_session.query(Subject).filter(Subject.course_code.in_(codes)).all()]
                    success, _ = add_batch_section(db_session, int(row['semester']), row['section'], int(row['strength']), sub_ids)
                    if success: count += 1
                st.success(f"Successfully imported {count} batches!")
