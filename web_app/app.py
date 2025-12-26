import os

import streamlit as st

from components import (
    render_bus_logging,
    render_channel_selection,
    render_file_conversion,
    render_plot_settings,
    render_tabular_view,
)
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
mode = st.sidebar.radio("Go to", ["File Header", "Visualization", "Tabular View", "File Conversion", "Bus Logging"])

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

            # Channel selection moved to Visualization page

elif mode == "Visualization":
    st.header("Visualization")

    # Use 2-column layout: Left for controls, Right for plot
    col_controls, col_plot = st.columns([1, 4])

    with col_controls:
        # Render settings
        # We need selected_channels for plot_settings
        # But we also render channel selection here.

        # 1. Render Channel Selection (populates st.session_state["selected_channels"])
        render_channel_selection()

        selected_channels = st.session_state["selected_channels"]

        # 2. Render Plot Settings (Stack/Overlay, Decimation)
        # Only show if channels selected, or always?
        # Better always so user can see options.
        plot_settings = render_plot_settings(selected_channels)

    with col_plot:
        if not selected_channels:
            st.info("Please select channels from the list on the left.")
        else:
            mdf = st.session_state["mdf_object"]

            if mdf:
                with st.spinner("Extracting and plotting data..."):
                    signals_data = get_plot_data(mdf, selected_channels, decimation=plot_settings["decimation"])

                    if signals_data:
                        fig = create_plot(
                            signals_data,
                            secondary_y_channels=plot_settings["secondary_y"],
                            plot_type=plot_settings["plot_type"],
                        )
                        # Increase height in layout if needed, but create_plot handles it
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("No data found for selected channels.")
            else:
                st.info("Please upload a file in 'File Header' first.")

elif mode == "Tabular View":
    render_tabular_view(st.session_state["selected_channels"])

elif mode == "File Conversion":
    render_file_conversion()

elif mode == "Bus Logging":
    render_bus_logging()
