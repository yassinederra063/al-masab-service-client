import streamlit as st
from auth import login
from database import save_user, load_users
from admin import admin_panel
from prof import prof_panel
from surveillant import surveillant_panel
from directeur import directeur_panel

# =========================
# 🟢 إعداد الصفحة
# =========================
st.set_page_config(
    page_title="School System",
    layout="wide"
)

# 🔴 زيد هذا الكود هنا
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
[data-testid="stToolbar"] {display: none;}
[data-testid="stDecoration"] {display: none;}
[data-testid="stStatusWidget"] {display: none;}
[data-testid="stDeployButton"] {display: none;}
</style>
""", unsafe_allow_html=True)

# =========================
# 🟢 إنشاء admin أول مرة
# =========================
if "init" not in st.session_state:
    df = load_users()

    if df.empty:
        save_user(
            "yassinederra@service",
            "yassinederra.2009",
            "admin",
            "Yassine",
            "Derra",
            "-",   # phone
            "-"    # subject
        )

    st.session_state.init = True

# =========================
# 🟢 تسجيل الدخول
# =========================
if "login" not in st.session_state:
    st.session_state["login"] = False

if not st.session_state["login"]:
    login()

# =========================
# 🟢 بعد تسجيل الدخول
# =========================
else:
    role = st.session_state.get("role", "")
    name = st.session_state.get("name", "")

    # Sidebar
    st.sidebar.title("📊 Dashboard")
    st.sidebar.write(f"👤 {name}")
    st.sidebar.write(f"🔑 Role: {role}")

    # زر logout
    if st.sidebar.button("🚪 تسجيل الخروج"):
        st.session_state.clear()
        st.rerun()

    st.sidebar.divider()

    # =========================
    # 🟢 توجيه حسب الدور
    # =========================
    if role == "admin":
        admin_panel()

    elif role == "prof":
        prof_panel()

    elif role == "surveillant":
        surveillant_panel()

    elif role == "directeur":
        directeur_panel()

    else:
        st.error("❌ دور غير معروف")
