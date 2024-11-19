from elements import *
from pages import *
import pickle
import os

def save_app_state(app_state, file_path="app_state.pkl"):
    with open(file_path, "wb") as f:
        pickle.dump(app_state, f)

def load_app_state(file_path="app_state.pkl"):
    try: 
        os.path.exists(file_path)
        with open(file_path, "rb") as f:
            content = pickle.load(f)
            return content
    except:
        return None 

class App(CTk):
    def __init__(self):
        super().__init__()
        self.minsize(width=600, height=550)
        self.title("Kouan: Storyboard")

        self.app_state = load_app_state()

        if not self.app_state:
            self.app_state = {
                "files": [],
            }
        
        self.view = MainView(self, app_state=self.app_state)
        self.view.pack(side=TOP, fill=BOTH, expand=True)
        
        self.bind('<Control-s>', self.save_state)

        self.auto_save_interval = 5 * 60 * 1000  # 5 minutes in milliseconds
        self.start_autosave()

    def save_state(self, event=None):
        save_app_state(self.app_state)

    def start_autosave(self):
        self.save_state()
        self.after(self.auto_save_interval, self.start_autosave)


def main():
    app = App()
    app.mainloop()

if __name__ == '__main__':
    main()