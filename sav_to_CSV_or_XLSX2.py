import streamlit as st
import pyreadstat
import os
import time
import tempfile

def main():
    # ---- Add a logo or banner image at the top (optional) ----
    st.image(
        "https://via.placeholder.com/600x100.png?text=My+SAV+Converter+Banner",
        use_container_width=True
    )

    st.title("SPSS .sav to CSV/XLSX Converter")

    # ---- Use columns to create a nicer layout for the file upload and format selection ----
    col1, col2 = st.columns(2)

    with col1:
        sav_file = st.file_uploader(
            "Upload your .sav file:",
            type=["sav"],
            accept_multiple_files=False
        )

    with col2:
        output_format = st.radio("Convert to:", ("CSV", "XLSX"))

    # -------------------------------------------------------------------
    # APPROACH A: Let the user manually type the output directory.
    # -------------------------------------------------------------------
    st.write("Specify the directory where you want to save the converted file.")
    output_dir = st.text_input("Output directory:", value=".")

    # File name (without extension)
    default_output_name = "converted_file"
    output_name = st.text_input("Output filename (without extension):", value=default_output_name)

    # Overwrite allowed?
    overwrite_allowed = st.checkbox("Allow overwrite if file already exists?", value=False)

    # -------------------------------------------------------------------
    # Conversion button
    # -------------------------------------------------------------------
    if st.button("Convert"):
        if not sav_file:
            st.warning("Please upload a .sav file first.")
            return

        # Build full output path
        full_output_path = os.path.join(output_dir, f"{output_name}.{output_format.lower()}")

        # Check if file already exists
        if os.path.exists(full_output_path) and not overwrite_allowed:
            st.warning(
                f"File '{full_output_path}' already exists. "
                "Enable 'Allow overwrite' or rename your output file."
            )
            return

        # Initialize a progress bar and status text
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.text("Starting conversion...")

        # STEP 1: Read the .sav file
        try:
            # Write the uploaded file to a temporary file so pyreadstat can read it
            with tempfile.NamedTemporaryFile(delete=False, suffix=".sav") as tmp:
                tmp.write(sav_file.read())
                temp_file_path = tmp.name

            progress_bar.progress(10)
            status_text.text("Reading .sav file...")

            # Pass the temp file path to pyreadstat
            df, meta = pyreadstat.read_sav(temp_file_path)
            time.sleep(0.5)  # Optional: simulate progress
            progress_bar.progress(50)
        except Exception as e:
            st.error(f"Error reading the .sav file: {e}")
            return
        finally:
            # Clean up temp file if you want to remove it after reading
            if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                os.remove(temp_file_path)

        # ---- Show a small preview of the data (optional) ----
        st.subheader("Data Preview")
        st.dataframe(df.head(5))  # show first 5 rows

        # STEP 2: Write to the chosen format
        try:
            status_text.text(f"Writing to {output_format}...")
            time.sleep(0.5)
            if output_format == "CSV":
                df.to_csv(full_output_path, index=False)
            else:
                df.to_excel(full_output_path, index=False)
            progress_bar.progress(100)
            status_text.text("Conversion complete!")
            st.balloons()

            st.success(f"Your file has been converted and saved to '{full_output_path}'.")
        except Exception as e:
            st.error(f"Error writing the {output_format} file: {e}")

# Optional: Add custom styling to your app
custom_css = """
<style>
/* Example of custom CSS for the Streamlit app */
h1 {
    color: #2E86C1;
    font-weight: bold;
}
</style>
"""

if __name__ == "__main__":
    # Inject custom CSS if desired
    st.markdown(custom_css, unsafe_allow_html=True)
    main()
