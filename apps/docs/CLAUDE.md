# Documentation (apps/docs)

## Documentation Writing Rules

- **MUST: Read every relevant TSX component in full BEFORE writing any documentation.** This is a hard requirement — do not write a single sentence of docs until all components that render the UI being documented have been fully read. This catches exact button labels, step order, dialog titles, status names, and flows that cannot be guessed or inferred from memory or summaries.
- **MUST: Grep both i18n files for every UI label before writing it.** Never assume, translate, or copy a label from existing docs. Always run `grep` on `apps/web/i18n/locales/en/common.json` and `apps/web/i18n/locales/de/common.json` to get the exact string the UI renders.
- **Always check the German glossary before writing German docs.** The glossary is at `apps/docs/docs/nerdy_content/GOAT_ui_glossary.md`. Use the exact German UI terms listed there for all UI element names, buttons, and section headings. Never translate UI terms from English without verifying in the glossary first.
- For Docusaurus docs, also check existing DE pages (e.g. `i18n/de/...`) to confirm which terms are already in use and to maintain consistency.
- **Screen recordings are MP4, screenshots are WebP — never GIF.** Embed a recording with `<Video src={require('/img/….mp4').default} alt="…" />` (registered globally, no import); it plays muted and looped like a GIF. Convert with `ffmpeg -i in.gif -movflags +faststart -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" -c:v libx264 -crf 26 out.mp4` and `ffmpeg -i in.png -c:v libwebp -quality 85 out.webp`. The PR `file-size` check rejects images over 1 MB, videos over 4 MB and other files over 2 MB (`scripts/check-file-sizes.sh`; exceptions go in `.github/large-files.txt`). Don't commit source files (`original_files/`, `.pptx`) next to the published images.

## Docs Diagram Exports (Figma API)

Diagrams used in the documentation are exported from Figma file `SmmQgQZ9QvWwg62NBlJcN8` (P4B-Website) using the Figma API. To re-export a diagram:

```bash
# Get image URL for a node (replace NODE_ID and TOKEN)
curl -s -H "X-Figma-Token: TOKEN" \
  "https://api.figma.com/v1/images/SmmQgQZ9QvWwg62NBlJcN8?ids=NODE_ID&format=png&scale=2" | python3 -m json.tool

# Download the returned URL directly to the static folder
curl -sL "IMAGE_URL" -o apps/docs/static/img/PATH/filename.png
```

**Current diagrams:**
| File | Figma node | Path |
|------|-----------|------|
| PT trip structure + combinations (EN) | `2581-83` | `apps/docs/static/img/routing/pt_trip_structure.png` |
| PT trip structure + combinations (DE) | `2584-2` | `apps/docs/static/img/routing/pt_trip_structure_de.png` |
| Cycling edge cost by topology (EN) | `2590-2` | `apps/docs/static/img/routing/bicycle_edge_cost.png` |
| Cycling edge cost by topology (DE) | `2590-47` | `apps/docs/static/img/routing/bicycle_edge_cost_de.png` |

**Token:** stored separately — ask the user. Do not hardcode in CLAUDE.md.
