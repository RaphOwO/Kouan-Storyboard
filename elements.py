from customtkinter import *
from PIL import Image
from functions import *
from abc import abstractmethod

font_size = 12

class Selectable:
    selected_object = None  # Class variable to track the currently selected object

    def __init__(self, widget, layer):
        self.widget = widget
        self.layer = layer
        self._drag_data = {"x": 0, "y": 0}
        self.is_selected = False

        # Default unselected border color
        self.unselected_border_color = "gray"

        # Bind events for selection and dragging
        self.widget.bind("<Button-1>", self.on_click)
        self.widget.bind("<B1-Motion>", self.do_drag)
        self.widget.bind("<ButtonRelease-1>", self.stop_drag)

        # Bind a click event on the layer to deselect the object
        self.layer.bind("<Button-1>", self.deselect)

        self.widget.bind("<Delete>", self.delete_if_selected)

    def on_click(self, event):
        # Select the current object
        self.select()
        # Give focus to the widget to enable typing
        self.widget.focus_set()
        # Start dragging
        self.start_drag(event)
        # Stop the event from propagating to the layer
        return "break"

    def select(self):
        # Deselect any previously selected object
        if Selectable.selected_object is not None and Selectable.selected_object != self:
            Selectable.selected_object.deselect()

        # Mark this object as selected
        Selectable.selected_object = self
        self.is_selected = True
        color = get_color()
        self.widget.configure(border_width = 2, border_color=color)

    def deselect(self, event=None):
        # Deselect the current object if selected
        if self.is_selected:
            self.is_selected = False
            self.widget.configure(border_width = 0, border_color=self.unselected_border_color)
            Selectable.selected_object = None

    def start_drag(self, event):
        # Record the initial click position for dragging
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def do_drag(self, event):
        # Calculate the new position based on mouse movement
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]

        # Update the widget's position
        x = self.widget.winfo_x() + dx
        y = self.widget.winfo_y() + dy
        self.widget.place(x=x, y=y)

    def stop_drag(self, event):
        self._drag_data = {"x": 0, "y": 0}
        self.layer.file_parent.save_file_state()

    def delete_if_selected(self, event):
        if Selectable.selected_object == self:
            self.deselect()
            self.widget.destroy()

        self.layer.file_parent.save_file_state()

    @abstractmethod
    def to_dict(self):
        """Serialize the current object state to a dictionary."""

        return {
            "type": self.__class__.__name__,
            "x": self.widget.winfo_x(),
            "y": self.widget.winfo_y(),
            "width": self.widget.winfo_width(),
            "height": self.widget.winfo_height(),
            "content": self.get_content()  # Specific method to get content, if any
        }

    # def from_dict(self, data):
    #     """Load object state from a dictionary."""
    #     print(data)
    #     self.widget.place(x=data["x"], y=data["y"])

    #     self.set_content(data.get("content", ""))  # Specific method to set content

    #     # After update, print the width and height
    #     print(self.widget.winfo_width(), self.widget.winfo_height())

    @abstractmethod
    def get_content(self):
        """Get the content of the object. Override in subclasses if needed."""
        return None

    @abstractmethod
    def set_content(self, content):
        """Set the content of the object. Override in subclasses if needed."""
        pass

class Toolbar(CTkFrame):
    def __init__(self, master, width=50, height=475, corner_radius=50, border_width=None, bg_color="transparent",
                 fg_color="transparent", border_color=None, background_corner_colors=None,
                 overwrite_preferred_drawing_method=None, **kwargs):
        super().__init__(master, width, height, corner_radius, border_width, bg_color, fg_color, border_color,
                         background_corner_colors, overwrite_preferred_drawing_method, **kwargs)
        self.place(x=35, rely=0.55, anchor="center")

        self.layer = master

        tool = CTkFrame(self, width=50, height=350, corner_radius=50, fg_color="light grey")
        tool.pack(side=TOP)

        undo_redo = CTkFrame(self, width=50, height=100, fg_color="light grey")
        undo_redo.pack(side=BOTTOM)

        for i in range(7):
            if i == 4:
                tools = CTkButton(tool, text=str(i), text_color="black", font=("Arial", 16), width=50, height=50,
                                  fg_color="transparent", corner_radius=0, hover_color= "dark grey",
                                  command=self.add_note)
            elif i == 3:
                tools = CTkButton(tool, text=str(i), text_color="black", font=("Arial", 16), width=50, height=50,
                                  fg_color="transparent", corner_radius=0, hover_color= "dark grey",
                                  command=self.add_textbox)
            elif i == 2:
                tools = CTkButton(tool, text=str(i), text_color="black", font=("Arial", 16), width=50, height=50,
                                  fg_color="transparent", corner_radius=0, hover_color= "dark grey",
                                  command=self.add_scene)
            else:
                tools = CTkButton(tool, text=str(i), text_color="black", font=("Arial", 16), width=50, height=50,
                                  fg_color="transparent", corner_radius=0, hover_color= "dark grey")
            tools.pack()

        redo = CTkButton(undo_redo, text="->", text_color="black", font=("Arial", 16), width=50, height=50,
                         fg_color="transparent", corner_radius=0, hover_color= "dark grey")
        redo.pack()

        undo = CTkButton(undo_redo, text="<-", text_color="black", font=("Arial", 16), width=50, height=50,
                         fg_color="transparent", corner_radius=0, hover_color= "dark grey")
        undo.pack()

    def add_note(self):
        """Callback to add a Note to the current layer.""" 
        self.layer.add_element(Note(self.layer))

    def add_textbox(self):
        self.layer.add_element(Textbox(self.layer))

    def add_scene(self):
        self.layer.add_element(Scene(self.layer))


class Note(CTkTextbox, Selectable):
    def __init__(self, master, width=200, height=200, corner_radius=None, border_width=None, border_spacing=3,
                 bg_color="transparent", fg_color="#ffd60a", border_color=None, text_color="black",
                 scrollbar_button_color=None, scrollbar_button_hover_color=None, font=("Arial", font_size), activate_scrollbars=True, **kwargs):
        CTkTextbox.__init__(self, master, width, height, corner_radius, border_width, border_spacing, bg_color, fg_color,
                            border_color, text_color, scrollbar_button_color, scrollbar_button_hover_color, font,
                            activate_scrollbars, **kwargs)
        Selectable.__init__(self, self, master)
    
    def get_content(self):
        return self.get("1.0", "end")  # Get the text content

    def set_content(self, content):
        self.delete("1.0", "end")
        self.insert("1.0", content)

class Textbox(CTkFrame, Selectable):
    def __init__(self, master, width = 262, height = 75, box_width = 200, box_height = 50, font_size = 12, **kwargs):
        # Initialize the frame with a default width and height
        initial_width = kwargs.pop("width", width)
        initial_height = kwargs.pop("height", height)
        self.font_size = kwargs.pop("font_size", 12)  # Keep track of the font size manually

        CTkFrame.__init__(self, master, width=initial_width, height=initial_height, **kwargs)
        Selectable.__init__(self, self, master)

        self.configure(width = initial_width, height = initial_height)

        self.master = master
        # Place the frame initially
        self.place(x=50, y=50)

        # Textbox inside the resizable frame
        self.textbox = CTkTextbox(self, wrap="word", width=box_width, height=box_height, font=("Arial", self.font_size))
        self.textbox.pack(fill=BOTH, expand=True, padx=5, pady=5)

        self.textbox.bind("<Delete>", self.delete_if_selected)

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

        # Resizer handles and other frame setup omitted for brevity...

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

    def get_content(self):
        return self.textbox.get("1.0", "end")  # Get the text content

    def set_content(self, content):
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", content)

    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "x": self.widget.winfo_x(),
            "y": self.widget.winfo_y(),
            "width": self.widget.winfo_width(),
            "height": self.widget.winfo_height(),
            "box_width": self.textbox.winfo_width() * 0.77,
            "box_height": self.textbox.winfo_height() * 0.77,
            "font_size": self.font_size,
            "content": self.get_content()  
        }

class SettingsWindow:
    def __init__(self, master, parent):
        self.master = master
        self.parent = parent

        self.top = CTkToplevel(master)
        self.top.title("Settings")

        self.settings_frame = CTkFrame(self.top)
        self.settings_frame.pack(fill="both", expand=True)

        self.dark_mode_switch = CTkSwitch(self.settings_frame, text="Light Mode", command=self.toggle_dark_mode)
        self.dark_mode_switch.pack()

        save_button = CTkButton(self.settings_frame, text="Save", font=("Arial", 16), command=self.save_settings)
        save_button.pack()

        help_button = CTkButton(self.settings_frame, text="Help", font=("Arial", 16), command=self.open_help)
        help_button.pack()

    def toggle_dark_mode(self):
        if self.dark_mode_switch.get():
            set_appearance_mode("light")
        else:
            set_appearance_mode("dark")

    def save_settings(self):
        self.parent.save_file_state()

    def open_help(self):
        help_window = CTkToplevel(self.top)
        help_window.title("Help")
        help_window.geometry("400x200")
        help_label = CTkLabel(help_window, text="Here is some help information!")
        help_label.pack(pady=20)

class Scene(CTkFrame, Selectable):
    def __init__(self, master, width = 200, height = 150, corner_radius = None, border_width = None, bg_color = "transparent", fg_color = "#252525", border_color = None, background_corner_colors = None, overwrite_preferred_drawing_method = None, **kwargs):
        CTkFrame.__init__(self, master, width, height, corner_radius, border_width, bg_color, fg_color, border_color,       
                          background_corner_colors, overwrite_preferred_drawing_method, **kwargs)
        Selectable.__init__(self, self, master)

        truncated_name = truncate_name("Scene 1")
        self.title_button = CTkButton(self, text=truncated_name, text_color="white", font=("Arial", 16), anchor= "sw",
                                    fg_color="transparent", hover_color="dark grey")
        self.title_button.pack(side=TOP, padx=5)

        self.textbox = CTkTextbox(self, wrap="word", font=("Arial", font_size), height= 120, corner_radius=0)
        self.textbox.pack(side = TOP, fill = BOTH)