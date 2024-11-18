from elements import *
from pages import *
import pickle
import os
import time

def save_app_state(app_state, file_path="app_state.pkl"):
    print("Saved")
    with open(file_path, "wb") as f:
        pickle.dump(app_state, f)

def load_app_state(file_path="app_state.pkl"):
    try: 
        os.path.exists(file_path)
        with open(file_path, "rb") as f:
            content = pickle.load(f)
            print(content)
            return content
    except:
        return None  # If the file doesn't exist, return None (start with a fresh state)

class App(CTk):
    def __init__(self):
        super().__init__()
        self.minsize(width=600, height=550)
        self.title("Kouan: Storyboard")

        # Try to load the saved state when the app starts
        self.app_state = load_app_state()

        # If no saved state, initialize a new state
        if not self.app_state:
            self.app_state = {
                "files": [],
            }
        
        self.view = MainView(self, app_state=self.app_state)
        self.view.pack(side=TOP, fill=BOTH, expand=True)
        
        self.bind('<Control-s>', self.save_state)

    def save_state(self, event=None):
        """ Saves the current app state to a file. """
        save_app_state(self.app_state)
        print("State saved!")


def main():
    app = App()
    app.mainloop()

if __name__ == '__main__':
    main()