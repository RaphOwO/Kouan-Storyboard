from elements import *
from functions import *
import uuid

class MainView(CTkFrame):
    def __init__(self, master, app_state=None, width=200, height=200, **kwargs):
        super().__init__(master, width, height, **kwargs)

        self.app_state = app_state

        self.container = CTkFrame(self)
        self.container.pack(side= TOP, fill= BOTH, expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.controller = PageController(self.container, master, app_state=self.app_state)

        self.controller.show_page("menu")

class Page(CTkFrame):
    def __init__(self, master, controller, width=600, height=500, **kwargs):
        super().__init__(master,  width=width, height=height, **kwargs)
        self.controller = controller

    def show(self):
        self.lift()


class Menu(Page):
    def __init__(self, master, controller, width=600, height=500, **kwargs):
        super().__init__(master, controller, width=width, height=height, **kwargs)

        tab = Tab(self, controller, file_parent=None)  
        tab.pack(side=TOP, fill=X)

        self.container = CTkScrollableFrame(self, fg_color="transparent")
        self.container.pack(side=TOP, fill=BOTH, expand=True)

        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        add_file_button = CTkButton(self.container, fg_color="black", text="Add New File", font=("Arial", 16), 
                                    command=lambda: self.controller.add_file())
        add_file_button.grid(row=0, column=0, sticky="news")

        self.file_buttons = {}
        self.file_frames = {}

    def update_file_buttons(self):
        for frame in self.file_frames.values():
            frame.destroy()
        self.file_frames.clear()

        for index, file_name in enumerate(self.controller.get_file_names(), start=1):
            frame = CTkFrame(self.container, fg_color="light grey")
            
            truncated_name = truncate_name(file_name, 30)
            file_button = CTkButton(frame, text=truncated_name, text_color=get_color(), fg_color="transparent", font=("Arial", 16), 
                                    anchor="w", hover_color="dark grey", command=lambda name=file_name: self.controller.show_page(name))
            file_button.pack(side=LEFT, fill=X, expand=True)

            delete = CTkImage(Image.open("images\\delete.png"), size=(20, 20))
            delete_button = CTkButton(frame, width=30, image=delete, text=None, text_color=get_color(), hover_color="dark grey", fg_color="transparent", font=("Arial", 16),
                                      command=lambda name=file_name: self.delete_file(name))
            delete_button.pack(side=RIGHT)

            frame.grid(row=index, column=0, sticky="news")
            self.file_frames[file_name] = frame 

    def delete_file(self, file_name):
        if file_name in self.controller.pages:
            self.controller.pages[file_name].delete_file() 

        if file_name in self.file_frames:
            self.file_frames[file_name].destroy() 
            del self.file_frames[file_name]


    def update_file_button_name(self, old_name, new_name):
        if old_name in self.file_buttons:
            button = self.file_buttons.pop(old_name)
            button.configure(text=new_name)
            self.file_buttons[new_name] = button


class File(Page):
    def __init__(self, master, controller, file_name="Untitled-1", file_id = None, **kwargs):
        super().__init__(master, controller, **kwargs)

        self.file_id = file_id or str(uuid.uuid4())
        self.file_name = file_name
        self.layers = []  
        self.current_layer_index = 0 

        self.tab = Tab(self, controller, file_parent=self) 
        self.tab.pack(side=TOP, fill=X)

        self.layer_container = CTkFrame(self)
        self.layer_container.pack(side=TOP, fill=BOTH, expand=True)

        self.bind('<Control-S>', command= self.save_file_state)

        if file_id == None:
            self.add_layer(default=True)

    def add_layer(self, default=False):
        layer_name = f"Act {len(self.layers) + 1}"
        new_layer = Layer(self.layer_container, layer_name=layer_name, file_parent=self)
        self.layers.append(new_layer)

        if not default:
            new_layer.pack_forget()

        if not default:
            self.switch_to_layer(len(self.layers) - 1)

        self.update_layer_dropdown()
        self.update_layer_view()
        self.save_file_state()

    def save_file_state(self):
        file_data = {
            "file_id": self.file_id,
            "file_name": self.file_name,
            "layers": [
            {
                "name": layer.layer_name,
                "elements": [element.to_dict() for element in layer.winfo_children() if isinstance(element, Selectable)]
            }
            for layer in self.layers
        ]
        }

        existing_file = next((file for file in self.controller.app_state["files"] if file["file_id"] == self.file_id), None)
        if existing_file:
            existing_file.update(file_data)
        else:
            self.controller.app_state["files"].append(file_data)

    def delete_layer(self):
        if len(self.layers) > 1:
            layer_to_delete = self.layers[self.current_layer_index]
            layer_to_delete.pack_forget() 
            self.layers.remove(layer_to_delete)


            if self.current_layer_index >= len(self.layers):
                self.current_layer_index = len(self.layers) - 1

            self.update_layer_dropdown()
            self.update_layer_view()
            
            self.save_file_state()

    def update_layer_dropdown(self):
        layer_names = [layer.layer_name for layer in self.layers]
        self.tab.layer_dropdown.configure(values=layer_names)  
        self.tab.layer_dropdown_var.set(self.layers[self.current_layer_index].layer_name)

    def on_layer_select(self, layer_name):
        for index, layer in enumerate(self.layers):
            if layer.layer_name == layer_name:
                self.switch_to_layer(index)
                break

    def switch_to_layer(self, index):
        if 0 <= index < len(self.layers):
            self.layers[self.current_layer_index].pack_forget()
            self.current_layer_index = index
            self.layers[self.current_layer_index].pack(fill=BOTH, expand=True)

        self.tab.layer_dropdown_var.set(self.layers[self.current_layer_index].layer_name)

    def update_layer_view(self):
        for i, layer in enumerate(self.layers):
            if i == self.current_layer_index:
                layer.pack(fill=BOTH, expand=True)
            else:
                layer.pack_forget()

    def rename_layer(self):
        current_layer = self.layers[self.current_layer_index]
        dialogue = CTkInputDialog(title="Rename Layer", text="Enter new layer name:")
        new_name = dialogue.get_input()
        if new_name:
            current_layer.layer_name = new_name
            self.update_layer_dropdown()
            self.save_file_state()

    def rename_file(self, new_name):
        old_name = self.file_name
        self.file_name = new_name
        self.tab.title_button.configure(text=new_name)

        self.controller.rename_file_in_controller(old_name, new_name)

        self.save_file_state()

    def delete_file(self):
        if self.file_name in self.controller.pages:
            del self.controller.pages[self.file_name]

        self.controller.app_state["files"] = [
            file for file in self.controller.app_state["files"] 
            if file["file_id"] != self.file_id
        ]

        menu_page = self.controller.pages["menu"]
        menu_page.update_file_buttons()

        self.destroy()

class Layer(CTkFrame):
    def __init__(self, master, layer_name="Layer", file_parent=None, **kwargs):
        super().__init__(master, **kwargs)

        self.layer_name = layer_name
        self.file_parent = file_parent  
        self.elements = []
        self.current_scene_index = 0
        self.is_dragging = False 
        self.drag_start_position = {"x": 0, "y": 0}

        self.toolbar = Toolbar(self)
        self.toolbar.place(x=35, rely=0.55, anchor="center")

        self.bind("<Button-1>", self.click)
        self.bind("<B1-Motion>", self.do_drag)
        self.bind("<ButtonRelease-1>", self.stop_drag)
    
    def add_element(self, element, x=150, y=150):
        if isinstance(element, Scene):
            self.current_scene_index += 1
            scene_name = f"Scene {self.current_scene_index}"
            element.name = scene_name
            element.title.delete("1.0", "end")
            element.title.insert("1.0", element.name)

        self.elements.append(element)
        element.place(x=x - 14, y=y)

        self.file_parent.save_file_state()
    
    def to_dict(self):
        return {
            "name": self.layer_name,
            "elements": [element.to_dict() for element in self.elements]
        }
    
    def click(self, event):
        self.toolbar.note_option.place_forget()
        self.start_drag(event)

    def start_drag(self, event):
        if self.is_dragging:
            self.drag_start_position = {"x": event.x_root, "y": event.y_root}

    def do_drag(self, event):
        if not self.is_dragging:
            return

        dx = event.x_root - self.drag_start_position["x"]
        dy = event.y_root - self.drag_start_position["y"]

        for element in self.elements:
            current_x = (element.winfo_x() + dx) * 0.80
            current_y = (element.winfo_y() + dy) * 0.80
            element.place(x=current_x, y=current_y)

        self.drag_start_position["x"] = event.x_root
        self.drag_start_position["y"] = event.y_root

    def stop_drag(self, event):
        if self.is_dragging:
            self.file_parent.save_file_state()

    
    def to_dict(self):
        return {
            "name": self.layer_name,
            "elements": [element.to_dict() for element in self.elements]
        }

class PageController:
    def __init__(self, container, parent, app_state=None):
        self.parent = parent
        self.app_state = app_state
        self.container = container
        self.pages = {}

        self.pages["menu"] = Menu(container, self)
        self.pages["menu"].grid(row=0, column=0, sticky="nsew")

        self.file_count = 0

        try:
            self.load_files()
        except:
            pass

    def show_page(self, page_name):
        if page_name in self.pages:
            self.pages[page_name].lift()
        else:
            self.pages["menu"].lift()

    def add_file(self):
        self.file_count += 1
        file_name = self.generate_unique_file_name(f"Untitled_{self.file_count}")

        new_file = File(self.container, self, file_name=file_name)
        self.pages[file_name] = new_file
        new_file.grid(row=0, column=0, sticky="nsew")

        self.pages["menu"].update_file_buttons()

        self.show_page(file_name)

    def generate_unique_file_name(self, base_name):
        existing_names = self.get_file_names()
        if base_name not in existing_names:
            return base_name
        counter = 1
        unique_name = f"{base_name}_{counter}"
        while unique_name in existing_names:
            counter += 1
            unique_name = f"{base_name}_{counter}"
        return unique_name

    def delete_file(self, file_name):
        if file_name in self.pages:
            file_page = self.pages.pop(file_name)


            menu_page = self.pages["menu"]
            menu_page.update_file_buttons()

    def get_file_names(self):
        return [page.file_name for page in self.pages.values() if isinstance(page, File)]

    
    def rename_file_in_controller(self, old_name, new_name):
        if old_name in self.pages:
            self.pages[new_name] = self.pages.pop(old_name)
            self.pages[new_name].file_name = new_name

            menu_page = self.pages["menu"]
            menu_page.update_file_button_name(old_name, new_name)
            menu_page.update_file_buttons() 

    def save_and_quit(self):
        self.parent.save_state()
        self.container.quit()

    def load_files(self):
        file_num = []
        for file_data in self.app_state.get("files", []):
            file_name = file_data.get("file_name", f"Untitled-{self.file_count + 1}")
            file_id = file_data.get("file_id", str(uuid.uuid4()))
            layers = file_data.get("layers", [])

            file_num.append((file_name, file_id, layers))

        for file in file_num:
            new_file = File(self.container, self, file_name=file[0], file_id=file[1])
            self.pages[file[0]] = new_file

            new_file.layers = []
            for layer_data in file[2]:
                layer_name = layer_data.get("name", f"Act {len(new_file.layers) + 1}")
                new_layer = Layer(new_file.layer_container, layer_name=layer_name, file_parent=new_file)
                new_file.layers.append(new_layer)

                elements = layer_data.get("elements", [])
                for element_data in elements:
                    element_class = globals().get(element_data.get("type"))
                    if element_class and issubclass(element_class, Selectable):
                        if issubclass(element_class, Note):
                            color = element_data.get("color", "#ffd60a")
                            element = element_class(new_layer, width = 200, height = 200)
                            element.set_content(element_data.get("content", ""), color=color)
                            new_layer.add_element(element, x = element_data["x"], y = element_data["y"])
                        elif issubclass(element_class, Textbox):
                            element = element_class(new_layer, width = element_data["width"], height = element_data["height"], 
                                                    box_width=element_data["box_width"], box_height=element_data["box_height"], 
                                                    font_size=element_data["font_size"])
                            element.set_content(element_data.get("content", ""))
                            new_layer.add_element(element, x = element_data["x"], y = element_data["y"])
                        elif issubclass(element_class, Scene):
                            element = element_class(new_layer)
                            new_layer.add_element(element, x = element_data["x"], y = element_data["y"])
                            element.set_content(element_data.get("content", ""), element_data["name"])
                        elif issubclass(element_class, ImageBox):
                            if os.path.exists(element_data["image_path"]):
                                element = element_class(new_layer, box_width=element_data["box_width"], image_path=element_data["image_path"])
                                element.set_content(element_data.get("content", ""))
                                new_layer.add_element(element, x = element_data["x"], y = element_data["y"])
                new_layer.toolbar.lift()
                        
            if new_file.layers:
                new_file.switch_to_layer(0)

            self.pages[file[0]] = new_file
            new_file.grid(row=0, column=0, sticky="nsew")
            self.file_count += 1

            new_file.update_layer_view()
            new_file.update_layer_dropdown()

        self.pages["menu"].update_file_buttons()

class Tab(CTkFrame):
    def __init__(self, master, controller, file_parent, height=40, width=600, fg_color = "light grey", **kwargs):
        super().__init__(master, height=height, width=width, fg_color=fg_color, **kwargs)

        self.controller = controller
        self.file_parent = file_parent
        
        iconhome = CTkImage(Image.open("images\\home.png"), size=(20, 20))
        home = CTkButton(self, image=iconhome, text=None, text_color=get_color(), width=60, height=40,
                         corner_radius=0, fg_color="transparent", hover_color="dark grey", command=self.on_home_button_click)
        home.pack(side=LEFT)

        if self.file_parent:
            truncated_name = truncate_name(self.file_parent.file_name)
            self.title_button = CTkButton(self, text=truncated_name, text_color=get_color(), font=("Arial", 16), anchor= "sw",
                                        fg_color="transparent", hover_color="dark grey",command=self.on_title_button_click)
            self.title_button.pack(side=LEFT, padx=10)

        iconsetting = CTkImage(Image.open("images\\setting.png"), size=(20, 20))
        setting = CTkButton(self, image=iconsetting, text=None, text_color=get_color(), width=60, height=40,
                         corner_radius=0, fg_color="transparent", hover_color="dark grey", command=self.open_settings)
        setting.pack(side=RIGHT)


        self.layer_dropdown_var = StringVar(value="Act 1")
        if self.file_parent:
            self.layer_dropdown = CTkOptionMenu(
                self,
                variable=self.layer_dropdown_var,
                values=[],
                fg_color="black",
                button_color="lightgray", 
                button_hover_color="gray",  
                command=self.file_parent.on_layer_select  
            )
            self.layer_dropdown.pack(side=RIGHT, padx=10)

            add_layer_button = CTkButton(self, text="+", text_color=get_color(), font=("Arial", 25), width= 30, fg_color="transparent", 
                                         hover_color="dark grey", command=self.add_layer)
            add_layer_button.pack(side=RIGHT)

            delete = CTkImage(Image.open("images\\delete.png"), size=(20, 20))
            delete_layer_button = CTkButton(self, image=delete, text=None, text_color=get_color(), font=("Arial", 16), width= 30, 
                                            fg_color="transparent", hover_color="dark grey", command=self.delete_layer)
            delete_layer_button.pack(side=RIGHT)

            rename = CTkImage(Image.open("images\\Rename.png"), size=(20, 20))
            rename_layer_button = CTkButton(self, image=rename, text=None, text_color=get_color(), font=("Arial", 16), width= 30, 
                                            fg_color="transparent", hover_color="dark grey",
                                            command=self.rename_layer)
            rename_layer_button.pack(side=RIGHT)
        else:
            self.layer_dropdown = None
            add_layer_button = None
            rename_layer_button = None

    def on_home_button_click(self):
        if not self.file_parent:
            self.controller.save_and_quit()
        else:
            self.file_parent.save_file_state()
            self.controller.show_page("menu")

    def add_layer(self):
        if self.file_parent:
            self.file_parent.add_layer()

    def delete_layer(self):
        if self.file_parent:
            self.file_parent.delete_layer()

    def rename_layer(self):
        if self.file_parent:
            self.file_parent.rename_layer()

    def open_settings(self):
        self.settings_window = SettingsWindow(self, self.master)

    def on_title_button_click(self):
        dialogue = CTkInputDialog(title="Rename File", text="Enter new file name:")
        new_name = dialogue.get_input()
        if new_name and new_name != self.file_parent.file_name:
            self.file_parent.rename_file(new_name)
            truncated_name = truncate_name(new_name)
            self.title_button.configure(text=truncated_name)
            self.controller.pages["menu"].update_file_buttons()
