import streamlit as st
from database.crud import add_teacher, get_all_teachers, get_all_subjects
from database.schema import Teacher

def render_teachers_page(db_session):
    st.title("👨‍🏫 Manage Faculty & Teachers")
    st.markdown("Add instructors and assign the specific subjects they are qualified to teach.")

    col1, col2 = st.columns([1, 2], gap="large")

    # Fetch subjects first so we can use them in the dropdown form
    available_subjects = get_all_subjects(db_session)
    # Create a mapping dictionary: {"AIF-301 - Artificial Intelligence": 1}
    # This allows us to show a friendly name but save the actual database ID.
    subject_map = {f"{sub.course_code} - {sub.subject_name}": sub.id for sub in available_subjects}

    # ==========================================
    # LEFT COLUMN: ADD NEW TEACHER FORM
    # ==========================================
    with col1:
        st.subheader("➕ Add Instructor")
        
        if not available_subjects:
            st.warning("⚠️ Please add subjects in the 'Manage Subjects' page before adding teachers.")
        
        with st.form("add_teacher_form", clear_on_submit=True):
            teacher_name = st.text_input("Full Name", placeholder="e.g., Dr. Ali Raza")
            cnic = st.text_input("CNIC (Optional)", placeholder="e.g., 31202-1234567-1")
            contact = st.text_input("Contact Number (Optional)", placeholder="e.g., 0300-1234567")
            
            # Multi-select dropdown for subjects
            selected_subject_labels = st.multiselect(
                "Subjects Qualified to Teach", 
                options=list(subject_map.keys()),
                help="Select all courses this teacher can handle. The algorithm will only assign them these courses."
            )
            
            submit_btn = st.form_submit_button("Save Teacher Profile", use_container_width=True)

            if submit_btn:
                if not teacher_name.strip():
                    st.error("❌ Teacher Name is required.")
                elif not selected_subject_labels:
                    st.error("❌ You must assign at least one subject to the teacher.")
                else:
                    # Convert the selected string labels back into database IDs
                    selected_ids = [subject_map[label] for label in selected_subject_labels]
                    
                    success, message = add_teacher(
                        session=db_session,
                        name=teacher_name.strip(),
                        cnic=cnic.strip() if cnic else None,
                        contact=contact.strip() if contact else None,
                        subject_ids=selected_ids
                    )
                    
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

    # ==========================================
    # RIGHT COLUMN: VIEW & MANAGE EXISTING TEACHERS
    # ==========================================
    with col2:
        st.subheader("📋 Faculty Roster")
        teachers = get_all_teachers(db_session)

        if not teachers:
            st.info("No teachers added yet.")
        else:
            # Table Header
            h1, h2, h3 = st.columns([1.5, 3, 1])
            h1.markdown("**Instructor Name**")
            h2.markdown("**Qualified Subjects**")
            h3.markdown("**Action**")
            st.markdown("---")

            # Table Rows
            for teacher in teachers:
                r1, r2, r3 = st.columns([1.5, 3, 1])
                r1.write(f"**{teacher.name}**")
                
                # Extract subject codes from the relationship and format them as tags
                subject_tags = " ".join([f"`{sub.course_code}`" for sub in teacher.subjects_can_teach])
                r2.write(subject_tags if subject_tags else "No subjects assigned")
                
                # Inline delete logic
                if r3.button("🗑️ Delete", key=f"del_teacher_{teacher.id}"):
                    try:
                        obj_to_delete = db_session.query(Teacher).filter(Teacher.id == teacher.id).first()
                        if obj_to_delete:
                            db_session.delete(obj_to_delete)
                            db_session.commit()
                            st.toast(f"Deleted {teacher.name}'s profile!")
                            st.rerun()
                    except Exception:
                        db_session.rollback()
                        st.error("Error deleting teacher profile.")
