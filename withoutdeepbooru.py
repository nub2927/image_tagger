import sqlite3
import time
from sqlite3 import Error
import cv2
import numpy as np
from PIL import Image, ImageGrab, ImageTk
import cv2
from tkinter import Frame, Label, Tk, Button, filedialog, Entry, OptionMenu, END, StringVar, Checkbutton
import tkinter as tk
from glob import glob
import os
import toml
import pickle

right_frame = None
search_frame = None
right_frame_col = 0
window = None
typing = False


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn


def set_pic(label, im):
    try:
        imgrgb = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
        out_image = Image.fromarray(imgrgb)
        tk_image_ = ImageTk.PhotoImage(out_image)
        label.configure(image=tk_image_)
        label.image = tk_image_
    except Exception as ex:
        print(ex)
    return


class TagSearchFrame:
    def __init__(self, master, limit=10, call_back_func=None, col=0):
        global window
        self.call_back_func = call_back_func
        self.text_frame = Frame(master=master)
        self.text_frame.grid(column=col, row=0, padx=5, pady=5)
        self.sv = StringVar()

        self.lbl = Label(master=self.text_frame, text='Tag Search')
        self.lbl.grid(column=0, row=0, padx=5, pady=5)

        self.text = Entry(master=self.text_frame, textvariable=self.sv)
        self.text.grid(column=0, row=1, padx=5, pady=5)
        self.text.configure(state='disabled')
        self.text.bind('<ButtonPress-1>', self.enable_text)
        window.bind('<Return>', self.disable_text)

        self.output_frame = Frame(master=self.text_frame)
        self.output_frame.grid(column=0, row=2, padx=5, pady=5)
        self.output_labels = Label(master=self.output_frame)
        self.output_labels.grid(column=0, row=0, padx=5, pady=5)
        self.sv.trace_add("write", self.change_callback)
        self.conn = create_connection('booru_tags.db')
        self.c = self.conn.cursor()
        self.limit = limit
        self.tag_btn_list = []

    def disable_text(self, event):
        global typing
        typing = False
        self.text.configure(state='disabled')

    def enable_text(self, event):
        global typing
        typing = True
        self.text.configure(state='normal')

    def change_callback(self, a, b, c):
        tag_like = self.text.get()
        if tag_like == '':
            return
        sql = f"SELECT tag FROM tag_table WHERE tag LIKE '{tag_like}%' ORDER BY tag_count DESC LIMIT {int(self.limit)};"
        self.c.execute(sql)
        total_rows = (self.c.fetchall())
        # txt_input = ''
        # for t, tag in enumerate(total_rows):
        #    txt_input += ' '
        #    txt_input += tag[0]
        #    txt_input += '\n'
        # self.output_labels.configure(text=txt_input)
        self.clearbtn()
        for t, tag in enumerate(total_rows):
            self.tag_btn_list += [TagButton(self.output_frame, tag[0], t, call_back_func=self.call_back_func)]

    def clearbtn(self):
        while True:
            if len(self.tag_btn_list) == 0:
                return
            tagbtn = self.tag_btn_list.pop()
            tagbtn.destroy()
            del tagbtn


class TagsFrame:
    def __init__(self, master, callback_func=None, indicator=False, description='BLANK', col=0):
        self.indicator = indicator
        self.tag_btn_list = []
        self.tag_dict = {}
        self.top_row_index = 1
        self.master = master
        self.frame = Frame(master=master)
        self.frame.grid(column=col, row=0, sticky='N')
        self.description_lbl = Label(master=self.frame, text=description)
        self.description_lbl.grid(column=0, row=0)
        self.callback_func = callback_func
        self.column_index = 0
        p = 0

    def clearbtn(self):
        while True:
            if len(self.tag_btn_list) == 0:
                break
            tagbtn = self.tag_btn_list.pop()
            tagbtn.destroy()
            del tagbtn
        self.top_row_index = 1
        self.column_index = 0
        self.tag_dict = {}

    def add_btn(self, event):
        data = toml.load('config.toml')
        button_row_limit = data['button_row_limit']
        tag_txt = event[0]
        event = (tag_txt, True)
        if not tag_txt in self.tag_dict:
            new_btn = TagButton(self.frame, tag_txt, self.top_row_index, indicator=self.indicator,
                                call_back_func=self.callback_func, column_index=self.column_index)
            self.tag_dict.update({tag_txt: new_btn})
            self.tag_btn_list += [new_btn]
            self.top_row_index += 1
            if self.top_row_index >= button_row_limit:
                self.top_row_index = 1
                self.column_index += 1

        else:
            self.tag_dict[tag_txt].set(True)
        self.callback_func(event)

    def set_callback(self, callback_func):
        self.callback_func = callback_func


def call_back_tester(event):
    tag_text = event[0]
    print('callback testy', event)


class TagButton:
    def __init__(self, master, tag_txt, row, call_back_func=None, indicator=False,column_index=0):
        data = toml.load('config.toml')
        self.frame = Frame(master=master)
        self.frame.grid(column=column_index, row=row)
        self.btn = Button(master=self.frame, command=self.button_press, text=tag_txt, width=data['button_width'])
        self.btn.grid(column=0, row=0)
        self.state = True
        self.indicator = indicator
        if self.indicator:
            self.lbl = Label(master=self.frame)
            self.lbl.grid(column=1, row=0)
            self.T = np.ones((10, 10, 3), dtype=np.uint8) * np.array([255, 0, 0], dtype=np.uint8)
            self.F = np.ones((10, 10, 3), dtype=np.uint8) * np.array([0, 0, 255], dtype=np.uint8)
            set_pic(self.lbl, self.T)
        self.call_back_func = call_back_func
        self.tag_txt = tag_txt

    def button_press(self):
        global search_frame, typing
        search_frame.text.configure(state='disabled')
        typing = False
        self.state = not self.state
        if self.indicator:
            if self.state:
                set_pic(self.lbl, self.T)
            else:
                set_pic(self.lbl, self.F)
        self.call_back_func((self.tag_txt, self.state))

        #########################################################################################################

    def destroy(self):
        self.btn.destroy()
        if self.indicator:
            self.lbl.destroy()
        self.frame.destroy()

    def set(self, boolean):
        self.state = boolean
        if self.indicator:
            if self.state:
                set_pic(self.lbl, self.T)
            else:
                set_pic(self.lbl, self.F)


def resize(img, new_size):
    h, w, c = img.shape
    mx = max(h, w)
    scale = new_size / mx
    new_w = int(scale * w)
    new_h = int(scale * h)
    img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    canvas = np.zeros((new_size, new_size, 3), dtype=np.uint8)
    canvas[0:new_h, 0:new_w] = img
    if new_h != new_size:
        shift_y = int((new_size - new_h) / 2)
        canvas = np.roll(canvas, shift_y, axis=0)
    if new_w != new_size:
        shift_x = int((new_size - new_w) / 2)
        canvas = np.roll(canvas, shift_x, axis=1)
    return canvas


# checks the extention for what it is
def get_ext(file_path):
    char_list = list(file_path)[::-1]
    for i, char_ in enumerate(char_list):
        if char_ == '.':
            ext = file_path[(-1 * i - 1):len(file_path)]
            return ext


class Pic:
    def __init__(self, pic_file_path, default_tags):
        self.tag_dict = {}
        for tag_text in default_tags:
            self.tag_dict.update({tag_text: True})

        self.pic_file_path = pic_file_path
        self.ext = get_ext(self.pic_file_path)
        self.txt_file = self.pic_file_path.replace(self.ext, '.txt')
        if os.path.exists(self.txt_file):
            rd = open(self.txt_file, 'r')
            txt = rd.read()
            rd.close()
            spl = txt.split(' ')
            for tag_text in spl:
                self.tag_dict.update({tag_text: True})

    def tag_callback(self, event):
        self.tag_dict.update({event[0]: event[1]})

    def get_tags(self):
        tmp_tag_list = []
        for tag_text in self.tag_dict:
            tag_enabled = self.tag_dict[tag_text]
            if tag_enabled:
                tmp_tag_list += [tag_text]
        return tmp_tag_list

    def get_path(self):
        return self.pic_file_path

    def save_tags(self):
        tmp_tag_txt = ''
        toggle = False
        for tag_text in self.tag_dict:
            tag_enabled = self.tag_dict[tag_text]
            if tag_enabled:
                tmp_tag_txt += tag_text
                tmp_tag_txt += ' '
        tmp_tag_txt = tmp_tag_txt[0:-1]

        if os.path.exists(self.txt_file):
            os.remove(self.txt_file)
        wrt = open(self.txt_file, 'w')
        wrt.write(tmp_tag_txt)
        wrt.close()


class PicFrame:
    def __init__(self, master, window, default_tags):
        self.master = master
        self.window = window
        self.default_tags = default_tags
        self.pic_lbl = Label(master=master)
        self.pic_lbl.grid(column=0, row=0, padx=5, pady=5)
        set_pic(self.pic_lbl, np.zeros((512, 512, 3), dtype=np.uint8))
        self.current_tag_frame = None
        self.limit = 0
        self.index = 0
        self.pic_list = []
        self.folder_path = ''

    def load_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path == '':
            return
        if folder_path is None:
            return
        self.folder_path = folder_path

        file_list = []
        file_list.extend(glob(folder_path + '/*.jpg'))
        file_list.extend(glob(folder_path + '/*.jpeg'))
        file_list.extend(glob(folder_path + '/*.png'))
        file_list.extend(glob(folder_path + '/*.webp'))
        default_tags = toml.load('config.toml')['default_tags']
        self.pic_list = []
        self.current_tag_frame.clearbtn()
        for file in file_list:
            self.pic_list += [Pic(file, default_tags)]
        self.index = 0
        self.limit = len(self.pic_list)
        self.load()

    def set_current_tag_frame(self, current_tag_frame):
        self.current_tag_frame = current_tag_frame

    def load(self,booru_reload=False):
        current_pic = self.pic_list[self.index]
        self.current_tag_frame.clearbtn()
        tag_list = current_pic.get_tags()
        for tag in tag_list:
            self.current_tag_frame.add_btn((tag, True))
        image_path = current_pic.get_path()
        try:
            img = cv2.imread(image_path)
        except:
            img = np.ones((512, 512, 3), dtype=np.uint8) * 255
        img = resize(img, new_size=512)
        set_pic(self.pic_lbl, img)



    def set_tag_call_back(self, event):
        if len(self.pic_list) <= 0:
            return
        current_pic = self.pic_list[self.index]
        current_pic.tag_callback(event)

    def inc(self, event):
        global typing
        if typing:
            return
        tmp = self.index + 1
        if tmp < self.limit:
            self.index = tmp
            self.load()

    def dec(self, event):
        global typing
        if typing:
            return
        tmp = self.index - 1
        if tmp >= 0:
            self.index = tmp
            self.load()

    def save_all(self):
        # first_create a back up
        dict = {}
        for pic in self.pic_list:
            path = pic.get_path()
            text_path = path.replace(get_ext(path), '.txt')
            if os.path.exists(text_path):
                rd = open(text_path, 'r')
                txt = rd.read()
                rd.close()
                dict.update({path: txt})
        backupname = self.folder_path + '/back_up_file' + str(time.time_ns()) + '.pickle'
        if len(list(dict)) > 0:
            with open(backupname, 'wb') as handle:
                pickle.dump(dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
        # now save txt in files
        for pic in self.pic_list:
            pic.save_tags()


window = Tk()
window.title("Image Annotation Program")
window.geometry('1500x1000')

left_frame = Frame(master=window)
left_frame.grid(column=0, row=0, padx=5, pady=5, sticky='NW')

middle_frame = Frame(master=window)
middle_frame.grid(column=1, row=0, padx=5, pady=5)

controlframe = Frame(master=middle_frame)
controlframe.grid(column=0, row=0, padx=5, pady=5)

pic_frame = Frame(master=middle_frame)
pic_frame.grid(column=0, row=1, padx=5, pady=5)

# pic_lbl = Label(master=pic_frame)
# pic_lbl.grid(column=0, row=0, padx=5, pady=5)
pic_subframe = PicFrame(pic_frame, window, [])
sub_frame = Frame(master=pic_frame)
sub_frame.grid(column=0, row=1, padx=5, pady=5)
current_tag_frame = TagsFrame(left_frame, indicator=True, description='current tags',
                              callback_func=pic_subframe.set_tag_call_back)
search_frame = TagSearchFrame(sub_frame, call_back_func=current_tag_frame.add_btn)

# quick acessdrame

right_frame = Frame(master=window)
right_frame.grid(column=2, row=0, padx=5, pady=5, sticky='NW')
quick_access_frame = TagsFrame(right_frame, indicator=True, description='quick access tags',
                               callback_func=current_tag_frame.add_btn, col=right_frame_col)
right_frame_col += 1
quick_access_tag_list = toml.load('config.toml')['quick_access_tags']
for tag in quick_access_tag_list:
    quick_access_frame.add_btn((tag, True))

pic_subframe.set_current_tag_frame(current_tag_frame)
#pic_subframe.load_folder()

load_folder_btn = Button(master=controlframe, text='load folder',command=pic_subframe.load_folder)
load_folder_btn.grid(column=0, row=0, padx=5, pady=5)
load_sug_btn = Button(master=controlframe, text='load suggestings')
load_sug_btn.grid(column=1, row=0, padx=5, pady=5)
save_btn = Button(master=controlframe, text='save all (this will override all text files)',
                  command=pic_subframe.save_all)
save_btn.grid(column=2, row=0, padx=5, pady=5)

window.bind('<a>', pic_subframe.dec)
window.bind('<d>', pic_subframe.inc)
window.mainloop()
