import pickle
import asyncio
from .model import translate

class Translation:
    """represent a translation being performed"""

    def __init__(self, data, language_source, language_target):
        self.source = data
        self.translation = list()
        self.language_source = language_source
        self.language_target = language_target

    def _translate_serial(self, name, source, translation, autosave_path=None, user_helped=False, verbose=False):
        """goes through the tree serialy and performs the translation"""
        # pick up where we were
        nb_done = len(translation)
        sources_done = source[:nb_done]
        sources_todo = source[nb_done:]
        # process down the tree recurcively
        if (len(source) > 0) and isinstance(source[0], str):
            # this is a leaf node
            history = list(zip(sources_done, translation))
            for i,text in enumerate(sources_todo):
                if verbose: print(f"{name} {1+i+nb_done}/{len(source)}")
                translated_text = translate(text, self.language_source, self.language_target, history, user_helped=user_helped, verbose=verbose)
                translation.append(translated_text)
                history.append((text,translated_text))
                # save at every leaf when user_helped is activated
                if user_helped and (autosave_path is not None): self.save(autosave_path)
            if autosave_path is not None: self.save(autosave_path)
            if verbose: print(f"{name} done.")
        else:
            # this is a root node
            # extends translation as much as needed
            translation_todo = [(name_child,list()) for (name_child,source_child) in sources_todo]
            translation.extend(translation_todo)
            # process all nodes
            for ((name_child,source_child),(_,translation_child)) in zip(source, translation):
                self._translate_serial(f"{name}|{name_child}", source_child, translation_child, autosave_path=autosave_path, user_helped=user_helped, verbose=verbose)

    async def _translate_async(self, name, source, translation, verbose=False):
        """goes through the tree asynchronously and perform the translation"""
        # process down the tree recurcively
        if (len(source) > 0) and isinstance(source[0], str):
            # this is a leaf node
            await asyncio.to_thread(self._translate_serial, name, source, translation, verbose=verbose)
        else:
            # this is a root node
            # extends translation as much as needed
            nb_done = len(translation)
            sources_todo = source[nb_done:]
            translation_todo = [(name_child,list()) for (name_child,source_child) in sources_todo]
            translation.extend(translation_todo)
            # process all nodes
            tasks = list()
            for ((name_child,source_child),(_,translation_child)) in zip(source, translation):
                task_child = self._translate_async(f"{name}|{name_child}", source_child, translation_child, verbose=verbose)
                tasks.append(task_child)
            # wait on all the tasks
            await asyncio.gather(*tasks)

    def _translate_parallel(self, name, source, translation, autosave_path=None, verbose=False):
        """goes through the tree asynchronously and perform the translation"""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._translate_async(name, source, translation, verbose=verbose))
        if autosave_path is not None: self.save(autosave_path)

    def translate(self, autosave_path=None, user_helped=False, verbose=False):
        """performs the translation"""
        if user_helped:
            self._translate_serial(name='', source=self.source, translation=self.translation, autosave_path=autosave_path, user_helped=user_helped, verbose=verbose)
        else:
            self._translate_parallel(name='', source=self.source, translation=self.translation, autosave_path=autosave_path, verbose=verbose)
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