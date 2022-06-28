# The Astrodynamics Book

[![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa] [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/dsavransky/astrodynamicsbook/HEAD?urlpath=lab/tree/Notebooks)

More description coming as soon as I figure out what this is going to be.  

## Reading the Book

This book is intended to be actively interacted with, and so requires a bit of setup.  You can avoid doing anything by accessing the book via mybinder (recommended), or you can go the hard route and install it locally.

### The Easy Way

Click the 'launch binder' badge at the top of this readme and wait a few minutes (it will take a while).  Once JupyterLab launches, click on the file browser (top icon in the left-hand panel) and select a notebook (I'd recommend starting from 01-Introduction.ipynb).  Pages will take a few seconds to fully render - if you see a bunch of garbage-looking code, just wait a bit and it will eventually turn into pretty equations.

### The Hard Way

The book is composed of a python backend and a Jupyter notebook frontend (the text).  In order to work with the text on your own machine locally, you must first install the backend.  It is recommended that you do this in a dedicated virtual environment.  The instructions below assume that you have python (version 3.8 or higher) and pip installed and working on your machine. For help with that, start here: https://wiki.python.org/moin/BeginnersGuide/Download  . We'll assume that python and pip are runnable as `python` and `pip`, respectively, but they might be called `python3` and `pip3` (or something else) on your particular system.

1. Download or clone this repository to your computer (https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository)
2. Create a python virtual environment (we'll call ours `bookenv` but you can replace this with any name you like). In a terminal/command prompt/powershell/etc run:
   
   ```python -m venv /full/path/to/bookenv```
   
3. Activate the environment. On macOS/Linux (see https://docs.python.org/3/library/venv.html for Windows details):

    ```source /full/path/to/bookenv/bin/activate```

4. In the same terminal with the active virtual environment, navigate to the cloned/downloaded repository.  From the top level directory of the repository (the one that contains the file `setup.py`) run:

    ```pip install .```
    
    This will install the book backend as well as a bunch of requirements to the virtual environment (it may take a while to download/install everything - go for a walk or something).
 
5. Navigate to the `Notebooks` subdirectory of the repo  (should just be `cd Notebooks` from where you were last) and then start JupyterLab by running `jupyter-lab`

6. From this point, everything is the same as via the [Easy Way](<#the-easy-way>)

7. To stop JupyterLab, type ctrl+c in the terminal where it is running and then hit ctrl+c again (or type `y` at the prompt). To deactivate the virtual environment just type `deactivate` at the prompt.  Next time you want to run the book, you just activate the environment again, navigate to the Notebooks directory and run `jupyter-lab`

>**Warning**
>There appears to be an issue (at least on macOS) where if you already have jupyter-lab installed in a system path, it will be executed initially instead of the one you install in your virtual environment.  A simple fix is to simply deactivate and re-activate the virtual environment after you run the initial pip installation.

## Feedback

Feedback is highly encouraged and sought after.  The best way to provide feedback is via the github Issue Tracker associated with this repository (https://github.com/dsavransky/astrodynamicsbook/issues)

## License
This work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg
