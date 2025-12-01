"""
Interfejs graficzny konwertera sprawozdań finansowych.

Prosty GUI tkinter umożliwiający:
- Wybór plików XML/XAdES
- Wybór folderu z plikami
- Opcjonalne przeszukiwanie podfolderów
- Wybór folderu wyjściowego
- Konwersję z logiem postępu
"""

import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext, messagebox
from pathlib import Path
import threading
import traceback
from datetime import datetime

from parser import SFParser
from converter import XLSXConverter


class SFConverterGUI:
    """Główne okno aplikacji konwertera."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Konwerter Sprawozdań Finansowych XML → XLSX")
        self.root.geometry("750x600")
        self.root.minsize(600, 500)

        # Stan aplikacji
        self.files_to_process = []
        self.output_dir = None
        self.is_converting = False

        # Komponenty
        self.sf_parser = SFParser()
        self.converter = XLSXConverter()

        # Tworzenie widżetów
        self._create_widgets()

        # Konfiguracja siatki
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)
        self.root.rowconfigure(5, weight=1)

    def _create_widgets(self):
        """Tworzy wszystkie widżety interfejsu."""
        # ===== FRAME: Przyciski wyboru plików =====
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.grid(row=0, column=0, sticky="ew")
        top_frame.columnconfigure(2, weight=1)

        ttk.Button(
            top_frame,
            text="Wybierz plik(i)...",
            command=self._select_files
        ).grid(row=0, column=0, padx=5)

        ttk.Button(
            top_frame,
            text="Wybierz folder...",
            command=self._select_folder
        ).grid(row=0, column=1, padx=5)

        self.recursive_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            top_frame,
            text="Przeszukuj podfoldery",
            variable=self.recursive_var
        ).grid(row=0, column=2, padx=10, sticky="w")

        # ===== LABEL: Nagłówek listy =====
        ttk.Label(
            self.root,
            text="Pliki do przetworzenia:",
            font=("", 10, "bold")
        ).grid(row=1, column=0, sticky="w", padx=10, pady=(10, 0))

        # ===== FRAME: Lista plików =====
        list_frame = ttk.Frame(self.root, padding="10")
        list_frame.grid(row=2, column=0, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # Lista plików ze scrollbarem
        self.file_listbox = tk.Listbox(
            list_frame,
            selectmode=tk.EXTENDED,
            font=("Consolas", 9)
        )
        self.file_listbox.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            list_frame,
            orient="vertical",
            command=self.file_listbox.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.file_listbox.config(yscrollcommand=scrollbar.set)

        # Przyciski zarządzania listą
        btn_frame = ttk.Frame(list_frame)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=(5, 0), sticky="w")

        ttk.Button(
            btn_frame,
            text="Usuń zaznaczone",
            command=self._remove_selected
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            btn_frame,
            text="Wyczyść listę",
            command=self._clear_list
        ).pack(side=tk.LEFT)

        self.file_count_label = ttk.Label(btn_frame, text="Plików: 0")
        self.file_count_label.pack(side=tk.RIGHT, padx=10)

        # ===== FRAME: Folder wyjściowy =====
        output_frame = ttk.Frame(self.root, padding="10")
        output_frame.grid(row=3, column=0, sticky="ew")
        output_frame.columnconfigure(1, weight=1)

        ttk.Label(output_frame, text="Folder wyjściowy:").grid(row=0, column=0, sticky="w")

        self.output_label = ttk.Label(
            output_frame,
            text="(ten sam co wejściowy)",
            foreground="gray"
        )
        self.output_label.grid(row=0, column=1, sticky="w", padx=10)

        ttk.Button(
            output_frame,
            text="Zmień...",
            command=self._select_output
        ).grid(row=0, column=2)

        # ===== BUTTON: Konwertuj =====
        self.convert_button = ttk.Button(
            self.root,
            text="KONWERTUJ",
            command=self._convert,
            style="Accent.TButton"
        )
        self.convert_button.grid(row=4, column=0, pady=15)

        # Stylizacja przycisku (większy)
        style = ttk.Style()
        style.configure("Accent.TButton", font=("", 11, "bold"), padding=10)

        # ===== FRAME: Log =====
        log_label = ttk.Label(
            self.root,
            text="Log:",
            font=("", 10, "bold")
        )
        log_label.grid(row=5, column=0, sticky="nw", padx=10)

        log_frame = ttk.Frame(self.root, padding="10")
        log_frame.grid(row=6, column=0, sticky="nsew")
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=10,
            font=("Consolas", 9),
            state="disabled"
        )
        self.log_text.grid(row=0, column=0, sticky="nsew")

        # Konfiguracja tagów do kolorowania logów
        self.log_text.tag_config("success", foreground="green")
        self.log_text.tag_config("error", foreground="red")
        self.log_text.tag_config("info", foreground="blue")
        self.log_text.tag_config("timestamp", foreground="gray")

        # ===== PASEK POSTĘPU =====
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.root,
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.grid(row=7, column=0, sticky="ew", padx=10, pady=(0, 10))

    def _select_files(self):
        """Otwiera dialog wyboru plików."""
        files = filedialog.askopenfilenames(
            title="Wybierz pliki XML sprawozdań finansowych",
            filetypes=[
                ("Pliki XML", "*.xml"),
                ("Pliki XAdES", "*.xades"),
                ("Wszystkie pliki", "*.*")
            ]
        )
        for f in files:
            if f not in self.files_to_process:
                self.files_to_process.append(f)
                self.file_listbox.insert(tk.END, Path(f).name)

        self._update_file_count()

    def _select_folder(self):
        """Otwiera dialog wyboru folderu."""
        folder = filedialog.askdirectory(title="Wybierz folder z plikami XML")
        if folder:
            folder_path = Path(folder)

            # Szukaj plików XML
            pattern = "**/*.xml" if self.recursive_var.get() else "*.xml"
            for f in folder_path.glob(pattern):
                if str(f) not in self.files_to_process:
                    self.files_to_process.append(str(f))
                    self.file_listbox.insert(tk.END, f.name)

            # Szukaj plików XAdES
            pattern_xades = pattern.replace('.xml', '.xades')
            for f in folder_path.glob(pattern_xades):
                if str(f) not in self.files_to_process:
                    self.files_to_process.append(str(f))
                    self.file_listbox.insert(tk.END, f.name)

            self._update_file_count()

    def _select_output(self):
        """Otwiera dialog wyboru folderu wyjściowego."""
        folder = filedialog.askdirectory(title="Wybierz folder wyjściowy")
        if folder:
            self.output_dir = folder
            self.output_label.config(text=folder, foreground="black")

    def _remove_selected(self):
        """Usuwa zaznaczone pliki z listy."""
        selected = list(self.file_listbox.curselection())
        for i in reversed(selected):
            self.file_listbox.delete(i)
            del self.files_to_process[i]
        self._update_file_count()

    def _clear_list(self):
        """Czyści całą listę plików."""
        self.file_listbox.delete(0, tk.END)
        self.files_to_process.clear()
        self._update_file_count()

    def _update_file_count(self):
        """Aktualizuje licznik plików."""
        count = len(self.files_to_process)
        self.file_count_label.config(text=f"Plików: {count}")

    def _log(self, message: str, tag: str = None):
        """Dodaje wpis do logu.

        Args:
            message: Treść komunikatu
            tag: Tag formatowania (success, error, info, timestamp)
        """
        self.log_text.config(state="normal")

        # Timestamp
        timestamp = datetime.now().strftime("[%H:%M:%S] ")
        self.log_text.insert(tk.END, timestamp, "timestamp")

        # Wiadomość
        self.log_text.insert(tk.END, message + "\n", tag)

        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def _convert(self):
        """Rozpoczyna konwersję plików."""
        if not self.files_to_process:
            messagebox.showwarning(
                "Brak plików",
                "Nie wybrano żadnych plików do przetworzenia!"
            )
            return

        if self.is_converting:
            return

        # Wyczyść log
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")

        # Uruchom konwersję w osobnym wątku
        self.is_converting = True
        self.convert_button.config(state="disabled")
        self.progress_var.set(0)

        thread = threading.Thread(target=self._convert_thread, daemon=True)
        thread.start()

    def _convert_thread(self):
        """Wątek konwersji plików."""
        success_count = 0
        error_count = 0
        total = len(self.files_to_process)

        self._log(f"Rozpoczęcie konwersji {total} plików...", "info")

        for i, file_path in enumerate(self.files_to_process):
            path = Path(file_path)

            # Określ folder wyjściowy
            if self.output_dir:
                output_dir = Path(self.output_dir)
            else:
                output_dir = path.parent

            try:
                self._log(f"Przetwarzanie: {path.name}")

                # Parsowanie
                sprawozdanie = self.sf_parser.parse(path)

                # Konwersja
                output_path, attachments = self.converter.convert(sprawozdanie, output_dir)

                self._log(f"  ✓ Zapisano: {output_path.name}", "success")

                # Informacja o załącznikach
                if attachments:
                    self._log(f"    → Zapisano {len(attachments)} załącznik(ów):", "info")
                    for att_path in attachments:
                        self._log(f"      • {att_path.name}", "info")

                success_count += 1

            except Exception as e:
                self._log(f"  ✗ Błąd: {str(e)}", "error")
                # Szczegóły błędu do debugowania
                traceback.print_exc()
                error_count += 1

            # Aktualizacja paska postępu
            progress = ((i + 1) / total) * 100
            self.progress_var.set(progress)

        # Podsumowanie
        self._log("")
        self._log(f"═══════════════════════════════════════", "info")
        self._log(f"Przetworzono: {success_count}/{total} plików", "info")
        if error_count > 0:
            self._log(f"Błędy: {error_count}", "error")
        self._log(f"═══════════════════════════════════════", "info")

        # Przywróć przycisk
        self.root.after(0, self._conversion_finished)

    def _conversion_finished(self):
        """Wywoływane po zakończeniu konwersji."""
        self.is_converting = False
        self.convert_button.config(state="normal")

    def run(self):
        """Uruchamia pętlę główną aplikacji."""
        self.root.mainloop()


def main():
    """Punkt wejścia aplikacji."""
    app = SFConverterGUI()
    app.run()


if __name__ == "__main__":
    main()
