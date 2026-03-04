import streamlit as st
from database.schema import init_db

# -------------------------------------------------------------------
# PAGE CONFIGURATION & IUB THEME
# -------------------------------------------------------------------
st.set_page_config(
    page_title="IUB AI Dept - Timetable Generator",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed" # We are moving menu to the top
)

# Custom CSS for IUB Branding (Green & White) and Top Navigation
st.markdown("""
    <style>
    /* IUB Green Theme Colors */
    :root {
        --iub-green: #006837;
    }
    
    .stApp { background-color: #ffffff; }
    
    /* Header Styling */
    .iub-header {
        background-color: var(--iub-green);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Button Styling */
    div.stButton > button:first-child {
        background-color: var(--iub-green);
        color: white;
        border: none;
    }
    
    /* Hide the default sidebar completely */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* Main container padding */
    .block-container {
        padding-top: 2rem;
    }
    </style>
    
    <div class="iub-header">
        <h1 style='margin:0;'>The Islamia University of Bahawalpur</h1>
        <p style='margin:0; opacity: 0.9;'>Department of Artificial Intelligence - Timetable Management System</p>
    </div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# DATABASE INITIALIZATION
# -------------------------------------------------------------------
if 'db_session' not in st.session_state:
    st.session_state.db_session = init_db()

# -------------------------------------------------------------------
# TOP NAVIGATION MENU (Replacing Sidebar)
# -------------------------------------------------------------------
# menu_options are kept identical to your previous code for syncing
menu_options = [
    "📊 Dashboard Overview",
    "⚙️ Global Settings",
    "🏫 Manage Rooms",
    "📚 Manage Subjects",
    "👨‍🏫 Manage Teachers",
    "🎓 Manage Batches",
    "🚀 Generate Timetable"
]

# Using segmented_control for a clean, horizontal top menu
selection = st.segmented_control(
    "Select Page", 
    options=menu_options, 
    default="📊 Dashboard Overview",
    label_visibility="collapsed"
)

st.markdown("---")

# -------------------------------------------------------------------
# ROUTING (Loading the correct page based on selection)
# -------------------------------------------------------------------

if selection == "📊 Dashboard Overview":
    from ui.views import dashboard
    dashboard.render_dashboard_page(st.session_state.db_session)

elif selection == "⚙️ Global Settings":
    from ui.views import settings 
    settings.render_settings_page(st.session_state.db_session)

elif selection == "🏫 Manage Rooms":
    from ui.views import rooms
    rooms.render_rooms_page(st.session_state.db_session)

elif selection == "📚 Manage Subjects":
    from ui.views import subjects
    subjects.render_subjects_page(st.session_state.db_session)

elif selection == "👨‍🏫 Manage Teachers":
    from ui.views import teachers
    teachers.render_teachers_page(st.session_state.db_session)

elif selection == "🎓 Manage Batches":
    from ui.views import batches
    batches.render_batches_page(st.session_state.db_session)

elif selection == "🚀 Generate Timetable":
    # Now correctly importing and rendering the generator page
    from ui.views import timetable
    timetable.render_timetable_page(st.session_state.db_session)

# Footer
st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.8rem; margin-top: 50px;'>
        Developed for IUB AI Department © 2026
    </div>
""", unsafe_allow_html=True)
