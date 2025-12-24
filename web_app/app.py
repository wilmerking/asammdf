import os

import streamlit as st

from components import render_channel_selection, render_plot_settings
from plotting import create_plot, get_plot_data
from utils import load_mdf

st.set_page_config(page_title="asammdf Streamlit", layout="wide")

# Initialize session state
if "mdf_object" not in st.session_state:
    st.session_state["mdf_object"] = None
if "selected_channels" not in st.session_state:
    st.session_state["selected_channels"] = []
if "file_path" not in st.session_state:
    st.session_state["file_path"] = None

# Sidebar Navigation
st.sidebar.title("Navigation")
mode = st.sidebar.radio("Go to", ["File Header", "Visualization"])

if mode == "File Header":
    st.header("File Upload & Header Info")

    uploaded_file = st.file_uploader("Upload MDF File (.mf4, .mdf)", type=["mf4", "mdf", "dat"])

    if uploaded_file:
        # Check if it's a new file
        if st.session_state["file_path"] and uploaded_file.name != os.path.basename(st.session_state["file_path"]):
            st.info("New file detected. Reloading...")
            st.session_state["mdf_object"] = None

        if st.session_state["mdf_object"] is None:
            with st.spinner("Loading MDF file..."):
                try:
                    mdf, path = load_mdf(uploaded_file)
                    st.session_state["mdf_object"] = mdf
                    st.session_state["file_path"] = path
                    st.success(f"Loaded: {uploaded_file.name}")
                except Exception as e:
                    st.error(f"Failed to load file: {e}")

        mdf = st.session_state["mdf_object"]
        if mdf:
            st.subheader("File Information")
            st.json(mdf.header)

            # Channel Pre-selection interface
            render_channel_selection()

elif mode == "Visualization":
    st.header("Visualization")

    selected_channels = st.session_state["selected_channels"]

    if not selected_channels:
        st.info("Please select channels in the 'File Header' tab first.")
    else:
        # Render settings in sidebar (only visible in this mode)
        plot_settings = render_plot_settings(selected_channels)

        mdf = st.session_state["mdf_object"]

        if mdf:
            with st.spinner("Extracting and plotting data..."):
                signals_data = get_plot_data(mdf, selected_channels, decimation=plot_settings["decimation"])

                if signals_data:
                    fig = create_plot(signals_data, secondary_y_channels=plot_settings["secondary_y"])
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No data found for selected channels.")
