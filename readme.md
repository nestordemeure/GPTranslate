# GPTranslate

*GPTranslate* is a universal translator based on the [GPT family of large language models](https://openai.com/product).
Give it a book and it will translate it into any language.

## Usage

Modify the parameters in the header of the `gptranslate.py` file to specify your file paths and languages.
The input is expected to be in `epub`, `html`, `txt` or `pdf` (to be avoided as that format is neither editable nor designed to extract text).

The program has two modes:
* `check_translation_manually=True` in which case the translation is done in collaboration between the user and algorithm, giving several potential translations to the user and letting them pick one or write their own (this can take a long time but gives the best results),
* `check_translation_manually=False` which is optimized for speed (good for a fast translation of a text).

Run `python3 gptranslate.py`.

Once the program is started, it will create a `tmp` file (deleted once the translation is done) in the same folder as the input.
As long as that file exists, you can kill and restart the program, picking up the translation where you left.

## Inner-workings

#### Pipeline

Our pipeline follows these steps:

* the book is parsed into lists of short texts (details vary per input format)
* each list is translated one element at a time (filtering out elements that do not contain actual text)
* the texts are then reshaped back into the input format

When `check_translation_manually` is unchecked, the pipeline is parallelized by processing each list concurrently using `asyncio`.
One can also set `split_leaves=True` to split the larger lists into overlapping chunks for even faster processing (at the price of an increased number of API calls and a potential degradation in translation quality around the overlapping section).

#### Translation

The translation is handled by the [ChatGPT API](https://platform.openai.com/docs/guides/chat).
We pass a *system* message followed by the latest 15 translations (one user message per snippet to translate and an AI answer per translation) and the text to translate.
If the context proves too large for the API, we retry with a smaller number of previous translations (we might also retry if the output appears incomplete).

The system message is written as follows:

```
I want you to act as a translator from {source_language} to {target_language}.
I will speak to you in {source_language} or English and you will translate in {target_language}.
Your output should be in json format with optional 'translation' (string, only include the translation and nothing else, do not write explanations here), 'notes' (string) and 'success' (boolean) fields.
If an input cannot be translated, return it unmodified.
```

Note that we ask for a `json` output. This is done to let us easily distinguish between the actual text of the translation and notes (the model tends to comment on its own translation).

The `translation` field of the `json` output is extracted with a hardened parser as the output is often malformed, crashing existing parsers.

## Potential improvements

* add a command line interface to extract the input parameters
* add support for other file formats such as `md`, `docx`, `odt`
* use a database to let the model look at previous parts of the translation that might be relevant to the current bit of text being translated
  (contrary to my initial beliefs, this does not seem to be needed for most applications)
