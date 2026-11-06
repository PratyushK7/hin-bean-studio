# Rendering engine integration

## What this folder means

This folder is an integration point, not a bundled renderer yet.

The original `PratyushK7/bean-studio` repository used a locally installed `line-boil` engine from the Claude animation skills kit. The Git repository staged an older `build.py` patch/backup, but did **not** contain the complete working renderer, engine JavaScript, sound tools, example projects or the full animation kit. Copying only that script would create a broken and misleading renderer package.

Hindi Explainer Studio therefore keeps the renderer path configurable through Settings and `config.json`.

## Default integration

The app's renderer setting points to:

```text
~/.claude/skills/line-boil/engine/build.py
```

On Windows, this resolves under the current user's home directory. Change the path in Settings if the renderer is installed elsewhere.

The engine interface expected by the app includes these commands (confirm them against your installed version):

```text
new <slug>
new <slug> --wide
voice <slug> ...
check <slug>
stills <slug> <times>
video <slug>
thumb <slug>
sheet <slug>
chapters <slug>
```

The dashboard calls the configured script with the local Python interpreter. The repo-local creative skills define the Hindi research and storyboard contracts; they do not replace the renderer's API reference.

## Hindi readiness test

Before rendering a full project, verify:

1. A Devanagari-capable font is available and included in the project/render environment.
2. Matras, half-letters, conjuncts, nukta characters and punctuation render correctly.
3. Hindi narration can be recorded or generated with intelligible pronunciation.
4. The speech aligner supports Hindi. Test words containing conjuncts, numbers and English technical terms.
5. Subtitle timings are checked against the actual audio, not guessed from word count.
6. A 10–15 second scene can render with the chosen font and visual palette.
7. Audio loudness and music ducking preserve speech intelligibility.

If any of these fail, keep the renderer for graphics only and use an external Hindi audio/alignment workflow. Do not claim word-level Hindi subtitle support until it is proven.

## Future extraction

A fully self-contained renderer can later be vendored or implemented under this folder, with its own tests, fonts, API reference, browser runtime, audio tools and sample project. Until then, treat it as an explicit local dependency.
