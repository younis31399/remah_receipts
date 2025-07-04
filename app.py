import os
import sys
import datetime
import webbrowser
import arabic_reshaper
from bidi.algorithm import get_display
from num2words import num2words
import streamlit as st
from reportlab.lib.pagesizes import A6
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

# ========== تعيين مسارات آمنة ==========
def resource_path(relative_path):
    try:
        base_path = getattr(sys, 'MEIPASS', os.path.dirname(os.path.abspath(_file_)))
        return os.path.join(base_path, relative_path)
    except Exception:
        return relative_path

# ========== تهيئة الخط ==========
def setup_font():
    try:
        font_path = resource_path("amiri.ttf")
        if not os.path.exists(font_path):
            font_path = resource_path(os.path.join("fonts", "amiri.ttf"))
        if not os.path.exists(font_path):
            st.error("لم يتم العثور على ملف الخط amiri.ttf في مجلد السكربت")
            return False
        pdfmetrics.registerFont(TTFont("Amiri", font_path))
        return True
    except Exception as e:
        st.error(f"تعذر تحميل الخط:\n{str(e)}")
        return False

if not setup_font():
    st.stop()

# ========== إنشاء مجلد الوصولات ==========
receipts_dir = os.path.join(os.getcwd(), "الفواتير")
if not os.path.exists(receipts_dir):
    try:
        os.makedirs(receipts_dir)
    except Exception as e:
        st.error(f"تعذر إنشاء مجلد الفواتير:\n{str(e)}")
        st.stop()

# ========== دوال مساعدة ==========
def get_next_invoice_number():
    counter_file = os.path.join(os.getcwd(), "invoice_counter.txt")
    try:
        with open(counter_file, 'r') as f:
            last_num = int(f.read().strip())
    except:
        last_num = 0
    next_num = last_num + 1
    with open(counter_file, 'w') as f:
        f.write(str(next_num))
    return str(next_num).zfill(4)

def format_arabic(text):
    try:
        if any("\u0600" <= c <= "\u06FF" for c in text):
            reshaped = arabic_reshaper.reshape(text)
            return get_display(reshaped)
        return text
    except:
        return text

def number_to_arabic_words(number, currency_name):
    try:
        number = float(number)
        if number.is_integer():
            words = num2words(int(number), lang='ar')
        else:
            words = num2words(number, lang='ar')
        if words:
            return f"{words} {currency_name} فقط"
        return ""
    except:
        return ""

def create_receipt_pdf(name, from_name, place_of_receipt, vehicle_name, amount, reason, invoice_number, currency_code, currency_name):
    try:
        file_name = f"وصل_{invoice_number}_{name.replace(' ', '')}.pdf"
        file_path = os.path.join(receipts_dir, file_name)

        c = canvas.Canvas(file_path, pagesize=A6)
        width, height = A6

        # الترويسة
        c.setFillColorRGB(1, 0, 0)
        c.rect(0, height - 77, width, 10, fill=1, stroke=0)

        logo_path = resource_path("logo.png")
        if os.path.exists(logo_path):
            c.drawImage(logo_path, 125, height - 60, width=50, height=50, mask='auto')

        c.setFillColorRGB(1, 1, 1)
        c.setFont("Amiri", 8)
        c.drawCentredString(width / 2, height - 75, "RIMAH AL EAMAR COMPANY for General Contracting")

        c.setFillColorRGB(1, 0, 0)
        c.rect(0, height - 402, width, 10, fill=1, stroke=0)
        c.setFillColorRGB(1, 1, 1)
        c.setFont("Amiri", 8)
        c.drawCentredString(width / 2, height - 398, format_arabic("وصل استلام اجل وصل استلام اجل وصل استلام اجل وصل استلام اجل"))

        c.setFillColorRGB(0, 0, 0.5)
        c.setFont("Amiri", 12)
        c.drawRightString(width - 8, height - 20, format_arabic("شركة رماح الاعمار"))
        c.drawRightString(width - 8, height - 40, format_arabic("للتجارة والمقاولات"))
        c.drawRightString(width - 8, height - 60, format_arabic("العامة المحدودة"))
        c.drawRightString(width - 200, height - 20, format_arabic("الادارة المالية العامة"))
        c.drawRightString(width - 200, height - 40, format_arabic("قسم الحسابات "))
        c.drawRightString(width - 200, height - 60, format_arabic("حسابات مواقع العمل"))

        c.setFont("Amiri", 14)
        c.drawCentredString(width / 2, height - 100, format_arabic("وصل استلام آجل"))

        # الوقت الحالي (يسار)
        time_str = datetime.datetime.now().strftime("%I:%M %p")
        c.setFont("Amiri", 8)
        c.setFillColorRGB(0, 0, 0)
        c.drawString(15, height - 98, format_arabic(f"الوقت: {time_str}"))

        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Amiri", 8)
        c.drawString(8, height - 87, format_arabic(f"الــتـاريــخ: {date_str}"))

        c.setFillColorRGB(0, 0, 1)
        c.setFont("Amiri", 8)
        c.drawString(250, height - 87, format_arabic(f"الوصل: {invoice_number}"))

        y_pos = height - 120
        c.setFont("Amiri", 10)
        details = [
            f"{float(amount):,} {currency_code}",
            f"الصنف  المستحق: {name}",
            f"مسؤول   الموقع: {from_name}",
            f"اسم موقع العمل: {place_of_receipt}",
            f"الالية  او  مادة : {vehicle_name}",
            f"مبلغ  الاستحقاق: {number_to_arabic_words(amount, currency_name)}",
            f"الوصف او كمية : {reason}",
            "اسم وتوقيع مسؤول الموقع"
        ]

        for i, detail in enumerate(details):
            c.setFillColorRGB(1, 0, 0) if i == 0 else c.setFillColorRGB(0, 0, 0)
            c.drawRightString(width - 10, y_pos, format_arabic(detail))
            y_pos -= 25

        c.save()
        return file_path
    except Exception as e:
        st.error(f"فشل إنشاء الوصل:\n{str(e)}")
        return None

# ========== الواجهة ==========
st.set_page_config(page_title="برنامج وصل دفع آجل", layout="centered")
st.markdown(
    """<style> .title {font-family: 'Amiri';font-size: 36px;font-weight: bold;color: #0B3D91;text-align: center;margin-bottom: 30px;}
    .input-label {font-family: 'Amiri';font-size: 18px;color: #073763;margin-bottom: 5px;}
    .stTextInput>div>div>input {text-align: right !important;font-family: 'Amiri';font-size: 16px;}
    .stButton>button {background-color: #0B3D91;color: white;font-weight: bold;font-size: 18px;padding: 10px 20px;border-radius: 8px;}
    .stButton>button:hover {background-color: #08306B;color: #FFFFFF;}
    .footer {text-align: center;margin-top: 50px;color: #888888;font-size: 12px;}
    </style>""", unsafe_allow_html=True)
st.markdown('<div class="title">برنامج وصل دفع آجل</div>', unsafe_allow_html=True)

with st.form("receipt_form"):
    name = st.text_input("اسم الصنف:", placeholder="ادخل اسم الصنف")
    from_name = st.text_input("اسم مسؤول الموقع:", placeholder="ادخل اسم مسؤول الموقع")
    place_of_receipt = st.text_input("موقع العمل:", placeholder="ادخل اسم موقع العمل")
    vehicle_name = st.text_input("نوع الآلية:", placeholder="ادخل نوع الآلية")
    amount = st.text_input("المبلغ المستحق:", placeholder="ادخل المبلغ المستحق")
    currency = st.radio("اختر العملة:", ["دينار عراقي", "دولار أمريكي"], horizontal=True)
    reason = st.text_input("الوصف:", placeholder="ادخل وصف العمل")
    submit = st.form_submit_button("✔ معاينة الوصل")

if submit:
    if not all([name.strip(), from_name.strip(), place_of_receipt.strip(), vehicle_name.strip(), amount.strip(), reason.strip()]):
        st.warning("يرجى تعبئة جميع الحقول!")
    else:
        try:
            amount_float = float(amount.replace(',', ''))
            if amount_float <= 0:
                st.error("المبلغ يجب أن يكون أكبر من الصفر!")
            else:
                invoice_number = get_next_invoice_number()
                currency_code = "IQD" if currency == "دينار عراقي" else "USD"
                currency_name = "دينار عراقي" if currency == "دينار عراقي" else "دولار أمريكي"
                pdf_path = create_receipt_pdf(name, from_name, place_of_receipt, vehicle_name, amount, reason, invoice_number, currency_code, currency_name)
                if pdf_path:
                    st.success(f"تم إنشاء الوصل بنجاح: {pdf_path}")
                    with open(pdf_path, "rb") as f:
                        st.download_button(label="تحميل الوصل PDF", data=f, file_name=os.path.basename(pdf_path), mime="application/pdf")
                    try:
                        webbrowser.open(pdf_path)
                    except:
                        pass
                else:
                    st.error("فشل في إنشاء الوصل!")
        except ValueError:
            st.error("المبلغ يجب أن يكون رقماً صحيحاً أو عشرياً!")