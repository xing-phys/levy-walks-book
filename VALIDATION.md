# Validation record

Validated on 2026-10-20.

- Quarto 1.10.18 builds the complete multipage HTML book and a 90-page combined PDF from one source tree.
- Ten teaching chapters, an unnumbered preface, a bibliography, and two appendices render successfully.
- `python3 scripts/check_book.py` passes for all 14 HTML pages: local links and fragments, source equation/section/figure references, citation keys, figure assets, the PDF download, and `.nojekyll`.
- All 43 bibliography records were audited. All 42 DOIs resolve to the intended papers with matching publication metadata; all 13 arXiv pages and both direct primary PDF links were checked. `data/source-audit.json` records the lookup evidence and registry exceptions.
- `julia scripts/check_numerics.jl` passes 1,214 checks, including path support, terminal-flight observation, seeded reproducibility, survival probabilities, and an independent exact exponential-renewal MSD benchmark.
- The Julia experiments record parameters, seeds, sample counts, and software version in `data/metadata.toml`. Five original figure pairs include vector PDFs and PNGs.
- Representative PDF equations, worked solutions, figures, citations, and the coverage table were visually inspected. Chapter/equation/figure numbering was checked after removing a preface override. A bounding-box scan found no text extending outside the expected horizontal page margins.
- The HTML home page and rendered mathematics were inspected using an isolated headless Chrome preview. MathJax produced 157 equation containers with no error elements in the scaling chapter.

Scientific qualifications are included in the text: fresh versus stationary initialization, independent velocity redraw versus mandatory reversal, finite-time corrections, trajectory censoring, and the limits of experimental evidence. These checks do not constitute external peer review.

To repeat the principal checks:

```sh
quarto render
python3 scripts/check_book.py
julia scripts/check_numerics.jl
```

GitHub Actions repeats the complete publication build and artifact checks before deploying GitHub Pages. Generated `_site/` output is excluded from the source history.
