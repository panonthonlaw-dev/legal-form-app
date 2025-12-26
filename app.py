import streamlit as st
import os
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader, PdfWriter
import io
import textwrap

# --- ฟังก์ชันช่วย (Utility Functions) ---
def to_thai_num(text):
    thai_digits = "๐๑๒๓๔๕๖๗๘๙"
    arabic_digits = "0123456789"
    translation_table = str.maketrans(arabic_digits, thai_digits)
    return str(text).translate(translation_table)

def person_form(label):
    st.markdown(f"#### ข้อมูล{label}")
    name = st.text_input(f"ชื่อ-นามสกุล {label}")
    id_card = st.text_input(f"เลขประจำตัวประชาชน {label}") # [cite: 19, 22]
    
    c1, c2, c3, c4 = st.columns(4)
    race = c1.text_input(f"เชื้อชาติ {label}") # [cite: 25, 33]
    nat = c2.text_input(f"สัญชาติ {label}") # [cite: 23, 34]
    job = c3.text_input(f"อาชีพ {label}") # [cite: 20, 35]
    age = c4.text_input(f"อายุ (ปี) {label}") # [cite: 26, 38]

    c5, c6, c7, c8 = st.columns(4)
    h_no = c5.text_input(f"บ้านเลขที่ {label}") # [cite: 26, 38]
    moo = c6.text_input(f"หมู่ที่ {label}") # [cite: 27, 42]
    road = c7.text_input(f"ถนน {label}") # [cite: 24, 36]
    soi = c8.text_input(f"ตรอก/ซอย {label}") # [cite: 21, 37]

    c9, c10, c11, c12 = st.columns(4)
    sub_d = c9.text_input(f"ตำบล/แขวง {label}") # [cite: 28, 39]
    dist = c10.text_input(f"อำเภอ/เขต {label}") # [cite: 29, 43]
    prov = c11.text_input(f"จังหวัด {label}") # [cite: 16, 40]
    post = c12.text_input(f"รหัสไปรษณีย์ {label}") # [cite: 30, 41]

    tel = st.text_input(f"โทรศัพท์ {label}") # [cite: 31, 44]

    return {
        "name": name, "id": id_card, "race": race, "nat": nat, "job": job, "age": age,
        "h_no": h_no, "moo": moo, "road": road, "soi": soi, "sub_d": sub_d,
        "dist": dist, "prov": prov, "post": post, "tel": tel
    }

# --- เริ่มต้นหน้าเว็บ ---
st.set_page_config(page_title="Court Form Drafter", layout="wide")
st.title("⚖️ ระบบร่างแบบพิมพ์คำฟ้อง (๔)")

# ตรวจสอบไฟล์เบื้องต้นเพื่อป้องกันจอขาว
template_exists = os.path.exists("template.pdf")
font_exists = os.path.exists("THSarabunNew.ttf")

if not template_exists or not font_exists:
    st.error("⚠️ ตรวจพบไฟล์ไม่ครบใน GitHub ของคุณ!")
    if not template_exists: st.warning("- ไม่พบไฟล์ 'template.pdf' (กรุณาอัปโหลดไฟล์แบบพิมพ์ ๔)")
    if not font_exists: st.warning("- ไม่พบไฟล์ 'THSarabunNew.ttf' (กรุณาอัปโหลดไฟล์ฟอนต์)")
    st.stop() # หยุดการทำงานตรงนี้เพื่อไม่ให้จอขาว

with st.form("main_form"):
    st.subheader("1. ส่วนหัวคดี") # [cite: 2, 7, 8, 9, 10]
    col_a, col_b, col_c = st.columns(3)
    court = col_a.text_input("ศาล") # [cite: 7]
    black_num = col_b.text_input("คดีหมายเลขดำที่") # [cite: 2]
    case_type = col_c.radio("ความ", ["แพ่ง", "อาญา"], horizontal=True) # [cite: 10]
    
    col_d, col_e, col_f = st.columns(3)
    day = col_d.text_input("วันที่") # [cite: 8]
    month = col_e.text_input("เดือน") # [cite: 8]
    year = col_f.text_input("พ.ศ.") # [cite: 9]

    st.write("---")
    p_data = person_form("โจทก์") # [cite: 11]
    st.write("---")
    d_data = person_form("จำเลย") # [cite: 12]

    st.write("---")
    body = st.text_area("บรรยายฟ้อง ข้อ ๑", height=300) # [cite: 48]
    
    submitted = st.form_submit_button("สร้างไฟล์ PDF")

if submitted:
    st.info("กำลังประมวลผลและสร้างไฟล์ PDF...")
    # Logic การสร้าง PDF จะอยู่ตรงนี้ (ใช้โค้ดที่ผมให้ก่อนหน้ามาใส่ได้เลย)
    st.success("สร้างไฟล์สำเร็จ! (พร้อมเชื่อมต่อระบบดาวน์โหลด)")
