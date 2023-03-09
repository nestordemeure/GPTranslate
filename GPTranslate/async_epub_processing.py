import asyncio
import ebooklib
from ebooklib import epub
from .epub_processing import translate_chapter, translate_metadata

async def translate_book_async(book, source_language, target_language, verbose=False):
    """
    async generator takes a book and translate it modifying it in place
    all chapters are translated simultaneously
    """
    tasks = []
    # translating the metadata
    task_meta = asyncio.to_thread(translate_metadata, 
                                book.metadata, source_language, target_language, verbose=verbose)
    tasks.append(task_meta)
    # translating the chapters
    chapters = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
    for i,chapter in enumerate(chapters):
        # translate the current chapter
        task_chapter = asyncio.to_thread(translate_chapter, 
                                         chapter, source_language, target_language, verbose=verbose)
        tasks.append(task_chapter)
    # wait on all the coroutines
    await asyncio.gather(*tasks)
    return book

def translate_book(book, source_language, target_language, output_file=None, verbose=False):
    """
    takes a book and translate it modifying it in place
    the translation is done asynchronously, all chapters simultaneously
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(translate_book_async(book, source_language, target_language, verbose=verbose))
    return book
