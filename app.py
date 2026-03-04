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

# The menu options
menu_options = [
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
# We will create these view files one by one. For now, we will link the Settings page.

if selection == "⚙️ Global Settings":
    # Importing the view locally to prevent circular imports
    from ui.views import settings 
    settings.render_settings_page(st.session_state.db_session)

elif selection == "🏫 Manage Rooms":
    from ui.views import rooms
    rooms.render_rooms_page(st.session_state.db_session)

elif selection == "📚 Manage Subjects":
    st.title("📚 Manage Subjects")
    st.info("Subject management interface will be built next.")

elif selection == "👨‍🏫 Manage Teachers":
    st.title("👨‍🏫 Manage Teachers")
    st.info("Teacher management interface will be built next.")

elif selection == "🎓 Manage Batches":
    st.title("🎓 Manage Batches")
    st.info("Batch & Section management interface will be built next.")

elif selection == "🚀 Generate Timetable":
    st.title("🚀 Generate Timetable")
    st.info("The optimization engine and visual timetable will be connected here.")
