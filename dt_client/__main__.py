from ui.start import Start
from tkinter import Tk


def main():
    my_window = Tk()
    my_window.resizable(width=800, height=800)
    canvas_tuple = (800, 800)
    start = Start(my_window, canvas_tuple)
    start.enter_game()
    my_window.mainloop()


main()
