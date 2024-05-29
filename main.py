# main.py
from interface import JobFinderApp

def main_fn():
    app = JobFinderApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
    
if __name__ == "__main__":
    main_fn()