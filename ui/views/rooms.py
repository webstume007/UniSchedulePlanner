import streamlit as st
from database.crud import add_room, get_all_rooms, delete_room
from datetime import time

def render_rooms_page(db_session):
    # IUB Specific Styling for this page
    st.markdown("""
        <style>
        .main-title { color: #006837; font-weight: bold; }
        .stButton>button { border-radius: 5px; }
        .add-card { 
            background-color: #f0f9f4; 
            padding: 20px; 
            border-radius: 10px; 
            border: 1px solid #d1e7dd; 
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 class='main-title'>🏫 Manage Rooms & Availability</h1>", unsafe_allow_html=True)
    st.markdown("Define IUB classroom/lab capacities and set the **specific time windows** these rooms are available for scheduling.")

    # Layout: Form on Left, Table on Right
    col1, col2 = st.columns([1, 2], gap="large")

    # ==========================================
    # LEFT COLUMN: ADD NEW ROOM FORM
    # ==========================================
    with col1:
        st.markdown("<div class='add-card'>", unsafe_allow_html=True)
        st.subheader("➕ Add New Space")
        
        with st.form("add_room_form", clear_on_submit=True):
            room_name = st.text_input("Room Name / Number", placeholder="e.g., AI Lab 01, Room 302")
            capacity = st.number_input("Maximum Student Capacity", min_value=10, max_value=300, value=50, step=5)
            is_lab = st.checkbox("🧪 This is a Computer/Hardware Lab")
            
            st.markdown("---")
            st.markdown("**⏰ Availability Window**")
            st.caption("Each room at IUB can have specific operating hours.")
            
            t_start = st.time_input("Available From", value=time(8, 0))
            t_end = st.time_input("Available To", value=time(16, 0))
            
            submit_btn = st.form_submit_button("Save Room to Database", use_container_width=True)

            if submit_btn:
                if not room_name.strip():
                    st.error("❌ Room Name is required.")
                elif t_start >= t_end:
                    st.error("❌ 'Available From' must be earlier than 'Available To'.")
                else:
                    # UPDATED CRUD CALL: Now passing time objects
                    success, message = add_room(
                        session=db_session, 
                        name=room_name.strip(), 
                        capacity=capacity, 
                        is_lab=is_lab,
                        available_from=t_start,
                        available_to=t_end
                    )
                    
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
        st.markdown("</div>", unsafe_allow_html=True)

    # ==========================================
    # RIGHT COLUMN: VIEW & MANAGE EXISTING ROOMS
    # ==========================================
    with col2:
        st.subheader("📋 IUB Room Roster")
        rooms = get_all_rooms(db_session)

        if not rooms:
            st.info("No rooms found in the system.")
        else:
            # Table Header with Time Columns
            h1, h2, h3, h4, h5 = st.columns([1.5, 0.8, 0.8, 1.5, 0.8])
            h1.markdown("**Room**")
            h2.markdown("**Cap**")
            h3.markdown("**Type**")
            h4.markdown("**Availability**")
            h5.markdown("**Action**")
            st.markdown("---")

            for room in rooms:
                r1, r2, r3, r4, r5 = st.columns([1.5, 0.8, 0.8, 1.5, 0.8])
                
                # Room & Capacity
                r1.write(f"**{room.room_name}**")
                r2.write(f"👥 {room.capacity}")
                r3.write("🧪 Lab" if room.is_lab else "🏫 Class")
                
                # Display the Time Window
                # Formatting time to 12-hour format for readability
                start_str = room.available_from.strftime("%I:%M %p")
                end_str = room.available_to.strftime("%I:%M %p")
                r4.write(f"🕒 {start_str} - {end_str}")
                
                # Delete Action
                if r5.button("🗑️", key=f"del_room_{room.id}", help=f"Delete {room.room_name}"):
                    if delete_room(db_session, room.id):
                        st.toast(f"Deleted {room.room_name}!")
                        st.rerun()
                    else:
                        st.error("Delete failed.")
