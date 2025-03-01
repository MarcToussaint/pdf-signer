#!/usr/bin/env python3

import os
import pymupdf
import numpy as np
import datetime
import glob
import subprocess
import argparse

import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox
from matplotlib.backend_bases import MouseEvent

parser = argparse.ArgumentParser(
    description='Python script to quickly put your signature (and date, check mark, or text) on pdfs at the mouse pointer.')

parser.add_argument('file', type=str, nargs='?', default='*',
                     help='file to sign - or * to loop through all files')

parser.add_argument('-saveTag', type=str, default='_signedMT', help='tag appended to the filename when saving the signed pdf')

parser.add_argument('-signatureFile', type=str, default='/home/mtoussai/lis/lis-admin/signatureColorTransparent.png', help='image file of the signature')

class Signer:

    def __init__(self, args):
        self.args = args
        self.w, self.h, self.o = 110, 30, 60
        self.date = datetime.datetime.now().strftime("%d.%m.%Y")
        self.text = self.date
        return

    def sign_file(self, file):

        # re-encode the pdf using ghostscript
        if True:
            subprocess.run(["gs","-sDEVICE=pdfwrite","-dNOPAUSE","-dQUIET","-dBATCH","-sOutputFile=z.pdf",file])
            doc = pymupdf.open('z.pdf')
        else:
            doc = pymupdf.open(file)

        plt.ion()
        fig = plt.figure(figsize=(10,14))
        ax = fig.add_subplot(111)
        fig.tight_layout()
        fig.canvas.mpl_connect('button_press_event', self.on_click)
        fig.canvas.mpl_connect('key_press_event', self.on_press)

        # a textbox user input to allow inserting text with 't' key
        axbox = fig.add_axes([0.9, 0.95, 0.1, 0.05])
        text_box = TextBox(axbox, "text", initial=self.text, textalignment="center")
        text_box.on_submit(self.on_text)

        imgplot = None
        self.saveNewFile = False

        for self.page in doc:
            pix = self.page.get_pixmap()
            img = np.frombuffer(pix.samples, dtype='B').reshape((pix.height,pix.width,pix.n))
            if not imgplot:
                imgplot = ax.imshow(img)
                plt.show()
            else:
                imgplot.set_data(img)

            self.pageDone = False
            self.needsDisplayUpdate = False

            while not self.pageDone: # the events below terminate this event loop
                plt.pause(.02) # calls the matplotlib event loop - necessary to process user input
                if self.needsDisplayUpdate: # update the pixmap
                    pix = self.page.get_pixmap()
                    img = np.frombuffer(pix.samples, dtype='B').reshape((pix.height,pix.width,pix.n))
                    imgplot.set_data(img)
                    self.needsDisplayUpdate = False

            if self.cmd=='quit': # key ' ' steps through pages, key 'q' quits document
                break

        fig.clear()

        if self.saveNewFile:
            path, ext = os.path.splitext(file)
            filename = f'{path}{self.args.saveTag}{ext}'
            print('=== saving', filename)
            doc.save(filename)


    def on_text(self, text):
        self.text = text

    def on_click(self, event: MouseEvent):
        coords=[event.xdata, event.ydata]
        print('click event ', event.button, coords, event.modifiers)

        if not coords[0]:
            print('off page')
            return

        if event.button==plt.MouseButton.LEFT: # signature
            coords[1] += 2
            rect = pymupdf.Rect(coords[0], coords[1]-self.h, coords[0]+self.w, coords[1])
            self.page.insert_image(rect, filename=self.args.signatureFile)
            if 'shift' not in event.modifiers: # and date
                #rect = pymupdf.Rect(coords[0]+self.o, coords[1]-self.h, coords[0]+self.o+self.w, coords[1])
                self.page.insert_text((coords[0]-self.o, coords[1]-2), self.date, fontsize=11, fontname='helv')

        elif event.button==plt.MouseButton.MIDDLE: # check mark
            self.page.insert_text((coords[0]-5.5, coords[1]+7), 'X', fontsize=16, fontname='helv')

        self.needsDisplayUpdate = True
        self.saveNewFile = True

    def on_press(self, event):
        coords=[event.xdata, event.ydata]
        print('key event ', event.key, coords)

        if event.key == ' ': # sign on more pages
            self.pageDone = True

        if event.key == 't':
            self.page.insert_text((coords[0], coords[1]), self.text, fontsize=11, fontname='helv')
            self.needsDisplayUpdate = True

        if event.key == 'q':
            self.cmd='quit'
            self.pageDone = True



def main():
    args = parser.parse_args()

    if args.file=='*':
        files = sorted(glob.glob('*.pdf'))
    else:
        files = [args.file]

    for file in files:
        if args.saveTag in file or 'z.pdf' in file:
            print('=== skipping', file)
            continue
        print('=== opening', file)
        S = Signer(args)
        S.sign_file(file)

if __name__ == "__main__":
    main()
