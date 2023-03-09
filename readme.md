# GPTranslate

GPTranslate is a universal translator based on GPT[0].
Give it a text (or a full book) and it will translate it into any source language.

[0]: This is mostly an exercise in using the [ChatGPT API](https://platform.openai.com/docs/guides/chat).

## Usage

**TODO**

## Inner-workings

* the text is loaded and cut into chunks
* it is sent one chunk at a time, in sequential order, to the ChatGPT API for translation
  (passing some of the previous translations along to let GPT use them as context)

## Potential improvements

* use a database to let the model look at previous parts of the translation

* build a user interface that lets a user 
    * pick the file themselves
    * pick the destination language (default to English)
* have the source language be autodetected
  (with user confirmation)
* let the user correct parts of the translation and use those corrections to help the automated translation
