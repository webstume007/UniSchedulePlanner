import streamlit as st
import pandas as pd
import io
from fpdf import FPDF
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

    # Persistent storage for the generated schedule - using session state
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
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "🎓 View by Batch", 
                "👨‍🏫 View by Teacher", 
                "🏫 View by Room", 
                "🗄️ Master Table",
                "📥 Download / Export"
            ])
            
            with tab1:
                batch_list = df['Batch / Class'].unique()
                selected_batch = st.selectbox("Select Batch to View", batch_list)
                batch_df = df[df['Batch / Class'] == selected_batch]
                try:
                    pivot_batch = batch_df.pivot(index="Time", columns="Day", values="Subject").fillna("-")
                    st.markdown(f"### Schedule for {selected_batch}")
                    st.table(pivot_batch)
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

            with tab5:
                st.subheader("Official Timetable Exports")
                st.write("Download the generated schedule in your preferred format:")
                
                exp_col1, exp_col2, exp_col3 = st.columns(3)

                # --- CSV Export ---
                csv = df.to_csv(index=False).encode('utf-8')
                exp_col1.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name='iub_timetable.csv',
                    mime='text/csv',
                    use_container_width=True
                )

                # --- Excel Export (XLSX) ---
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='IUB_Timetable')
                exp_col2.download_button(
                    label="📥 Download Excel (XLSX)",
                    data=excel_buffer.getvalue(),
                    file_name='iub_timetable.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    use_container_width=True
                )

                # --- PDF Export ---
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(200, 10, txt="IUB AI Department Timetable", ln=True, align='C')
                pdf.set_font("Arial", size=10)
                pdf.ln(10)
                
                # Simplified table for PDF
                for index, row in df.iterrows():
                    text = f"{row['Day']} | {row['Time']} | {row['Batch / Class']} | {row['Subject']} | {row['Teacher']} | {row['Room']}"
                    pdf.cell(0, 10, txt=text, ln=True)

                pdf_output = pdf.output(dest='S').encode('latin-1')
                exp_col3.download_button(
                    label="📥 Download PDF",
                    data=pdf_output,
                    file_name="iub_timetable.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
