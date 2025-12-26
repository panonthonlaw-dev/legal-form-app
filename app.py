import streamlit as st
from pypdf import PdfReader, PdfWriter
import io

st.set_page_config(page_title="ระบบร่างคำฟ้อง", layout="wide")

st.title("⚖️ ระบบร่างคำฟ้องอัตโนมัติ (แบบพิมพ์ ๔)")
st.subheader("กรอกข้อมูลเพื่อสร้างไฟล์ PDF")

# ส่วนที่ 1: ข้อมูลคดี [cite: 2, 3, 7, 8, 9]
with st.expander("1. ข้อมูลคดีและศาล", expanded=True):
    col1, col2 = st.columns(2)
    court_name = col1.text_input("ศาล [cite: 7]")
    black_case_num = col2.text_input("คดีหมายเลขดำที่ [cite: 2, 3]")
    
    col3, col4, col5 = st.columns(3)
    day = col3.text_input("วันที่ [cite: 8]")
    month = col4.text_input("เดือน [cite: 8]")
    year = col5.text_input("พุทธศักราช [cite: 9]")

# ส่วนที่ 2: ข้อมูลโจทก์และจำเลย [cite: 11, 12, 19, 33]
with st.expander("2. ข้อมูลคู่ความ"):
    st.write("### ข้อมูลโจทก์ [cite: 11]")
    plaintiff_name = st.text_input("ชื่อโจทก์ [cite: 11]")
    plaintiff_id = st.text_input("เลขประจำตัวประชาชนโจทก์ [cite: 19]")
    
    st.write("### ข้อมูลจำเลย [cite: 12]")
    defendant_name = st.text_input("ชื่อจำเลย [cite: 12]")
    defendant_id = st.text_input("เลขประจำตัวประชาชนจำเลย (ถ้าทราบ) [cite: 22]")

# ส่วนที่ 3: เนื้อหาคำฟ้อง [cite: 48]
st.write("### 3. เนื้อหาคำฟ้อง (ข้อ ๑) [cite: 48]")
case_body = st.text_area("บรรยายฟ้อง...", height=300)

# ปุ่มกด Generate PDF
if st.button("สร้างไฟล์คำฟ้อง (PDF)"):
    # (ในขั้นตอนนี้จะต้องมีการเขียน Logic การวาง Text ลงบน PDF)
    st.success("ระบบจำลองการสร้างไฟล์สำเร็จ! (ในโปรแกรมจริงจะใช้ pdfrw หรือ reportlab วางตำแหน่งเลขไทยตามแบบฟอร์ม )")
    
    # ตัวอย่างการ Export
    st.download_button(label="ดาวน์โหลดไฟล์ PDF", data="sample_data", file_name="output.pdf")
