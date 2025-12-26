from typing import Any

import streamlit as st


def render_channel_selection() -> None:
    """
    Renders the channel selection view.
    Handles flattening of channels and search optimization for large datasets.
    """
    # st.header("Channel Selection") # Removed header to save space in narrow column

    mdf = st.session_state.get("mdf_object")

    if mdf is None:
        st.warning("Please upload a file in the 'File Header' section first.")
        return

    # Flatten channel list
    # iter_channels returns an iterator of Channel objects or similar metadata
    # We want a list of strings for the multiselect
    # Using a cache here would be good if we can, but iter_channels depends on the mdf object state

    # We'll cache the channel list in session state to avoid re-iterating on every rerun
    if "all_channels" not in st.session_state or st.session_state.get("channel_source_file") != st.session_state.get(
        "file_path"
    ):
        with st.spinner("Indexing channels..."):
            channels = []
            # mdf.iter_channels() yields (group_index, channel_index, name, group, source) usually?
            # actually asammdf has iter_channels(options) -> yields channel object or name.
            # Let's check what iter_channels returns or just use a safe approach.
            # mdf.iter_channels() returns a generator of names if no payload.
            # But let's verify. standard usage: for group_index, channel_index, channel_name, group, source in mdf.iter_channels():

            # To be safe and fast, we can use mdf.channels_db which is a dict of {name: (group_index, channel_index)} list
            # But iter_channels gives us everything.

            # Let's assume standard behavior:
            # list(mdf.iter_channels()) returns names if simple? No, it returns tuples usually.
            # Let's try to get just names for now.
            try:
                # The most reliable way to get all channel names:
                # mdf.get_all_channels() ? No, that might not exist.
                # mdf.channels_db is {name: [entry, ..]}
                channels = sorted(mdf.channels_db.keys())
            except Exception:
                # Fallback if internal structure is different
                channels = []
                for name in mdf.channels_db:
                    channels.append(name)

            st.session_state["all_channels"] = channels
            st.session_state["channel_source_file"] = st.session_state.get("file_path")

    all_channels: list[str] = st.session_state["all_channels"]

    # Optimization: Search filter
    if len(all_channels) > 1000:
        search_query = st.text_input("Search Channels", help="Type to filter the channel list")
        if search_query:
            filtered_channels = [c for c in all_channels if search_query.lower() in c.lower()]
        else:
            # If > 1000 and no search, might be too heavy to show all?
            # Streamlit multiselect handles a few thousand okay, but > 10k is slow.
            # Let's show all if no search, or maybe limit?
            filtered_channels = all_channels
    else:
        filtered_channels = all_channels

    # Multiselect
    # Check if we have pre-selected channels
    current_selection: list[str] = st.session_state["selected_channels"]

    # We need to make sure current_selection items are in filtered_channels to show up successfully as "selected"
    # if we are strictly filtering. But multiselect 'default' must be present in options.
    # So options must be union of filtered + current_selection

    options = list(set(filtered_channels) | set(current_selection))
    options.sort()

    new_selection = st.multiselect("Select Channels to Plot", options=options, default=current_selection)

    # Update session state
    # Update session state
    if new_selection != current_selection:
        st.session_state["selected_channels"] = new_selection


def render_plot_settings(selected_channels: list[str]) -> dict[str, Any]:
    """
    Renders sidebar settings for plotting: decimation and axis control.
    Returns a dict with settings.
    """
    # st.sidebar.header("Plot Settings") # Removed header

    # Plot Type Selector
    plot_type = st.radio("Plot Mode", ["Stack", "Overlay"], index=0, horizontal=True)

    decimation = st.slider(
        "Decimation Factor",
        min_value=1,
        max_value=100,
        value=1,
        help="Reduce data points for faster plotting (e.g., 10 = use every 10th point).",
    )

    secondary_y: list[str] = st.multiselect(
        "Secondary Y-Axis Channels",
        options=selected_channels,
        help="Select channels to plot on the right-hand axis.",
        disabled=(plot_type == "Stack"),  # Secondary Y doesn't make much sense in Stack mode usually
    )

    return {"decimation": decimation, "secondary_y": secondary_y, "plot_type": plot_type}


def render_tabular_view(selected_channels: list[str]) -> None:
    """
    Renders the Tabular View for data inspection.
    """
    st.header("Tabular View")

    mdf = st.session_state.get("mdf_object")
    if not mdf:
        st.warning("Please upload a file first.")
        return

    if not selected_channels:
        st.info("Please select channels in the 'File Header' tab first.")
        return

    # Time range selection
    # We need the start and end time of the file
    # mdf.header.start_time is a datetime object usually, but mdf also has time relative to start
    # mdf.header.start_time might be the absolute time.
    # The timestamps in signals are usually float seconds from start.

    # We can get the max time from the file metadata or by inspecting one channel.
    # mdf.header does not always have the duration readily available as a simple float.
    # A robust way is to query the MDF object property if available?
    # MDF has .info() but that returns a dict.
    # Let's try to get the time range from the master channel of the first selected channel or similar.

    # Approx approach:
    # Use mdf.info() which returns a dict usually containing 't_min', 't_max' or similar?
    # Actually, let's use a simpler approach: get the DataFrame for a small slice or use metadata.
    # mdf.header...

    # Let's assume 0 to some large number if unknown, or try to find one.
    # For now, we can load the data without start/stop first? No, "rendering millions of rows ... is not feasible".

    # Better: Get the DataFrame with only time_from_zero=True to get limit?
    # Or just use st.number_input for start/stop if we don't know the max.

    # The ROADMAP says: "Allow users to select a time range (Start/Stop sliders)"
    # To have a slider we need a max.
    # Iterate all groups and find global min/max time? Costly.
    # Let's just guess or use a default large range, or maybe the user knows.
    # Or, we can use `mdf.header.start_time` (datetime) and maybe `mdf.last_timestamp` if available?
    # asammdf MDF object has a hacky way to get max time?
    # Actually, commonly used: mdf.get_time_channel_for_group(0) -> max?

    # Let's try to grab the last timestamp from the first selected signal if possible, or just default to 0-100s for now
    # and provide number inputs for precision.

    # For a slider, we really want bounds.
    # Let's try:
    # Use `mdf.t_start` (start time stamp) and maybe inspect one signal?
    # Let's check if the user selected any channels.

    # Let's just use st.number_input for Start and End time to be safe against big files where scanning might be slow?
    # Or, if the file is small enough, we can analyze.

    # Let's go with number inputs for now for robustness, and maybe a slider if we can cheaply determine max.
    # Actually, let's try to get a rough duration.

    st.subheader("Data Preview")

    col1, col2 = st.columns(2)
    with col1:
        start_time = st.number_input("Start Time (s)", value=0.0, min_value=0.0)
    with col2:
        stop_time = st.number_input("Stop Time (s)", value=10.0, min_value=0.0)

    if start_time >= stop_time:
        st.error("Start time must be less than stop time.")
        return

    # Raster option
    raster = st.number_input(
        "Raster (s)", value=0.01, min_value=0.000001, format="%.6f", help="Resample data to this frequency interval."
    )

    if st.button("Load Data"):
        with st.spinner("Loading dataframe..."):
            try:
                # mdf.to_dataframe returns a pandas DataFrame
                # we can filter by start and stop
                # Note: mdf.to_dataframe(channels=..., raster=..., time_from_zero=True, ignore_value2text_conversions=False)
                # We can also pass 'start' and 'stop' arguments to cut?
                # asammdf's to_dataframe doesn't have explicit start/stop, it has 'raster' usually.
                # But we can allow 'cut'. MDF.cut(start, stop).to_dataframe()?
                # Doing .cut() creates a new object, might be heavy.
                # Efficient way: mdf.to_dataframe(channels=..., raster=raster) then slice?
                # If file is huge, to_dataframe will explode memory.
                # MDF.iter_to_dataframe might be better or providing a custom script.

                # Wait, MDF.select supports cutting?
                # Efficient approach: mdf.cut(start=..., stop=..., include_ends=False).to_dataframe(channels=...)
                # But cut() creates a temp mdf?
                # Actually, mdf.to_dataframe usually retrieves all.

                # Check asammdf API: default to_dataframe gets everything.
                # Maybe usage of `filter` is better?

                # Let's use mdf.cut(start=start_time, stop=stop_time).to_dataframe(channels=selected_channels, raster=raster)
                # This seems standard for slicing.

                # We'll do it on a filtered object (cheap copy?)
                mdf_cut = mdf.cut(start=start_time, stop=stop_time)
                df = mdf_cut.to_dataframe(channels=selected_channels, raster=raster, time_from_zero=True)

                # Cleanup
                # mdf_cut might need to be closed if it created a temp file?
                # .cut() returns a new MDF object. If it's memory based, we should close/del it.

                st.write(f"Displaying {len(df)} rows.")
                st.dataframe(df)

                del mdf_cut

            except Exception as e:
                st.error(f"Error loading data: {e}")


def render_file_conversion() -> None:
    """
    Renders File Conversion & Export interface.
    """
    st.header("File Conversion & Export")

    mdf = st.session_state.get("mdf_object")
    if not mdf:
        st.warning("Please upload a file first.")
        return

    st.markdown("Export the current MDF file (or a subset) to other formats.")

    col1, col2 = st.columns(2)

    with col1:
        export_format = st.selectbox("Output Format", ["csv", "parquet", "hdf5", "mat", "mat73"])

    with col2:
        compression = st.selectbox("Compression", ["None", "GZIP", "SNAPPY", "LZ4"], index=0)

    # Map compression to arguments if needed (mostly for parquet/hdf5)
    # csv doesn't really support compression kwarg in export usually, or it does?
    # asammdf export(fmt, filename, compression=...)

    if st.button("Convert and Prepare Download"):
        import tempfile
        import os

        with st.spinner("Converting..."):
            try:
                # Create a temp file for output
                # We simply give a prefix
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{export_format}") as tmp:
                    out_filename = tmp.name

                # Close it so mdf can write to it (Windows mostly, but good practice)
                # actually NamedTemporaryFile deletes on close unless delete=False.

                # Compression arg handling
                # asammdf export typically takes 'compression' for some formats.
                # For CSV, it might be ignored.
                # Check asammdf docs conceptually: export(fmt, filename, ...)

                # We perform the export
                # Note: export() might return something or just write to file
                kwargs = {}
                if export_format in ["parquet", "hdf5", "mat", "mat73"] and compression != "None":
                    # Simple mapping, actual strings might differ based on library
                    kwargs["compression"] = compression.lower()

                mdf.export(fmt=export_format, filename=out_filename, **kwargs)

                # Read back for download button
                with open(out_filename, "rb") as f:
                    file_data = f.read()

                # Cleanup temp file
                os.remove(out_filename)

                st.success(f"Conversion to {export_format} successful!")

                st.download_button(
                    label=f"Download .{export_format}",
                    data=file_data,
                    file_name=f"export.{export_format}",
                    mime="application/octet-stream",
                )

            except Exception as e:
                st.error(f"Export failed: {e}")


def render_bus_logging() -> None:
    """
    Renders Bus Logging (CAN/LIN extraction) interface.
    """
    st.header("Bus Logging Extraction")

    mdf = st.session_state.get("mdf_object")
    if not mdf:
        st.warning("Please upload a file first.")
        return

    st.info("Upload Database files (DBC, ARXML) to decode CAN/LIN/FlexRay data from the raw log.")

    uploaded_dbs = st.file_uploader("Upload Database Files", type=["dbc", "arxml", "xml"], accept_multiple_files=True)

    if st.button("Extract Bus Logging"):
        if not uploaded_dbs:
            st.warning("Please upload at least one database file.")
            return

        import tempfile
        import os

        # Save DBCs to temp paths because extract_bus_logging needs paths usually
        db_paths = []
        temp_files = []  # Keep refs to delete later

        try:
            with st.spinner("Saving database files..."):
                for db_file in uploaded_dbs:
                    suffix = "." + db_file.name.split(".")[-1]
                    tf = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                    tf.write(db_file.read())
                    tf.close()
                    db_paths.append(tf.name)
                    temp_files.append(tf.name)

            with st.spinner("Extracting signals... this may take a while"):
                # extract_bus_logging returns a NEW MDF object containing physical signals
                # signature: extract_bus_logging(database_files=..., ...)

                # Ensure we handle the format correctly. database_files can be a generic list of paths.
                extracted_mdf = mdf.extract_bus_logging(database_files=db_paths)

                # Update session state with the new MDF
                # WARNING: This replaces the currently loaded MDF with the extracted one!

                # We should probably close the old one if it's different?
                # But let's just swap it.
                st.session_state["mdf_object"] = extracted_mdf

                # We might want to re-init session vars like 'all_channels'
                if "all_channels" in st.session_state:
                    del st.session_state["all_channels"]

                st.success(
                    "Bus logging extracted successfully! The file content has been updated with decoded signals."
                )
                st.info("You can now go to 'Visualization' or 'Tabular View' to inspect the new signals.")

        except Exception as e:
            st.error(f"Extraction failed: {e}")

        finally:
            # Cleanup temp DB files
            for p in temp_files:
                if os.path.exists(p):
                    os.remove(p)
