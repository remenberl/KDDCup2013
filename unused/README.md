This folder keeps some modules that are not used in the model or irrelevant to the final submission files.

Files:
    cannot_links_must_links_generator.py tries to infer the confident relations between author ids infered from train anv valid data provided by track 1. It does not work well.

    dedup.py is to reduce the lines in the generation files for analysis.

    deep_convert.py tries to guess the missing strings in Author.csv and PaperAuthor.csv originally represented by question marks. No effect on the submission files.

    preprocess.py tries to recover the short names in Author.csv using info in PaperAuthor.csv. Results seem convincing but the evalution does not buy it.

    refine_paper_author.py uses train and validation files to clean the author-paper links. Results seem not good.

    simhash.py is a module for computing similar hashes for similar strings. Not effective.
