#!/usr/bin/env python3

import os
import pymupdf
import matplotlib.pyplot as plt
import numpy as np
import datetime
import glob
import subprocess

cmd = ''
sign_coords = []
tick_coords = []

def onclick(event):
    global cmd
    global sign_coords
    global tick_coords
    if event.button==plt.MouseButton.LEFT:
        cmd='signDate'
        sign_coords=[event.xdata, event.ydata]
        print('signing with date', event.button, sign_coords)
    if event.button==plt.MouseButton.RIGHT:
        cmd='sign'
        sign_coords=[event.xdata, event.ydata]
        print('signing without date', event.button, sign_coords)
    elif event.button==plt.MouseButton.MIDDLE:
        tick_coords=[event.xdata, event.ydata]
        print('ticking', event.button, tick_coords)

def on_press(event):
    print('press', event.key)
    global cmd
    if event.key == 'd':
        cmd='signDate'
        sign_coords=[event.xdata, event.ydata]
        print('signing with date', sign_coords)
        plt.close(event.canvas.figure)
    if event.key == 'd':
        cmd='skip'
        print('skipping')
        plt.close(event.canvas.figure)
        
def sign_file(file):
    w, h, o = 110, 30, 60
    signature = '/home/mtoussai/lis/lis-admin/signatureColorTransparent.png'
    date = datetime.datetime.now().strftime("%d.%m.%Y")
    edited = False

    if True:
        subprocess.run(["gs","-sDEVICE=pdfwrite","-dNOPAUSE","-dQUIET","-dBATCH","-sOutputFile=z.pdf",file])
        doc = pymupdf.open('z.pdf')
    else:
        doc = pymupdf.open(file)

    for page in doc:
        pix = page.get_pixmap()
        img = np.frombuffer(pix.samples, dtype='B').reshape((pix.height,pix.width,pix.n))

        global cmd
        global sign_coords
        global tick_coords
        cmd = ''
        sign_coords = []
        tick_coords = []
        fig = plt.figure(figsize=(10,14))
        ax = fig.add_subplot(111)
        fig.tight_layout()
        imgplot = ax.imshow(img)
        fig.canvas.mpl_connect('button_press_event', onclick)
        fig.canvas.mpl_connect('key_press_event', on_press)
        plt.show()
        fig.clear()

        if len(sign_coords):
            print('command:', cmd, sign_coords, tick_coords)
            if cmd=='signDate':
                rect = pymupdf.Rect(sign_coords[0]+o, sign_coords[1]-h, sign_coords[0]+o+w, sign_coords[1])
                page.insert_image(rect, filename=signature)
                page.insert_text((sign_coords[0], sign_coords[1]), date, fontsize=11, fontname='helv')
            elif cmd=='sign':
                rect = pymupdf.Rect(sign_coords[0], sign_coords[1]-h, sign_coords[0]+w, sign_coords[1])
                page.insert_image(rect, filename=signature)
            edited = True

        if len(tick_coords):
            print('adding tick at', tick_coords)
            page.insert_text((tick_coords[0]-5, tick_coords[1]+10), 'X', fontsize=18, fontname='helv')
            edited = True

        if edited:
            break

    if edited:
        output_filename = "{}_signedMT{}".format(*os.path.splitext(file))
        doc.save(output_filename)

def main():
    files = sorted(glob.glob('*.pdf'))
    for file in files:
        if 'signedMT' in file or 'z.pdf' in file:
            continue
        sign_file(file)

if __name__ == "__main__":
    main()
