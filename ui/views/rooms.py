import streamlit as st
from database.crud import add_room, get_all_rooms, delete_room

def render_rooms_page(db_session):
    st.title("🏫 Manage Rooms & Labs")
    st.markdown("Add classrooms and computer labs, define their capacities, and manage existing spaces.")

    # Create two columns: Left (1 part width) for adding, Right (2 parts width) for viewing
    col1, col2 = st.columns([1, 2], gap="large")

    # ==========================================
    # LEFT COLUMN: ADD NEW ROOM FORM
    # ==========================================
    with col1:
        st.subheader("➕ Add New Space")
        # clear_on_submit ensures the form resets after a successful save
        with st.form("add_room_form", clear_on_submit=True):
            room_name = st.text_input("Room Name / Number", placeholder="e.g., Room 304, AI Lab 1")
            capacity = st.number_input("Maximum Student Capacity", min_value=10, max_value=300, value=50, step=5)
            is_lab = st.checkbox("🧪 This is a Computer/Hardware Lab")
            
            submit_btn = st.form_submit_button("Save Room", use_container_width=True)

            if submit_btn:
                # Basic validation
                if not room_name.strip():
                    st.error("❌ Room Name cannot be empty.")
                else:
                    # Call the CRUD function
                    success, message = add_room(
                        session=db_session, 
                        name=room_name.strip(), 
                        capacity=capacity, 
                        is_lab=is_lab
                    )
                    
                    if success:
                        st.success(message)
                        st.rerun() # Forces Streamlit to instantly refresh and show the new data
                    else:
                        st.error(message)

    # ==========================================
    # RIGHT COLUMN: VIEW & MANAGE EXISTING ROOMS
    # ==========================================
    with col2:
        st.subheader("📋 Existing Rooms")
        rooms = get_all_rooms(db_session)

        if not rooms:
            st.info("No rooms added yet. Use the form on the left to add your first room.")
        else:
            # We build a custom table layout using Streamlit columns for full control
            
            # Table Header
            h1, h2, h3, h4 = st.columns([2, 1, 1, 1])
            h1.markdown("**Room Name**")
            h2.markdown("**Capacity**")
            h3.markdown("**Type**")
            h4.markdown("**Action**")
            st.markdown("---")

            # Table Rows (Loop through the database records)
            for room in rooms:
                r1, r2, r3, r4 = st.columns([2, 1, 1, 1])
                r1.write(room.room_name)
                r2.write(f"👥 {room.capacity}")
                r3.write("🧪 Lab" if room.is_lab else "🏫 Class")
                
                # Delete button requires a unique key so Streamlit knows exactly which one was clicked
                if r4.button("🗑️ Delete", key=f"del_room_{room.id}", help="Remove this room"):
                    if delete_room(db_session, room.id):
                        st.toast(f"Deleted {room.room_name}!") # A small popup notification
                        st.rerun() # Refresh UI to remove the deleted row
                    else:
                        st.error("Failed to delete room.")
