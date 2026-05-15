# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**CAE** is the corrections and research repository for the Cologne digitization of Cappeller's *Sanskrit-English Dictionary* (1891). The canonical source lives in `csl-orig/v02/cae/cae.txt`.

## Architecture

| Directory | Purpose |
|---|---|
| `verbs01/` | Root identification: maps CAE verb entries to MW root spellings, identifies prefixed verbs |
| `english_corrections/` | English word spell-check error analysis |

### Verb root pipeline (`verbs01/`)

Identifies Cappeller verb entries and maps them to their MW equivalents, with preverb (upasarga) resolution. See [CAE issue #1](https://github.com/sanskrit-lexicon/CAE/issues/1).

Issues and corrections are tracked via the [GitHub issue tracker](https://github.com/sanskrit-lexicon/CAE/issues).

## Common Commands

### Apply line-level corrections (standard pattern)
```bash
python updateByLine.py <input_file> <changein_file> <output_file>
```

### Rebuild and validate XML (from `csl-pywork/v02/`)
```bash
sh generate_dict.sh cae ../../CAEScan/2020
sh xmlchk_xampp.sh cae
```

## Dependencies

- **Python 3**
- **cae.txt** — in `$BASE/cologne/csl-orig/v02/cae/cae.txt`
