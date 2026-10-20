# Lévy Walks: a self-contained course

A Quarto web book on finite-speed anomalous transport for senior undergraduates and beginning graduate students, organized around Zaburdaev, Denisov, and Klafter, *Rev. Mod. Phys.* **87**, 483 (2015), [doi:10.1103/RevModPhys.87.483](https://doi.org/10.1103/RevModPhys.87.483).

Read the book at **https://xing-phys.github.io/levy-walks-book/**. The sidebar includes a combined PDF download. This independent companion contains original explanations, derivations, figures, Julia experiments, and worked exercises. It does not reproduce the review. The coverage appendix maps all review sections to chapters. The manuscript was developed with AI assistance; corrections are welcome through issues.

## Build and preview

Install [Quarto](https://quarto.org/) 1.10.18 (the version used here) or a compatible later version. A LuaLaTeX distribution is required for the PDF; `quarto install tinytex` supplies one. The checked-in figures and data let the book render without Julia or Python plotting dependencies.

```sh
quarto render
python3 scripts/check_book.py
quarto preview --no-browser
```

The render produces multipage HTML in `_site/` and `_site/levy-walks-book.pdf`. Quarto prints the local preview URL; previews can choose a free port. `quarto render --to html` builds only the website, and `quarto render --to pdf` builds only the combined PDF. A format-specific build cleans the output directory by default; add `--no-clean` to preserve an existing output in the other format. Use `quarto render` for a complete publication build, and avoid concurrent renders in the same project.

## Reproduce the numerical figures

Julia uses only standard libraries; no package installation is needed. The scripts set explicit seeds and write metadata beside their CSV output.

```sh
julia scripts/check_numerics.jl
julia scripts/simulate.jl
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements-figures.txt
.venv/bin/python scripts/plot_figures.py
```

Numerical sampling and plotting are separate so that Python is used only for static scientific graphics. PDF/PNG figure pairs in `figs/` retain vector quality in the book PDF. The numerical chapter documents sample sizes, parameters, censoring, and interpretation limits.

## Organization

- `*.qmd`: course chapters, mathematical toolbox, and coverage appendix.
- `_quarto.yml`: book order, HTML/PDF formats, metadata, and GitHub URLs.
- `assets/refs-*.bib`: verified bibliography; APS CSL controls citation style.
- `assets/macros.sty` and `assets/mathjax-config.html`: equivalent PDF/HTML physics macros.
- `scripts/`, `data/`, `figs/`: reproducible computations and original figures.
- `.github/workflows/publish.yml`: complete HTML/PDF build, link validation, GitHub Pages deployment.

## Publication

GitHub Pages uses **GitHub Actions** as its publishing source. Pushing to `main` builds the book and deploys `_site/`. Pull requests build and validate without deploying. The workflow also supports manual dispatch. The repository source is versioned; generated site output stays outside Git. The live site offers source and issue links.

Original prose, diagrams, figures, and data are available under CC BY 4.0; code is MIT licensed. See `LICENSE` and `LICENSE-CODE`. Third-party scientific results and bibliographic metadata remain attributed to their original sources.
