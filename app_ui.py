import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from typing import Optional

from logger_config import app_logger
from downloader_service import DownloaderService, DownloadRequest


class AppUI:
    def __init__(self, root: tk.Tk, service: DownloaderService):
        try:
            app_logger.log_info("Initializing AppUI...")
            self.root = root
            self.service = service

            self.root.title("YouTube Downloader")
            
            # Handle window closing properly
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            app_logger.log_info("AppUI initialized successfully")
        except Exception as e:
            app_logger.log_exception("Error initializing AppUI")
            raise

        self.mainframe = ttk.Frame(self.root)
        self.mainframe.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        ttk.Label(self.mainframe, text="Video/Audio URL:").grid(
            column=0, row=0, sticky=tk.W
        )
        self.url_entry = ttk.Entry(self.mainframe, width=50)
        self.url_entry.grid(column=1, row=0, sticky=(tk.W, tk.E))

        self.format_var = tk.StringVar(value="Video")
        self.quality_var = tk.StringVar(value="High")

        ttk.Label(self.mainframe, text="Format:").grid(column=0, row=1, sticky=tk.W)
        ttk.Radiobutton(
            self.mainframe, text="Video", variable=self.format_var, value="Video"
        ).grid(column=1, row=1, sticky=tk.W)
        ttk.Radiobutton(
            self.mainframe, text="Audio", variable=self.format_var, value="Audio"
        ).grid(column=1, row=2, sticky=tk.W)

        ttk.Label(self.mainframe, text="Quality:").grid(column=0, row=3, sticky=tk.W)
        ttk.Radiobutton(
            self.mainframe, text="High", variable=self.quality_var, value="High"
        ).grid(column=1, row=3, sticky=tk.W)
        ttk.Radiobutton(
            self.mainframe, text="Medium", variable=self.quality_var, value="Medium"
        ).grid(column=1, row=4, sticky=tk.W)
        ttk.Radiobutton(
            self.mainframe, text="Low", variable=self.quality_var, value="Low"
        ).grid(column=1, row=5, sticky=tk.W)

        ttk.Button(
            self.mainframe, text="Download", command=self.on_download_click
        ).grid(column=1, row=6, sticky=tk.W)

        for child in self.mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

        self.url_entry.focus()
        self.root.bind("<Return>", lambda _: self.on_download_click())

    def on_download_click(self):
        try:
            url = self.url_entry.get().strip()
            app_logger.log_info(f"Download button clicked with URL: {url}")
            
            if not url:
                app_logger.log_warning("Empty URL provided")
                messagebox.showerror("Error", "Please enter a valid YouTube URL.")
                return

            req = DownloadRequest(
                url=url, format_=self.format_var.get(), quality=self.quality_var.get()
            )
            app_logger.log_info(f"Created download request: {req.format_}, {req.quality}")
            self.show_progress_window(req)
            
        except Exception as e:
            app_logger.log_exception("Error in on_download_click")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def show_progress_window(self, req: DownloadRequest):
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Download in Progress")
        progress_window.geometry("500x300")

        ttk.Label(progress_window, text="Downloading...").pack(pady=5)

        text_area = scrolledtext.ScrolledText(progress_window, wrap=tk.WORD, height=10)
        text_area.pack(expand=True, fill="both", padx=10, pady=5)

        progress_bar = ttk.Progressbar(progress_window, mode="indeterminate")
        progress_bar.pack(fill="x", padx=10, pady=5)
        progress_bar.start()

        def on_line(line: str) -> None:
            self.root.after(0, lambda: self._append_text(text_area, line))

        def on_done(
            success: bool, destination: Optional[str], error: Optional[str]
        ) -> None:
            def finalize():
                progress_window.after(1000, progress_window.destroy)
                if success:
                    if destination:
                        messagebox.showinfo(
                            "Download Completed", f"File saved to:\n{destination}"
                        )
                        print(f"File saved to: {destination}")
                    else:
                        messagebox.showinfo(
                            "Success", "Download completed, but file path not found!"
                        )
                else:
                    messagebox.showerror("Error", f"Download failed: {error}")

            self.root.after(0, finalize)

        self.service.run(req, on_line=on_line, on_done=on_done)

    def on_closing(self):
        """Handle window closing event"""
        app_logger.log_info("User requested to close application")
        if messagebox.askokcancel("Quit", "Do you want to quit YouTube Downloader?"):
            app_logger.log_info("Application closing by user request")
            self.root.quit()
            self.root.destroy()

    @staticmethod
    def _append_text(text_area: scrolledtext.ScrolledText, message: str) -> None:
        text_area.insert(tk.END, message + "\n")
        text_area.yview(tk.END)
