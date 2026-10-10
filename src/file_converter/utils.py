import os
import tkinter as tk
from tkinter import filedialog, ttk

from .converter import convert_file, normalize_output_name
from .metadata import inspect_file


class FileConverterApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("File Converter")
        self.geometry("700x420")
        self.minsize(650, 360)

        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.target_format = tk.StringVar(value="hex")
        self.result_text = tk.StringVar(value="Ready")

        main = ttk.Frame(self, padding=18)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text="Input file").grid(row=0, column=0, sticky="w", pady=(0, 8))
        entry1 = ttk.Entry(main, textvariable=self.input_path, width=70)
        entry1.grid(row=1, column=0, sticky="ew", padx=(0, 10))
        ttk.Button(main, text="Browse", command=self.choose_input).grid(row=1, column=1, sticky="ew")

        ttk.Label(main, text="Output format").grid(row=2, column=0, sticky="w", pady=(10, 8))
        format_combo = ttk.Combobox(main, textvariable=self.target_format, values=["bin", "hex", "base64", "txt", "json"], state="readonly", width=20)
        format_combo.grid(row=3, column=0, sticky="w")

        ttk.Label(main, text="Output path").grid(row=4, column=0, sticky="w", pady=(12, 8))
        entry2 = ttk.Entry(main, textvariable=self.output_path, width=70)
        entry2.grid(row=5, column=0, sticky="ew", padx=(0, 10))
        ttk.Button(main, text="Choose output", command=self.choose_output).grid(row=5, column=1, sticky="ew")

        btn_frame = ttk.Frame(main)
        btn_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(18, 12))
        ttk.Button(btn_frame, text="Convert", command=self.convert_file).pack(side="left", padx=(0, 10))
        ttk.Button(btn_frame, text="Inspect", command=self.inspect_file).pack(side="left")

        ttk.Label(main, textvariable=self.result_text, wraplength=620, justify="left").grid(row=7, column=0, columnspan=2, sticky="w")

        main.columnconfigure(0, weight=1)

    def choose_input(self) -> None:
        selected = filedialog.askopenfilename(title="Select input file")
        if selected:
            self.input_path.set(selected)
            if not self.output_path.get():
                self.output_path.set(normalize_output_name(selected, self.target_format.get()))

    def choose_output(self) -> None:
        selected = filedialog.asksaveasfilename(title="Choose output path")
        if selected:
            self.output_path.set(selected)

    def convert_file(self) -> None:
        input_value = self.input_path.get()
        if not input_value:
            self.result_text.set("Please select an input file first.")
            return
        try:
            output_value = self.output_path.get() or normalize_output_name(input_value, self.target_format.get())
            result = convert_file(input_value, self.target_format.get(), output_path=output_value)
            self.result_text.set(f"Converted successfully: {result['output']}")
        except Exception as exc:  # pragma: no cover - GUI feedback
            self.result_text.set(f"Conversion failed: {exc}")

    def inspect_file(self) -> None:
        input_value = self.input_path.get()
        if not input_value:
            self.result_text.set("Please select a file to inspect.")
            return
        try:
            info = inspect_file(input_value)
            lines = [f"{key}: {value}" for key, value in info.items()]
            self.result_text.set("\n".join(lines[:20]))
        except Exception as exc:  # pragma: no cover - GUI feedback
            self.result_text.set(f"Inspection failed: {exc}")


def main() -> None:
    app = FileConverterApp()
    app.mainloop()


if __name__ == "__main__":
    main()
