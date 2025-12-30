import tkinter as tk
from src.gui.app import App

def main():
    root = tk.Tk()
    root.title("Switch CIS-style Configuration Review (Cisco + Juniper)")
    App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
