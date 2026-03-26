import tkinter as tk
from tkinter import filedialog
import sys

def main():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    folder_path = filedialog.askdirectory(title="Chọn thư mục chứa Dataset NuScenes (VD: v1.0-mini)")
    print(folder_path)
    root.destroy()

if __name__ == '__main__':
    main()
