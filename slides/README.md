# slides/

Marp markdown source for class presentations.

## Files planned for this folder

| File | When | Status |
|------|------|--------|
| `22-05.md` | Team presentation 22 May 2026 | TBD |
| (later dates) | | |

Any SVG diagrams used by the slides also go in this folder.

## Render

```
npx --yes @marp-team/marp-cli@latest slides/22-05.md --pptx --allow-local-files -o slides/22-05.pptx
```

Or use the Marp VS Code extension for live preview.

## Conventions

- One `.md` per presentation, named by the presentation date (`DD-MM.md`)
- Generated `.pptx` files are git-ignored (regenerable from source)
- Keep the style block at the top consistent between decks for visual continuity
