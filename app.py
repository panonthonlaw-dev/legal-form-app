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

def create_pdf_overlay(data):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(595.27, 841.89))
    
    # ลงทะเบียนฟอนต์ไทย (ต้องอัปโหลดไฟล์ THSarabunNew.ttf ไว้ใน Repo)
    try:
        pdfmetrics.registerFont(TTFont('ThaiFont', 'THSarabunNew.ttf'))
        can.setFont('ThaiFont', 15) # ขนาดฟอนต์มาตรฐานศาล
    except:
        can.setFont('Helvetica', 12)

    # --- [ส่วนที่ 1] หัวกระดาษ ---
    can.drawString(445, 764, to_thai_num(data['black_num'])) # คดีหมายเลขดำที่ [cite: 2]
    can.drawString(360, 706, data['court']) # ศาล [cite: 7]
    can.drawString(308, 680, to_thai_num(data['day'])) # วันที่ [cite: 8]
    can.drawString(365, 680, data['month']) # เดือน [cite: 8]
    can.drawString(495, 680, to_thai_num(data['year'])) # พุทธศักราช [cite: 9]
    can.drawString(340, 652, data['case_type']) # ความ 

    # --- [ส่วนที่ 2] คู่ความ (ระหว่าง...) ---
    can.drawString(250, 595, data['plaintiff_name']) # ชื่อโจทก์ [cite: 11]
    can.drawString(250, 550, data['defendant_name']) # ชื่อจำเลย [cite: 12]

    # --- [ส่วนที่ 3] ข้อมูลรายละเอียดโจทก์ (ข้าพเจ้า...) ---
    # บรรทัดข้าพเจ้า
    can.drawString(245, 524, data['plaintiff_name']) # ข้าพเจ้า 
    # บรรทัดที่อยู่และเลขบัตร (ปรับพิกัดตามตำแหน่งในไฟล์ภาพ) [cite: 19, 26, 27, 28, 29]
    can.drawString(185, 498, to_thai_num(data['plaintiff_id'])) # เลขประจำตัวประชาชน [cite: 19]
    can.drawString(500, 498, data['plaintiff_race']) # เชื้อชาติ [cite: 25]
    # บรรทัดที่อยู่บรรทัดที่ 2
    can.drawString(100, 472, data['plaintiff_address']) 

    # --- [ส่วนที่ 4] เนื้อหาฟ้อง ข้อ ๑ ---
    text_object = can.beginText(135, 235) # พิกัดช่อง ข้อ ๑ [cite: 48]
    text_object.setFont('ThaiFont', 15)
    lines = textwrap.wrap(data['body'], width=80)
    for line in lines:
        text_object.textLine(to_thai_num(line))
    can.drawText(text_object)

    can.save()
    packet.seek(0)
    return packet

# --- UI Layout ---
st.set_page_config(page_title="Draft Court Form", layout="centered")
st.title("📝 ร่างคำฟ้อง (แบบพิมพ์ ๔)")

with st.form("court_form"):
    st.subheader("1. ส่วนหัวคดี")
    col1, col2 = st.columns(2)
    with col1:
        court = st.text_input("ศาล", "แพ่ง")
        black_num = st.text_input("คดีหมายเลขดำที่")
        case_type = st.radio("ความ", ["แพ่ง", "อาญา"], horizontal=True)
    with col2:
        day = st.text_input("วันที่", "26")
        month = st.text_input("เดือน", "ธันวาคม")
        year = st.text_input("พ.ศ.", "2568")

    st.subheader("2. ข้อมูลโจทก์")
    p_name = st.text_input("ชื่อ-นามสกุล โจทก์")
    p_id = st.text_input("เลขบัตรประชาชนโจทก์")
    p_race = st.text_input("เชื้อชาติ/สัญชาติโจทก์", "ไทย")
    p_addr = st.text_area("ที่อยู่โจทก์โดยละเอียด")

    st.subheader("3. ข้อมูลจำเลย")
    d_name = st.text_input("ชื่อ-นามสกุล จำเลย")
    d_addr = st.text_area("ที่อยู่จำเลย (ถ้ามี)")

    st.subheader("4. เนื้อหาฟ้อง")
    body = st.text_area("บรรยายฟ้อง ข้อ ๑", height=250)
    
    submitted = st.form_submit_button("Preview & Generate PDF")

if submitted:
    # Logic การรวมไฟล์เหมือนเดิม (อย่าลืม template.pdf และฟอนต์)
    st.info("กำลังประมวลผลข้อมูลลงในแบบฟอร์มศาล...")
