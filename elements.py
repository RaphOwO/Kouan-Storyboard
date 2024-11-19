from customtkinter import *
from PIL import Image
from functions import *
from tkinter import colorchooser
from abc import abstractmethod

font_size = 12

class Selectable:
    selected_object = None 

    def __init__(self, widget, layer):
        self.widget = widget
        self.layer = layer
        self._drag_data = {"x": 0, "y": 0}
        self.is_selected = False

        self.unselected_border_color = "gray"

        self.widget.bind("<Button-1>", self.on_click)
        self.widget.bind("<B1-Motion>", self.do_drag)
        self.widget.bind("<ButtonRelease-1>", self.stop_drag)

        self.layer.bind("<Button-1>", self.deselect)

        self.widget.bind("<Delete>", self.delete_if_selected)

    def on_click(self, event):
        self.select()
        self.widget.focus_set()
        self.start_drag(event)
        return

    def select(self):
        if Selectable.selected_object is not None and Selectable.selected_object != self:
            Selectable.selected_object.deselect()

        Selectable.selected_object = self
        self.is_selected = True
        color = get_color()
        self.widget.configure(border_width = 2, border_color=color)

        if isinstance(self, ImageBox):
            self.show_resizers()

    def deselect(self, event=None):
        if self.is_selected:
            self.is_selected = False
            self.widget.configure(border_width = 0, border_color=self.unselected_border_color)
            Selectable.selected_object = None

        if isinstance(self, ImageBox):
                self.hide_resizers()

        self.layer.file_parent.save_file_state()

    def start_drag(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def do_drag(self, event):
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]

        x = (self.widget.winfo_x() + dx) * 0.8
        y = (self.widget.winfo_y() + dy) * 0.8
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
        pass

    @abstractmethod
    def get_content(self):
        return None

    @abstractmethod
    def set_content(self, content):
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
        
        iconcursor = CTkImage(Image.open("images\\cursor.png"), size=(20, 20))
        iconhand = CTkImage(Image.open("images\\hand.png"), size=(30, 30))
        icontext = CTkImage(Image.open("images\\Textbox.png"), size=(20, 20))
        iconnote = CTkImage(Image.open("images\\Note.png"), size=(30, 30))
        iconimage = CTkImage(Image.open("images\\Image.png"), size=(20, 20))
        iconscene = CTkImage(Image.open("images\\Scene.png"), size=(20, 20))
        tools = []

        cursor = CTkButton(tool, image=iconcursor, text=None, text_color="black", width=50, height=50,
                                  fg_color="transparent", corner_radius=0, hover_color= "dark grey",
                                  command=self.is_select)
        tools.append(cursor)
           
        hand  = CTkButton(tool, image=iconhand, text=None, text_color="black", width=50, height=50,
                                   fg_color="transparent", corner_radius=0, hover_color= "dark grey",
                                   command=self.is_drag)
        tools.append(hand)  
  
        Text = CTkButton(tool, image=icontext, text=None, text_color="black", width=50, height=50,
                             fg_color="transparent", corner_radius=0, hover_color= "dark grey",
                             command=self.add_textbox)
        tools.append(Text) 
   
        note = CTkButton(tool, image=iconnote, text=None,  text_color="black", width=50, height=50,
                                   fg_color="transparent", corner_radius=0, hover_color= "dark grey",
                                   command=self.show_options)
        tools.append(note)

        image = CTkButton(tool, image=iconimage, text=None, text_color="black", width=50, height=50,
                                  fg_color="transparent", corner_radius=0, hover_color= "dark grey",
                                   command=self.add_image)
        tools.append(image)

        scene = CTkButton(tool, image=iconscene, text=None, text_color="black", width=50, height=50,
                                  fg_color="transparent", corner_radius=0, hover_color= "dark grey",
                                  command=self.add_scene)
        tools.append(scene)

        for tool in tools:
            tool.pack()

        self.note_option = CTkFrame(self.layer, width=50, height=100, corner_radius=50, border_width=None, bg_color="transparent",
                                fg_color="light grey")
        
        iconstandard = CTkImage(Image.open("images\\yellow.png"), size=(30, 30))
        iconcolorwheel = CTkImage(Image.open("images\\colorwheel.png"), size=(30, 30))

        standard = CTkButton(self.note_option, image=iconstandard, text=None, text_color="black", width=50, height=50,
                                  fg_color="transparent", corner_radius=0, hover_color= "dark grey", command=self.add_note)
        standard.pack()

        choose_color = CTkButton(self.note_option, image=iconcolorwheel, text=None, text_color="black", width=50, height=50,
                                  fg_color="transparent", corner_radius=0, hover_color= "dark grey", command=self.choose_color)
        choose_color.pack()

    def show_options(self):
        self.note_option.place(x=80, rely=0.55, anchor="center")
        self.note_option.lift()

    def is_drag(self):
        self.layer.is_dragging = True

    def choose_color(self):
        color = colorchooser.askcolor(title="Select a Color")

        if color:
            rgb_color: tuple[int, int, int] = color[0]

            hex_color = "#{:02x}{:02x}{:02x}".format(*map(int, rgb_color))

            self.add_note(hex_color)

    def is_select(self):
        self.layer.is_dragging = False

    def add_note(self, color = "#ffd60a"):      
        self.layer.add_element(Note(self.layer, color=color))
        self.lift()

    def add_textbox(self):
        self.layer.add_element(Textbox(self.layer))
        self.lift()

    def add_scene(self):
        self.layer.add_element(Scene(self.layer))
        self.lift()

    def add_image(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".ects",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPG files", "*.jpg"),
            ],
        )

        if file_path:
            self.layer.add_element(ImageBox(self.layer, file_path))


class Note(CTkTextbox, Selectable):
    def __init__(self, master, width=200, height=200, color="#ffd60a", **kwargs):
        self.color = color
        CTkTextbox.__init__(self, master, width, height, fg_color=self.color, text_color="black", **kwargs)
        Selectable.__init__(self, self, master)
    
    def get_content(self):
        return self.get("1.0", "end")

    def set_content(self, content, color=None):
        if color:
            self.configure(fg_color=color)
            self.color = color 
        
        self.delete("1.0", "end")
        self.insert("1.0", content)

    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "x": self.winfo_x() * 0.8,
            "y": self.winfo_y() * 0.8,
            "color": self._fg_color,
            "content": self.get_content() 
        }

class Textbox(CTkFrame, Selectable):
    def __init__(self, master, width = 262, height = 75, box_width = 200, box_height = 50, font_size = 12, **kwargs):
        initial_width = kwargs.pop("width", width)
        initial_height = kwargs.pop("height", height)
        self.font_size = kwargs.pop("font_size", 12)

        CTkFrame.__init__(self, master, width=initial_width, height=initial_height, **kwargs)
        Selectable.__init__(self, self, master)

        self.configure(width = initial_width, height = initial_height)

        self.master = master
        self.place(x=50, y=50)

        self.textbox = CTkTextbox(self, wrap="word", width=box_width, height=box_height, font=("Arial", self.font_size))
        self.textbox.pack(fill=BOTH, expand=True, padx=5, pady=5)

        self.textbox.bind("<Delete>", self.delete_if_selected)

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

        self.start_x = 0
        self.start_y = 0
        self.start_width = initial_width
        self.start_height = initial_height
        self.start_font_size = self.font_size 

    def delete_if_selected(self, event):
        if Selectable.selected_object == self:
            self.deselect()
            self.destroy()

        self.master.file_parent.save_file_state()

    def start_resizing(self, event):
        self.start_x = event.x_root
        self.start_y = event.y_root
        self.start_width = self.winfo_width()
        self.start_height = self.winfo_height()

    def resize_frame(self, event):
        dx = event.x_root - self.start_x
        dy = event.y_root - self.start_y

        new_width = max(self.start_width + dx, 50)
        new_height = max(self.start_height + dy, 50)

        self.configure(width=new_width, height=new_height)
        self.textbox.configure(width=new_width, height=new_height)

        self.font_size = max(new_height / self.start_height * self.start_font_size, 12)
        self.textbox.configure(font=("Arial", self.font_size))

    def resize_frame_width_right(self, event):
        dx = event.x_root - self.start_x
        new_width = max(self.start_width + dx, 50) 

        self.configure(width=new_width)
        self.textbox.configure(width=new_width)
    
    def resize_frame_width_left(self, event):
        dx = event.x_root - self.start_x
        new_width = max(self.start_width - dx, 50)
    
        self.configure(width=new_width)
        print(event.x_root - self.master.winfo_rootx())
        self.textbox.configure(width=new_width)
        self.place(x=event.x_root - self.master.winfo_rootx(), y=self.winfo_y())

    def resize_frame_height_bottom(self, event):
        dy = event.y_root - self.start_y
        new_height = max(self.start_height + dy, 50)

        self.configure(height=new_height)
        self.textbox.configure(height=new_height)
    
    def resize_frame_height_top(self, event):
        dy = event.y_root - self.start_y
        new_height = max(self.start_height - dy, 50)

        self.configure(height=new_height)
        self.textbox.configure(height=new_height)
        self.place(y=event.y_root - self.master.winfo_rooty(), x=self.winfo_x())

    def get_content(self):
        return self.textbox.get("1.0", "end")

    def set_content(self, content):
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", content)

    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "x": self.widget.winfo_x() * 0.8,
            "y": self.widget.winfo_y() * 0.8,
            "width": self.widget.winfo_width(),
            "height": self.widget.winfo_height(),
            "box_width": self.textbox.winfo_width() * 0.8,
            "box_height": self.textbox.winfo_height() * 0.8,
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

        save_button = CTkButton(self.settings_frame, text="Save", font=("Arial", 16), fg_color="black", 
                                hover_color="gray",command=self.save_settings)
        save_button.pack()

        help_button = CTkButton(self.settings_frame, text="Help", font=("Arial", 16), fg_color="black", 
                                hover="gray", command=self.open_help)
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
        help_label = CTkLabel(help_window, text="To delete press the detele button \nTo delete image double-right-click  \n To Save press ctrl + S \n")
        help_label.pack()


class ImageBox(CTkFrame, Selectable):
    def __init__(self, master, image_path, width = 262, height = 75, box_width = 200, box_height = 50, image: Image = None, **kwargs):
        self.path = image_path
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

        initial_width = kwargs.pop("width", width)
        initial_height = kwargs.pop("height", height)

        CTkFrame.__init__(self, master, width=initial_width, height=initial_height, fg_color="transparent", **kwargs)
        Selectable.__init__(self, self, master)

        self.configure(width = initial_width, height = initial_height)

        self.place(x=50, y=50)

        self.label = CTkLabel(self, width=box_width, height=box_height, image=self.img, text="")
        self.label.pack(fill=BOTH, expand=True, padx=5, pady=5)

        self.resizer_corner_se = CTkFrame(self, width=10, height=10, fg_color="dark grey", cursor="bottom_right_corner")
        self.resizer_corner_se.place(relx=1.0, rely=1.0, anchor="se")

        self.resizer_right = CTkFrame(self, width=5, height=initial_height, fg_color="grey", cursor="sb_h_double_arrow")

        self.resizer_bottom = CTkFrame(self, height=5, width=initial_height, fg_color="grey", cursor="sb_v_double_arrow")

        self.resizer_corner_se.bind("<B1-Motion>", self.resize_frame_se)
        self.resizer_corner_se.bind("<Button-1>", self.start_resizing)

        self.resizer_right.bind("<B1-Motion>", self.resize_frame_width_right)
        self.resizer_right.bind("<Button-1>", self.start_resizing)

        self.resizer_bottom.bind("<B1-Motion>", self.resize_frame_height_bottom)
        self.resizer_bottom.bind( self.start_resizing)

        self.start_x = 0
        self.start_y = 0
        self.start_width = initial_width
        self.start_height = initial_height

        self.label.bind("<Double-Button-3>", self.delete_if_selected)

    def delete_if_selected(self, event):
        if Selectable.selected_object == self:
            self.deselect()
            self.destroy()

        self.master.file_parent.save_file_state()

    def show_resizers(self):
        self.resizer_right.place(relx=1.0, rely=0.25, anchor="ne", relheight=0.5)
        self.resizer_bottom.place(relx=0.25, rely=1.0, anchor="sw", relwidth=0.5)

    def hide_resizers(self):
        self.resizer_right.place_forget()
        self.resizer_bottom.place_forget()

    def fix_ratio(self, in_width, in_height, ratio, increasing: bool):
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
        self.start_x = event.x_root
        self.start_y = event.y_root
        self.start_width = self.winfo_width()
        self.start_height = self.winfo_height()
    

    def resize_frame_se(self, event):
        dx = event.x_root - self.start_x
        dy = event.y_root - self.start_y

        new_width = max(self.start_width + dx, 50)
        new_height = max(self.start_height + dy, 50)

        fixed_dims = self.fix_ratio(new_width, new_height, self.img_ratio, True)

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

    def resize_frame_width_right(self, event):
        dx = event.x_root - self.start_x
        new_width = max(self.start_width + dx, 50) 
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
        dy = event.y_root - self.start_y
        new_height = max(self.start_height + dy, 50)

        fixed_dims = self.fix_ratio(self.start_width, new_height, self.img_ratio, new_height>self.start_height)

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

    def get_content(self):
        pass

    def set_content(self, content):
        pass

    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "x": self.widget.winfo_x() * 0.8,
            "y": self.widget.winfo_y() * 0.8,
            "width": self.widget.winfo_width(),
            "height": self.widget.winfo_height(),
            "box_width": self.label.winfo_width() * 0.8,
            "image_path": self.path,
        }


class Scene(CTkFrame, Selectable):
    def __init__(self, master, name = "Scene", width = 250, height = 200, corner_radius = None, border_width = None, bg_color = "transparent", fg_color = "#252525", border_color = None, background_corner_colors = None, overwrite_preferred_drawing_method = None, **kwargs):
        CTkFrame.__init__(self, master, width, height, corner_radius, border_width, bg_color, fg_color, border_color,       
                          background_corner_colors, overwrite_preferred_drawing_method, **kwargs)
        Selectable.__init__(self, self, master)

        self.name = name

        self.title = CTkTextbox(self, font = ("Arial", 16), height= 30, text_color="white", fg_color="transparent", 
                                activate_scrollbars= False)
        self.title.insert("1.0", name)
        self.title.pack(side=TOP, fill = X, padx=5)

        self.textbox = CTkTextbox(self, wrap="word", font=("Arial", font_size), height= 120, corner_radius=0)
        self.textbox.pack(side = TOP, fill = BOTH)

        self.textbox.bind("<Delete>", self.delete_if_selected)

    def get_content(self):
        return self.textbox.get("1.0", "end")

    def set_content(self, content, name=None):
        if name:
            self.title.delete("1.0", "end")
            self.title.insert("1.0", name)
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", content)

    def delete_if_selected(self, event):
        if Selectable.selected_object == self:
            self.deselect()
            self.destroy()

        self.master.file_parent.save_file_state()

    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "name": self.title.get("1.0", "end"),
            "x": self.winfo_x() * 0.8,
            "y": self.winfo_y() * 0.8,
            "content": self.get_content(),
        }