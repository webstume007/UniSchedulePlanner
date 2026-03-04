import streamlit as st
from database.crud import add_subject, get_all_subjects
from database.schema import Subject  # Imported so we can safely delete without modifying crud.py

def render_subjects_page(db_session):
    st.title("📚 Manage Subjects & Curriculum")
    st.markdown("Define the courses taught in the department. You must add subjects here before assigning them to Teachers or Batches.")

    col1, col2 = st.columns([1, 2], gap="large")

    # ==========================================
    # LEFT COLUMN: ADD NEW SUBJECT FORM
    # ==========================================
    with col1:
        st.subheader("➕ Add New Subject")
        with st.form("add_subject_form", clear_on_submit=True):
            course_code = st.text_input("Course Code", placeholder="e.g., AIF-301")
            subject_name = st.text_input("Subject Name", placeholder="e.g., Artificial Intelligence")
            
            # University credit hours typically range from 1 to 4
            credit_hours = st.number_input("Total Credit Hours", min_value=1, max_value=6, value=3, step=1)
            
            requires_lab = st.checkbox("🧪 Requires Computer Lab")
            
            submit_btn = st.form_submit_button("Save Subject", use_container_width=True)

            if submit_btn:
                if not course_code.strip() or not subject_name.strip():
                    st.error("❌ Course Code and Subject Name are required.")
                else:
                    # Convert code to uppercase automatically for consistency (e.g., aif-301 -> AIF-301)
                    success, message = add_subject(
                        session=db_session,
                        code=course_code.strip().upper(),
                        name=subject_name.strip(),
                        credit_hours=credit_hours,
                        requires_lab=requires_lab
                    )
                    
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

    # ==========================================
    # RIGHT COLUMN: VIEW & MANAGE EXISTING SUBJECTS
    # ==========================================
    with col2:
        st.subheader("📋 Existing Curriculum")
        subjects = get_all_subjects(db_session)

        if not subjects:
            st.info("No subjects added yet. Use the form on the left to build the curriculum.")
        else:
            # Table Header - 5 columns for subjects
            h1, h2, h3, h4, h5 = st.columns([1.5, 2.5, 1, 1, 1])
            h1.markdown("**Code**")
            h2.markdown("**Subject Name**")
            h3.markdown("**Cr. Hrs**")
            h4.markdown("**Type**")
            h5.markdown("**Action**")
            st.markdown("---")

            # Table Rows
            for subject in subjects:
                r1, r2, r3, r4, r5 = st.columns([1.5, 2.5, 1, 1, 1])
                r1.write(f"`{subject.course_code}`")
                r2.write(subject.subject_name)
                r3.write(str(subject.total_credit_hours))
                r4.write("🧪 Lab" if subject.requires_lab else "📚 Theory")
                
                # Inline delete logic
                if r5.button("🗑️ Delete", key=f"del_sub_{subject.id}"):
                    try:
                        # Fetch the exact object and delete it
                        obj_to_delete = db_session.query(Subject).filter(Subject.id == subject.id).first()
                        if obj_to_delete:
                            db_session.delete(obj_to_delete)
                            db_session.commit()
                            st.toast(f"Deleted {subject.course_code}!")
                            st.rerun()
                    except Exception:
                        db_session.rollback()
                        st.error("Cannot delete subject. It might already be assigned to a teacher or batch.")
