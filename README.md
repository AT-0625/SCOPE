# Stellar Catalog & Observation Planning Engine (SCOPE)

**SCOPE** is a Python-based tool for stellar catalog management, observation planning, and data visualization. It allows users to inspect, modify, and filter catalogs, perform visibility checks, and generate plots for astrophysical analysis.

---

## Features

- Load, inspect, and update stellar catalogs through an interactive interface  
- Supports both `.csv` / `.fits` table formats for input and output  
- Perform coordinate conversion and observability checks from a chosen Earth location  
- Plan observations using full-night visibility filters based on local time and altitude  
- Generate multiple plot types for catalog structure and observability analysis  
- Modular and menu-driven design with robust input validation  
- Save outputs as `.csv` or `.fits` tables, and `.png` / `.pdf` plots  

---

## Included files

- `SCOPE.ipynb`: Interactive notebook version for step-by-step execution  
- `SCOPE.py`: Clean Python script version for direct use

---

## Demo Data Files

This repository includes one demo stellar catalog in both `.csv` and `.fits` formats:

- `SCOPE_StellarCatalog.csv` / `SCOPE_StellarCatalog.fits`: Contains data such as Right Ascension, Declination, Apparent Magnitude, Spectral Type, etc.

This file serves as input data for the simulations. Its specific purpose corresponds to the information conveyed by its filename, and the code structure reflects how it is utilized.

> **Note:** `.fits` files are binary and cannot be previewed on GitHub. Download and open with `Astropy`, `fv` (FITS viewer), or other astronomy tools.

---

## Installation

No special installation required. Just clone the repo and run the script in your Python environment.

---

## Usage

- Open `SCOPE.ipynb` in Google Colab or Jupyter Notebook.  
- Run cells step-by-step.  
- Modify inputs as needed.  
- Alternatively, run `SCOPE.py` as a script in your local Python setup.  
- When prompted for data files, you may use either `.csv` or `.fits` table formats.

---

## Status

The current version reflects a completed code structure with support for both `.csv` and `.fits` table formats, awaiting formal validation.

---

## License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for details.

---

## Contact

Feel free to reach out via my GitHub profile.

