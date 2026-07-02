# inputs/

Design/reference inputs. **Not** the canonical long-term source.

## bab1_source.pdf

The Arabic–Chinese reference translation of Book One / الباب الأول of the Saudi
Companies Law, Articles 1–34 (31 pages). The combined file internally contains three
parts (1–15, 16–25, 26–34); the repository treats them as **one continuous Book One**.

### Why this is not canonical

- The PDF is the *design artifact*; canonical structured sources live in `data/`.
- The PDF's **Chinese** text layer extracts cleanly and was used (with the targeted
  legal upgrades) as the reference Chinese.
- The PDF's **Arabic** text layer extracts **garbled**; it was **not** used verbatim.
  Arabic reference summaries in `data/articles/*.json` are manually reconstructed MSA.

### Inspecting the PDF

```bash
python scripts/extract_pdf_text.py inputs/bab1_source.pdf -o /tmp/bab1_text.txt
```

`pypdf` is an optional dependency (`pip install pypdf`). The extractor is a diagnostic
tool only — do **not** feed its garbled Arabic back into the canonical JSON.
