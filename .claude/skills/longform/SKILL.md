---
name: longform
description: Produces 16:9 Hindi documentary explainers with chaptered narrative, primary-source research, scene planning, code-generated motion graphics and verified subtitles.
---

# Long-form Hindi documentary explainer

Use the master `hindi-explainer`, `research`, `hindi-script` and `storyboard` skills.

## Format

- 16:9 landscape, 1920x1080 final delivery where the installed renderer supports it.
- Usually 8–15 minutes. Do not stretch a story to fit a runtime target.
- 5–9 chapters, typically 45–120 seconds each; chapter length follows the argument.
- One central question or thesis. Every chapter must add a new explanatory layer.

## Narrative architecture

1. **Cold open:** establish the question and why the answer is surprising or consequential. No long channel intro.
2. **Context:** define the subject, time range and relevant background.
3. **Mechanism:** explain how the system works or how events unfolded.
4. **Evidence:** use primary sources, meaningful data and visual demonstrations.
5. **Complication:** include limitations, exceptions, competing explanations or counter-evidence.
6. **Implications:** show what follows from the explanation.
7. **Conclusion:** answer the opening question precisely. Do not overclaim.

## Chapter design

Each chapter needs:
- a title that promises a specific piece of understanding;
- a clear opening question or transition;
- one main argument;
- evidence and a visual explanation;
- a takeaway that sets up the next chapter.

Write `chapters.json` with renderer-compatible sentence indices, then generate YouTube chapter timestamps from the real aligned narration. Confirm the first chapter begins at 0:00 and timestamps are ordered and valid.

## Scene and sound plan

Before writing scene code, create `<slug>-plan.md`:

| Chapter | Explanatory job | Visual form | Location / composition | Evidence IDs | Sound / music intent |
|---|---|---|---|---|---|

Use this plan to keep the visual language coherent while allowing the story to change visual form when the concept changes. A chapter may use multiple graphic scenes. Do not reuse the same shot layout simply to save time if it obscures the idea.

## Pacing

- Give viewers a visual beat when the idea changes, not at arbitrary intervals.
- Dense evidence needs enough screen time to be read.
- Switch between explanation modes: a map, a diagram, a chart, a source document, a real image, a comparison, a quiet hold.
- Avoid repeating narration as a text card.
- Music must support the narrative and remain subordinate to speech. Silence is valid.
- Avoid a noisy sound effect on every transition.

## Production sequence

1. Finish research and claim ledger.
2. Approve the thesis and chapter outline.
3. Write the Hindi script chapter by chapter.
4. Record/produce voiceover and verify Hindi timing.
5. Create storyboard and scene/sound plan.
6. Create visual components and chapter scene files. Use the renderer's actual documented API.
7. Render stills for each chapter and inspect a contact sheet.
8. Run structural checks; confirm no missing scenes, labels or assets.
9. Render the final video and inspect audio, captions, chapters and full-screen playback.
10. Generate a 1280x720 thumbnail and YouTube packaging.
11. Do not upload without explicit user approval.

## Long-form project contract

Alongside the common files, create:
- `chapters.json`
- `<slug>-chapters.txt`
- `<slug>-plan.md`
- `<slug>-sources.md`
- one scene source file per chapter where supported (for example `web/shots/ch01.js`).
