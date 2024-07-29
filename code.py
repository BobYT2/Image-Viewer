import tkinter as tk
from tkinter import Label, filedialog, Menu, Toplevel, StringVar, IntVar, OptionMenu, Spinbox, Button
from PIL import Image, ImageTk
import os
import glob
from tkinterdnd2 import DND_FILES, TkinterDnD

class ImageViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Viewer")
        self.is_fullscreen = False
        self.slideshow_running = False
        self.image_index = 0
        self.image_paths = []
        self.transition_types = ["None", "Fade", "Slide"]
        self.current_image = None  # to store the current image

        self.slideshow_delay = IntVar(value=3)
        self.transition_type = StringVar(value=self.transition_types[0])

        self.create_menu()
        self.create_widgets()
        self.bind_keys()
        self.setup_drag_and_drop()

    def create_menu(self):
        menubar = Menu(self.root)
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open", command=self.choose_image)
        file_menu.add_command(label="Slideshow", command=self.slideshow_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menubar)

    def create_widgets(self):
        self.import_button = Button(self.root, text="Import Image", command=self.choose_image)
        self.import_button.pack(pady=20)

        self.label = Label(self.root)
        self.label.pack(expand=True)

        self.info_label = Label(self.root, text="Drag and drop an image or click 'Import Image'", bg="grey", fg="white")
        self.info_label.pack(side="bottom", fill="x")

    def bind_keys(self):
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen_or_slideshow)
        self.root.bind("<Configure>", self.on_resize)  # bind the resize event

    def setup_drag_and_drop(self):
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.handle_drop)

    def handle_drop(self, event):
        file_path = event.data
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]
        self.display_image(file_path)

    def choose_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp")]
        )
        if file_path:
            self.display_image(file_path)

    def display_image(self, file_path):
        self.image_paths = [file_path]
        self.show_image(file_path)
        self.import_button.pack_forget()
        self.info_label.pack_forget()

    def show_image(self, file_path):
        self.current_image = Image.open(file_path)
        self.resize_image()  # call resize_image to fit the window
        self.root.geometry(f"{self.current_image.width}x{self.current_image.height+30}")
        self.root.attributes('-fullscreen', False)  # Ensure fullscreen is off when showing a new image

    def resize_image(self):
        if self.current_image:
            img = self.current_image.copy()
            img.thumbnail((self.root.winfo_width(), self.root.winfo_height() - 30), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.label.config(image=photo)
            self.label.image = photo  # keep a reference to prevent garbage collection

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes('-fullscreen', self.is_fullscreen)

    def exit_fullscreen_or_slideshow(self, event=None):
        if self.is_fullscreen:
            self.is_fullscreen = False
            self.root.attributes('-fullscreen', False)
        elif self.slideshow_running:
            self.slideshow_running = False
            self.root.after_cancel(self.slideshow_after_id)
            self.label.pack(expand=True)
            self.info_label.pack(side="bottom", fill="x")

    def on_resize(self, event):
        self.resize_image()  # call resize_image on window resize

    def slideshow_settings(self):
        settings_window = Toplevel(self.root)
        settings_window.title("Slideshow Settings")
        settings_window.geometry("300x200")

        Label(settings_window, text="Seconds between images:").pack(pady=5)
        Spinbox(settings_window, from_=1, to=10, textvariable=self.slideshow_delay).pack(pady=5)

        Label(settings_window, text="Transition type:").pack(pady=5)
        OptionMenu(settings_window, self.transition_type, *self.transition_types).pack(pady=5)

        Button(settings_window, text="Choose Folder", command=self.choose_folder).pack(pady=10)
        Button(settings_window, text="Start Slideshow", command=self.start_slideshow).pack(pady=10)

    def choose_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.image_paths = glob.glob(os.path.join(folder_path, "*.*"))
            self.image_paths = [path for path in self.image_paths if path.lower().endswith(('jpg', 'jpeg', 'png', 'gif', 'bmp'))]

    def start_slideshow(self):
        if not self.image_paths:
            return
        self.slideshow_running = True
        self.image_index = 0
        self.show_next_image()
        self.label.pack(expand=True)
        self.info_label.pack_forget()

    def show_next_image(self):
        if not self.slideshow_running:
            return
        if self.image_index >= len(self.image_paths):
            self.image_index = 0
        self.show_image(self.image_paths[self.image_index])
        self.image_index += 1
        self.slideshow_after_id = self.root.after(self.slideshow_delay.get() * 1000, self.show_next_image)

def main():
    root = TkinterDnD.Tk()
    app = ImageViewerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
