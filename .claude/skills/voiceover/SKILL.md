---
name: voiceover
description: Prepares, records or imports Hindi narration, checks pronunciation and aligns captions and timing to the actual audio for Hindi explainer videos.
---

# Hindi voiceover and timing

Hindi audio quality is a critical dependency. Never assume an English-oriented TTS voice, speech recogniser or forced aligner can handle Devanagari Hindi accurately.

## Preferred order

1. **Human Hindi recording:** use the user's clean narration when available. Record in a quiet room, close enough for a consistent voice level, with no clipping or strong room echo.
2. **Tested Hindi TTS:** use only a voice explicitly known to support Hindi and the intended register. Listen to a representative passage before generating a full episode.
3. **External voice production:** if neither path is adequate, prepare a pronunciation-ready script and use an approved Hindi-capable recording or TTS workflow.

Do not silently substitute an English voice.

## Audio preparation

- Preserve the source recording.
- Convert a working copy to mono PCM WAV at the sample rate required by the installed renderer.
- Remove long dead air only when it does not change the delivery.
- Use light, transparent noise reduction only if needed.
- Do not apply aggressive compression or denoising that damages consonants.
- Keep pronunciation notes outside the spoken script.

## Alignment

- Verify the language and script supported by the aligner before trusting word times.
- Inspect at least 30–60 seconds spanning ordinary Hindi, English technical terms, names, numbers and punctuation.
- Check sentence boundaries and subtitle timing manually.
- If the aligner fails on Hindi, use a Hindi-capable aligner or align by sentence/phrase. Report the lower precision honestly.
- Never create fake word-level timestamps from a fixed words-per-second formula.
- Actual voiceover duration, not estimated script length, determines final runtime.

## Captions

- Use Devanagari subtitles.
- Break captions at natural phrase and sentence boundaries.
- Preserve spoken wording, names and units.
- Check matras, conjuncts, punctuation, line breaks and glyph rendering in the final video.
- Ensure subtitle contrast and avoid covering charts, faces or essential labels.
- Keep an editable source transcript alongside the final SRT.

## Final audio QC

Listen to the entire rendered video. Check:
- clipped words or missing syllables;
- unnatural TTS pronunciation;
- inconsistent loudness;
- music masking speech;
- subtitle and narration mismatch;
- abrupt edits or silence;
- names, units and numbers spoken incorrectly.
