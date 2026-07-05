# REPOSITORY RENAME

This repository is being renamed. This note records the rename and the manual
steps. **The GitHub repository rename is done manually after this change merges —
it is not performed by this PR.**

- **Target repository name:** `saudi-legal-corpus-ai`
- **Former repository name:** `saudi-companies-law-ar-zh-llm`
- **Target GitHub path:** `al3obdi/saudi-legal-corpus-ai`
- **Former GitHub path:** `al3obdi/saudi-companies-law-ar-zh-llm`

## Why the rename

The project is now a **multilingual, LLM-ready, official-source-based Saudi legal
corpus for AI** — it structures Saudi laws and regulations into auditable,
machine-readable legal layers. The Companies Law is the **first implemented law
profile**, and Chinese is **one language layer**. The old name
(`saudi-companies-law-ar-zh-llm`) framed the project as only a Companies-Law
Arabic–Chinese translation, which no longer reflects the repository's identity.
The new name (`saudi-legal-corpus-ai`) reflects the actual scope.

## Manual GitHub rename steps (after this PR merges)

1. Open the repository on GitHub.
2. Go to **Settings → General**.
3. Under **Repository name**, change `saudi-companies-law-ar-zh-llm` to
   **`saudi-legal-corpus-ai`**.
4. Click **Rename**.

## Update your local remote after the rename

Once the GitHub rename is done, update your local clone's `origin` remote so it
points at the new path:

```bash
# SSH
git remote set-url origin git@github.com:al3obdi/saudi-legal-corpus-ai.git

# HTTPS alternative
git remote set-url origin https://github.com/al3obdi/saudi-legal-corpus-ai.git
```

## Notes

- After the rename, **GitHub automatically redirects** old repository links and
  git operations (clone/fetch/push) from `al3obdi/saudi-companies-law-ar-zh-llm`
  to `al3obdi/saudi-legal-corpus-ai`. Existing clones keep working, but you
  should still update local remotes (above) to avoid confusion.

## Warning

- **Do not create a new repository using the old name**
  (`saudi-companies-law-ar-zh-llm`). Reusing the old name would **break the
  redirects** GitHub sets up for the rename.

## Historical references

Where the former name appears in historical context (archived PR references,
migration notes, or local filesystem paths), it is preserved as history and not
rewritten. The mapping is:

- **Former:** `al3obdi/saudi-companies-law-ar-zh-llm`
- **Current intended:** `al3obdi/saudi-legal-corpus-ai`

This is internal repository metadata only. Arabic official source governs;
English and Chinese are reference layers (Chinese is not official, not binding,
not governing). No official government publication, adoption, or translation is
claimed. Not legal advice.
