# pdf signer

The python script allows to place your signature (with or without date next to it) on pdfs, at the position you point with your mouse. Also a check mark and small text can be placed. It's made to quickly go through many pdfs (by default looping through all in the folder).

It uses pymupdf to open and edit the pdfs, and matplotlib to display the pages pixmaps and enable crude GUI callbacks.

Clicks:
* left: place signature & date
* shift-left: place only signature
* middle: place a 'X' check mark

Keys:
* ' ' proceed to the next page
* 'q' done with the document (saves it if edited)
* 't' add the text given in the top right textbox at the location

Parameters:
* signatureFile: your signature image file
* saveTag: the tag that is added to the filename when saving

Dependencies:

      pip install pymupdf numpy matplotlib
