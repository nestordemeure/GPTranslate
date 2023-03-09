# GPTranslate

GPTranslate is a universal translator based on GPT.
Give it a book in `epub` format and it will translate it into any language.

## Usage

Modify the parameters in the header of the `translate.py` file to specify your file paths and languages (the input is expected to be in `epub` format).

Run `python3 gptranslate.py`.

## Inner-workings

#### Pipeline

Our pipeline follows these steps:

* the epub is parsed into metadata and a series of `html` files (roughly one per chapter).
* each `html` file is split into text nodes
* each text node is translated
* we then update the node in place

The pipeline is parallelized by running the translation of the chapters (and metadata) concurrently using `asyncio`.

#### Translation

The translation is handled by the [ChatGPT API](https://platform.openai.com/docs/guides/chat).
We pass a *system* message followed by the latest 15 translations (one user message per snippet to translate and an AI answer per translation) and the text to translate.
If the context proves too large for the API, we retry with a smaller number of previous translations.

The system message is written as follows:

```json
I want you to act as a translator from {source_language} to {target_language}.
I will speak to you in {source_language} or English and you will translate it and answer in {target_language}.
Your output should be in json format with optional 'translation' (string, only include the translation and nothing else, do not write explanations here), 'notes' (string) and 'success' (boolean) fields.
If an input cannot be translated, return it unmodified.
```

Note that we ask for a `json` output. This is done to let us easily distinguish between the actual text of the translation and notes (the model tends to comment on its own translation).

The `translation` field of the `json` output is extracted using a rough parser that slices the string based on the positions of the field names.
We are purposefully avoiding the use of a proper `json` parser as the output is often malformed, crashing existing parsers.

## Potential improvements

* add ways to pause the translation process and restart it later
* add the possibility to pick one of 3 translations or type one by hand

* use a database to let the model look at previous parts of the translation that might be relevant to the current bit of text being translated
* build a user interface that lets a user 
    * pick the file
    * pick the destination language (default to English)
    * pick the source language (should default to autodetected)
