from typing import Any

import streamlit as st


def render_channel_selection() -> None:
    """
    Renders the channel selection view.
    Handles flattening of channels and search optimization for large datasets.
    """
    st.header("Channel Selection")

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
    st.sidebar.markdown("---")
    st.sidebar.header("Plot Settings")

    decimation = st.sidebar.slider(
        "Decimation Factor",
        min_value=1,
        max_value=100,
        value=1,
        help="Reduce data points for faster plotting (e.g., 10 = use every 10th point).",
    )

    secondary_y: list[str] = st.sidebar.multiselect(
        "Secondary Y-Axis Channels", options=selected_channels, help="Select channels to plot on the right-hand axis."
    )

    return {"decimation": decimation, "secondary_y": secondary_y}
