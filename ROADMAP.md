# Project Roadmap

Last updated: 2025-12-24

### New Features 🚀

- [ ] Phase 4 Feature-Specific Instructions
  - Tabular View (Replacing Tabular Widget)
  - Refer to asammdf.gui.widgets.tabular.py.
  - Action: Use st.dataframe or st.data_editor.
  - Allow users to select a time range (Start/Stop sliders) to limit the rows displayed, as rendering millions of rows in the DOM is not feasible.
  - File Conversion & Export
  - Refer to the "Modify & Export" logic in asammdf.gui.widgets.file.
  - Action: Create a form with:
  - Output Format Selector (CSV, Parquet, HDF5, MAT, Matlab).
  - Compression Options (LZ4, ZLIB).
  - "Convert" Button.
  - Backend: On click, call mdf_object.export(format=..., filename=...).
  - Download: Use st.download_button to serve the resulting file back to the user.
  - Bus Logging (CAN/LIN)
  - If supporting generic bus logging (BLF/ASC), add a section to upload DBC/ARXML database files alongside the log file.
  - Use mdf.extract_bus_logging(database_files=...) to convert raw CAN frames into physical signals before the "Channel Selection" phase.

---

- [ ] Phase 5 Performance & Cleanup
  - Memory Management
  - MDF objects can be memory-intensive. Explicitly call mdf_object.close() and del mdf_object when the user clicks a "Close File" or "Reset" button.
  - Implement a cleanup routine to delete the temporary uploaded files from the server's temp directory when the session ends.
  - Error Handling
  - Wrap file loading in try/except blocks to catch corrupted files or unsupported versions (MDF v2/v3/v4).
  - Display errors using st.error instead of the desktop ErrorDialog.

### Bug Fixes 🐛

- [ ] Fix the zoom in/out issue on the signal plot
  - when the zoom in/out is used, the plot should scale the x axis but not the y axis
