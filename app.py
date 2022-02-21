import tkinter as tk
import tkinter.font as fnt
import time
import main as HATD

class app():
    def __init__(self):
        #ventana principal
        print ("main menu opened")
        self.HATD = HATD.HATD()
        self.main = tk.Tk()
        self.main.title("HATD")
        self.main.geometry("800x480+0+0")
        #self.main.attributes("-zoomed",True)
        #botones menu
        self.DTC_button = tk.Button(self.main, text="Dtc Memories")
        self.DTC_button.configure(command=self.run_dtc_mem, bg='pale green', height = '12', width = '47', font = fnt.Font(size = 10))
        self.measval_button = tk.Button(self.main, text="Measured Values")
        self.measval_button.configure(command=self.run_meas_val, bg='pale green', height = '12', width = '47', font = fnt.Font(size = 10))
        self.clearDTC_button = tk.Button(self.main, text="Clear Dtc's")
        self.clearDTC_button.configure(command=self.second_win, bg = 'pale green', height = '12', width = '47', font = fnt.Font(size = 10))
        self.close_button = tk.Button(self.main, text="Close", command=self.main.destroy, bg = 'tomato', height = '12', width = '47', font = fnt.Font(size = 10))
        self.DTC_button.grid(column=0, row=0, sticky='nesw')
        self.measval_button.grid(column=1, row=0, sticky='nesw') #sticky='nesw'
        self.clearDTC_button.grid(column=0, row=1, sticky='nesw')
        self.close_button.grid(column=1, row=1, sticky='nesw')
        
        #self.main.bind("<Escape>", self.main.destroy())
        
    def second_win(self):
        self.window = tk.Toplevel(self.main)
        self.window.title = ("Clear DTCs")
        self.window.geometry("300x125+150+150")
        self.advise_text = tk.Label(self.window, text = "Are you sure to reset DTC memories?")
        self.advise_text.pack()
        self.yes_button = tk.Button(self.window, text="Yes")
        self.yes_button.configure(command=self.run_clear_dtc, bg='#80ff42')
        self.no_button = tk.Button(self.window, text="No", command=self.window.destroy, bg = '#fd4444')
        self.yes_button.pack()#grid(column=1,row=0, sticky='nesw')
        self.no_button.pack()#grid(column=1,row=1, sticky='nesw')
    
        result = True
        return result
    
    def run_dtc_mem(self):
        self.HATD.__init__('dtc_mem')
        self.HATD.run()
        self.infowindow = tk.messagebox.showinfo(title=None, message="DTC memories test finished.")
    def run_meas_val(self):
        self.HATD.__init__('meas_val')
        self.HATD.run()
        self.infowindow = tk.messagebox.showinfo(title=None, message="Measurement values test finished.")
    def run_clear_dtc(self):
        self.HATD.__init__('clear_dtc')
        self.HATD.run()
        self.window.destroy()
        self.infowindow = tk.messagebox.showinfo(title=None, message="DTC memories reset.")
        
    def run(self):
        print ("inicia la app")
        self.main.mainloop()
             
if __name__ == '__main__':
        app().run()
        
