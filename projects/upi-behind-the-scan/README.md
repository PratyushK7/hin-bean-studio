# UPI: Aapke ₹20 ke Peeche Kaun Kaam Karta Hai?

- **Format:** 16:9 long-form explainer
- **Target runtime:** 8–9 minutes (final timing depends on the human recording)
- **Language:** Roman-script Hinglish
- **Narration:** Creator's own voice; no English TTS fallback
- **Visual direction:** Hybrid documentary — code-generated transaction diagrams, motion graphics, and carefully selected documentary context.

## Central question
Jab aap UPI se kisi ko paise bhejte ho, toh phone screen ke peeche kaunse systems milkar payment complete karte hain?

## Editorial thesis
UPI ek app ya simple digital wallet nahi hai. Common bank-linked UPI payment mein app interface hota hai; PSPs, NPCI ka routing layer, aur sender/receiver banks milkar transaction ko authenticate, route, debit aur credit karte hain.

## Status
- [x] Research and claim ledger
- [x] Hinglish narration draft
- [x] Storyboard and visual plan
- [x] Thumbnail and YouTube metadata
- [ ] Script approval
- [ ] Human voice recording at `audio/hindi-voice.wav`
- [ ] Hindi/Hinglish font and alignment smoke test
- [ ] Renderer-specific shot implementation
- [ ] Render and quality review

## Important
The repo's line-boil renderer is a configurable local dependency, not bundled here. The storyboard is a plan, not a renderer-ready scene implementation. Do not run full rendering until the actual renderer API, font shaping, audio alignment and a 10–15 second test render are verified.

## Files
- `research.md`, `sources.md`, `claims.json`
- `script-hinglish.md`, `script.json`, `pronunciation.md`
- `storyboard.json`, `chapters.json`
- `thumbnail.md`, `youtube-metadata.md`, `recording-notes.md`
