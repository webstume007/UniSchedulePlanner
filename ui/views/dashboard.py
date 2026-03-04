import streamlit as st
from database.crud import get_all_teachers, get_all_rooms, get_all_subjects, get_all_batches

def render_dashboard_page(db_session):
    st.title("📊 AI Department Timetable Dashboard")
    st.markdown("Overview of the scheduling system data and readiness for timetable generation.")

    # Fetch all data to calculate metrics
    teachers = get_all_teachers(db_session)
    rooms = get_all_rooms(db_session)
    subjects = get_all_subjects(db_session)
    batches = get_all_batches(db_session)

    # ==========================================
    # METRICS ROW
    # ==========================================
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Teachers", len(teachers))
    col2.metric("Total Rooms & Labs", len(rooms))
    col3.metric("Total Curriculum Subjects", len(subjects))
    col4.metric("Active Batches/Sections", len(batches))

    st.markdown("---")

    # ==========================================
    # READINESS CHECKLIST
    # ==========================================
    st.subheader("✅ System Readiness Check")
    st.markdown("The optimization engine requires all four pillars of data to generate a clash-free schedule.")

    # Check conditions
    has_rooms = len(rooms) > 0
    has_subjects = len(subjects) > 0
    has_teachers = len(teachers) > 0
    has_batches = len(batches) > 0

    req_col1, req_col2 = st.columns(2)
    
    with req_col1:
        st.checkbox("Rooms & Labs Configured", value=has_rooms, disabled=True)
        st.checkbox("Curriculum (Subjects) Defined", value=has_subjects, disabled=True)
        
    with req_col2:
        st.checkbox("Faculty (Teachers) Added", value=has_teachers, disabled=True)
        st.checkbox("Batches & Sections Created", value=has_batches, disabled=True)

    if has_rooms and has_subjects and has_teachers and has_batches:
        st.success("🌟 All data pillars are present! The system is ready to compute timetables.")
    else:
        st.warning("⚠️ Please complete the missing data steps from the sidebar before navigating to the generator.")
        
    st.markdown("---")

    # ==========================================
    # QUICK INSIGHTS
    # ==========================================
    st.subheader("🔍 Quick Insights")
    insight_col1, insight_col2 = st.columns(2)
    
    with insight_col1:
        lab_rooms = sum(1 for r in rooms if r.is_lab)
        st.info(f"🧪 **Lab Resources:** {lab_rooms} dedicated computer labs out of {len(rooms)} total rooms.")
        
    with insight_col2:
        total_students = sum(b.student_strength for b in batches)
        st.info(f"👥 **Student Load:** Scheduling for approximately {total_students} students across all active batches.")
