from customtkinter import get_appearance_mode

def truncate_name(name, max_length=20):
    if len(name) > max_length:
        return name[:max_length - 3] + "..."
    return name

def get_color():
    current_mode = get_appearance_mode()
    if current_mode == "dark":
        return "white" 
    else:
        return "black"