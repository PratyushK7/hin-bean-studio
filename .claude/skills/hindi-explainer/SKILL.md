---
name: hindi-explainer
description: Produces serious, research-led Hindi explainers and documentaries using a hybrid of code-generated motion graphics, diagrams, maps, timelines, charts and carefully sourced visual evidence. Use whenever making or revising a Hindi explainer video, Short, documentary script, storyboard or production package for this channel.
---

# Hindi Explainer — production master skill

A clear question, researched and explained in natural Hindi, becomes a finished video. The channel is serious, accessible and evidence-led. It is not a comedy cartoon channel. Do not use beans, mascots, gags, slapstick or forced "what if" framing.

## Editorial identity

- **Language:** Hindi-first. Write narration in Devanagari. Use standard English technical terms in Latin script only when that is genuinely how an educated Hindi speaker would say them or when translation would reduce clarity. Define unfamiliar terms the first time.
- **Tone:** composed, intelligent, curious, precise and human. Never sound like a news anchor shouting headlines, a coaching-centre lecturer, a conspiracy channel or a translated textbook.
- **Promise:** viewers should understand a mechanism, event, system or argument more clearly than before. Do not merely list facts.
- **Audience:** curious Hindi-speaking general audience. Assume no specialist background; do not assume low intelligence.
- **Visual identity:** premium editorial documentary. Combine custom code-generated motion graphics with maps, charts, timelines, labelled diagrams, source-derived visual evidence and restrained cinematic compositions.
- **Default formats:** 9:16 Shorts, 30–60 seconds; 16:9 long-form, normally 8–15 minutes. Let the subject determine the final length.

## Non-negotiable workflow

1. **Define the question.** Write one sentence describing what the viewer will understand by the end. Identify the likely misconception or missing mental model.
2. **Research before scripting.** Use the `research` skill. Create a claim ledger and source list. Do not write confident narration around facts that have not been checked.
3. **Choose the explanatory spine.** Select the smallest useful model: a causal chain, timeline, map, comparison, feedback loop, system diagram, case study or evidence-based argument.
4. **Write Hindi narration.** Use `hindi-script`. The narration must sound natural when spoken aloud. Avoid literal translations and ornamental vocabulary.
5. **Storyboard.** Use `storyboard`. Every scene must perform an explanatory job. Use code-generated graphics when they make relationships or change over time easier to see.
6. **Plan visual assets.** Use the `visual-language` reference. Mark every external image, map, clip, data point and archival object with its source and permission/licensing status. Never present generated illustration as archival evidence.
7. **Build the voice track.** Use `voiceover`. Prefer a clean human Hindi recording unless a tested Hindi TTS voice is deliberately selected. Never assume an English TTS or aligner supports Hindi.
8. **Implement animation.** Use the installed renderer's actual API and inspect its current examples before drawing. Keep source code deterministic and split long videos into chapter or scene files.
9. **Validate.** Run the renderer's check and still-image commands. Inspect one contact sheet first, then inspect problem frames. Check factual labels, Devanagari glyph shaping, subtitles, contrast, cropping and temporal sync.
10. **Package.** Create Hindi title, description, tags, chapters, subtitles, thumbnail and source notes. Do not upload without explicit user approval.
11. **Handover.** State the project path, actual rendered duration, unresolved claims, source coverage and files created.

## Output contract

A video project should contain, where relevant:

- `research.md` — question, context and research summary.
- `sources.md` — source register with URLs, publishers, dates and access/verification notes.
- `claims.csv` or `claims.json` — claim-level evidence ledger.
- `script.json` — one spoken sentence per entry for renderer compatibility.
- `script-hi.md` — readable Hindi script with chapter/scene markers.
- `storyboard.json` — structured scene plan.
- `chapters.json` — long-form chapter starts mapped to script sentence indices.
- `web/cast.js` — reusable visual components, typography and scene helpers; no mascot requirement.
- `web/shots.js` or `web/shots/chNN.js` — code-drawn visual scenes.
- `audio/voice.wav` — local recording when supplied/generated.
- `<slug>.srt` — Hindi subtitles.
- `<slug>-thumbnail.png` — final thumbnail.
- `<slug>-youtube.txt` — title, description, tags, chapters and upload settings.

Do not invent that a file exists. If the installed renderer or its asset pipeline does not support a requested asset, report the limitation and offer a compatible code-drawn alternative.

## Shorts vs long-form

- For a Short, start with the viewer's question or a surprising but verifiable fact. Explain one mechanism only. Land a specific conclusion. No rapid-fire fact dump.
- For long-form, build a narrative argument: hook → context → mechanism/evidence → complication or counterargument → implications → conclusion. Use chapters to advance the argument, not merely to divide the runtime.
- A Short is not simply a clipped long-form segment. It needs its own opening, context and payoff.
- A long video should not be padded to hit an arbitrary duration. Stop when the argument is complete.

## Safety and epistemic discipline

- Distinguish fact, interpretation, estimate, hypothesis and speculation.
- Never invent sources, quotations, statistics, study results, dates, chart values or expert consensus.
- Cite primary sources where possible. When relying on a secondary source, say so in the production notes.
- For live or disputed issues, date-stamp the research and state what is not known.
- For medical, legal, financial and political topics, use extra care, show uncertainty and avoid prescriptive advice unsupported by authoritative guidance.
- Never remove a caveat from narration just because it weakens a dramatic hook.

## Before rendering

The script and storyboard are approval artifacts. Unless the user explicitly asks for fully autonomous production, show the Hindi script, central thesis, key sources and visual plan for approval before the expensive render. A successful render is not proof that the video is factually correct.
