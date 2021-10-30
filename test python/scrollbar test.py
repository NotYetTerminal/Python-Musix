from tkinter import *

window = Tk()
window.geometry("680x500")

Label(window, text="Top label").pack()

frame = Frame(window)
frame.pack()

listNodes = Listbox(frame, width=20, height=20, font=("Helvetica", 12))
listNodes.pack(side="left", fill="y")

scrollbar = Scrollbar(frame, orient="vertical")
scrollbar.config(command=listNodes.yview)
scrollbar.pack(side="right", fill="y")

listNodes.config(yscrollcommand=scrollbar.set)

for x in range(100):
    listNodes.insert(END, str(x))

Label(window, text="Bottom label").pack()

window.mainloop()