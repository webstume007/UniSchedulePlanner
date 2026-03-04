import streamlit as st
from database.crud import add_batch_section, get_all_batches, get_all_subjects
from database.schema import BatchSection

def render_batches_page(db_session):
    st.title("🎓 Manage Batches & Sections")
    st.markdown("Define semesters, sections, student counts, and assign the curriculum for each batch.")

    col1, col2 = st.columns([1, 2], gap="large")

    # Fetch subjects for the curriculum assignment
    available_subjects = get_all_subjects(db_session)
    subject_map = {f"{sub.course_code} - {sub.subject_name}": sub.id for sub in available_subjects}

    # ==========================================
    # LEFT COLUMN: ADD NEW BATCH FORM
    # ==========================================
    with col1:
        st.subheader("➕ Add New Section")
        
        if not available_subjects:
            st.warning("⚠️ Please add subjects to the curriculum first.")
        
        with st.form("add_batch_form", clear_on_submit=True):
            # Using standard BS Artificial Intelligence structure
            semester = st.number_input("Semester Level", min_value=1, max_value=8, value=3, step=1, help="e.g., 3 for 3rd Semester")
            section = st.text_input("Section Name", placeholder="e.g., A, B, or Morning")
            strength = st.number_input("Student Strength", min_value=5, max_value=200, value=50, step=5, help="Total number of students in this specific section.")
            
            selected_subject_labels = st.multiselect(
                "Assign Curriculum (Subjects)", 
                options=list(subject_map.keys()),
                help="Select all subjects this specific section will study this semester."
            )
            
            submit_btn = st.form_submit_button("Save Batch Profile", use_container_width=True)

            if submit_btn:
                if not section.strip():
                    st.error("❌ Section Name is required.")
                elif not selected_subject_labels:
                    st.error("❌ You must assign at least one subject to this batch.")
                else:
                    selected_ids = [subject_map[label] for label in selected_subject_labels]
                    
                    success, message = add_batch_section(
                        session=db_session,
                        semester=semester,
                        section=section.strip().upper(),
                        strength=strength,
                        subject_ids=selected_ids
                    )
                    
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

    # ==========================================
    # RIGHT COLUMN: VIEW & MANAGE EXISTING BATCHES
    # ==========================================
    with col2:
        st.subheader("📋 Active Batches")
        batches = get_all_batches(db_session)

        if not batches:
            st.info("No batches added yet.")
        else:
            # Table Header
            h1, h2, h3, h4 = st.columns([1.5, 1, 3, 1])
            h1.markdown("**Semester & Section**")
            h2.markdown("**Strength**")
            h3.markdown("**Curriculum**")
            h4.markdown("**Action**")
            st.markdown("---")

            # Table Rows
            # Sorting the batches by semester level for better readability
            for batch in sorted(batches, key=lambda x: (x.semester_level, x.section_name)):
                r1, r2, r3, r4 = st.columns([1.5, 1, 3, 1])
                r1.write(f"**Semester {batch.semester_level} - {batch.section_name}**")
                r2.write(f"👥 {batch.student_strength}")
                
                # Show assigned subjects
                subject_tags = " ".join([f"`{sub.course_code}`" for sub in batch.curriculum_subjects])
                r3.write(subject_tags if subject_tags else "No subjects")
                
                if r4.button("🗑️ Delete", key=f"del_batch_{batch.id}"):
                    try:
                        obj_to_delete = db_session.query(BatchSection).filter(BatchSection.id == batch.id).first()
                        if obj_to_delete:
                            db_session.delete(obj_to_delete)
                            db_session.commit()
                            st.toast(f"Deleted Semester {batch.semester_level} - {batch.section_name}!")
                            st.rerun()
                    except Exception:
                        db_session.rollback()
                        st.error("Error deleting batch.")
