from elements import *
from functions import *
import uuid

class MainView(CTkFrame):
    def __init__(self, master, app_state=None, width=200, height=200, **kwargs):
        super().__init__(master, width, height, **kwargs)

        self.app_state = app_state

        # Initialize the container to hold pages
        self.container = CTkFrame(self)
        self.container.pack(side= TOP, fill= BOTH, expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Initialize the controller to manage pages
        self.controller = PageController(self.container, app_state=self.app_state)

        # Show the initial menu page
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

        # Tab setup
        tab = Tab(self, controller, file_parent=None)  
        tab.pack(side=TOP, fill=X)

        # Container for Menu items
        self.container = CTkScrollableFrame(self, fg_color="transparent")
        self.container.pack(side=TOP, fill=BOTH, expand=True)

        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        # Button to add a new file page
        add_file_button = CTkButton(self.container, text="Add New File", font=("Arial", 16), 
                                    command=lambda: self.controller.add_file())
        add_file_button.grid(row=0, column=0, sticky="news")

        # Dictionary to hold file buttons with their names as keys
        self.file_buttons = {}
        self.file_frames = {}

    def update_file_buttons(self):
        """ Refreshes the list of frames representing each file. """
        # Remove existing file frames
        for frame in self.file_frames.values():
            frame.destroy()
        self.file_frames.clear()

        # Create new frames for each file
        for index, file_name in enumerate(self.controller.get_file_names(), start=1):
            frame = CTkFrame(self.container, fg_color="light grey")
            
            truncated_name = truncate_name(file_name, 30)
            file_button = CTkButton(frame, text=truncated_name, text_color=get_color(), fg_color="transparent", font=("Arial", 16), 
                                    anchor="w", hover_color="dark grey", command=lambda name=file_name: self.controller.show_page(name))
            file_button.pack(side=LEFT, fill=X, expand=True)

            delete_button = CTkButton(frame, width=30, text="-", text_color=get_color(), hover_color="dark grey", fg_color="transparent", font=("Arial", 16),
                                      command=lambda name=file_name: self.delete_file(name))  # Use the new delete method
            delete_button.pack(side=RIGHT)

            frame.grid(row=index, column=0, sticky="news")
            self.file_frames[file_name] = frame  # Track the frame by the file's name

    def delete_file(self, file_name):
        """ Deletes the file and its associated frame in the menu. """
        # Delete the file page from the controller
        if file_name in self.controller.pages:
            self.controller.pages[file_name].delete_file()  # Delete the file page

        # Remove the file frame from the menu
        if file_name in self.file_frames:
            self.file_frames[file_name].destroy()  # Destroy the frame
            del self.file_frames[file_name]


    def update_file_button_name(self, old_name, new_name):
        """ Updates the text of a file button when the file name changes and refreshes the menu. """
        if old_name in self.file_buttons:
            # Update the button text and key in the dictionary
            button = self.file_buttons.pop(old_name)
            button.configure(text=new_name)
            self.file_buttons[new_name] = button


class File(Page):
    def __init__(self, master, controller, file_name="Untitled-1", file_id = None, **kwargs):
        super().__init__(master, controller, **kwargs)

        self.file_id = file_id or str(uuid.uuid4())
        self.file_name = file_name
        self.layers = []  # To store layers within this file
        self.current_layer_index = 0  # Track the current visible layer

        # Tab setup for layers
        self.tab = Tab(self, controller, file_parent=self)  # Pass self as file_parent
        self.tab.pack(side=TOP, fill=X)

        # Initialize the container to hold the layers
        self.layer_container = CTkFrame(self)
        self.layer_container.pack(side=TOP, fill=BOTH, expand=True)

        self.bind('<Control-S>', command= self.save_file_state)

        # Create a default layer when initializing a file
        if file_id == None:
            self.add_layer(default=True)

    def add_layer(self, default=False):
        """ Adds a new layer to the file. """
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
        """ Save the current file state to the app state. """
        print("something")
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
        """ Deletes the current layer if there are more than one layer. """
        if len(self.layers) > 1:
            layer_to_delete = self.layers[self.current_layer_index]
            layer_to_delete.pack_forget()  # Remove the layer visually
            self.layers.remove(layer_to_delete)  # Remove from the layers list

            # Adjust the current layer index if necessary
            if self.current_layer_index >= len(self.layers):
                self.current_layer_index = len(self.layers) - 1  # Move to the last layer if the current index is out of bounds

            self.update_layer_dropdown()
            self.update_layer_view()
            
            self.save_file_state()

    def update_layer_dropdown(self):
        """ Updates the dropdown with the current list of layers. """
        layer_names = [layer.layer_name for layer in self.layers]
        self.tab.layer_dropdown.configure(values=layer_names)  # Update the dropdown in Tab
        self.tab.layer_dropdown_var.set(self.layers[self.current_layer_index].layer_name)

    def on_layer_select(self, layer_name):
        """ Switch to the layer selected in the dropdown menu. """
        for index, layer in enumerate(self.layers):
            if layer.layer_name == layer_name:
                self.switch_to_layer(index)
                break

    def switch_to_layer(self, index):
        """ Switch to a specific layer by index. """
        if 0 <= index < len(self.layers):
            # Hide the current layer
            self.layers[self.current_layer_index].pack_forget()
            # Show the new layer
            self.current_layer_index = index
            self.layers[self.current_layer_index].pack(fill=BOTH, expand=True)

        # Update the dropdown to reflect the current layer
        self.tab.layer_dropdown_var.set(self.layers[self.current_layer_index].layer_name)

    def update_layer_view(self):
        # Ensure only the current layer is visible
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
            self.save_file_state()  # Save the updated layer name

    def rename_file(self, new_name):
        """ Renames the file and updates the file name in the controller and menu page. """
        old_name = self.file_name
        self.file_name = new_name
        self.tab.title_button.configure(text=new_name)  # Update the title button text

        # Notify the controller to update file name references
        self.controller.rename_file_in_controller(old_name, new_name)

        # Update the app state
        self.save_file_state()  # Ensure state is updated after renaming

    def delete_file(self):
        """ Delete the file and remove its page from the controller and menu. """
        # Remove this file's page from the controller
        if self.file_name in self.controller.pages:
            del self.controller.pages[self.file_name]

        # Remove the file from the app state
        self.controller.app_state["files"] = [
            file for file in self.controller.app_state["files"] 
            if file["file_id"] != self.file_id
        ]

        # Call method in Menu to update the file buttons
        menu_page = self.controller.pages["menu"]
        menu_page.update_file_buttons()

        self.destroy()

class Layer(CTkFrame):
    def __init__(self, master, layer_name="Layer", file_parent=None, **kwargs):
        super().__init__(master, **kwargs)

        self.layer_name = layer_name
        self.file_parent = file_parent  
        self.elements = []  # Track elements added to this layer

        self.toolbar = Toolbar(self)
        self.toolbar.place(x=35, rely=0.55, anchor="center")
    
    def add_element(self, element, x = 150, y = 150):
        """Add an element to the layer and track it."""
        self.elements.append(element)
        element.place(x = x - 14, y = y)
        self.file_parent.save_file_state()
    
    def to_dict(self):
        """Serialize the current layer and its elements to a dictionary."""
        return {
            "name": self.layer_name,
            "elements": [element.to_dict() for element in self.elements]
        }


class PageController:
    def __init__(self, container, app_state=None):
        self.app_state = app_state
        self.container = container
        self.pages = {}

        # Create and store the menu page
        self.pages["menu"] = Menu(container, self)
        self.pages["menu"].grid(row=0, column=0, sticky="nsew")

        # Track the number of files
        self.file_count = 0

        # Load files if app_state contains any saved data
        try:
            self.load_files()
        except:
            pass

    def show_page(self, page_name):
        if page_name in self.pages:
            # Use lift() to bring the correct page to the front
            self.pages[page_name].lift()
        else:
            # If the page does not exist, fallback to the menu
            self.pages["menu"].lift()

    def add_file(self):
        """ Adds a new file and updates the menu page. """
        self.file_count += 1
        file_name = self.generate_unique_file_name(f"Untitled_{self.file_count}")

        # Create a new file page and store it
        new_file = File(self.container, self, file_name=file_name)
        self.pages[file_name] = new_file
        new_file.grid(row=0, column=0, sticky="nsew")

        # Update the Menu page to include a button for the new file
        self.pages["menu"].update_file_buttons()

        # Automatically switch to the new file
        self.show_page(file_name)

    def generate_unique_file_name(self, base_name):
        """ Generate a unique file name to avoid duplicates. """
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
        """ Deletes the specified file and updates the menu page. """
        if file_name in self.pages:
            # Remove the file page
            file_page = self.pages.pop(file_name)
            file_page.destroy()  # Destroy the file page to clean up

            # Update the Menu page
            menu_page = self.pages["menu"]
            menu_page.update_file_buttons()  # Refresh the file buttons

    def get_file_names(self):
        """ Returns a list of all file names. """
        return [page.file_name for page in self.pages.values() if isinstance(page, File)]

    
    def rename_file_in_controller(self, old_name, new_name):
        """ Updates the file name in the controller and refreshes the menu page. """
        if old_name in self.pages:
            # Update the file reference
            self.pages[new_name] = self.pages.pop(old_name)
            self.pages[new_name].file_name = new_name

            # Update the menu page's button text and refresh the file buttons
            menu_page = self.pages["menu"]
            menu_page.update_file_button_name(old_name, new_name)
            menu_page.update_file_buttons()  # Refresh the list of buttons in the menu

    def save_and_quit(self):
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
                            element = element_class(new_layer, width = 200, height = 200)
                        elif issubclass(element_class, Textbox):
                            element = element_class(new_layer, width = element_data["width"], height = element_data["height"], 
                                                    box_width=element_data["box_width"], box_height=element_data["box_height"], 
                                                    font_size=element_data["font_size"])
                        element.set_content(element_data.get("content", ""))
                        new_layer.add_element(element, x = element_data["x"], y = element_data["y"])

            if new_file.layers:
                new_file.switch_to_layer(0)

            self.pages[file[0]] = new_file
            new_file.grid(row=0, column=0, sticky="nsew")
            self.file_count += 1

            new_file.update_layer_view()
            new_file.update_layer_dropdown()

        self.pages["menu"].update_file_buttons()

class StoryBoard(Page):
    def __init__(self, master, controller, width=600, height=500, **kwargs):
        super().__init__(master, controller, width, height, **kwargs)

class Tab(CTkFrame):
    def __init__(self, master, controller, file_parent, height=40, width=600, fg_color = "light grey", **kwargs):
        super().__init__(master, height=height, width=width, fg_color=fg_color, **kwargs)

        self.controller = controller
        self.file_parent = file_parent

        home = CTkButton(self, text="<=", text_color=get_color(), font=("Arial", 16), width=60, height=40,
                         corner_radius=0, fg_color="transparent", hover_color="dark grey", command=self.on_home_button_click)
        home.pack(side=LEFT)

        if self.file_parent:
            truncated_name = truncate_name(self.file_parent.file_name)
            self.title_button = CTkButton(self, text=truncated_name, text_color=get_color(), font=("Arial", 16), anchor= "sw",
                                        fg_color="transparent", hover_color="dark grey",command=self.on_title_button_click)
            self.title_button.pack(side=LEFT, padx=10)


        setting = CTkButton(self, text="Setting", text_color=get_color(), font=("Arial", 16), width=60, height=40,
                            corner_radius=0, fg_color="transparent", hover_color="dark grey", command=self.open_settings)
        setting.pack(side=RIGHT)

        # Layer dropdown (only shown if file_parent is not None)
        self.layer_dropdown_var = StringVar(value="Act 1")
        if self.file_parent:
            # Only show the layer dropdown if in a file page
            self.layer_dropdown = CTkOptionMenu(
                self,
                variable=self.layer_dropdown_var,
                values=[],
                command=self.file_parent.on_layer_select  # Delegate to File class to handle layer selection
            )
            self.layer_dropdown.pack(side=RIGHT, padx=10)

            # Add Layer button (only shown if file_parent is not None)
            add_layer_button = CTkButton(self, text="+", text_color=get_color(), font=("Arial", 16), width= 30, fg_color="transparent", 
                                         hover_color="dark grey", command=self.add_layer)
            add_layer_button.pack(side=RIGHT)

            delete_layer_button = CTkButton(self, text="-", text_color=get_color(), font=("Arial", 16), width= 30, 
                                            fg_color="transparent", hover_color="dark grey", command=self.delete_layer)
            delete_layer_button.pack(side=RIGHT)

            # Rename Layer button (only shown if file_parent is not None)
            rename_layer_button = CTkButton(self, text="Rename Layer", text_color=get_color(), font=("Arial", 16), fg_color="transparent", hover_color="dark grey",
                                            command=self.rename_layer)
            rename_layer_button.pack(side=RIGHT)
        else:
            # When file_parent is None (Menu page), disable the renaming and layer features
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
        """ Called when the title button is clicked to prompt for a new file name. """
        dialogue = CTkInputDialog(title="Rename File", text="Enter new file name:")
        new_name = dialogue.get_input()
        if new_name and new_name != self.file_parent.file_name:
            self.file_parent.rename_file(new_name)
            truncated_name = truncate_name(new_name)
            self.title_button.configure(text=truncated_name)
            self.controller.pages["menu"].update_file_buttons()
