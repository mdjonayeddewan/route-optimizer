# Comprehensive Project Report (LaTeX)

This folder contains a full, standard, informative report template tailored to the Route Optimizer project.

## Files
- `main.tex`: Full report source
- `references.bib`: Bibliography entries
- `figures/`: Place screenshots and diagrams here

## Build
From this folder, run:

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

If using latexmk:

```bash
latexmk -pdf main.tex
```

## Notes
- Replace placeholders on the title page (student name, IDs, course details, teacher details, submission date).
- Add your own screenshots in `figures/` and update figure paths in `main.tex`.
- Update GA parameter values in the experiment chapter if you change configs.
