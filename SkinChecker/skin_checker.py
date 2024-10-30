from genericpath import isfile
import os
import tkinter
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk

from more_itertools import unzip
import scd_parser
from skin_checkerui import SkinCheckerUI
import sv_ttk

with open("osu_files.scd", "r") as f:
    osu_files = scd_parser.parse(f.read())

print(osu_files)


class SkinChecker(SkinCheckerUI):
    def __init__(self, master=None, on_first_object_cb=None):
        super().__init__(master, on_first_object_cb=None)
        self.skins = {}
        self.skin = ""
        self.settings = {}
        self.files = []
        for cat in osu_files.keys():
            for sub in osu_files[cat].keys():
                for file in osu_files[cat][sub]:
                    self.files.append(file)
        
    def get_setting(self,name):
        return self.settings.get(name,False)

    def set_osu_folder(self):
        self.settings["osu_directory"] = os.path.realpath(filedialog.askdirectory(title="osu! Main Directory"))
        self.builder.get_object("warning_osu_folder").configure(text="")
        self.update_skin_list()

    def update_skin_list(self):
        self.skins = {}
        if os.path.isdir(self.get_setting("osu_directory")) and "Skins" in os.listdir(self.get_setting("osu_directory")):
            skins_folder = os.path.join(self.get_setting("osu_directory"),"Skins/")
            for skin in sorted(os.listdir(skins_folder)):
                path = os.path.join(skins_folder,skin)
                if os.path.isdir(path) and "skin.ini" in os.listdir(path):
                    self.skins[skin.replace(",",".")] = path
                    print(skin)
        else:
            messagebox.showerror("Can't update skins","osu! directory is invalid.")
            self.builder.get_object("warning_osu_folder").configure(text="osu! directory is invalid! Please set the correct directory.")
        self.builder.get_object("skins").set_menu("Select a skin",*list(self.skins.keys()))


    def change_skin(self, option):
        self.skin = self.skins[option]

    def true_false(self,boolean,true,false):
        return true if boolean else false

    def gen_values(self,missing,animated,has_sd,has_hd):
        return (self.true_false(missing,"Missing","No"), self.true_false(animated,"Yes","No"), self.true_false(has_sd,"Yes","No"), self.true_false(has_hd,"Yes","No"))

    def gen_tree(self,file_list,display_list):
        columns = ["missing","animated","sd","hd"]
        for cat in osu_files.keys():
            tree: ttk.Treeview = self.builder.get_object(cat + "_view")
            for i in tree.get_children():
                tree.delete(i)
            tree["columns"] = " ".join(columns)
            for i in columns:
                tree.column(i,width=50)
                tree.heading(i,text=i.title())
            for sub in osu_files[cat].keys():
                sub_category = tree.insert("","end",text=sub.title(),open=True)
                for file in osu_files[cat][sub]:
                    if file in display_list:
                        tree.insert(sub_category,"end",text=file,values=file_list[file])

    def start_check(self):
        file_list = {}
        display = []
        for filename in self.files:
            missing = True
            animated = False
            has_sd = False
            has_hd = False
            warning = False
            full_fn = os.path.join(self.skin,filename)
            
            if os.path.isfile(full_fn):
                missing = False
                has_sd = True
            elif os.path.isfile(full_fn.replace(".png","-0.png")):
                missing = False
                animated = True
                has_sd = True
            if os.path.isfile(full_fn.replace(".png","@2x.png")):
                missing = False
                has_hd = True
            elif os.path.isfile(full_fn.replace("@2x","-0@2x")):
                missing = False
                animated = True
                has_hd = True
            
            if self.get_setting("checks_hd") and not has_hd and (has_sd or not self.get_setting("ignore_if_sd")):
                warning = True
            if self.get_setting("checks_sd") and not has_sd and (has_hd or not self.get_setting("ignore_if_hd")):
                warning = True
            if warning and (not self.get_setting("checks_missing") and missing):
                warning = False
            if self.get_setting("checks_missing") and missing:
                warning = True
            
            if warning or not self.get_setting("only_missing"):
                display.append(filename)
            
            file_list[filename] = self.gen_values(missing,animated,has_sd,has_hd)
        
        self.gen_tree(file_list,display)

    def update_setting(self, widget_id):
        self.settings[widget_id] = "selected" in self.builder.get_object(widget_id).state()
        print(widget_id)

app = SkinChecker()

sv_ttk.set_theme("dark")
app.run()