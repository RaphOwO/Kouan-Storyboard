from customtkinter import *
from elements import Selectable
from PIL import Image

class ImageBox(CTkFrame, Selectable):
    def __init__(self, master, image_path, width = 262, height = 75, box_width = 200, box_height = 50, image: Image = None, **kwargs):
        self.pil_img = Image.open(image_path) 

        self.img_ratio = self.pil_img.width / self.pil_img.height

        fixed_dims = self.fix_ratio(width, height, self.img_ratio, True)
        width = fixed_dims[0]
        height = fixed_dims[1]

        self.img = CTkImage(
            light_image=self.pil_img,
            dark_image=self.pil_img,
            size=(width, height)
        )

        # Initialize the frame with a default width and height
        initial_width = kwargs.pop("width", width)
        initial_height = kwargs.pop("height", height)

        CTkFrame.__init__(self, master, width=initial_width, height=initial_height, **kwargs)
        Selectable.__init__(self, self, master)

        self.configure(width = initial_width, height = initial_height)

        # Place the frame initially
        self.place(x=50, y=50)

        # Textbox inside the resizable frame
        self.label = CTkLabel(self, width=box_width, height=box_height, image=self.img, text="")
        self.label.pack(fill=BOTH, expand=True, padx=5, pady=5)

        self.label.bind("<Delete>", self.delete_if_selected)

        # Resizer handles
        self.resizer_corner_se = CTkFrame(self, width=10, height=10, fg_color="dark grey", cursor="bottom_right_corner")
        self.resizer_corner_se.place(relx=1.0, rely=1.0, anchor="se")

        self.resizer_right = CTkFrame(self, width=5, height=initial_height, fg_color="grey", cursor="sb_h_double_arrow")
        self.resizer_right.place(relx=1.0, rely=0.25, anchor="ne", relheight=0.5)

        self.resizer_bottom = CTkFrame(self, height=5, width=initial_height, fg_color="grey", cursor="sb_v_double_arrow")
        self.resizer_bottom.place(relx=0.25, rely=1.0, anchor="sw", relwidth=0.5)


        # Bind events to the resizers
        self.resizer_corner_se.bind("<B1-Motion>", self.resize_frame_se)
        self.resizer_corner_se.bind("<Button-1>", self.start_resizing)

        self.resizer_right.bind("<B1-Motion>", self.resize_frame_width_right)
        self.resizer_right.bind("<Button-1>", self.start_resizing)

        self.resizer_bottom.bind("<B1-Motion>", self.resize_frame_height_bottom)
        self.resizer_bottom.bind("<Button-1>", self.start_resizing)
        
        # Variables to track initial position and size
        self.start_x = 0
        self.start_y = 0
        self.start_width = initial_width
        self.start_height = initial_height

        # Resizer handles and other frame setup omitted for brevity...


    def fix_ratio(self, in_width, in_height, ratio, increasing: bool):
        # logical xor
        if not (bool((in_width) > (in_height * ratio)) ^ bool(increasing)):
            return (in_width, int(in_width / ratio))
        else:
            return (in_height * ratio, in_height)

    def delete_if_selected(self, event):
        if Selectable.selected_object == self:
            self.deselect()
            self.destroy()

        self.master.file_parent.save_file_state()

    def start_resizing(self, event):
        # Record the initial position and dimensions when resizing begins
        self.start_x = event.x_root
        self.start_y = event.y_root
        self.start_width = self.winfo_width()
        self.start_height = self.winfo_height()
    

    def resize_frame_se(self, event):
        # Calculate new dimensions based on mouse movement (corner resize)
        dx = event.x_root - self.start_x
        dy = event.y_root - self.start_y

        new_width = max(self.start_width + dx, 50)  # Minimum width set to 50
        new_height = max(self.start_height + dy, 50)  # Minimum height set to 50

        fixed_dims = self.fix_ratio(new_width, new_height, self.img_ratio, True)

        self.img = CTkImage(
            light_image=self.pil_img,
            dark_image=self.pil_img,
            size=fixed_dims
        )

        new_width = fixed_dims[0]
        new_height = fixed_dims[1]

        # Resize the frame and the textbox
        self.configure(width=new_width, height=new_height)
        self.label.configure(image=self.img)
        self.label.configure(width=new_width, height=new_height)

    def resize_frame_width_right(self, event):
        # Resize only the width of the frame
        dx = event.x_root - self.start_x
        new_width = max(self.start_width + dx, 50)  # Minimum width set to 50

        # Adjust width
        fixed_dims = self.fix_ratio(new_width, self.start_height, self.img_ratio, new_width>self.start_width)

        self.img = CTkImage(
            light_image=self.pil_img,
            dark_image=self.pil_img,
            size=fixed_dims
        )

        new_width = fixed_dims[0]
        new_height = fixed_dims[1]

        self.configure(width=new_width, height=new_height)
        self.label.configure(image=self.img)
        self.label.configure(width=new_width, height=new_height)


    def resize_frame_height_bottom(self, event):
        # Resize only the height of the frame
        dy = event.y_root - self.start_y
        new_height = max(self.start_height + dy, 50)  # Minimum width set to 50

        fixed_dims = self.fix_ratio(self.start_width, new_height, self.img_ratio, new_height>self.start_height)

        self.img = CTkImage(
            light_image=self.pil_img,
            dark_image=self.pil_img,
            size=fixed_dims
        )

        new_width = fixed_dims[0]
        new_height = fixed_dims[1]

        # Resize the frame and the textbox
        self.configure(width=new_width, height=new_height)
        self.label.configure(image=self.img)
        self.label.configure(width=new_width, height=new_height)

    def get_content(self):
        return self.label.get("1.0", "end")  # Get the text content

    def set_content(self, content):
        self.label.delete("1.0", "end")
        self.label.insert("1.0", content)

    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "x": self.widget.winfo_x(),
            "y": self.widget.winfo_y(),
            "width": self.widget.winfo_width(),
            "height": self.widget.winfo_height(),
            "box_width": self.label.winfo_width() * 0.8,
            "box_height": self.label.winfo_height() * 0.8,
            "font_size": self.font_size,
            "content": self.get_content()  
        }

def main():
    app = CTk()
    app.minsize(width=600, height=400)
    app.title("Draggable Resizable Image Example")
    set_appearance_mode("light")

    # Create an instance of the draggable resizablec textbox
    resizable_img = ImageBox(app, fg_color="light grey", corner_radius=10, width=300, height=200)

    app.mainloop()

if __name__ == "__main__":
    main()
