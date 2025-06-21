from tkinter import *
from PIL import Image, ImageTk
import yt_dlp

class YouTubeDownloaderApp:
    def __init__(self, master):
        self.master = master
        master.title("Youtube Video Downloader")
        master.geometry("750x900+400+50")
        master.configure(bg="#d8d9e5", height=20, width=20)
        master.resizable(True, True)

        self.gui_font = "Microsoft yahie UI Light"

        # --- Progress label ---
        self.progress_label = Label(master, text="", fg="blue", bg="#d8d9e5", font=(self.gui_font, 12))
        self.progress_label.place(x=74, y=770)

        # --- Image ---
        original_image = Image.open("youtube-log0.png")
        resized_image = original_image.resize((400, 250))
        self.img = ImageTk.PhotoImage(resized_image)
        Label(master, image=self.img, bd=2, bg="#d8d9e5").place(x=72, y=0)

        # --- Frame ---
        frame = Frame(master, width=600, height=530, bg="#fff")
        frame.place(x=74, y=252)

        Label(frame, text="Youtube Video Download", fg="#57a1f8", bg="#F8FBE7", font=(self.gui_font, 22, "bold")).place(x=10, y=10)
        Label(frame, text="Link to video :-> ", fg="#019f90", bg="#F8EBE7", font=(self.gui_font, 14, "bold")).place(x=10, y=80)

        self.link = Text(frame, fg="black", bd=1, height=1, width=45, bg="light yellow", font=(self.gui_font, 13))
        self.link.place(x=135, y=80)

        Button(frame, width=10, padx=1, pady=3, text="Download", bg="#57a1f8", fg="white", border=3,
               command=self.download, font=(self.gui_font, 14, "bold")).place(x=140, y=200)

    def download(self):
        v_link = self.link.get("1.0", "end").strip()

        def hook(d):
            if d['status'] == 'downloading':
                percent = d.get('_percent_str', '').strip()
                self.master.title(f"Downloading... {percent}")
                self.progress_label.config(text=f"Downloading... {percent}")
            elif d['status'] == 'finished':
                self.master.title("Processing...")
                self.progress_label.config(text="Processing video...")

        ydl_opts = {
            'format': 'best[ext=mp4]',
            'outtmpl': '%(title)s.%(ext)s',
            'progress_hooks': [hook],
            'noplaylist': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([v_link])
            self.master.title("Download complete!")
            self.progress_label.config(text="Download complete!")
        except Exception as e:
            print(f"Error: {e}")
            self.master.title("Error")
            self.progress_label.config(text="Download error.")


# --- App start ---
if __name__ == "__main__":
    root = Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()
