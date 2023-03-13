import pickle
import asyncio
from .translator import translate
from .language_detection import detect_language
from .tree_processing import *
from leaf_slicing import should_slice, slice_leaf, unslice_leaf

class Translation:
    """
    represent a translation being performed
    intermediate results will automatically be saved in `autosave_path`
    """

    def __init__(self, data, language_source='auto', language_target='English', autosave_path=None):
        self.source = data
        self.translation = empty_clone(data)
        self.language_source = detect_language(flatten(self.source)) if (language_source=='auto') else language_source
        self.language_target = language_target
        self.autosave_path = autosave_path

    def _translate_leaf(self, name, source, translation, user_helped=False, verbose=False):
        """translate a leaf node"""
        # pick up where we were
        nb_done = len(translation)
        sources_done = source[:nb_done]
        sources_todo = source[nb_done:]
        history = list(zip(sources_done, translation))
        # go through text left
        for i,text in enumerate(sources_todo):
            if contains_text(text):
                if verbose: print(f"{name} {1+i+nb_done}/{len(source)}")
                translated_text = translate(text, self.language_source, self.language_target, history, user_helped=user_helped, verbose=verbose)
                history.append((text,translated_text))
            else:
                # skip text that does not contain letters
                translated_text = text
            translation.append(translated_text)
            # autosave at every translation when user_helped is activated
            if user_helped and (self.autosave_path is not None): self.save(self.autosave_path)

    def _translate_serial(self, name, source, translation, user_helped=False, verbose=False):
        """goes through the tree serialy and performs the translation"""
        # process down the tree recurcively
        if is_leaf(source):
            # this is a leaf node
            self._translate_leaf(name, source, translation, user_helped=False, verbose=verbose)
            # autosave at the end of every leaf
            if self.autosave_path is not None: self.save(self.autosave_path)
            if verbose: print(f"{name} done.")
        else:
            # this is a root node
            # process all children
            for ((name_child,source_child),(_,translation_child)) in zip(source, translation):
                self._translate_serial(f"{name}|{name_child}", source_child, translation_child, user_helped=user_helped, verbose=verbose)

    async def _translate_async(self, name, source, translation, split_leaves=False, verbose=False):
        """goes through the tree asynchronously and perform the translation"""
        # process down the tree recurcively
        if is_leaf(source):
            # this is a leaf node
            if split_leaves and should_slice(source):
                # slices sources and translations for greater paralelism
                sources, translations, overlaps = slice_leaf(source, translation)
                # performs the translation
                tasks = list()
                for i, (slice_source, slice_translation) in enumerate(zip(sources, translations)):
                    slice_task = asyncio.to_thread(self._translate_leaf, f"{name}|slice_{i+1}", slice_source, slice_translation, verbose=verbose)
                    tasks.append(slice_task)
                await asyncio.gather(*tasks)
                # merge our result into translation
                result = unslice_leaf(translations, overlaps)
                translation.clear()
                translation.extend(result)
            else:
                # does the leaf as a single block
                await asyncio.to_thread(self._translate_leaf, name, source, translation, verbose=verbose)
            # autosave at the end of every leaf
            if self.autosave_path is not None: self.save(self.autosave_path)
            if verbose: print(f"{name} done.")
        else:
            # this is a root node
            # process all children
            tasks = list()
            for ((name_child,source_child),(_,translation_child)) in zip(source, translation):
                task_child = self._translate_async(f"{name}|{name_child}", source_child, translation_child, split_leaves=split_leaves, verbose=verbose)
                tasks.append(task_child)
            # wait on all the tasks
            await asyncio.gather(*tasks)

    def _translate_parallel(self, name, source, translation, split_leaves=False, verbose=False):
        """goes through the tree asynchronously and perform the translation"""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._translate_async(name, source, translation, split_leaves=split_leaves, verbose=verbose))

    def translate(self, user_helped=False, split_leaves=False, verbose=False):
        """performs the translation"""
        # check if a translation is already underway
        if (self.autosave_path is not None) and self.autosave_path.exists():
            previous_translation = Translation.load(self.autosave_path)
            if (previous_translation.language_source == self.language_source) and (previous_translation.language_target == self.language_target) and tree_equal(previous_translation.source,self.source):
                print(f"Loading '{self.autosave_path}' partial translation.")
                self.translation = previous_translation.translation
        # performs the translation
        if user_helped:
            self._translate_serial(name='', source=self.source, translation=self.translation, user_helped=user_helped, verbose=verbose)
        else:
            self._translate_parallel(name='', source=self.source, translation=self.translation, split_leaves=split_leaves, verbose=verbose)
        # delete the autosaved file
        if (self.autosave_path is not None) and self.autosave_path.exists():
            self.autosave_path.unlink()
        return self.translation

    def save(self, path):
        """save the translation to disk"""
        with open(path, 'wb') as f:
            pickle.dump(self, f)
    
    @staticmethod
    def load(path) -> 'Translation':
        """loads the translation from disk"""
        with open(path, 'rb') as f:
            obj = pickle.load(f)
        return obj