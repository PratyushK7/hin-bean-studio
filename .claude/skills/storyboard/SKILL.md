---
name: storyboard
description: Turns an approved Hindi explainer script into a production-ready visual storyboard for code-generated documentary animation, charts, maps, timelines and sourced visual material.
---

# Storyboard skill

A storyboard is a communication plan. Each scene must make the narration easier to understand.

## Scene-design rules

- Start from the concept being explained, not from an animation trick.
- Pick the best visual form: causal diagram, process flow, comparison, timeline, map, chart, cross-section, system boundary, scale model, document close-up or restrained cinematic scene.
- Use code-generated graphics for transformations, relationships, quantities and sequences that benefit from exact timing or repeatability.
- Use real source imagery only when the image itself is evidence or provides necessary context. Record the source, date, rights/permissions and intended use.
- AI-generated visuals may be used for illustrative reconstructions, but never present them as photographs, archival records, data or documentary proof.
- No mascot characters, beans, random characters or decorative motion. Human figures may be used when a real person or a clearly labelled illustrative stand-in is relevant.
- Keep the frame composed around one visual point. Avoid clutter and text walls.
- Use labels only for essential names, units, places, dates and numbers. Hindi labels should be short and correctly typeset.
- Make every chart legible at phone size. Include units, baseline, source and data period where relevant.
- A map must have correct borders, labels, scale and context. Never invent a border or location.

## Timing and visual rhythm

- Every shot should have a clear start state, transformation and end state.
- Give key figures enough time to be read.
- A new visual beat should generally occur every 4–10 seconds; slower moments are acceptable when the information is dense.
- Do not change shots just to create artificial pace.
- A shot may contain several animation beats, but the viewer should never have to decode several new ideas at once.
- Match cuts and visual callbacks are useful when they clarify a relationship.

## Storyboard schema

Write `storyboard.json` as an array of objects:

```json
[
  {
    "id": "S01",
    "script_lines": [0, 1],
    "start_hint": "first spoken phrase",
    "duration_target_s": 6,
    "narrative_job": "establish the question",
    "visual_type": "diagram | chart | map | timeline | comparison | documentary | source-image",
    "description": "what the viewer sees and how it changes",
    "on_screen_text": ["short label"],
    "data_or_source_ids": ["C01"],
    "camera": "static | push | pan | cut | match",
    "transition": "cut | dissolve | match",
    "sound": "quiet pulse; no effect on the number reveal",
    "render_notes": "layout, scale, legibility and asset requirements"
  }
]
```

The schema is a planning contract. Adapt it to the renderer's actual scene API during implementation. Do not pretend the renderer automatically consumes this JSON unless an adapter has been built.

## Review before code

Check:
- Does every scene have a narrative job?
- Can the viewer understand the image without reading a paragraph?
- Are numbers and labels correct and sourced?
- Does the visual sequence explain the causal relationship?
- Are any visual metaphors likely to mislead?
- Are any source images presented out of context?
- Are transitions helping the story rather than distracting?

Deliver the storyboard and unresolved visual requirements before coding the shots.
