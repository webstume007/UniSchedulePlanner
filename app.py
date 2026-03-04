import streamlit as st
from database.schema import init_db

# -------------------------------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------------------------------
st.set_page_config(
    page_title="IUB AI Dept - Timetable Generator",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------------
# DATABASE INITIALIZATION
# -------------------------------------------------------------------
# We store the database session in Streamlit's session_state so it 
# persists across different button clicks and page reloads.
if 'db_session' not in st.session_state:
    st.session_state.db_session = init_db()

# -------------------------------------------------------------------
# SIDEBAR NAVIGATION
# -------------------------------------------------------------------
st.sidebar.title("📅 AI Dept Timetable")
st.sidebar.markdown("---")

# The menu options (Synced perfectly with the routing logic below)
menu_options = [
    "📊 Dashboard Overview",
    "⚙️ Global Settings",
    "🏫 Manage Rooms",
    "📚 Manage Subjects",
    "👨‍🏫 Manage Teachers",
    "🎓 Manage Batches",
    "🚀 Generate Timetable"
]

selection = st.sidebar.radio("Navigation", menu_options)

st.sidebar.markdown("---")
st.sidebar.info("Developed for The Islamia University of Bahawalpur (IUB) - AI Department.")

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
    st.title("🚀 Generate Timetable")
    st.info("The visual grid and algorithm engine will be connected here next.")
