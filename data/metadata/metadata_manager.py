import tkinter as tk
from tkinter import simpledialog
import json
from data.metadata.fetch_metadata import fetch_metadata_from_isbn

class MetadataManager:
    def __init__(self, viewer):
        self.viewer = viewer

    def display_metadata(self):
        self.viewer.metadata_text.delete(1.0, tk.END)
        metadata_display = "\n".join([f"{key}: {value}" for key, value in self.viewer.metadata.items()])
        self.viewer.metadata_text.insert(tk.END, metadata_display)

    def edit_metadata(self):
        dialog = tk.Toplevel(self.viewer)
        dialog.title("Edit Metadata")

        metadata_fields = ["Title", "Author", "Publisher", "Language", "Edition", "ISBN", "Place of publication", "Original Title", "Genre"]
        self.viewer.metadata_vars = {field: tk.StringVar(value=self.viewer.metadata.get(field, "")) for field in metadata_fields}

        for field in metadata_fields:
            tk.Label(dialog, text=field).pack(pady=5)
            tk.Entry(dialog, textvariable=self.viewer.metadata_vars[field]).pack(pady=5)

        def save_metadata():
            self.viewer.metadata = {field: var.get() for field, var in self.viewer.metadata_vars.items()}
            self.viewer.data["metadata"] = self.viewer.metadata
            self.viewer.data_manager.save_data()
            self.display_metadata()
            dialog.destroy()

        save_button = tk.Button(dialog, text="Save Metadata", command=save_metadata)
        save_button.pack(pady=20)

    def fetch_metadata_by_isbn(self):
        isbn = simpledialog.askstring("ISBN", "Enter ISBN:")
        if isbn:
            metadata = fetch_metadata_from_isbn(isbn)
            if metadata:
                self.viewer.metadata.update(metadata)
                self.viewer.data["metadata"] = self.viewer.metadata
                self.viewer.data_manager.save_data()
                self.display_metadata()
