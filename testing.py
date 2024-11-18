from customtkinter import *

class ResizableTextbox(CTkFrame):
    def __init__(self, master=None, **kwargs):
        # Initialize the frame with a default width and height
        initial_width = kwargs.pop("width", 300)
        initial_height = kwargs.pop("height", 200)
        self.font_size = kwargs.pop("font_size", 12)  # Keep track of the font size manually

        super().__init__(master, **kwargs, width=initial_width, height=initial_height)

        self.master = master
        # Place the frame initially
        self.place(x=50, y=50)

        # Textbox inside the resizable frame
        self.textbox = CTkTextbox(self, wrap="word", font=("Arial", self.font_size))
        self.textbox.pack(fill=BOTH, expand=True, padx=5, pady=5)

        # Resizer handles
        self.resizer_corner = CTkFrame(self, width=10, height=10, fg_color="dark grey", cursor="bottom_right_corner")
        self.resizer_corner.place(relx=1.0, rely=1.0, anchor="se")

        self.resizer_left = CTkFrame(self, width=5, height=initial_height, fg_color="grey", cursor="sb_h_double_arrow")
        self.resizer_left.place(relx=0, rely=0.25, anchor="nw", relheight=0.5)

        self.resizer_right = CTkFrame(self, width=5, height=initial_height, fg_color="grey", cursor="sb_h_double_arrow")
        self.resizer_right.place(relx=1.0, rely=0.25, anchor="ne", relheight=0.5)

        self.resizer_top = CTkFrame(self, height=5, width=initial_height, fg_color="grey", cursor="sb_v_double_arrow")
        self.resizer_top.place(relx=0.25, rely=0.0, anchor="nw", relwidth=0.5)

        self.resizer_bottom = CTkFrame(self, height=5, width=initial_height, fg_color="grey", cursor="sb_v_double_arrow")
        self.resizer_bottom.place(relx=0.25, rely=1.0, anchor="sw", relwidth=0.5)


        # Bind events to the resizers
        self.resizer_corner.bind("<B1-Motion>", self.resize_frame)
        self.resizer_corner.bind("<Button-1>", self.start_resizing)

        self.resizer_right.bind("<B1-Motion>", self.resize_frame_width_right)
        self.resizer_right.bind("<Button-1>", self.start_resizing)

        self.resizer_left.bind("<B1-Motion>", self.resize_frame_width_left)
        self.resizer_left.bind("<Button-1>", self.start_resizing)

        self.resizer_bottom.bind("<B1-Motion>", self.resize_frame_height_bottom)
        self.resizer_bottom.bind("<Button-1>", self.start_resizing)

        self.resizer_top.bind("<B1-Motion>", self.resize_frame_height_top)
        self.resizer_top.bind("<Button-1>", self.start_resizing)
        """

        self.resizer_left.bind("<B1-Motion>", self.resize_frame_width_only)
        self.resizer_left.bind("<Button-1>", self.start_resizing)

        """
        
        # Variables to track initial position and size
        self.start_x = 0
        self.start_y = 0
        self.start_width = initial_width
        self.start_height = initial_height
        self.start_font_size = self.font_size 

    def start_resizing(self, event):
        # Record the initial position and dimensions when resizing begins
        self.start_x = event.x_root
        self.start_y = event.y_root
        self.start_width = self.winfo_width()
        self.start_height = self.winfo_height()

        print("e")

    def resize_frame(self, event):
        # Here's how this works:
        # x -> change frame size
        # y -> change text size
        # Calculate new dimensions based on mouse movement (corner resize)
        dx = event.x_root - self.start_x
        dy = event.y_root - self.start_y

        new_width = max(self.start_width + dx, 50)  # Minimum width set to 50
        new_height = max(self.start_height + dy, 50)  # Minimum height set to 50

        # Resize the frame and the textbox
        self.configure(width=new_width, height=new_height)
        self.textbox.configure(width=new_width, height=new_height)

        # Adjust font size based on height change (proportional resizing)
        self.font_size = max(new_height / self.start_height * self.start_font_size, 12)
        self.textbox.configure(font=("Arial", self.font_size))

    def resize_frame_width_right(self, event):
        # Resize only the width of the frame
        dx = event.x_root - self.start_x
        new_width = max(self.start_width + dx, 50)  # Minimum width set to 50

        # Adjust width
        self.configure(width=new_width)
        self.textbox.configure(width=new_width)
    
    def resize_frame_width_left(self, event):
        # Resize only the width of the frame
        dx = event.x_root - self.start_x
        new_width = max(self.start_width - dx, 50)  # Minimum width set to 50
    
        # Adjust width
        self.configure(width=new_width)
        print(event.x_root - self.master.winfo_rootx())
        self.textbox.configure(width=new_width)
        self.place(x=event.x_root - self.master.winfo_rootx(), y=self.winfo_y())

    def resize_frame_height_bottom(self, event):
        # Resize only the height of the frame
        dy = event.y_root - self.start_y
        new_height = max(self.start_height + dy, 50)  # Minimum width set to 50

        # Adjust height
        self.configure(height=new_height)
        self.textbox.configure(height=new_height)
    
    def resize_frame_height_top(self, event):
         # Resize only the height of the frame
        dy = event.y_root - self.start_y
        new_height = max(self.start_height - dy, 50)  # Minimum width set to 50

        # Adjust height
        self.configure(height=new_height)
        self.textbox.configure(height=new_height)
        self.place(y=event.y_root - self.master.winfo_rooty(), x=self.winfo_x())


def main():
    app = CTk()
    app.minsize(width=600, height=400)
    app.title("Draggable Resizable Textbox Example")
    set_appearance_mode("light")

    # Create an instance of the draggable resizable textbox
    resizable_textbox = ResizableTextbox(app, fg_color="light grey", corner_radius=10, width=300, height=200)

    app.mainloop()

if __name__ == "__main__":
    main()
