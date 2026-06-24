# DeepSedHg figure-generation code

This repository contains the Python scripts, plotting data, map resources, and reference outputs used to generate Figures 1-8 for the manuscript **"The Global Database of Deep-time Sedimentary Mercury Concentrations and Isotope Compositions (DeepSedHg)"**.

DeepSedHg is a global compilation of published sedimentary mercury (Hg) concentrations and Hg isotope records spanning approximately 2.7 billion years of Earth history. Version 1.0 contains 28,264 sample-level records compiled from 199 peer-reviewed publications.

## Repository contents

| Directory | Main script | Input files | Output | Description |
| --- | --- | --- | --- | --- |
| `Figure1` | `Figure1.py` | None | `Figure1.png` | Overall database structure |
| `Figure2` | `Figure2.py` | `Figure2_data.xlsx` | `Figure2.png` | Publication and record accumulation through time |
| `Figure3` | `Figure3.py` | `Figure3_data.xlsx` | `Figure3.png` | Modern geographic and latitudinal coverage |
| `Figure4` | `Figure4.py` | `Figure4_data.xlsx` | `Figure4.png` | Latitudinal distribution across geological eras |
| `Figure5` | `Figure5.py` | `Figure5_data.xlsx`, `Maps/` | `Figure5.png` | Phanerozoic paleogeographic distribution |
| `Figure6` | `Figure6.py` | `Figure6_data.xlsx`, `Geo_Time.xlsx` | `Figure6.png` | Temporal Hg concentration and isotope records |
| `Figure7` | `Figure7.py` | `Figure7_data.xlsx` | `Figure7.png` | Frequency distributions of Hg concentration and isotope parameters |
| `Figure8` | `Figure8.py` | `Figure8_data.xlsx` | `Figure8.png` | Relationships among Hg isotope parameters |

Each script uses relative paths and should be run from its own figure directory. Running a script writes or replaces the corresponding `FigureX.png` file in that directory.

## Software environment

The figures were generated with Python 3.11.5. The tested package versions are listed in `requirements.txt`.

Create and activate a dedicated environment, then install the dependencies:

```bash
conda create -n deepsedhg python=3.11.5
conda activate deepsedhg
pip install -r requirements.txt
```

Cartopy depends on compiled geospatial libraries. If installation with `pip` fails, install Cartopy from `conda-forge` before installing the remaining requirements:

```bash
conda install -c conda-forge cartopy=0.24.1 shapely=2.1.0
pip install -r requirements.txt
```

## Running the scripts

For example, to reproduce Figure 6:

```bash
cd Figure6
python Figure6.py
```

Use the same pattern for the other figures:

```bash
cd Figure1
python Figure1.py
```

```bash
cd Figure8
python Figure8.py
```

## Dataset

The full DeepSedHg v1.0 database is distributed separately through Zenodo:

<https://doi.org/10.5281/zenodo.20713398>

The figure-level Excel files in this repository contain only the processed plotting inputs required to reproduce the published figures. The primary database should be obtained from Zenodo.

## Paleogeographic map attribution

Figure 5 uses paleogeographic map files exported with GPlates and based on the PALEOMAP reconstruction framework described in the manuscript. Users should cite:

Scotese, C. R. (2021). An Atlas of Phanerozoic Paleogeographic Maps: The Seas Come In and the Seas Go Out. *Annual Review of Earth and Planetary Sciences*, 49, 679-728. <https://doi.org/10.1146/annurev-earth-081320-064052>

The map resources remain subject to the terms and attribution requirements of their original providers. Their redistribution status must be confirmed before the repository is made public.

## Authors

- Yuchen Yang
- Songjing Li
- Wang Zheng
- Yi Liu
- Jiubin Chen
- Ruoyu Sun

Correspondence: Ruoyu Sun, Tianjin University (`ruoyu.sun@tju.edu.cn`).

## License

A software license must be added before public release. The recommended choice for the Python code is the MIT License. Plotting data and third-party map resources may require separate licensing and attribution statements.
