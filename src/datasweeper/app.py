import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.pdfgen import canvas

# Configure Streamlit page
st.set_page_config(page_title="Data Sweeper", layout="wide")

# Title and description
st.title("📊 Advanced Data Sweeper")
st.write("Convert files into CSV, Excel, PDF, and images (JPG/PNG) with built-in data cleaning and visualization.")

# File uploader
uploaded_files = st.file_uploader("Upload your files (CSV or Excel):", type=["csv", "xlsx"], accept_multiple_files=True)

# Process uploaded files
if uploaded_files:
    for file in uploaded_files:
        file_extension = os.path.splitext(file.name)[-1].lower()
        
        # Read the uploaded file
        if file_extension == ".csv":
            df = pd.read_csv(file)
        elif file_extension == ".xlsx":
            df = pd.read_excel(file)
        else:
            st.error(f"❌ Unsupported file type: {file_extension}")
            continue
        
        # Display file info
        st.write(f"**📄 File Name:** {file.name}")
        st.write(f"**📏 File Size:** {file.size / 1024:.2f} KB")

        # 🔹 Data Cleaning Options
        st.subheader("🧹 Data Cleaning Options")
        if st.checkbox(f"Remove Duplicates ({file.name})", key=f"dup_{file.name}"):
            df = df.drop_duplicates()
            st.success("✅ Duplicates removed!")

        if st.checkbox(f"Fill Missing Values ({file.name})", key=f"fillna_{file.name}"):
            df = df.fillna("N/A")
            st.success("✅ Missing values filled!")

        # 🔹 Editable Data Table
        st.subheader("✏️ Edit Data Before Conversion")
        edited_df = st.data_editor(df, num_rows="dynamic", key=f"edit_{file.name}")  # Editable DataFrame

        # 🔹 Data Visualization (Moved inside the loop)
        st.subheader("📊 Data Visualization")
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

        if numeric_cols:
            selected_cols = st.multiselect(f"Select Column for Histogram ({file.name}):", numeric_cols, key=f"hist_{file.name}")

            if selected_cols:  
                fig, ax = plt.subplots()

                # Generate different colors for multiple datasets
                colors = plt.cm.viridis(range(len(selected_cols)))  

                for col, color in zip(selected_cols, colors):
                    ax.hist(df[col], bins=20, color=color, edgecolor="black", alpha=0.7, label=col)

                ax.set_title(f"Histogram of Selected Columns")
                ax.set_xlabel("Value")
                ax.set_ylabel("Frequency")
                ax.legend()
                st.pyplot(fig)

                # 🎨 Image (PNG) Export
                img_buffer = BytesIO()
                fig.savefig(img_buffer, format="png")
                img_buffer.seek(0)

                st.download_button(
                    label="⬇️ Download Chart as PNG",
                    data=img_buffer,
                    file_name=f"{file.name}_chart.png",
                    mime="image/png"
                )

        # 🔹 Conversion Options
        st.subheader("🔄 Conversion Options")
        conversion_type = st.radio(
            f"Convert {file.name} to:",
            ["CSV", "Excel", "PDF", "PNG"],
            key=f"convert_{file.name}"
        )

        # Convert and Download
        if st.button(f"Convert & Download {file.name}"):
            buffer = BytesIO()
            
            if conversion_type == "CSV":
                edited_df.to_csv(buffer, index=False)
                file_name = file.name.replace(file_extension, ".csv")
                mime_type = "text/csv"
            elif conversion_type == "Excel":
                edited_df.to_excel(buffer, index=False, engine='openpyxl')
                file_name = file.name.replace(file_extension, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            elif conversion_type == "PDF":
                buffer = BytesIO()
                pdf = canvas.Canvas(buffer)
                text = pdf.beginText(40, 800)
                text.setFont("Helvetica", 10)
                text.textLine(f"Data Preview: {file.name}")
                for i, row in edited_df.head(20).iterrows():
                    text.textLine(", ".join(str(x) for x in row[:5]))
                pdf.drawText(text)
                pdf.save()
                buffer.seek(0)
                file_name = file.name.replace(file_extension, ".pdf")
                mime_type = "application/pdf"
            elif conversion_type == "PNG":
                fig, ax = plt.subplots(figsize=(8, 4))
                ax.axis("tight")
                ax.axis("off")
                table = ax.table(cellText=edited_df.head(10).values, colLabels=edited_df.columns, loc="center", cellLoc="center")
                fig.savefig(buffer, format="png", bbox_inches="tight")
                buffer.seek(0)
                file_name = file.name.replace(file_extension, ".png")
                mime_type = "image/png"

            buffer.seek(0)

            # Download button
            st.download_button(
                label=f"⬇️ Download {file.name} as {conversion_type}",
                data=buffer,
                file_name=file_name,
                mime=mime_type
            )

st.success("🎉 All files processed successfully!")
