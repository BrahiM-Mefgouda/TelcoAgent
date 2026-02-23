# 📡 TelcoAgent
**Telecom-specific multilingual (English - Arabic) benchmark for evaluating Large Language Models (SLM) agents on troubleshooting workflows.**

This repository packages the **data + annotations + evaluation outputs** introduced in our paper: **“A Roadmap to Evaluating Multi-Lingual Telecom LLM Agents: A Benchmark” (2026)**

> **Core idea:** TelcoAgent does not only test whether a model can *answer telecom questions*.  
> It evaluates whether an **agent** can **operate like a telecom engineer assistant**:
> 1) infer the correct troubleshooting **intent**,  
> 2) execute the right **tool sequence** in the correct **order**,  
> 3) produce a final **resolution summary** that matches the gold outcome,  
> 4) and remain **stable** across variations of the same scenario family (blueprint).

---

## 🧭 Table of Contents
- [What’s inside](#-whats-inside)
- [Repository structure](#-repository-structure)
- [Alignment contract (1:1 mapping)](#-alignment-contract-11-mapping)
- [Data formats](#-data-formats)
  - [A) Blueprint YAML spec](#a-blueprint-yaml-spec)
  - [B) Benchmark JSON spec (TelcoAgent-Bench)](#b-benchmark-json-spec-telcoagent-bench)
  - [C) Evaluation JSON spec (TelcoAgent-Metrics)](#c-evaluation-json-spec-telcoagent-metrics)
- [Tool schema](#-tool-schema)
- [Metrics schema (IRA / MSC / EAP / SAS / RA)](#-metrics-schema-ira--msc--eap--sas--ra)
- [Blueprint-level stability (BRS / GPC-0 / GPC-1 / SD)](#-blueprint-level-stability-brs--gpc-0--gpc-1--sd)
- [Intent & blueprint coverage](#-intent--blueprint-coverage)
- [Minimal usage example](#-minimal-usage-example)
- [Auxiliary files](#-auxiliary-files)
- [Dataset notes (Data Card)](#-dataset-notes-data-card)
- [Citation](#-citation)
- [License](#-license)

---

## ✨ What’s inside
TelcoAgent contains **three aligned assets**:

1) **`BLUEPRINTS/`**  
   Blueprint templates (YAML) that define *scenario families* and constrain KPI sampling.

2) **`TelcoAgent-Bench/`**  
   Benchmark samples (JSON): bilingual engineer↔agent dialogues + **gold tool path** + **gold resolution**.

3) **`TelcoAgent-Metrics/`**  
   Evaluation outputs (JSON): per-sample model predictions + per-sample scores for intent/tools/resolution.

---

## 🗂 Repository structure

```text
.
├── BLUEPRINTS/
│   └── <INTENT>/*.yaml
├── TelcoAgent-Bench/
│   └── <INTENT>/<BLUEPRINT_ID>/*.json
└── TelcoAgent-Metrics/
    └── <INTENT>/<BLUEPRINT_ID>/*.json
