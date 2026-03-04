import streamlit as st
import pandas as pd
import io
import time
from fpdf import FPDF
from engine.scheduler import TimetableEngine
from database.crud import get_all_teachers, get_all_rooms, get_all_subjects, get_all_batches

def render_timetable_page(db_session):
    # IUB Specific Styling
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
        .console-log {
            background-color: #1e1e1e;
            color: #00ff00;
            padding: 15px;
            border-radius: 5px;
            font-family: 'Courier New', Courier, monospace;
            font-size: 0.85rem;
            border: 1px solid #444;
            margin-top: 10px;
            height: 150px;
            overflow-y: auto;
        }
        .stButton>button { width: 100%; border-radius: 5px; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 class='gen-header'>🚀 Generate & View Timetable</h1>", unsafe_allow_html=True)
    st.markdown("Run the AI optimization algorithm to create a schedule based on IUB department constraints.")

    # ==========================================
    # GENERATOR SECTION (Control Panel)
    # ==========================================
    st.markdown("<div class='control-panel'>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Control Panel")
        generate_btn = st.button("⚡ Run AI Algorithm", type="primary")
        # Placeholder for real-time console updates
        log_placeholder = st.empty()

    with col2:
        st.info("""
        **IUB Generation Rules Applied:**
        - Maximum daily lecture limit respected.
        - No teacher/room/batch overlaps.
        - Friday Jumma Break enforced.
        - Room Availability hours respected.
        - Automatic "Not Assigned" for missing data.
        """)
    st.markdown("</div>", unsafe_allow_html=True)

    if 'generated_schedule' not in st.session_state:
        st.session_state.generated_schedule = None

    if generate_btn:
        start_time = time.time()
        
        # Callback to update the terminal-style log
        def update_log(message):
            elapsed = time.time() - start_time
            log_placeholder.markdown(f"""
                <div class='console-log'>
                    > [{elapsed:.1f}s] {message}<br>
                    > AI is processing...
                </div>
            """, unsafe_allow_html=True)

        update_log("Initializing IUB AI Engine...")
        engine = TimetableEngine(db_session, status_callback=update_log)
        
        success, result = engine.generate()
        
        if success:
            st.session_state.generated_schedule = result
            update_log("✅ Optimization Complete! Loading data visualization...")
            st.success("Timetable generated successfully!")
        else:
            st.error(f"❌ {result}")
            st.session_state.generated_schedule = None

    # ==========================================
    # RESULTS & VISUALIZATION SECTION
    # ==========================================
    if st.session_state.generated_schedule:
        st.markdown("---")
        
        # 1. Fetch data for mapping IDs to Names
        teachers = {t.id: t.name for t in get_all_teachers(db_session)}
        teachers[-1] = "Not Assigned"
        
        rooms = {r.id: r.room_name for r in get_all_rooms(db_session)}
        rooms[-1] = "Not Assigned"
        
        subjects = {s.id: f"{s.course_code}: {s.subject_name}" for s in get_all_subjects(db_session)}
        
        raw_batches = get_all_batches(db_session)
        batch_map = {b.id: {"sem": f"Semester {b.semester_level}", "sec": f"Section {b.section_name}"} for b in raw_batches}

        # 2. Transform into readable DataFrame
        formatted_data = []
        for entry in st.session_state.generated_schedule:
            b_info = batch_map.get(entry["batch_id"], {"sem": "N/A", "sec": "N/A"})
            formatted_data.append({
                "Semester": b_info["sem"],
                "Section": b_info["sec"],
                "Day": entry["day"],
                "Time": f"{entry['start_time']} - {entry['end_time']}",
                "Subject": subjects.get(entry["subject_id"], "Unknown"),
                "Teacher": teachers.get(entry["teacher_id"], "Not Assigned"),
                "Room": rooms.get(entry["room_id"], "Not Assigned")
            })
            
        df = pd.DataFrame(formatted_data)
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        df['Day'] = pd.Categorical(df['Day'], categories=day_order, ordered=True)

        # 3. Interactive Tabs for Different Views
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🎓 View by Semester", "👨‍🏫 View by Teacher", "🏫 View by Room", "🗄️ Master Table", "📥 Export"
        ])
        
        with tab1:
            sem_list = sorted(df['Semester'].unique())
            sel_sem = st.selectbox("🎯 Select Semester", sem_list)
            
            sem_df = df[df['Semester'] == sel_sem]
            sec_list = sorted(sem_df['Section'].unique())
            sel_sec = st.radio("📂 Select Section", sec_list, horizontal=True)
            
            final_view = sem_df[sem_df['Section'] == sel_sec]
            
            try:
                # Pivot for the classic timetable grid view
                pivot_grid = final_view.pivot(index="Time", columns="Day", values="Subject").fillna("-")
                st.markdown(f"### 📅 Weekly Plan: {sel_sem} ({sel_sec})")
                st.table(pivot_grid)
            except:
                st.dataframe(final_view, use_container_width=True)

        with tab2:
            t_list = sorted(df['Teacher'].unique())
            sel_t = st.selectbox("Select Teacher", t_list)
            st.dataframe(df[df['Teacher'] == sel_t][['Day', 'Time', 'Semester', 'Section', 'Subject', 'Room']], use_container_width=True)

        with tab3:
            r_list = sorted(df['Room'].unique())
            sel_r = st.selectbox("Select Room", r_list)
            st.dataframe(df[df['Room'] == sel_r][['Day', 'Time', 'Semester', 'Section', 'Subject', 'Teacher']], use_container_width=True)

        with tab4:
            st.subheader("Master Department Schedule")
            st.dataframe(df.sort_values(['Semester', 'Section', 'Day', 'Time']), use_container_width=True)

        with tab5:
            st.subheader("📥 Official Exports")
            exp_col1, exp_col2, exp_col3 = st.columns(3)

            # CSV Download
            csv_data = df.to_csv(index=False).encode('utf-8')
            exp_col1.download_button("Download CSV", csv_data, "iub_timetable.csv", "text/csv", use_container_width=True)

            # Excel Download (XLSX)
            xlsx_buffer = io.BytesIO()
            with pd.ExcelWriter(xlsx_buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Timetable')
            exp_col2.download_button("Download XLSX", xlsx_buffer.getvalue(), "iub_timetable.xlsx", use_container_width=True)

            # PDF Download
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt="The Islamia University of Bahawalpur", ln=True, align='C')
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 10, txt="Department of Artificial Intelligence - Official Timetable", ln=True, align='C')
            pdf.ln(10)
            
            pdf.set_font("Arial", size=9)
            # Add headers
            pdf.cell(30, 8, "Day", 1)
            pdf.cell(30, 8, "Time", 1)
            pdf.cell(40, 8, "Class", 1)
            pdf.cell(90, 8, "Subject", 1)
            pdf.ln()

            for _, row in df.sort_values(['Semester', 'Section', 'Day']).iterrows():
                pdf.cell(30, 8, str(row['Day']), 1)
                pdf.cell(30, 8, str(row['Time']), 1)
                pdf.cell(40, 8, f"{row['Semester']}-{row['Section']}", 1)
                pdf.cell(90, 8, str(row['Subject'][:45]), 1) # Truncate long names
                pdf.ln()
            
            exp_col3.download_button("Download PDF", pdf.output(dest='S').encode('latin-1'), "iub_timetable.pdf", "application/pdf", use_container_width=True)
