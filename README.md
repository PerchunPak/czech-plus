# czech-plus

[![Support Ukraine](https://badgen.net/badge/support/UKRAINE/?color=0057B8&labelColor=FFD700)](https://www.gov.uk/government/news/ukraine-what-you-can-do-to-help)

[![Build Status](https://github.com/PerchunPak/czech-plus/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/PerchunPak/czech-plus/actions?query=workflow%3Atest)
[![Documentation Build Status](https://readthedocs.org/projects/czech-plus/badge/?version=latest)](https://czech-plus.readthedocs.io/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

My addon to learn Czech

## Features

- Free! We don't want any money from you!
- Add yours!

## Warning

This addon is not supposed to be used with invalid input, it expects always valid input and almost never validates it.
You will see unexpected behaviour and confusing errors if you use it with invalid input.

## Installing

Is not released yet.

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

### Configuration

All configuration happens in Anki interface.

### If something is not clear

You can always write me!

## Updating

Use Anki's addon manager.

## Thanks

This project was generated with [python-template](https://github.com/PerchunPak/python-template).
Current template version: [5afea199e68f5100ddd394dfb765071b27b31373](https://github.com/PerchunPak/python-template/tree/5afea199e68f5100ddd394dfb765071b27b31373).
See what [updated](https://github.com/PerchunPak/python-template/compare/5afea199e68f5100ddd394dfb765071b27b31373...master).
