---
name: thumbnail
description: Designs accurate, high-contrast documentary thumbnails for Hindi explainers and renders them using the project's code-based visual system.
---

# Documentary thumbnail skill

The thumbnail should communicate the topic and the central tension in a fraction of a second. It must be accurate, specific and visually simple.

## Process

1. Read the final Hindi script, source notes, title and current storyboard.
2. Generate three distinct concepts, each with a clear visual trigger: curiosity, consequence, scale, mystery or comparison.
3. Rank them and explain why each is relevant to the actual video.
4. Let the user choose a concept when the interface asks for a selection.
5. Implement the chosen thumbnail using the renderer's supported code-drawing or asset pipeline.
6. Render it at 1280x720 for long-form and the channel's chosen vertical cover size for Shorts.
7. Inspect a small preview, crop and safe areas. Check the actual image, not just the source code.

## Design rules

- One dominant subject: object, map, chart, document, person or mechanism that identifies the video.
- Two to four words at most, preferably concise Hindi in Devanagari when it reads naturally.
- Strong focal hierarchy and generous negative space.
- A restrained palette with one strong accent.
- Use a real person's image only when relevant and contextually accurate.
- Do not use a misleading expression, fake quote, fabricated chart, false before/after or unrelated visual.
- Avoid stock-photo collage, tiny text, excessive arrows, random circles, emoji, multiple competing faces and clickbait phrases.
- A thumbnail is not a summary slide. It is a precise visual promise.

## Accuracy test

- **Subject test:** hide the text. Can the viewer identify the topic or the central object?
- **Promise test:** hide the image. Do the words accurately describe the question or consequence explored?
- **Truth test:** does the full thumbnail imply something the video does not establish?
- **Small-size test:** is the focal subject and text still legible at mobile feed size?
- **Cultural/language test:** is the Hindi natural, spelled correctly and fully rendered?

Keep the old thumbnail as a backup before replacing it. Update the YouTube packaging sheet to match the final rendered image. Do not upload from this skill.
