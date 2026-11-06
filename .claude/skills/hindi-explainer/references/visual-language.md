# Visual language: hybrid documentary graphics

## Design intent

The channel should feel like a premium editorial documentary made with a small, precise motion-design team. The visual language is a hybrid:

1. **Code-generated graphics are the default** for explanations: diagrams, charts, timelines, maps, process flows, system models, comparisons, labels, counters, scale models and animated equations.
2. **Sourced documentary material supports the explanation** when the real place, object, person, document, photograph or footage matters to the story.
3. **Cinematic illustrative scenes** can establish mood or scale, but must never masquerade as documentary evidence.
4. **Typography and sound** guide attention; they do not substitute for a clear explanation.

Do not use recurring mascot characters. Human figures are appropriate when the subject requires them or when a neutral, clearly illustrative figure helps explain scale or action.

## Palette

Use a restrained editorial palette, adapted to the actual renderer's supported colours:

- Deep navy / ink for structure and primary text.
- Warm off-white for clean backgrounds.
- Muted slate for secondary information.
- Ochre / gold for key emphasis and important numbers.
- Coral for warnings, friction, risk or a negative outcome.
- Teal / cyan for systems, data, movement or a contrasting category.

Use one dominant background per scene and no more than two emphasis colours at once. If the renderer only exposes a fixed palette, preserve semantic colour roles through the available constants rather than patching its engine blindly.

## Composition

- One dominant idea per frame.
- Strong hierarchy: focal object, explanatory relation, concise label, supporting context.
- Use grid alignment and consistent margins.
- Keep important content inside platform-safe areas.
- Leave negative space for Hindi captions and labels.
- Never solve a layout problem by shrinking all text.
- Use a consistent title/label hierarchy and avoid decorative font combinations.
- Verify Devanagari glyph coverage, matras, conjuncts and punctuation in actual rendered output.

## Programmatic visual grammar

Use the right graphic for the problem:

| Explanation need | Preferred visual |
|---|---|
| Sequence or change over time | Animated timeline |
| Cause and effect | Causal chain or flow diagram |
| Scale or proportion | Common-baseline comparison, scaled objects |
| Geography | Correctly sourced map with highlighted route/region |
| Quantitative change | Chart with visible axes, units and source |
| Internal mechanism | Cutaway, exploded view or labelled schematic |
| Competing explanations | Split-screen or evidence matrix |
| Network or institution | Node-link diagram with named roles |
| Abstract process | Carefully labelled visual metaphor |
| Documentary event | Verified photographs, maps, records or contextualised footage |

Charts should be built from data arrays, not manually improvised shapes, whenever numerical accuracy matters. Keep the source data and transformation in the project folder.

## Real imagery and rights

- Record the URL, creator/publisher, date and licence/permission for each sourced image or clip.
- Prefer public-domain or appropriately licensed assets.
- Respect source terms and attribution requirements.
- Do not remove watermarks or imply rights that have not been established.
- A screenshot of a website, chart or document must retain enough context to avoid misleading viewers.
- AI-generated illustrations and reconstructions must not be described as actual photographs, archival footage or original records.

## Motion

- Motion should reveal, compare, connect or focus.
- Use restrained camera moves and purposeful transitions.
- Animate the data or mechanism itself where possible, rather than adding arbitrary movement to the whole frame.
- Give viewers enough time to read every label.
- Use holds at important conclusions.
- Avoid constant zooms, parallax on every layer, gratuitous particles and sound effects on every cut.

## Typography and subtitles

- Keep on-screen labels short. Use Hindi when the audience benefits from it; preserve standard scientific symbols and units.
- Use English terms alongside Hindi only when the term is commonly recognised or the translation would be less clear.
- Subtitle tracks should be uploaded separately as SRT where possible. Burned-in captions are an optional design choice, not a substitute for accessible captions.
- Test subtitle glyph rendering and word timing with actual Hindi narration before producing a full episode.
