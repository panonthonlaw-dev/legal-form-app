import streamlit as st
import os
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader, PdfWriter
import io
import textwrap

# --- 1. ฟังก์ชันสนับสนุน (Utility Functions) ---

def to_thai_num(text):
    """แปลงตัวเลขเป็นเลขไทย [cite: 3, 9, 13, 14, 19, 22, 26, 27, 30, 31, 38, 41, 42, 44]"""
    thai_digits = "๐๑๒๓๔๕๖๗๘๙"
    arabic_digits = "0123456789"
    translation_table = str.maketrans(arabic_digits, thai_digits)
    return str(text).translate(translation_table)

def draw_party_details(can, data, start_y):
    """วาดรายละเอียดที่อยู่และข้อมูลส่วนตัวลงใน PDF [cite: 16-32, 33-46]"""
    # บรรทัดที่ 1: เลขประจำตัวประชาชน, เชื้อชาติ
    can.drawString(185, start_y, to_thai_num(data['id'])) # [cite: 19, 22]
    can.drawString(510, start_y, data['race']) # [cite: 25, 33]
    
    # บรรทัดที่ 2: สัญชาติ, อาชีพ, อายุ, บ้านเลขที่, หมู่
    y2 = start_y - 26
    can.drawString(100, y2, data['nat']) # [cite: 23, 34]
    can.drawString(250, y2, data['job']) # [cite: 20, 35]
    can.drawString(455, y2, to_thai_num(data['age'])) # [cite: 26, 38]
    can.drawString(530, y2, to_thai_num(data['h_no'])) # [cite: 26, 38]
    can.drawString(585, y2, to_thai_num(data['moo'])) # [cite: 27, 42]
    
    # บรรทัดที่ 3: ถนน, ซอย, ตำบล, อำเภอ
    y3 = y2 - 26
    can.drawString(100, y3, data['road']) # [cite: 24, 36]
    can.drawString(250, y3, data['soi']) # [cite: 21, 37]
    can.drawString(400, y3, data['sub_d']) # [cite: 28, 39]
    can.drawString(530, y3, data['dist']) # [cite: 29, 43]
    
    # บรรทัดที่ 4: จังหวัด, รหัสไปรษณีย์, โทรศัพท์
    y4 = y3 - 26
    can.drawString(100, y4, data['prov']) # [cite: 16, 40]
    can.drawString(380, y4, to_thai_num(data['post'])) # [cite: 30, 41]
    can.drawString(485, y4, to_thai_num(data['tel'])) # [cite: 31, 44]

    # บรรทัดที่ 5: โทรสาร, ไปรษณีย์อิเล็กทรอนิกส์
    y5 = y4 - 26
    can.drawString(100, y5, to_thai_num(data['fax'])) # [cite: 17, 45]
    can.drawString(300, y5, data['email']) # [cite: 32, 46]

def create_pdf_overlay(data):
    """สร้างเลเยอร์ข้อมูลเพื่อวางทับแบบพิมพ์ (๔) [cite: 1]"""
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(595.27, 841.89))
    
    try:
        pdfmetrics.registerFont(TTFont('ThaiFont', 'THSarabunNew.ttf'))
        can.setFont('ThaiFont', 15)
    except:
        st.error("❌ ไม่พบไฟล์ฟอนต์ THSarabunNew.ttf")
        return None

    # 1. ส่วนหัวคดี [cite: 2-10]
    can.drawString(445, 764, to_thai_num(data['black_num'])) # คดีหมายเลขดำที่ [cite: 2, 3]
    can.drawString(360, 706, data['court']) # ศาล [cite: 7]
    can.drawString(308, 680, to_thai_num(data['day'])) # วันที่ [cite: 8]
    can.drawString(365, 680, data['month']) # เดือน [cite: 8]
    can.drawString(495, 680, to_thai_num(data['year'])) # พ.ศ. [cite: 9]
    can.drawString(340, 652, data['case_type']) # ความ [cite: 10]

    # 2. คู่ความและทุนทรัพย์ [cite: 4-6, 11-14]
    can.drawString(250, 595, data['plaintiff']['name']) # โจทก์ [cite: 11]
    can.drawString(250, 550, data['defendant']['name']) # จำเลย [cite: 12]
    can.drawString(250, 518, data['charge']) # ข้อหา [cite: 5]
    can.drawString(250, 492, to_thai_num(data['capital_baht'])) # บาท [cite: 6, 13]
    can.drawString(510, 492, to_thai_num(data['capital_stang'])) # สตางค์ [cite: 14]

    # 3. รายละเอียดโจทก์ (ข้าพเจ้า...) [cite: 15-32]
    can.drawString(245, 466, data['plaintiff']['name']) # [cite: 15]
    draw_party_details(can, data['plaintiff'], 440) 

    # 4. รายละเอียดจำเลย (ขอยื่นฟ้อง...) [cite: 18, 33-46]
    can.drawString(245, 258, data['defendant']['name']) # [cite: 18]
    draw_party_details(can, data['defendant'], 232)

    # 5. เนื้อหาฟ้อง ข้อ ๑ [cite: 48]
    text_object = can.beginText(135, 145)
    text_object.setFont('ThaiFont', 15)
    lines = textwrap.wrap(data['body'], width=80)
    for line in lines:
        text_object.textLine(to_thai_num(line))
    can.drawText(text_object)

    can.save()
    packet.seek(0)
    return packet

def person_form(label):
    """สร้างฟอร์มกรอกข้อมูลบุคคลแยกช่อง [cite: 19-32, 33-46]"""
    st.markdown(f"#### ข้อมูล{label}")
    name = st.text_input(f"ชื่อ-นามสกุล {label}")
    id_card = st.text_input(f"เลขบัตรประชาชน {label}")
    c1, c2, c3, c4 = st.columns(4)
    race = c1.text_input(f"เชื้อชาติ {label}")
    nat = c2.text_input(f"สัญชาติ {label}")
    job = c3.text_input(f"อาชีพ {label}")
    age = c4.text_input(f"อายุ {label}")
    c5, c6, c7, c8 = st.columns(4)
    h_no, moo, road, soi = c5.text_input(f"บ้านเลขที่ {label}"), c6.text_input(f"หมู่ {label}"), c7.text_input(f"ถนน {label}"), c8.text_input(f"ซอย {label}")
    c9, c10, c11, c12 = st.columns(4)
    sub_d, dist, prov, post = c9.text_input(f"แขวง {label}"), c10.text_input(f"เขต {label}"), c11.text_input(f"จังหวัด {label}"), c12.text_input(f"ไปรษณีย์ {label}")
    c13, c14, c15 = st.columns(3)
    tel, fax, email = c13.text_input(f"เบอร์โทร {label}"), c14.text_input(f"โทรสาร {label}"), c15.text_input(f"อีเมล {label}")
    return {"name": name, "id": id_card, "race": race, "nat": nat, "job": job, "age": age,
            "h_no": h_no, "moo": moo, "road": road, "soi": soi, "sub_d": sub_d,
            "dist": dist, "prov": prov, "post": post, "tel": tel, "fax": fax, "email": email}

# --- 2. หน้าจอหลักของ Web App ---

st.set_page_config(page_title="ระบบร่างคำฟ้อง", layout="wide")
st.title("⚖️ ระบบร่างแบบพิมพ์คำฟ้อง (๔)")

# ตรวจสอบไฟล์ในระบบ
if not os.path.exists("template.pdf") or not os.path.exists("THSarabunNew.ttf"):
    st.error("⚠️ ขาดไฟล์ template.pdf หรือ THSarabunNew.ttf ใน GitHub")
    st.stop()

with st.form("main_form"):
    st.subheader("1. ส่วนหัวคดีและทุนทรัพย์")
    ca, cb, cc = st.columns(3)
    court, black_num = ca.text_input("ศาล [cite: 7]"), cb.text_input("เลขดำ [cite: 2, 3]")
    case_type = cc.radio("ความ [cite: 10]", ["แพ่ง", "อาญา"], horizontal=True)
    cd, ce, cf = st.columns(3)
    day, month, year = cd.text_input("วันที่"), ce.text_input("เดือน"), cf.text_input("พ.ศ.")
    charge = st.text_input("ข้อหาหรือฐานความผิด [cite: 5]")
    cg, ch = st.columns(2)
    c_baht, c_stang = cg.text_input("ทุนทรัพย์ (บาท) [cite: 13]"), ch.text_input("สตางค์ [cite: 14]", value="00")

    st.write("---")
    p_data = person_form("โจทก์")
    st.write("---")
    d_data = person_form("จำเลย")
    st.write("---")
    body = st.text_area("บรรยายฟ้อง ข้อ ๑ [cite: 48]", height=250)
    
    if st.form_submit_button("สร้างไฟล์ PDF"):
        all_data = {
            'black_num': black_num, 'court': court, 'case_type': case_type,
            'day': day, 'month': month, 'year': year, 'charge': charge,
            'capital_baht': c_baht, 'capital_stang': c_stang,
            'plaintiff': p_data, 'defendant': d_data, 'body': body
        }
        try:
            overlay_packet = create_pdf_overlay(all_data)
            if overlay_packet:
                existing_pdf = PdfReader(open("template.pdf", "rb"))
                output = PdfWriter()
                page = existing_pdf.pages[0]
                page.merge_page(PdfReader(overlay_packet).pages[0])
                output.add_page(page)
                
                final_pdf = io.BytesIO()
                output.write(final_pdf)
                st.success("✅ สร้างไฟล์สำเร็จ!")
                st.download_button("💾 ดาวน์โหลดไฟล์ PDF", final_pdf.getvalue(), f"คำฟ้อง_{p_data['name']}.pdf")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")
