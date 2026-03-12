# 🗂️ Working with Large OSM PBF Files

> Source: [Working with Large OSM PBF Files ( <https://copilot.microsoft.com/shares/qwUcEezWBgzzBZxmQmwC2>)](<https://copilot.microsoft.com/shares/qwUcEezWBgzzBZxmQmwC2>)

OpenStreetMap PBF files are highly compressed binary containers. They are
efficient on disk, but their uncompressed memory footprint can be an order of
magnitude larger. Understanding how PBFs behave is essential for building
reliable, reproducible pipelines.

## 🧠 Why PBFs Appear Small but Behave “Huge”

Running:

```sh
osmium fileinfo -e yourfile.osm.pbf
```

**reveals two important metrics**:

| Metric | Meaning |
| :-- | :-- |
| **Size (bytes)** | Actual compressed file size on disk |
| **Sum of buffer capacities (bytes)** | Maximum possible uncompressed size of all internal buffers |

For example:

| File | Size | Sum of buffer capacities |
| :-- | :--: | :-- |
| north-america-260304.osm.pbf | 18.7 | GB 235 GB |
| us-260304.osm.pbf | 11.7 GB | 156 GB |

This illustrates a critical point:

> A PBF may decompress to 10–20× its on‑disk size.
>
> Any tool that attempts to load the entire file into memory risks exhausting
RAM, even on high‑end machines.

## 🚫 What Not to Do

Avoid workflows that:

- fully decompress the PBF

- convert it to XML

- parse it with non‑streaming libraries

- rely on older OSMnx patterns without pyrosm

- attempt to build a global graph in memory

These approaches can easily require hundreds of gigabytes of RAM for a file that
is only 10–20 GB on disk.

## ✅ Recommended Approach: Stream, Filter, and Localize

To safely and efficiently work with large PBFs:

1. Use streaming extractors
    - Tools like:
      - osmium extract
      - pyrosm
      - OSMnx (when pyrosm is installed)
    - read only the relevant parts of the file instead of decompressing
    everything.

1. Operate on bounding boxes or polygons

    Extract only the region you need:

    ```sh
    osmium extract -b minlon,minlat,maxlon,maxlat input.pbf -o subset.pbf
    ```

    This keeps memory usage tiny and predictable.

1. Avoid global loads

    - Instead of loading an entire state or continent:

    - maintain a registry of PBF files

    - load only the file that contains the city or region of interest

    - extract a local subgraph on demand

    This pattern scales cleanly to national datasets.

## 🧩 Why This Matters for Reproducible Pipelines

Large PBFs are unavoidable when working at national or continental scale.
The key is to design workflows that:

- never require full decompression

- stream data in small chunks

- extract only what is needed

- avoid global merges

This ensures:

- low memory usage

- fast extraction

- predictable performance

- reproducible results across machines

## 📌 Summary

- PBFs are small on disk but can decompress to 10–20× their size.

- Use streaming tools (osmium extract, pyrosm) to avoid RAM blowups.

- Always extract local subsets rather than loading entire files.

**This approach is essential for large‑scale, reproducible OSM pipelines.**
