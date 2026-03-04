import streamlit as st
from database.crud import get_global_settings, update_global_settings

def render_settings_page(db_session):
    st.title("⚙️ Global University Settings")
    st.markdown("Set the master rules for the timetable algorithm. The algorithm will strictly follow these boundaries.")

    # Fetch current settings from the database
    current_settings = get_global_settings(db_session)

    # Use a Streamlit form so the database is only updated when the user clicks 'Save'
    with st.form("settings_form"):
        st.subheader("🕰️ Operating Hours")
        col1, col2 = st.columns(2)
        with col1:
            open_time = st.time_input("University Open Time", value=current_settings.uni_open_time)
        with col2:
            close_time = st.time_input("University Close Time", value=current_settings.uni_close_time)

        st.markdown("---")
        
        st.subheader("🕌 Jumma Break Settings")
        col3, col4 = st.columns(2)
        with col3:
            jumma_start = st.time_input("Jumma Break Start", value=current_settings.jumma_break_start)
        with col4:
            jumma_end = st.time_input("Jumma Break End", value=current_settings.jumma_break_end)

        st.markdown("---")

        st.subheader("⏳ Academic Rules")
        col5, col6 = st.columns(2)
        with col5:
            credit_mins = st.number_input(
                "Duration of 1 Credit Hour (Minutes)", 
                min_value=30, 
                max_value=120, 
                value=current_settings.credit_hour_duration_mins,
                step=5,
                help="If a subject is 3 credit hours, and this is set to 60, the algorithm will block 180 minutes."
            )
        with col6:
            st.markdown("<br>", unsafe_allow_html=True) # Just for vertical alignment spacing
            sun_off = st.checkbox("Keep Sunday Completely Off", value=current_settings.sunday_off)

        # Submit button for the form
        submitted = st.form_submit_button("💾 Save Global Settings", use_container_width=True)

        if submitted:
            # Logic: Validate times (Open time must be before Close time)
            if open_time >= close_time:
                st.error("❌ Open Time must be earlier than Close Time.")
            elif jumma_start >= jumma_end:
                st.error("❌ Jumma Break Start must be earlier than End time.")
            else:
                # Call the CRUD function to update the database
                update_global_settings(
                    session=db_session,
                    open_time=open_time,
                    close_time=close_time,
                    jumma_start=jumma_start,
                    jumma_end=jumma_end,
                    credit_mins=credit_mins,
                    sun_off=sun_off
                )
                st.success("✅ Global settings updated successfully! The algorithm will now use these new rules.")
