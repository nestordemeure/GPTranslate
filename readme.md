# GPTranslate

*GPTranslate* is a universal translator based on the [GPT family of large language models](https://openai.com/product).
Give it a book in `epub` format and it will translate it into any language.

## Usage

Modify the parameters in the header of the `gptranslate.py` file to specify your file paths and languages (the input is expected to be in `epub` format).

The program has two modes:
* `check_translation_manually=True` in which case the translation is done in collaboration between the user and algorithm, giving several potential translations to the user and letting them pick one or write their own (this can take a long time but gives the best results),
* `check_translation_manually=False` which is optimized for speed (good for a fast translation of a text).

Run `python3 gptranslate.py`.

## Inner-workings

#### Pipeline

Our pipeline follows these steps:

* the epub is parsed into metadata and a series of `html` files (roughly one per chapter).
* each `html` file is split into text nodes
* each text node is translated
* we then update the node in place

When `check_translation_manually` is unchecked, the pipeline is parallelized by running the translation of the chapters (and metadata) concurrently using `asyncio`.

#### Translation

The translation is handled by the [ChatGPT API](https://platform.openai.com/docs/guides/chat).
We pass a *system* message followed by the latest 15 translations (one user message per snippet to translate and an AI answer per translation) and the text to translate.
If the context proves too large for the API, we retry with a smaller number of previous translations.

The system message is written as follows:

```
I want you to act as a translator from {source_language} to {target_language}.
I will speak to you in {source_language} or English and you will translate in {target_language}.
Your output should be in json format with optional 'translation' (string, only include the translation and nothing else, do not write explanations here), 'notes' (string) and 'success' (boolean) fields.
If an input cannot be translated, return it unmodified.
```

Note that we ask for a `json` output. This is done to let us easily distinguish between the actual text of the translation and notes (the model tends to comment on its own translation).

The `translation` field of the `json` output is extracted manually by slicing the string based on the indices of the field names.
We are purposefully avoiding the use of a proper `json` parser as the output is often malformed, crashing existing parsers.

## Potential improvements

* refactor the code so that, once loaded, a book is in a `Book` class with:
    * a `read(self) -> dict(string:[string])` method that produces a dict of lists of string (one list per chapter)
    * a `write(self, translated_chapters:dict(string:[string]))` method that takes a dict of lists of (translated) string and updates the book
  the idea is that we use the determinism in iterating on the texts to abstract over the file format and structure  
  this would enable both restarting and introducing alternative file formats easily

* add ways to pause the translation process and restart it later
  (important for manual translation as one will not translate a book in a continuous run)
* add support for other file formats such as `txt`, `pdf`, `docx` and `html`

* use a database to let the model look at previous parts of the translation that might be relevant to the current bit of text being translated
* build a user interface that lets a user:
    * pick the file
    * pick the destination language (default to English)
    * pick the source language (should default to autodetected)