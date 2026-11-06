---
name: research
description: Researches Hindi explainer and documentary topics, verifies claims against reliable sources, and creates an auditable claim ledger and source register before scripting.
---

# Research skill

Research is not a search-results summary. The goal is a defensible explanation whose important claims can be traced to evidence.

## 1. Frame the research

Write:
- the central question;
- why the question matters to a general viewer;
- the likely misconception;
- the time period, geography and definitions that constrain the answer;
- what evidence would change the conclusion.

Separate what is known from what the video wants to argue.

## 2. Source hierarchy

Prefer, in order:
1. Original datasets, official statistics, legislation, court judgments, government or institutional documents, technical standards and primary records.
2. Peer-reviewed research papers, systematic reviews and meta-analyses.
3. University, scientific institution and recognised expert publications.
4. High-quality specialist journalism that links to primary evidence.
5. General media, explainers, social posts and forums only as leads, not final support for consequential claims.

Use more than one independent source for high-impact or disputed claims. Do not treat two articles that cite the same press release as independent corroboration.

## 3. Claim ledger

For each claim that may appear in narration, record:

| Field | Required content |
|---|---|
| Claim ID | Stable identifier such as C01 |
| Draft claim | One concise sentence |
| Claim type | Fact, estimate, interpretation, hypothesis or contested claim |
| Best source | Direct URL and publisher |
| Publication date | Date shown by the source |
| Verification | Full text, abstract, official summary, secondary report, or not verified |
| Limitation | Population, sample, date range, definition or caveat |
| Script status | Use, qualify, omit or investigate |

A source list without claim-to-source mapping is insufficient.

## 4. Verify quantitative claims

- Record the unit, denominator, geography, date range and definition.
- Check whether values are nominal or inflation-adjusted, per capita or total, annual or cumulative.
- Recalculate simple percentages and ratios independently.
- Never compare incompatible measurements.
- Avoid false precision. Round only when the underlying source and the explanation justify it.
- For charts, retain the raw source data and calculation method.

## 5. Verify scientific and medical claims

- Prefer original papers and systematic reviews.
- Distinguish correlation from causation, animal models from human outcomes, early evidence from established practice, and relative risk from absolute risk.
- Never overstate one study as consensus.
- If the full text is unavailable, say whether the abstract or a secondary summary was checked.
- For medical topics, include a concise scope note and avoid diagnosing or prescribing.

## 6. Verify history, politics and conflict

- Use primary documents and serious scholarship.
- Identify whose perspective a record represents.
- Distinguish documented events from disputed motives or causal interpretations.
- Date-stamp current facts and rapidly changing figures.
- Avoid false balance: represent evidentiary strength, not just the number of people holding a view.

## 7. Final research package

Write `research.md`, `sources.md` and `claims.json` (or CSV). Mark unresolved issues explicitly. Do not silently turn an uncertain claim into confident narration. If a key claim remains unverified, pause scripting or remove it.
