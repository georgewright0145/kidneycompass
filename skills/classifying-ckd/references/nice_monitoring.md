# NICE monitoring frequency (reference for classifying-ckd)

Canonical source: `spec/guidelines/kdigo_2024_classification.md` (monitoring section) +
`spec/guidelines/nice_ng203_management.md`. Pending UK renal-clinician sign-off.

Plain-English summary of how often NICE suggests monitoring, keyed to the risk band and returned by
`engines/classify.py` as `monitoring_per_year`:

- **green** → about once a year (1/yr)
- **amber** → about once a year (1/yr)
- **orange** → about twice a year (2/yr)
- **red** → two or more times a year (2/yr; 3–4/yr at the most severe G4–G5 cells, encoded as 3)

> Flag for clinician review: confirm the exact NICE NG203 "number of times per year" table before pilot.
