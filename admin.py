import streamlit as st
import random
import string
import pandas as pd
from database import get_connection, get_system_status, set_system_status
from sqlalchemy import text

def generate_password():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))

def generate_login(name, lastname):
    return f"{name.lower()}{lastname.lower()}@taalim.ma"

def admin_panel():
    st.title("🧑‍🔧 Service technique")

    conn = get_connection()
    df = pd.read_sql("SELECT * FROM users", conn)
    conn.close()

    st.info("login: yassinederra@service")

    name = st.text_input("الإسم")
    lastname = st.text_input("النسب")
    phone = st.text_input("الهاتف")
    subject = st.text_input("المادة")
    role = st.selectbox("الدور", ["prof", "surveillant", "directeur"])

    if st.button("إنشاء حساب"):
        login = generate_login(name, lastname)
        password = generate_password()

        conn = get_connection()

        conn.execute(text("""
        INSERT INTO users (login, password, role, name, lastname, phone, subject, status)
        VALUES (:login,:password,:role,:name,:lastname,:phone,:subject,'active')
        """), {
            "login": login,
            "password": password,
            "role": role,
            "name": name,
            "lastname": lastname,
            "phone": phone,
            "subject": subject
        })

        conn.commit()
        conn.close()

        st.success(login)
        st.warning(password)
        st.rerun()

    st.dataframe(df)

    user = st.selectbox("اختار user", df["login"])

    # =========================
    # 🚫 توقيف user
    # =========================
    if st.button("توقيف"):
        conn = get_connection()
        conn.execute(text("UPDATE users SET status='stopped' WHERE login=:login"), {"login": user})
        conn.commit()
        conn.close()
        st.rerun()

    # =========================
    # 🗑️ حذف user
    # =========================
    if st.button("حذف"):
        conn = get_connection()
        conn.execute(text("DELETE FROM users WHERE login=:login"), {"login": user})
        conn.commit()
        conn.close()
        st.rerun()

    # =========================
    # 🔌 التحكم في النظام
    # =========================
    st.divider()
    status = get_system_status()
    st.write(f"حالة النظام الحالية: {status}")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("إيقاف النظام 🚫"):
            set_system_status("off")
            st.rerun()
    with c2:
        if st.button("تشغيل النظام ✅"):
            set_system_status("on")
            st.rerun()