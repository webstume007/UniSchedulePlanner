import streamlit as st
import pandas as pd
from engine.scheduler import TimetableEngine
from database.crud import get_all_teachers, get_all_rooms, get_all_subjects, get_all_batches

def render_timetable_page(db_session):
    # IUB Specific Styling for the Timetable Page
    st.markdown("""
        <style>
        .gen-header { color: #006837; font-weight: bold; }
        .control-panel { 
            background-color: #f0f9f4; 
            padding: 20px; 
            border-radius: 10px; 
            border: 1px solid #d1e7dd; 
            margin-bottom: 25px;
        }
        .stButton>button { width: 100%; border-radius: 5px; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 class='gen-header'>🚀 Generate & View Timetable</h1>", unsafe_allow_html=True)
    st.markdown("Run the AI optimization algorithm to create a clash-free schedule based on IUB department constraints.")

    # ==========================================
    # GENERATOR SECTION (Control Panel)
    # ==========================================
    st.markdown("<div class='control-panel'>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Control Panel")
        generate_btn = st.button("⚡ Run AI Algorithm", type="primary")
        st.caption("Calculation may take a few seconds based on constraints.")

    with col2:
        st.info("""
        **Generation Rules Applied:**
        - No teacher/room/batch overlaps.
        - Strict Jumma Break (Friday) enforced.
        - Room Capacity matching with Student Strength.
        - Room Availability hours respected.
        """)
    st.markdown("</div>", unsafe_allow_html=True)

    # Persistent storage for the generated schedule
    if 'generated_schedule' not in st.session_state:
        st.session_state.generated_schedule = None

    if generate_btn:
        with st.spinner("Crunching millions of combinations for IUB... Please wait."):
            engine = TimetableEngine(db_session)
            success, result = engine.generate()
            
            if success:
                st.session_state.generated_schedule = result
                st.success("✅ Timetable generated successfully! Zero clashes detected.")
            else:
                st.error(f"❌ {result}")
                st.session_state.generated_schedule = None

    # ==========================================
    # RESULTS & VISUALIZATION SECTION
    # ==========================================
    if st.session_state.generated_schedule:
        st.markdown("---")
        
        # 1. Fetch data to map raw IDs back to readable names
        teachers = {t.id: t.name for t in get_all_teachers(db_session)}
        rooms = {r.id: r.room_name for r in get_all_rooms(db_session)}
        subjects = {s.id: s.course_code for s in get_all_subjects(db_session)}
        batches = {b.id: f"Sem {b.semester_level} - Sec {b.section_name}" for b in get_all_batches(db_session)}

        # 2. Transform the raw engine output into a readable format
        formatted_data = []
        for entry in st.session_state.generated_schedule:
            formatted_data.append({
                "Batch / Class": batches[entry["batch_id"]],
                "Day": entry["day"],
                "Time": f"{entry['start_time']} - {entry['end_time']}",
                "Subject": subjects[entry["subject_id"]],
                "Teacher": teachers[entry["teacher_id"]],
                "Room": rooms[entry["room_id"]]
            })
            
        # Create a Pandas DataFrame for easy manipulation
        df = pd.DataFrame(formatted_data)

        # SAFETY CHECK: Prevent Pandas crash if no data exists
        if df.empty:
            st.warning("⚠️ No classes were scheduled. Please ensure you have assigned subjects to batches and teachers.")
        else:
            # Sort logically by Day and Time
            day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            df['Day'] = pd.Categorical(df['Day'], categories=day_order, ordered=True)
            df = df.sort_values(['Batch / Class', 'Day', 'Time']).reset_index(drop=True)

            # 3. Create interactive tabs with IUB Visuals
            tab1, tab2, tab3, tab4 = st.tabs(["🎓 View by Batch", "👨‍🏫 View by Teacher", "🏫 View by Room", "🗄️ Master Table"])
            
            with tab1:
                batch_list = df['Batch / Class'].unique()
                selected_batch = st.selectbox("Select Batch to View", batch_list)
                batch_df = df[df['Batch / Class'] == selected_batch]
                # Pivot table to make it look like a classic timetable grid
                try:
                    pivot_batch = batch_df.pivot(index="Time", columns="Day", values="Subject").fillna("-")
                    st.markdown(f"### Schedule for {selected_batch}")
                    st.table(pivot_batch) # Using st.table for a cleaner static look for IUB
                except:
                    st.dataframe(batch_df)

            with tab2:
                teacher_list = df['Teacher'].unique()
                selected_teacher = st.selectbox("Select Teacher to View", teacher_list)
                teacher_df = df[df['Teacher'] == selected_teacher]
                st.dataframe(teacher_df[['Day', 'Time', 'Batch / Class', 'Subject', 'Room']], use_container_width=True)

            with tab3:
                room_list = df['Room'].unique()
                selected_room = st.selectbox("Select Room to View", room_list)
                room_df = df[df['Room'] == selected_room]
                st.dataframe(room_df[['Day', 'Time', 'Batch / Class', 'Subject', 'Teacher']], use_container_width=True)

            with tab4:
                st.markdown("### Full Department Master Schedule")
                st.dataframe(df, use_container_width=True)
                
                # Export functionality
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Official Timetable (CSV)",
                    data=csv,
                    file_name='iub_ai_timetable.csv',
                    mime='text/csv',
                )
