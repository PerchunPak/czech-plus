# czech-plus

[![Support Ukraine](https://badgen.net/badge/support/UKRAINE/?color=0057B8&labelColor=FFD700)](https://www.gov.uk/government/news/ukraine-what-you-can-do-to-help)

[![Build Status](https://github.com/PerchunPak/czech-plus/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/PerchunPak/czech-plus/actions?query=workflow%3Atest)
[![Documentation Build Status](https://readthedocs.org/projects/czech-plus/badge/?version=latest)](https://czech-plus.readthedocs.io/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Addon for professional Czech words learning!

## Warning

This addon is not supposed to be used with invalid input, it expects always valid input and almost never validates it.
You will see unexpected behaviour and confusing errors if you use it with invalid input.

## Installing

Is not released yet, but you can still install it.

P.S. If you do not want to install Python, I can send a copy of the addon, which doesn't require
Python. That copy just need to be copied to the addons folder.

### Install Python

Firstly, you need to install [Python 3.9](https://www.python.org/downloads/release/python-3913/).
There are a lot of instructions in the Internet, you can easily follow them. But note, that Anki
supports only 3.9, so other version possibly will not work.

### Download the repository

You can use green `Code` button or Git. If you have Git on your computer - it's preferable.

Note that you need to download the repository to the [addons folder](https://addon-docs.ankiweb.net/addon-folders.html).

```bash
git clone https://github.com/PerchunPak/czech-plus.git
cd czech-plus
```

Then create, in the downloaded code folder, file `__init__.py` with content:

```py
import sys
from pathlib import Path
import aqt

sys.path.append(str(Path(__file__).parent.resolve()))

import czech_plus

aqt.gui_hooks.main_window_did_init.append(czech_plus.main)
```

### Download dependencies

```bash
python3 -m venv ./venv
```

Then, if you're on Linux, use `source venv/bin/activate` and if you use Windows - `venv\Scripts\activate.bat`
(replace `.bat` in the end with `.ps1`, if you use PowerShell instead of cmd).

And finally you need to actually install the dependencies:

```bash
vendoring sync
```

Done! Just restart Anki and everything should work.

## Installing for local developing

```bash
git clone https://github.com/PerchunPak/czech-plus.git
cd czech-plus
```

### Installing `poetry`

Next we need install `poetry` with [recommended way](https://python-poetry.org/docs/master/#installation).

If you use Linux, use command:

```bash
curl -sSL https://install.python-poetry.org | python -
```

If you use Windows, open PowerShell with admin privileges and use:

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

### Installing dependencies

```bash
poetry install
poerty run vendoring sync
```

### Adding to Anki

Then you need to add addon in Anki. Go to `Tools` -> `Add-ons` menu item in the main Anki window. Click on the
`View Files` button, and a folder will pop up. If you had no add-ons installed, the top level add-ons folder will be
shown. If you had an add-on selected, the add-on's module folder will be shown, and you will need to go up one level.

There you need to create a new folder (name as you want), and run some commands to sync it with downloaded code:

```bash
cd <path to your new folder>
# for Linux
ln -s <path to folder with source code>/czech_plus czech_plus
# for Windows
mklink /J czech_plus <path to folder with source code>/czech_plus
```

You also need to add a file, near the `czech_plus` folder, with name `__init__.py` and content:

```python
import sys
from pathlib import Path
import aqt

sys.path.append(str(Path(__file__).parent.resolve()))

import czech_plus

aqt.gui_hooks.main_window_did_init.append(czech_plus.main)
```

Then rerun your Anki, and here it is!

## Configuration

All configuration happens in Anki interface. You can also read the `CONFIG.md` file.

## If something is not clear

You can always write me!

## Updating

If you downloaded with Git, just use `git pull`. But if it gives some errors or you didn't
download with Git, just do all the instalation steps again.

## Thanks

This project was generated with [python-template](https://github.com/PerchunPak/python-template).
