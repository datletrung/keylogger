import tkinter as tk
import tkinter.font as font
from tkcalendar import Calendar

class Log(object):
    def __init__(self, root):
        self.root = root
        self.render()

    def view_log(self):
        date = str(self.cal.selection_get())
        self.msg.config(state='normal')
        self.msg.delete(0, tk.END)
        self.msg.insert(0, date)
        self.msg.config(state='disabled')
        
    def view_screenshot(self):
        pass
        
    def view_camera(self):
        pass

    def clear_selected_log(self):
        pass

    def clear_all_log(self):
        pass
        
    def render(self):
        self.msg = tk.Entry(self.root, justify='center')
        self.msg.config(state='disabled')
        self.msg.grid(row=1, column=1, columnspan=2, sticky='news')
        
        self.cal = Calendar(self.root, selectmode='day')
        self.cal.grid(row=2, column=1, rowspan=5, sticky='nesw')
        
        button_2 = tk.Button(self.root, text='View Keyboard Log', width=25, command=self.view_log)
        button_3 = tk.Button(self.root, text='View Screenshot Log', width=25, command=self.view_screenshot)
        button_4 = tk.Button(self.root, text='View Camera Log', width=25, command=self.view_camera)
        button_5 = tk.Button(self.root, text='Clear Log Selected Day', width=25, command=self.clear_selected_log)
        button_6 = tk.Button(self.root, text='Clear All Log', width=25, command=self.clear_all_log)
        button_2.grid(row=2, column=2, sticky='ns')
        button_3.grid(row=3, column=2, sticky='ns')
        button_4.grid(row=4, column=2, sticky='ns')
        button_5.grid(row=5, column=2, sticky='ns')
        button_6.grid(row=6, column=2, sticky='ns')


root = tk.Tk()
root.geometry("435x207")

Log(root)

root.mainloop()

