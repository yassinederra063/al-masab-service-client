import streamlit as st  
import pandas as pd  
import random  
import string  
from database import get_connection  
from sqlalchemy import text  
  
def generate_password():  
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))  
  
def generate_login(name, lastname):  
    return f"{name.lower().replace(' ', '')}{lastname.lower().replace(' ', '')}@taalim.ma"  
  
def find_column(columns, keywords):  
    for key in keywords:  
        for col in columns:  
            if key in str(col).lower():  
                return col  
    return None  
  
def directeur_panel():  
    st.markdown("<h1 style='text-align: center;'>🤵 لوحة المدير</h1>", unsafe_allow_html=True)  
      
    menu = [  
        "➕ إضافة قسم جديد (Excel)",   
        "🗑️ حذف قسم",  
        "👤 إضافة تلميذ يدوي",   
        "🚫 توقيف تلميذ",   
        "✅ إرجاع تلميذ موقوف",  
        "📊 إحصائيات الغياب الأسبوعي",  
        "🔐 إضافة Login"  
    ]  
  
    choice = st.sidebar.selectbox("القائمة", menu)  
    conn = get_connection()  
  
    # ===============================  
    # ➕ إضافة قسم + Excel  
    # ===============================  
    if choice == "➕ إضافة قسم جديد (Excel)":  
        level = st.selectbox("السلك", ["الأولى إعدادي","الثانية إعدادي","الثالثة إعدادي","جدع مشترك"])  
        class_num = st.text_input("القسم")  
        file = st.file_uploader("Excel")  
  
        if st.button("حفظ"):  
            if file:  
                df = pd.read_excel(file).fillna("")  
  
                conn.execute(text("""  
                INSERT INTO classes (level,class_num)  
                VALUES (:level,:class_num)  
                ON CONFLICT DO NOTHING  
                """), {"level": level, "class_num": class_num})  
  
                result = conn.execute(text("""  
                    SELECT id FROM classes WHERE level=:level AND class_num=:class_num  
                """), {"level": level, "class_num": class_num}).fetchone()  
  
                c_id = result[0]  
  
                df.columns = df.columns.str.strip()

                for _, row in df.iterrows():  
                    conn.execute(text("""  
                    INSERT INTO students (name,lastname,birth,number,gender,class_id,status)  
                    VALUES (:name,:lastname,:birth,:number,:gender,:class_id,'active')  
                    """), {  
                         "name": row["الإسم"],
                         "lastname": row["النسب"],
                         "birth": row["تاريخ الإزدياد"],
                         "number": row["ر.ت"],   # ✅ هذا هو لي نسيتي
                         "gender": row["النوع"],
                         "class_id": c_id  
                    })  
  
                conn.commit()  
                st.success("تم")  
  
    # ===============================  
    # 🗑️ حذف قسم  
    # ===============================  
    elif choice == "🗑️ حذف قسم":  
        df = pd.read_sql("SELECT * FROM classes", conn)  
  
        if not df.empty:  
            selected = st.selectbox("اختار القسم", df["id"])  
  
            if st.button("حذف"):  
  
                conn.execute(text("""  
                    DELETE FROM attendance WHERE student_id IN  
                    (SELECT id FROM students WHERE class_id=:id)  
                """), {"id": selected})  
  
                conn.execute(text("DELETE FROM students WHERE class_id=:id"), {"id": selected})  
                conn.execute(text("DELETE FROM classes WHERE id=:id"), {"id": selected})  
  
                conn.commit()  
                st.success("تم الحذف")  
                st.rerun()  
  
    # ===============================  
    # 👤 إضافة تلميذ  
    # ===============================  
    elif choice == "👤 إضافة تلميذ يدوي":  
        name = st.text_input("الإسم")  
        lastname = st.text_input("النسب")  
        level = st.text_input("السلك")  
        class_num = st.text_input("القسم")  
  
        if st.button("إضافة"):  
  
            res = conn.execute(text("""  
                SELECT id FROM classes WHERE level=:level AND class_num=:class_num  
            """), {"level": level, "class_num": class_num}).fetchone()  
  
            if res:  
                conn.execute(text("""  
                INSERT INTO students (name,lastname,class_id,status)  
                VALUES (:name,:lastname,:class_id,'active')  
                """), {"name": name, "lastname": lastname, "class_id": res[0]})  
  
                conn.commit()  
                st.success("تمت الإضافة")  
            else:  
                st.error("القسم غير موجود")  
  
    # ===============================  
    # 🚫 توقيف تلميذ  
    # ===============================  
    elif choice == "🚫 توقيف تلميذ":  
        students = pd.read_sql("SELECT id, name, lastname FROM students WHERE status='active'", conn)  
  
        if not students.empty:  
            selected = st.selectbox("اختار التلميذ", students["id"])  
  
            if st.button("توقيف"):  
                conn.execute(text("UPDATE students SET status='stopped' WHERE id=:id"), {"id": selected})  
                conn.commit()  
                st.success("تم التوقيف")  
                st.rerun()  
  
    # ===============================  
    # ✅ إرجاع تلميذ  
    # ===============================  
    elif choice == "✅ إرجاع تلميذ موقوف":  
        students = pd.read_sql("SELECT id, name, lastname FROM students WHERE status='stopped'", conn)  
  
        if not students.empty:  
            selected = st.selectbox("اختار التلميذ", students["id"])  
  
            if st.button("إرجاع"):  
                conn.execute(text("UPDATE students SET status='active' WHERE id=:id"), {"id": selected})  
                conn.commit()  
                st.success("تم الإرجاع")  
                st.rerun()  
  
    # ===============================  
    # 📊 إحصائيات الغياب  
    # ===============================  
    elif choice == "📊 إحصائيات الغياب الأسبوعي":  
        df = pd.read_sql("""  
        SELECT s.name, s.lastname, COUNT(*) as total_abs  
        FROM attendance a  
        JOIN students s ON a.student_id = s.id  
        WHERE a.allowed = 0  
        GROUP BY s.name, s.lastname  
        ORDER BY total_abs DESC  
        """, conn)  
  
        if df.empty:  
            st.info("لا توجد بيانات")  
        else:  
            st.dataframe(df)  
  
    # ===============================  
    # 🔐 إنشاء Login  
    # ===============================  
    elif choice == "🔐 إضافة Login":  
        name = st.text_input("الإسم")  
        lastname = st.text_input("النسب")  
        role = st.selectbox("الدور", ["prof", "surveillant"])  
  
        if st.button("إنشاء"):  
            login = generate_login(name, lastname)  
            password = generate_password()  
  
            conn.execute(text("""  
            INSERT INTO users (login,password,role,name,lastname,status)  
            VALUES (:login,:password,:role,:name,:lastname,'active')  
            """), {  
                "login": login,  
                "password": password,  
                "role": role,  
                "name": name,  
                "lastname": lastname  
            })  
  
            conn.commit()  
  
            st.success(f"Login: {login}")  
            st.warning(f"Password: {password}")  
  
    conn.close()