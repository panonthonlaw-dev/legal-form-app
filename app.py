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
    can = canvas.Canvas(packet, pagesize=(595.27, 841.89)) # ขนาด A4
    
    # ลงทะเบียนฟอนต์ (ต้องมีไฟล์ THSarabunNew.ttf ในโปรเจกต์)
    try:
        pdfmetrics.registerFont(TTFont('ThaiFont', 'THSarabunNew.ttf'))
        can.setFont('ThaiFont', 16)
    except:
        can.setFont('Helvetica', 12) # สำรองกรณีไม่มีฟอนต์

    # --- ส่วนหัว (Header) ตามรูปภาพที่คุณแนบมา ---
    # 1. คดีหมายเลขดำที่ 
    can.drawString(445, 765, to_thai_num(data['black_case'])) 
    
    # 2. ศาล 
    can.drawString(355, 705, data['court_name'])
    
    # 3. วันที่ เดือน พุทธศักราช 
    can.drawString(310, 678, to_thai_num(data['day']))
    can.drawString(365, 678, data['month'])
    can.drawString(495, 678, to_thai_num(data['year']))
    
    # 4. ความ (อาญา/แพ่ง) 
    can.drawString(340, 652, data['case_type'])

    # --- ส่วนคู่ความ และ เนื้อหา ---
    can.drawString(200, 612, data['plaintiff']) # โจทก์ [cite: 11]
    can.drawString(200, 562, data['defendant']) # จำเลย [cite: 12]

    # บรรยายฟ้อง ข้อ ๑ [cite: 48]
    text_object = can.beginText(135, 480)
    text_object.setFont('ThaiFont', 16)
    lines = textwrap.wrap(data['body'], width=75)
    for line in lines:
        text_object.textLine(to_thai_num(line))
    can.drawText(text_object)

    can.save()
    packet.seek(0)
    return packet

# --- หน้าจอ Web App ---
st.title("⚖️ ระบบร่างคำฟ้องอัตโนมัติ")

with st.form("legal_form"):
    col1, col2 = st.columns(2)
    with col1:
        court = st.text_input("ศาล ", "อาญา")
        black_case = st.text_input("คดีหมายเลขดำที่ ", "123/2567")
        case_type = st.radio("ความ ", ["อาญา", "แพ่ง"], horizontal=True)
    
    with col2:
        day = st.text_input("วันที่ [cite: 8]", "1")
        month = st.text_input("เดือน [cite: 8]", "มกราคม")
        year = st.text_input("พ.ศ. [cite: 9]", "2567")

    plaintiff = st.text_input("โจทก์ [cite: 11]")
    defendant = st.text_input("จำเลย [cite: 12]")
    body = st.text_area("บรรยายฟ้อง ข้อ ๑ [cite: 48]", height=200)
    
    submit = st.form_submit_button("สร้างไฟล์ PDF")

if submit:
    data = {
        'court_name': court, 'black_case': black_case, 'case_type': case_type,
        'day': day, 'month': month, 'year': year,
        'plaintiff': plaintiff, 'defendant': defendant, 'body': body
    }
    
    overlay = create_pdf_overlay(data)
    
    # Merge กับ Template (ต้องมีไฟล์ชื่อ template.pdf)
    try:
        existing_pdf = PdfReader(open("template.pdf", "rb"))
        output = PdfWriter()
        page = existing_pdf.pages[0]
        page.merge_page(PdfReader(overlay).pages[0])
        output.add_page(page)
        
        final_pdf = io.BytesIO()
        output.write(final_pdf)
        
        st.success("สร้างไฟล์สำเร็จ!")
        st.download_button("ดาวน์โหลดคำฟ้อง (PDF)", final_pdf.getvalue(), "lawsuit.pdf")
    except FileNotFoundError:
        st.error("ไม่พบไฟล์ template.pdf กรุณาอัปโหลดไฟล์ต้นฉบับเข้า GitHub")
