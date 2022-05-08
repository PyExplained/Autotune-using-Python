from autotune import *


class ExtraWindow:
    def __init__(self, at):
        self.at = at
        self.tk = tkinter.Tk()
        self.tk.title('Select Scale')
        self.tk.geometry('300x400')
        self.tk.resizable(0, 0)

        tkinter.Label(self.tk, text="PRESETS:", font=('helvetica', 9)).place(x=20, y=20, anchor="nw")

        scale_names = list(AudioHandler.SCALES.keys())
        self.preset_box = Combobox(self.tk, width=20, values=scale_names)
        self.preset_box.bind('<<ComboboxSelected>>', self.update_preset)
        self.preset_box.place(x=125, y=20, anchor="nw")

        tkinter.Label(self.tk, text="SELECT NOTES IN SCALE:", font=('helvetica', 9)).place(x=20, y=60)

        self.note_vars = [tkinter.BooleanVar(self.tk, self.at.scale[note.replace("o", "")])
                          for note in AudioHandler.NOTE_NAMES]
        for i, note in enumerate(AudioHandler.NOTE_NAMES):
            self.note_chk = tkinter.Checkbutton(self.tk, text=note.replace("o", ""), font=('helvetica', 11),
                                                var=self.note_vars[i])
            self.note_chk.place(x=40, y=80 + 20 * i, anchor='nw')

        self.update_btn = tkinter.Button(self.tk, text="Save Preferences", command=self.save_and_close)
        self.update_btn.place(x=150, y=360, anchor="center")

        self.tk.mainloop()

    def update_preset(self, event):
        for note_var in self.note_vars:
            note_var.set(False)

        for note in AudioHandler.SCALES[self.preset_box.get()]:
            for i, note_ in enumerate(AudioHandler.NOTE_NAMES):
                if note in note_.replace("o", "").split("/"):
                    self.note_vars[i].set(True)

    def save_and_close(self):
        for i, note_var in enumerate(self.note_vars):
            self.at.scale[list(self.at.scale.keys())[i]] = note_var.get()
        self.tk.destroy()
