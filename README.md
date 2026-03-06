# US Cities Distances

This repo is dedicated to build a list of connected U.S. cities for the joy of
studying graph theory and graph algorithms.

## Setup

This section explains how to prepare the environment to run the scripts if you
need to extend or reduce the scope of the datasets generated.

### Virtual Environment

For this research `conda-forge` was used as the virtual environment.

The requiered environment file is provided.

- To generate the virtual environment:

  - `conda env create -f environment.yml`

- To activate the virtual environment:
  - `conda activate us-cities`

## Licensing

This repository contains two separately licensed components:

### Software (MIT License)

All Python code in `/src` and supporting scripts are licensed under the MIT
License.

See the root `LICENSE` file.

### OpenStreetMap (OSM) Data (ODbL 1.0)

All datasets in `/data/osm`, including files derived from OpenStreetMap or
generated from OSM‑derived data, are licensed under the Open Database License
(ODbL) 1.0.

You must attribute:
    © OpenStreetMap contributors

See `/data/osm/LICENSE` for the full ODbL terms and `/data/ATTRIBUTION` for
attribution details.

### U.S. Census Data

All datasets in `/data/census`, including files derived from "City and Town
Population Totals" (Vintage 2024) dataset or generated from U.S. Census data,
are a work of the United States Government and is in the public domain under
17 U.S.C. §105. Attribution is not legally required, but is provided here as a
courtesy. **No endorsement by the U.S. Census Bureau is implied**.

All processed, cleaned, or transformed versions of Census data contained
in this directory are released into the public domain under the Creative
Commons Zero (CC0 1.0) Public Domain Dedication.
