from typing import Any

import plotly.graph_objects as go  # type: ignore
import streamlit as st
from plotly.subplots import make_subplots  # type: ignore


def get_plot_data(mdf: Any, channel_names: list[str], decimation: int = 1) -> list[dict[str, Any]]:
    """
    Extracts signals for the given channel names from the MDF object.
    Applies decimation to reduce data points for performance.

    Args:
        mdf: The MDF object.
        channel_names: List of strings (channel names).
        decimation: Integer decimation factor (take every Nth sample).

    Returns:
        A list of signal objects (or similar structures) ready for plotting.
    """
    if not channel_names:
        return []

    # mdf.select returns a list of Signal objects
    # We catch exceptions in case a channel name is ambiguous or not found
    try:
        signals = mdf.select(channel_names)
    except Exception as e:
        st.error(f"Error selecting channels: {e}")
        return []

    extracted_data = []

    for sig in signals:
        # Apply decimation
        # Signal object has .samples and .timestamps (numpy arrays)
        # Slicing works directly on them usually, or we can use the cut/interp methods if needed.
        # Simple slicing is fastest for visualization.

        # Check if decimation is valid
        decimation = max(decimation, 1)

        # We store metadata for plotting
        extracted_data.append(
            {
                "name": sig.name,
                "unit": sig.unit,
                "timestamps": sig.timestamps[::decimation],
                "samples": sig.samples[::decimation],
                "comment": sig.comment,
            }
        )

    return extracted_data


def create_plot(signals_data: list[dict[str, Any]], secondary_y_channels: list[str] | None = None) -> go.Figure:
    """
    Creates a Plotly Figure from the extracted signal data.

    Args:
        signals_data: List of dicts returned by get_plot_data.
        secondary_y_channels: List of channel names to plot on the secondary Y-axis.

    Returns:
        plotly.graph_objects.Figure
    """
    if secondary_y_channels is None:
        secondary_y_channels = []

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    for sig in signals_data:
        name = sig["name"]
        unit = sig["unit"]

        # Determine axis
        on_secondary = name in secondary_y_channels

        # Add trace
        fig.add_trace(
            go.Scatter(
                x=sig["timestamps"],
                y=sig["samples"],
                name=f"{name} [{unit}]",
                mode="lines",
            ),
            secondary_y=on_secondary,
        )

    # Update layout
    fig.update_layout(
        title_text="Signal Plot",
        xaxis_title="Time [s]",
        height=600,
        hovermode="x unified",
        template="plotly_dark",  # Matching 'Aesthetics' requirement for dark/premium feel
    )

    # Set y-axes titles
    fig.update_yaxes(title_text="Primary Axis", secondary_y=False)
    fig.update_yaxes(title_text="Secondary Axis", secondary_y=True)

    return fig
