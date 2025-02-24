import streamlit as st
import pandas as pd
import os
from io import BytesIO
import matplotlib.pyplot as plt
from fpdf import FPDF
from PIL import Image

# Configure Streamlit app
st.set_page_config(page_title="Data Sweeper", layout="wide")


def df_to_pdf(df):
    buffer = BytesIO()
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    # Table Headers
    for col in df.columns:
        pdf.cell(40, 10, col, border=1)
    pdf.ln()

    # Table Data
    for _, row in df.iterrows():
        for col in df.columns:
            pdf.cell(40, 10, str(row[col]), border=1)
        pdf.ln()

    pdf.output("temp.pdf")  # Save temporarily
    with open("temp.pdf", "rb") as f:
        buffer.write(f.read())  # Write to BytesIO

    buffer.seek(0)
    return buffer


def df_to_image(df, file_format="PNG"):
    fig, ax = plt.subplots(figsize=(len(df.columns) * 2, len(df) * 0.5))
    ax.axis('tight')
    ax.axis('off')
    ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')

    buffer = BytesIO()
    plt.savefig(buffer, format=file_format)
    buffer.seek(0)
    return buffer

# Sidebar for language selection
language_options = {"English": "en", "Arabic": "ar", "Urdu": "ur", "Persian": "fa"}
language = st.sidebar.selectbox("🌍 Select Language", list(language_options.keys()))

# Language translations
def translate(text):
    translations = {
        "Advanced Data Sweeper": {"ar": "ماسح البيانات المتقدم", "ur": "جدید ڈیٹا سویپر", "fa": "جاروبرقی داده پیشرفته"},
        "Transform your files between CSV and Excel formats with built-in data cleaning and visualization.": {
            "ar": "قم بتحويل ملفاتك بين تنسيقات CSV و Excel مع تنظيف البيانات المدمج والتصور.",
            "ur": "CSV اور Excel فارمیٹس میں اپنی فائلوں کو تبدیل کریں، اندرونی ڈیٹا صفائی اور تصویری نمائندگی کے ساتھ۔",
            "fa": "تبدیل فایل‌های شما بین فرمت‌های CSV و Excel با پاکسازی داده و نمایش داده‌های داخلی."
        },
        "Upload your files (CSV or Excel):": {"ar": "تحميل ملفاتك (CSV أو Excel):", "ur": "اپنی فائلیں اپ لوڈ کریں (CSV یا Excel):", "fa": "بارگذاری فایل‌های خود (CSV یا Excel):"},
    }
    return translations.get(text, {}).get(language_options[language], text)

# Display main title and introduction
st.title(translate("Advanced Data Sweeper"))
st.write(translate("Transform your files between CSV and Excel formats with built-in data cleaning and visualization."))

uploaded_files = st.file_uploader(translate("Upload your files (CSV or Excel):"), type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_extension = os.path.splitext(file.name)[-1].lower()
        if file_extension == ".csv":
            df = pd.read_csv(file)
        elif file_extension == ".xlsx":
            df = pd.read_excel(file)
        else:
            st.error(f"Unsupported file type: {file_extension}")
            continue

        st.write(f"📄 **{file.name}**")
        st.write(f"📏 **{file.size / 1024:.2f} KB**")
        st.write("🔍", translate("Preview of the Uploaded File:"))
        st.dataframe(df.head())

        st.subheader("🔄 " + translate("Conversion Options"))
        conversion_type = st.radio(f"{translate('Convert to:')} {file.name}", ["CSV", "Excel", "PDF", "PNG", "JPG"], key=file.name)
        if st.button(f"{translate('Download')} {file.name}"):
            buffer = BytesIO()
            mime_type = ""
            new_file_name = file.name.rsplit(".", 1)[0]

            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                new_file_name += ".csv"
                mime_type = "text/csv"
            elif conversion_type == "Excel":
                df.to_excel(buffer, index=False, engine='openpyxl')
                new_file_name += ".xlsx"
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            elif conversion_type == "PDF":
                buffer = df_to_pdf(df)
                new_file_name += ".pdf"
                mime_type = "application/pdf"
            elif conversion_type in ["PNG", "JPG"]:
                buffer = df_to_image(df, file_format=conversion_type)
                new_file_name += f".{conversion_type.lower()}"
                mime_type = f"image/{conversion_type.lower()}"

            buffer.seek(0)
            st.download_button(label=f"⬇️ Download {new_file_name}", data=buffer, file_name=new_file_name, mime=mime_type)

st.success("🎉 " + translate("All files processed successfully!"))

st.markdown(
    """
    <div style="text-align: center; margin-top: 50px;">
        <b>Developed by Donia Batool</b>
    </div>
    """,
    unsafe_allow_html=True
)