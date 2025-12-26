import streamlit as st
import os
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader, PdfWriter
import io
import textwrap

# --- 1. ฟังก์ชันช่วย (Utility Functions) ---
def to_thai_num(text):
    thai_digits = "๐๑๒๓๔๕๖๗๘๙"
    arabic_digits = "0123456789"
    translation_table = str.maketrans(arabic_digits, thai_digits)
    return str(text).translate(translation_table)

def draw_party_details(can, data, start_y):
    # บรรทัดที่ 1: เลขประจำตัวประชาชน [cite: 19, 22], เชื้อชาติ [cite: 25, 33]
    can.drawString(185, start_y, to_thai_num(data['id']))
    can.drawString(510, start_y, data['race'])
    
    # บรรทัดที่ 2: สัญชาติ [cite: 23, 34], อาชีพ [cite: 20, 35], อายุ [cite: 26, 38], บ้านเลขที่ [cite: 26, 38], หมู่ [cite: 27, 42]
    y2 = start_y - 26
    can.drawString(100, y2, data['nat'])
    can.drawString(250, y2, data['job'])
    can.drawString(455, y2, to_thai_num(data['age']))
    can.drawString(530, y2, to_thai_num(data['h_no']))
    can.drawString(585, y2, to_thai_num(data['moo']))
    
    # บรรทัดที่ 3: ถนน [cite: 24, 36], ซอย [cite: 21, 37], ตำบล [cite: 28, 39], อำเภอ [cite: 29, 43]
    y3 = y2 - 26
    can.drawString(100, y3, data['road'])
    can.drawString(250, y3, data['soi'])
    can.drawString(400, y3, data['sub_d'])
    can.drawString(530, y3, data['dist'])
    
    # บรรทัดที่ 4: จังหวัด [cite: 16, 40], รหัสไปรษณีย์ [cite: 30, 41], โทรศัพท์ [cite: 31, 44]
    y4 = y3 - 26
    can.drawString(100, y4, data['prov'])
    can.drawString(380, y4, to_thai_num(data['post']))
    can.drawString(485, y4, to_thai_num(data['tel']))

def create_pdf_overlay(data):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(595.27, 841.89))
    pdfmetrics.registerFont(TTFont('ThaiFont', 'THSarabunNew.ttf'))
    can.setFont('ThaiFont', 15)

    # ส่วนหัว: เลขดำ [cite: 2, 3], ศาล [cite: 7], วันที่[cite: 8, 9], ความ
    can.drawString(445, 764, to_thai_num(data['black_num']))
    can.drawString(360, 706, data['court'])
    can.drawString(308, 680, to_thai_num(data['day']))
    can.drawString(365, 680, data['month'])
    can.drawString(495, 680, to_thai_num(data['year']))
    can.drawString(340, 652, data['case_type'])

    # คู่ความ (ระหว่าง...) [cite: 11, 12]
    can.drawString(250, 595, data['plaintiff']['name'])
    can.drawString(250, 550, data['defendant']['name'])

    # รายละเอียดโจทก์ (ข้าพเจ้า...) [cite: 15]
    can.drawString(245, 524, data['plaintiff']['name'])
    draw_party_details(can, data['plaintiff'], 498)

    # รายละเอียดจำเลย (ขอยื่นฟ้อง...) [cite: 18]
    can.drawString(245, 314, data['defendant']['name'])
    draw_party_details(can, data['defendant'], 288)

    # เนื้อหาฟ้อง ข้อ ๑ [cite: 48]
    text_object = can.beginText(135, 145) # พิกัดเริ่มบรรทัดแรกของ ข้อ ๑
    text_object.setFont('ThaiFont', 15)
    lines = textwrap.wrap(data['body'], width=80)
    for line in lines:
        text_object.textLine(to_thai_num(line))
    can.drawText(text_object)

    can.save()
    packet.seek(0)
    return packet

def person_form(label):
    st.markdown(f"#### ข้อมูล{label}")
    name = st.text_input(f"ชื่อ-นามสกุล {label}")
    id_card = st.text_input(f"เลขประจำตัวประชาชน {label}")
    c1, c2, c3, c4 = st.columns(4)
    race = c1.text_input(f"เชื้อชาติ {label}")
    nat = c2.text_input(f"สัญชาติ {label}")
    job = c3.text_input(f"อาชีพ {label}")
    age = c4.text_input(f"อายุ (ปี) {label}")
    c5, c6, c7, c8 = st.columns(4)
    h_no = c5.text_input(f"บ้านเลขที่ {label}")
    moo = c6.text_input(f"หมู่ที่ {label}")
    road = c7.text_input(f"ถนน {label}")
    soi = c8.text_input(f"ตรอก/ซอย {label}")
    c9, c10, c11, c12 = st.columns(4)
    sub_d = c9.text_input(f"ตำบล/แขวง {label}")
    dist = c10.text_input(f"อำเภอ/เขต {label}")
    prov = c11.text_input(f"จังหวัด {label}")
    post = c12.text_input(f"รหัสไปรษณีย์ {label}")
    tel = st.text_input(f"โทรศัพท์ {label}")
    return {"name": name, "id": id_card, "race": race, "nat": nat, "job": job, "age": age,
            "h_no": h_no, "moo": moo, "road": road, "soi": soi, "sub_d": sub_d,
            "dist": dist, "prov": prov, "post": post, "tel": tel}

# --- 2. หน้าเว็บ (Main Interface) ---
st.set_page_config(page_title="Court Form Drafter", layout="wide")
st.title("⚖️ ระบบร่างแบบพิมพ์คำฟ้อง (๔)")

if not os.path.exists("template.pdf") or not os.path.exists("THSarabunNew.ttf"):
    st.error("⚠️ ขาดไฟล์ template.pdf หรือ THSarabunNew.ttf")
    st.stop()

with st.form("main_form"):
    st.subheader("1. ส่วนหัวคดี")
    ca, cb, cc = st.columns(3)
    court = ca.text_input("ศาล")
    black_num = cb.text_input("คดีหมายเลขดำที่")
    case_type = cc.radio("ความ", ["แพ่ง", "อาญา"], horizontal=True)
    cd, ce, cf = st.columns(3)
    day, month, year = cd.text_input("วันที่"), ce.text_input("เดือน"), cf.text_input("พ.ศ.")

    st.write("---")
    p_data = person_form("โจทก์")
    st.write("---")
    d_data = person_form("จำเลย")
    st.write("---")
    body = st.text_area("บรรยายฟ้อง ข้อ ๑", height=250)
    
    if st.form_submit_button("สร้างไฟล์ PDF"):
        # รวบรวมข้อมูล
        all_data = {
            'black_num': black_num, 'court': court, 'case_type': case_type,
            'day': day, 'month': month, 'year': year,
            'plaintiff': p_data, 'defendant': d_data, 'body': body
        }
        
        try:
            # 1. ลองสร้าง Overlay
            st.write("🔄 กำลังเตรียมข้อมูล...") # Debug log
            overlay = create_pdf_overlay(all_data)
            
            # 2. ลองเปิด Template
            if not os.path.exists("template.pdf"):
                st.error("❌ หาไฟล์ template.pdf ไม่เจอ")
                st.stop()
                
            existing_pdf = PdfReader(open("template.pdf", "rb"))
            output = PdfWriter()
            
            # 3. ลอง Merge ไฟล์
            st.write("🔄 กำลังรวมข้อมูลลงในแบบฟอร์ม...") # Debug log
            page = existing_pdf.pages[0]
            page.merge_page(PdfReader(overlay).pages[0])
            output.add_page(page)
            
            # 4. เขียนไฟล์ลง Memory
            final_pdf = io.BytesIO()
            output.write(final_pdf)
            pdf_bytes = final_pdf.getvalue()
            
            if len(pdf_bytes) > 0:
                st.success("✅ สร้างไฟล์สำเร็จ!")
                # ปุ่มดาวน์โหลดต้องอยู่ตรงนี้
                st.download_button(
                    label="💾 คลิกที่นี่เพื่อดาวน์โหลดไฟล์ PDF",
                    data=pdf_bytes,
                    file_name=f"คำฟ้อง_{p_data['name']}.pdf",
                    mime="application/pdf"
                )
            else:
                st.warning("⚠️ ไฟล์ที่สร้างมีขนาด 0 byte โปรดตรวจสอบข้อมูล")

        except Exception as e:
            # ถ้าเกิด Error อะไรก็ตาม ให้แสดงออกมาที่หน้าจอเลย
            st.error("❌ เกิดข้อผิดพลาดทางเทคนิค:")
            st.exception(e)
