import streamlit as st
from database.crud import get_all_teachers, get_all_rooms, get_all_subjects, get_all_batches

def render_dashboard_page(db_session):
    # IUB Specific Styling
    st.markdown("""
        <style>
        .dash-title { color: #006837; font-weight: bold; margin-bottom: 0px; }
        .metric-card {
            background-color: #f0f9f4;
            padding: 15px;
            border-radius: 10px;
            border-left: 5px solid #006837;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 class='dash-title'>📊 AI Department Timetable Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("Overview of the scheduling system data and readiness for timetable generation.")

    # Fetch all data to calculate metrics
    teachers = get_all_teachers(db_session)
    rooms = get_all_rooms(db_session)
    subjects = get_all_subjects(db_session)
    batches = get_all_batches(db_session)

    # ==========================================
    # METRICS ROW
    # ==========================================
    # We use custom HTML columns to make them look more like IUB brand cards
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.markdown(f"<div class='metric-card'><h3>👨‍🏫</h3><p>Teachers</p><h2>{len(teachers)}</h2></div>", unsafe_allow_html=True)
    with m2:
        st.markdown(f"<div class='metric-card'><h3>🏫</h3><p>Rooms & Labs</p><h2>{len(rooms)}</h2></div>", unsafe_allow_html=True)
    with m3:
        st.markdown(f"<div class='metric-card'><h3>📚</h3><p>Subjects</p><h2>{len(subjects)}</h2></div>", unsafe_allow_html=True)
    with m4:
        st.markdown(f"<div class='metric-card'><h3>🎓</h3><p>Batches</p><h2>{len(batches)}</h2></div>", unsafe_allow_html=True)

    st.markdown("---")

    # ==========================================
    # READINESS CHECKLIST
    # ==========================================
    st.subheader("✅ System Readiness Check")
    st.info("The AI optimization engine requires data in all four pillars below to compute a valid, clash-free schedule.")

    # Check conditions
    has_rooms = len(rooms) > 0
    has_subjects = len(subjects) > 0
    has_teachers = len(teachers) > 0
    has_batches = len(batches) > 0

    req_col1, req_col2 = st.columns(2)
    
    with req_col1:
        st.checkbox("Rooms & Labs Configured", value=has_rooms, disabled=True, key="chk_rooms")
        st.checkbox("Curriculum (Subjects) Defined", value=has_subjects, disabled=True, key="chk_subs")
        
    with req_col2:
        st.checkbox("Faculty (Teachers) Added", value=has_teachers, disabled=True, key="chk_tea")
        st.checkbox("Batches & Sections Created", value=has_batches, disabled=True, key="chk_bat")

    if has_rooms and has_subjects and has_teachers and has_batches:
        st.success("🌟 **System Ready!** All data pillars are present. You can now proceed to the 'Generate Timetable' section.")
    else:
        st.warning("⚠️ **Missing Data:** Please complete the required steps in the navigation menu before attempting to generate a schedule.")
        
    st.markdown("---")

    # ==========================================
    # QUICK INSIGHTS
    # ==========================================
    

[Image of data visualization dashboard metrics]

    st.subheader("🔍 Department Insights")
    insight_col1, insight_col2 = st.columns(2)
    
    with insight_col1:
        lab_rooms = sum(1 for r in rooms if r.is_lab)
        st.info(f"🧪 **Lab Resources:** {lab_rooms} dedicated computer labs out of {len(rooms)} total rooms available.")
        
    with insight_col2:
        total_students = sum(b.student_strength for b in batches)
        st.info(f"👥 **Student Load:** The AI will schedule for approximately {total_students} students across all sections.")
