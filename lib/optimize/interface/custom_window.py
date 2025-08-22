import tkinter as tk
from PIL import ImageTk, Image  # Add this import

class CustomWindow(tk.Tk):
    def __init__(self, title, icon_path, parent=None):
        super().__init__(parent)

        self.icon_path = icon_path

        self.title(title)
        icon_image = ImageTk.PhotoImage(Image.open(icon_path))  # Add this line
        self.wm_iconphoto(True, icon_image)  # Add this line
        
        self.iconbitmap(icon_path)
        self.overrideredirect(True)

        self.custom_frame = CustomFrame(self, title, icon_path)
        self.custom_frame.pack(side="top", fill="x")

        self.content_frame = tk.Frame(self, bg='#2b2b2b', padx=10, pady=10)
        self.content_frame.pack(side="top", fill="both", expand=True)

        self._drag_data = {"x": 0, "y": 0}

    def _on_start_drag(self, event):
        self._drag_data["x"] = event.x_root
        self._drag_data["y"] = event.y_root

    def _on_drag_motion(self, event):
        dx = event.x_root - self._drag_data["x"]
        dy = event.y_root - self._drag_data["y"]

        x = self.winfo_x() + dx
        y = self.winfo_y() + dy

        self.geometry(f"+{x}+{y}")

        self._drag_data["x"] = event.x_root
        self._drag_data["y"] = event.y_root
        


class CustomFrame(tk.Frame):
    def __init__(self, parent, title, icon_path, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.configure(bg='#4d4d4d')

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=0)

        self.rowconfigure(0, weight=0)

        self.title_label = tk.Label(self, text=title, bg='#4d4d4d', fg='white', font=('Arial', 10, 'bold'))
        self.title_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')

        self.minimize_button = tk.Button(self, text='-', width=3, height=1, relief=tk.FLAT, bg='#4d4d4d', fg='white', font=('Arial', 10, 'bold'), command=self.minimize_window)
        self.minimize_button.grid(row=0, column=1, padx=5, pady=5)

        self.close_button = tk.Button(self, text='X', width=3, height=1, relief=tk.FLAT, bg='#4d4d4d', fg='white', font=('Arial', 10, 'bold'), command=self.close_window)
        self.close_button.grid(row=0, column=2, padx=5, pady=5)

        self.title_label.bind('<ButtonPress-1>', parent._on_start_drag)
        self.title_label.bind('<B1-Motion>', parent._on_drag_motion)

    def minimize_window(self):
        # Create a hidden Toplevel widget to iconify the main window
        self.iconify_helper = tk.Toplevel(self.master)
        self.iconify_helper.withdraw()
        self.iconify_helper.iconify()
        self.iconify_helper.protocol("WM_DELETE_WINDOW", self.restore_window)
        self.master.lower()
        self.master.withdraw()

    def restore_window(self):
        # Restore the main window when the hidden Toplevel widget is de-iconified
        self.master.deiconify()
        self.master.lift()
        self.iconify_helper.destroy()
