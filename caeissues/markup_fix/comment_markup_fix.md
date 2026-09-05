_Created: 22-05-2026 · Last updated: 05-09-2026_

### Location

Counterpart of https://github.com/sanskrit-lexicon/PWG/issues/175 (PWG) and https://github.com/sanskrit-lexicon/PWK/issues/113 (PWK) for `cae.txt`.

I ran the same two-job recipe over `csl-orig/v02/cae/cae.txt`: auto-fix the few things with a single safe resolution; audit everything else with line refs. Added `08_markup_fix.py` plus outputs to a new `caeissues/markup_fix/` folder on the branch `markup-fix-audit`.

@funderburkjim @Andhrabharati — please review the findings listed below.

## Markup fixer + audit for `cae.txt`

### What it auto-fixes

| Pattern | Result |
|---|---|
| `<ab><ab>X</ab> Y</ab>` | `<ab>X Y</ab>` |
| `<lex> word </lex>` | `<lex>word</lex>` |
| `<ab> word </ab>` | `<ab>word</ab>` |
| `<lang> word </lang>` | `<lang>word</lang>` |

Whitespace trimming applies to all 3 paired tag(s) in `cae.txt`: `<lex>`, `<ab>`, `<lang>`. The original file is never modified — output goes to `cae_fixed.txt`, with the full diff in `markup_fix_changes.txt` (updateByLine format). **Output is byte-identical to source** (no auto-fixes triggered).

### Closing-tag inventory in current `cae.txt`

| Tag | Count |
|---|---:|
| `</lex>` | 44 |
| `</925)>` | ? |
| `</ab>` | 25 |
| `</564)>` | ? |
| `</lang>` | 3 |

### What it found in current `cae.txt`

- 0 whitespace trims — byte-identical to source.
- 1,194 within-line adjacent `</ab> <ab>` pairs for verification.
- 0 `<ab n="…">` attributes.
- 314 `{{old → new || …}}` correction records present.

### Usage

```
cd caeissues/markup_fix
python 08_markup_fix.py                        # uses csl-orig/v02/cae/cae.txt by default
python 08_markup_fix.py IN.txt OUT.txt         # custom paths
```

Outputs: `cae_fixed.txt`, `markup_fix_changes.txt`, `markup_audit.txt`.

### Summary

No unusual findings.

### Severity

`minor`

_Dr. Mārcis Gasūns_
