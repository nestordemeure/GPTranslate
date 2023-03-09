# GPTranslate

GPTranslate is a universal translator based on GPT[0].
Give it a book in epub format and it will translate it into any language.

[0]: This is mostly an exercise in using the [ChatGPT API](https://platform.openai.com/docs/guides/chat).

## Usage

Modify the parameters in the header of the `translate.py` file to specify your file paths and languages (the input is expected to be in epub format).

Run `python3 translate.py`.

## Inner-workings

* the epub is parsed into a serie of html nodes
* the nodes are translated one at a time by ChatGPT
  passing it the latest translations to be used as context
* the epub is updated on the fly and then written to disk

## Potential improvements

* use a database to let the model look at previous parts of the translation

* build a user interface that lets a user 
    * pick the file themselves
    * pick the destination language (default to English)
* have the source language be autodetected
  (with user confirmation)
* let the user correct parts of the translation and use those corrections to help the automated translation
