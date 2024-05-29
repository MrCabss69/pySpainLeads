# interface.py
import tkinter as tk
from tkinter import messagebox, ttk
import threading
import queue
import logging
from core import JobFinderScraper

logging.basicConfig(level=logging.INFO)

class JobFinderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Job Finder App")
        self.geometry("800x600")  # Tamaño de ventana ajustado
        self.running = False
        self.task_queue = queue.Queue()
        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        """Crea los widgets para la interfaz gráfica utilizando ttk para un mejor estilo."""
        ttk.Label(self, text="Términos de búsqueda (separados por comas):").pack(pady=10)
        self.search_terms_entry = ttk.Entry(self, width=50)
        self.search_terms_entry.pack(pady=5)

        ttk.Label(self, text="Localidades (separadas por comas):").pack(pady=10)
        self.locations_entry = ttk.Entry(self, width=50)
        self.locations_entry.pack(pady=5)
        
        self.headless_var = tk.BooleanVar(value=True)
        self.headless_checkbox = ttk.Checkbutton(self, text="Modo Headless", variable=self.headless_var)
        self.headless_checkbox.pack(pady=10)

        self.search_button = ttk.Button(self, text="Buscar", command=self.start_search)
        self.search_button.pack(pady=5)

        self.cancel_button = ttk.Button(self, text="Cancelar", command=self.cancel_search, state=tk.DISABLED)
        self.cancel_button.pack(pady=5)

        self.progress = ttk.Progressbar(self, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)

        self.log = tk.Text(self, height=10, state='disabled', wrap='word')
        self.log.pack(pady=10, padx=10)

    def start_search(self):
        """Handles input validation and thread initiation for searching."""
        headless = self.headless_var.get()
        self.scraper = JobFinderScraper(headless)
        
        
        search_terms = self.search_terms_entry.get().split(',')
        locations = self.locations_entry.get().split(',')
        if not search_terms or not locations:
            messagebox.showwarning("Entrada inválida", "Por favor, introduzca términos de búsqueda y localidades válidas.")
            return

        search_terms = [term.strip() for term in search_terms if term.strip()]
        locations = [location.strip() for location in locations if location.strip()]

        self.running = True
        self.configure_buttons_for_search()
        self.initialize_progress_bar(len(search_terms), len(locations))
        
        # Create and start the search thread
        self.start_thread_for_search(search_terms, locations)

    def configure_buttons_for_search(self):
        self.search_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)

    def initialize_progress_bar(self, num_terms, num_locations):
        self.progress["maximum"] = num_terms * num_locations
        self.progress["value"] = 0

    def start_thread_for_search(self, search_terms, locations):
        for term in search_terms:
            for location in locations:
                self.task_queue.put((term, location))
        self.search_thread = threading.Thread(target=self.process_queue)
        self.search_thread.start()

    def process_queue(self):
        """ Procesar la cola en un hilo separado para evitar bloquear la GUI """
        while not self.task_queue.empty() and self.running:
            term, location = self.task_queue.get()
            self.update_log(f"Buscando: {term} en {location}")
            try:
                self.scraper.search(term, location)
                self.update_progress()
            except Exception as e:
                self.update_log(f"Error al buscar {term} en {location}: {e}")
            finally:
                self.task_queue.task_done()
            self.after(100, self.process_queue)

        self.finalize_search()

    def update_progress(self):
        """Update the progress bar and check if task is complete."""
        self.progress.step(1)
        if self.progress['value'] == self.progress['maximum']:
            messagebox.showinfo("Búsqueda completada", "La búsqueda ha sido completada.")

    def finalize_search(self):
        """Handles UI updates after search is completed or canceled."""
        self.running = False
        self.search_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)

    def cancel_search(self):
        """Cancels the ongoing search and informs the user."""
        self.running = False
        self.update_log("Búsqueda cancelada por el usuario.")
        self.finalize_search()

    def update_log(self, message):
        """Appends messages to the log widget."""
        self.log.config(state='normal')
        self.log.insert(tk.END, message + "\n")
        self.log.config(state='disabled')
        self.log.yview(tk.END)

    def on_closing(self):
        """Handles application closure ensuring threads and WebDriver are safely closed."""
        if messagebox.askokcancel("Salir", "¿Está seguro que desea salir?"):
            self.running = False
            if hasattr(self, 'search_thread') and self.search_thread.is_alive():
                self.search_thread.join()
            self.scraper.close_driver()
            self.destroy()