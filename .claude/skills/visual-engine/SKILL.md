---
name: visual-engine
description: Implements explanatory visuals as deterministic JavaScript graphics and motion scenes using the configured renderer, with sourced maps/data and a hybrid documentary visual system.
---

# Visual engine skill

This skill turns an approved storyboard into maintainable, code-generated documentary graphics. It does not assume a particular drawing API: inspect the configured renderer's current API reference and example project before writing code.

## 1. Renderer discovery

- Read `config.json` if present; otherwise inspect the studio Settings/default configuration for the `engine` path.
- Open the renderer's current API reference, sample project and scene templates.
- Confirm supported canvas dimensions, image asset support, fonts, text rendering, paths, clipping, animation timing and export commands.
- Do not invent helper names. Use only APIs verified in the installed renderer.
- If the requested visual needs unsupported raster images, maps or typography, state the limitation and propose a supported alternative.

## 2. Choose the representation

Prefer code-generated visuals for:
- time series, comparisons and quantitative data;
- maps with sourced boundary/route data;
- process, causal and system diagrams;
- timelines and event sequences;
- labelled cutaways, cross-sections and exploded views;
- animated equations or step-by-step mechanisms;
- interface walkthroughs that can be recreated accurately.

Use sourced imagery when the real-world object, place, person or document is itself important evidence. Keep the source, licence and attribution record alongside the asset. Do not disguise an illustrative recreation as real footage.

## 3. Data-driven graphics

- Store source values in JSON/CSV, not only as hand-positioned drawing commands.
- Keep units, denominators, time periods, source IDs and any transformation formula.
- Separate data ingestion, visual mapping and animation.
- Use meaningful scales and honest baselines.
- Check every label, number, map marker and unit against the source register.
- Preserve source files and a reproducible transformation script.

## 4. Scene-code quality

- Keep shared drawing primitives in reusable modules.
- Keep scene code small and composable.
- Use deterministic values so rerenders are reproducible.
- Separate scene timing from the spoken script where the renderer supports word/phrase anchors.
- Do not hard-code many magic coordinates. Define layout constants and reusable grids.
- Use easing to clarify motion, not to decorate every object.
- Ensure the final pose holds long enough for the viewer to understand the result.
- Avoid rendering text as geometry when the renderer can typeset it correctly.

## 5. Hybrid asset policy

Use the following decision order:
1. Can a diagram or animation explain it more clearly than a photograph? Draw it in code.
2. Is the real source image itself evidence or necessary context? Use it with source/rights notes.
3. Is a visual reconstruction needed? Make it clearly illustrative and label it where ambiguity is possible.
4. Is the asset pipeline unsupported? Use a code-drawn alternative or explain the blocker.

Do not use generic stock footage as filler. Every external visual must support a specific sentence or claim.

## 6. Validation

Before final render:
- run the configured renderer's structural check;
- render stills from every scene or chapter;
- inspect one contact sheet before individual frames;
- verify Devanagari text shaping, units, source labels, chart scales and map boundaries;
- check contrast, safe areas, overlap and text duration;
- verify the visual matches the narration and claim ledger.

For long-form, split scene code by chapter when the renderer supports it. Render and review chapter by chapter to contain errors and reduce rework.
