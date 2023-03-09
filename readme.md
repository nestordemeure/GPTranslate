# GPTranslate

GPTranslate is a universal translator based on GPT[^0].
Give it a book in epub format and it will translate it into any language.

[^0]: This is mostly an exercise in using the [ChatGPT API](https://platform.openai.com/docs/guides/chat).

## Usage

Modify the parameters in the header of the `translate.py` file to specify your file paths and languages (the input is expected to be in epub format).

Run `python3 gptranslate.py`.

## Inner-workings

* the epub is parsed into a serie of html each turned into a list html text nodes
* the nodes are translated one at a time by ChatGPT
  passing the latest translations to be used as context
  and asking for the output to be json formatted in order to simplify the extraction of the translation
* the epub is updated on the fly and rewritten to disk at the end of each chapter

Most of the work is done by the following prompt:

```json
I want you to act as a translator from {source_language} to {target_language}.
I will speak to you in {source_language} or English and you will translate it and answer in {target_language}.
Your output should be in json format with optional 'translation' (string), 'notes' (string) and 'success' (boolean) fields.
If an input cannot be translated, return it unmodified.
```

## Potential improvements

* add the possibility to pick one of 3 translations or type one by hand (with ways to stop and restart the process)
* add an async mode to run the translation in parallel

* use a database to let the model look at previous parts of the translation that might be relevant to the current bit of text being translated
* build a user interface that lets a user 
    * pick the file
    * pick the destination language (default to English)
    * pick the source language (should default to autodetected)
* let the user correct parts of the translation and use those corrections to help the automated translation
