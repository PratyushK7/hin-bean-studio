---
name: hindi-script
description: Writes and edits natural spoken-Hindi scripts for serious explainers, documentaries and Shorts, with clear narrative structure, accurate terminology and voiceover-friendly sentence timing.
---

# Hindi script skill

Write for the ear, not for the page. The result should sound like an intelligent Hindi-speaking person explaining something clearly to another curious person.

## Language and register

- Use Devanagari for Hindi narration.
- Use conversational, contemporary Hindi. Prefer familiar words over unnecessarily Sanskritised constructions.
- Keep widely used technical terms in English where that is clearer (for example, `डेटा`, `सिस्टम`, `एल्गोरिदम`, `इंटरनेट`). Explain a specialised term at first use.
- Do not switch randomly between Hindi and English. Keep the sentence structure Hindi even when a technical noun is English.
- Avoid literal translation, textbook prose, rhetorical filler, exaggerated adjectives and repetitive rhetorical questions.
- Read each sentence aloud mentally. Rewrite tongue-twisters and long clauses.

## Narrative clarity

Every script needs:
1. **A real question or tension.** It must be answerable by the video, not a vague curiosity hook.
2. **Context.** Give viewers enough information to understand why the question matters.
3. **Mechanism or evidence.** Explain how or why, not just what happened.
4. **A turn.** Introduce the detail that changes the viewer's initial mental model.
5. **A precise payoff.** Answer the opening question without claiming more than the evidence shows.

Use one main idea per sentence. Give unfamiliar concepts a short plain-language explanation before using them again.

## Hooks

Draft five candidate openings. Score each on:
- **Promise:** does it identify what the viewer will learn?
- **Specificity:** is the question concrete rather than generic?
- **Accuracy:** can the video genuinely deliver the statement?
- **Curiosity:** does it create a meaningful information gap?
- **Clarity:** can a general viewer understand it immediately?

Choose the strongest accurate hook, not the loudest one. Never start with unsupported superlatives, "आपको यकीन नहीं होगा", "दुनिया का सबसे बड़ा रहस्य" or fear-based claims the evidence cannot support.

## Voiceover-friendly construction

- Prefer short and medium sentences with deliberate pauses.
- Put the important noun or verb early.
- Avoid nested subordinate clauses and long lists.
- Spell units naturally for speech where necessary; the visual can show the exact symbol.
- Keep acronyms readable. Expand unfamiliar acronyms once.
- Use punctuation to guide delivery, not as decoration.
- Mark pronunciation notes for names, places, acronyms and uncommon words in a separate `pronunciation.md`, not in the spoken script.

## Shorts: 30–60 seconds

- One question, one core mechanism and one payoff.
- Establish the context quickly. Do not assume the viewer watched another video.
- Use a visual turn or comparison, not a fact dump.
- End with the answer or an implication, not a generic "like and subscribe" line.

## Long-form: 8–15 minutes by default

- Build around one central question or argument.
- Each chapter must add evidence, a mechanism, a counterpoint or an implication.
- Use transitions that make the logic between chapters explicit.
- Explain caveats in the same place the relevant claim is made.
- Remove repetition and any chapter that does not move the argument forward.

## Script output

Return:
- the final spoken script in Devanagari;
- a sentence-by-sentence numbered version for timing;
- pronunciation notes;
- source claim IDs beside non-obvious factual claims in the editorial copy (not spoken aloud);
- the five hook candidates and a short reason for the selected one.

Keep `script.json` as an array of one spoken sentence per entry. Store source annotations in separate files; do not put citation markup into the narration array.
