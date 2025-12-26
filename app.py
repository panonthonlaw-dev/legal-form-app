import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader, PdfWriter
import io
import textwrap

# ฟังก์ชันแปลงเลขไทย
def to_thai_num(text):
    thai_digits = "๐๑๒๓๔๕๖๗๘๙"
    arabic_digits = "0123456789"
    translation_table = str.maketrans(arabic_digits, thai_digits)
    return str(text).translate(translation_table)

# ฟังก์ชันสร้างข้อมูลคน (โจทก์/จำเลย) แยกช่อง
def person_form(label):
    st.markdown(f"#### ข้อมูล{label}")
    name = st.text_input(f"ชื่อ-นามสกุล {label}")
    id_card = st.text_input(f"เลขประจำตัวประชาชน {label}") # [cite: 19, 22]
    
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
    race = c1.text_input(f"เชื้อชาติ {label}") # [cite: 25, 33]
    nat = c2.text_input(f"สัญชาติ {label}") # [cite: 23, 34]
    job = c3.text_input(f"อาชีพ {label}") # [cite: 20, 35]
    age = c4.text_input(f"อายุ (ปี) {label}") # [cite: 26, 38]

    c5, c6, c7, c8 = st.columns([1, 1, 1, 1])
    h_no = c5.text_input(f"บ้านเลขที่ {label}") # [cite: 26, 38]
    moo = c6.text_input(f"หมู่ที่ {label}") # [cite: 27, 42]
    road = c7.text_input(f"ถนน {label}") # [cite: 24, 36]
    soi = c8.text_input(f"ตรอก/ซอย {label}") # [cite: 21, 37]

    c9, c10, c11, c12 = st.columns([1, 1, 1, 1])
    sub_d = c9.text_input(f"ตำบล/แขวง {label}") # [cite: 28, 39]
    dist = c10.text_input(f"อำเภอ/เขต {label}") # [cite: 29, 43]
    prov = c11.text_input(f"จังหวัด {label}") # [cite: 16, 40]
    post = c12.text_input(f"รหัสไปรษณีย์ {label}") # [cite: 30, 41]

    c13, c14, c15 = st.columns(3)
    tel = c13.text_input(f"โทรศัพท์ {label}") # [cite: 31, 44]
    fax = c14.text_input(f"โทรสาร {label}") # [cite: 17, 45]
    email = c15.text_input(f"อีเมล {label}") # [cite: 32, 46]

    return {
        "name": name, "id": id_card, "race": race, "nat": nat, "job": job, "age": age,
        "h_no": h_no, "moo": moo, "road": road, "soi": soi, "sub_d": sub_d,
        "dist": dist, "prov": prov, "post": post, "tel": tel, "fax": fax, "email": email
    }

# --- ส่วนการคำนวณตำแหน่งลง PDF ---
def draw_party_details(can, data, start_y):
    # บรรทัดที่ 1: เลขบัตร, เชื้อชาติ
    can.drawString(185, start_y, to_thai_num(data['id']))
    can.drawString(510, start_y, data['race'])
    
    # บรรทัดที่ 2: สัญชาติ, อาชีพ, อายุ, บ้านเลขที่, หมู่
    y2 = start_y - 26
    can.drawString(100, y2, data['nat'])
    can.drawString(250, y2, data['job'])
    can.drawString(455, y2, to_thai_num(data['age']))
    can.drawString(530, y2, to_thai_num(data['h_no']))
    can.drawString(585, y2, to_thai_num(data['moo']))
    
    # บรรทัดที่ 3: ถนน, ซอย, ตำบล, อำเภอ
    y3 = y2 - 26
    can.drawString(100, y3, data['road'])
    can.drawString(250, y3, data['soi'])
    can.drawString(400, y3, data['sub_d'])
    can.drawString(530, y3, data['dist'])
    
    # บรรทัดที่ 4: จังหวัด, รหัสไปรษณีย์, โทรศัพท์
    y4 = y3 - 26
    can.drawString(100, y4, data['prov'])
    can.drawString(380, y4, to_thai_num(data['post']))
    can.drawString(485, y4, to_thai_num(data['tel']))

    # บรรทัดที่ 5: โทรสาร, อีเมล
    y5 = y4 - 26
    can.drawString(100, y5, to_thai_num(data['fax']))
    can.drawString(300, y5, data['email'])

# --- Web Interface ---
st.set_page_config(page_title="Court Form Drafter", layout="wide")
st.title("⚖️ ระบบร่างแบบพิมพ์คำฟ้อง (๔)")

with st.form("main_form"):
    # ส่วนหัวคดี
    st.subheader("1. ส่วนหัวคดี") # [cite: 2-10]
    col_a, col_b, col_c = st.columns(3)
    court = col_a.text_input("ศาล")
    black_num = col_b.text_input("คดีหมายเลขดำที่")
    case_type = col_c.radio("ความ", ["แพ่ง", "อาญา"], horizontal=True)
    
    col_d, col_e, col_f = st.columns(3)
    day = col_d.text_input("วันที่")
    month = col_e.text_input("เดือน")
    year = col_f.text_input("พ.ศ.")

    # ข้อมูลคู่ความ
    st.write("---")
    plaintiff_data = person_form("โจทก์") # 
    st.write("---")
    defendant_data = person_form("จำเลย") # [cite: 12, 18]

    # เนื้อหาฟ้อง
    st.write("---")
    body = st.text_area("บรรยายฟ้อง ข้อ ๑", height=300) # 
    
    if st.form_submit_button("สร้างไฟล์ PDF"):
        # ในที่นี้จะเรียกฟังก์ชัน Merge PDF ที่เตรียมไว้
        st.success("เตรียมพิกัดและข้อมูลพร้อมแล้ว!")
