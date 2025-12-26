from typing import Any

import plotly.graph_objects as go  # type: ignore
from plotly.subplots import make_subplots  # type: ignore
import streamlit as st


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


def create_plot(
    signals_data: list[dict[str, Any]], secondary_y_channels: list[str] | None = None, plot_type: str = "Overlay"
) -> go.Figure:
    """
    Creates a Plotly Figure from the extracted signal data.

    Args:
        signals_data: List of dicts returned by get_plot_data.
        secondary_y_channels: List of channel names to plot on the secondary Y-axis (only for Overlay).
        plot_type: "Overlay" or "Stack".

    Returns:
        plotly.graph_objects.Figure
    """
    if secondary_y_channels is None:
        secondary_y_channels = []

    num_signals = len(signals_data)
    if num_signals == 0:
        return go.Figure()

    if plot_type == "Stack":
        # Create subplots: one row per signal
        fig = make_subplots(
            rows=num_signals,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.02,
            subplot_titles=[s["name"] for s in signals_data],
        )

        # Calculate dynamic height
        # Requirement: "The plot should remain full page height but ... fill the height of the signal plot area."
        # We'll use a fixed height for the figure, and Plotly automatically scales subplots.
        total_height = 800  # Fixed height filling the view

        for i, sig in enumerate(signals_data):
            name = sig["name"]
            unit = sig["unit"]

            # Row index is 1-based
            row_idx = i + 1

            fig.add_trace(
                go.Scatter(
                    x=sig["timestamps"],
                    y=sig["samples"],
                    name=f"{name} [{unit}]",
                    mode="lines",
                ),
                row=row_idx,
                col=1,
            )

            # Update y-axis for this specific row to be fixed range
            # access yaxis object like 'yaxis', 'yaxis2', etc.
            # but update_yaxes with row/col selector is easier
            fig.update_yaxes(title_text=unit, row=row_idx, col=1, fixedrange=True)

    else:
        # Overlay Mode
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        total_height = 800

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

        # Set y-axes titles
        # Setting fixedrange=True disables interactive zoom on y-axes, so selection only zooms X
        fig.update_yaxes(title_text="Primary Axis", secondary_y=False, fixedrange=True)
        fig.update_yaxes(title_text="Secondary Axis", secondary_y=True, fixedrange=True)

    # Update layout common to both
    fig.update_layout(
        title_text="Signal Plot",
        xaxis_title="Time [s]",
        height=total_height,
        hovermode="x unified",
        template="plotly_dark",  # Matching 'Aesthetics' requirement
        showlegend=True,
    )

    # Ensure X axis is always zoomed correctly
    # If shared_xaxes=True (stack), zooming one zooms all.

    return fig
