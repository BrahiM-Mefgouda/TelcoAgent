# 📡 TelcoAgent-Bench
**Telecom-specific multilingual (English–Arabic) benchmark for evaluating language-model-based telecom agents on troubleshooting workflows.**

This repository accompanies the paper **“TelcoAgent-Bench: A Multilingual Benchmark for Telecom AI Agents”** and provides the benchmark assets, blueprint-driven data generation framework, and evaluation artifacts used to assess multilingual telecom AI agents.

> **Core idea:** TelcoAgent-Bench does not only test whether a model can answer telecom questions.  
> It evaluates whether an **agent** can:
> 1. infer the correct troubleshooting **intent**,
> 2. execute the correct **tool sequence** in the right **order**,
> 3. produce a final **resolution summary** aligned with the gold outcome, and
> 4. remain **stable** across variations of the same scenario family (**blueprint**).

---

## 🧭 Table of Contents
- [✨ What’s inside](#-whats-inside)
- [🗂 Repository structure](#-repository-structure)
- [🔗 Alignment contract (1:1 mapping)](#-alignment-contract-11-mapping)
- [📦 Data formats](#-data-formats)
  - [A) Blueprint YAML spec](#a-blueprint-yaml-spec)
  - [B) Benchmark JSON spec (TelcoAgent-Bench)](#b-benchmark-json-spec-telcoagent-bench)
  - [C) Evaluation JSON spec (TelcoAgent-Metrics)](#c-evaluation-json-spec-telcoagent-metrics)
- [🛠 Tool schema](#-tool-schema)
- [📏 Metrics schema (IRA / MSC / EAP / SAS / RA)](#-metrics-schema-ira--msc--eap--sas--ra)
- [📘 Blueprint-level stability (BRS / GPC-0 / GPC-1 / SD)](#-blueprint-level-stability-brs--gpc-0--gpc-1--sd)
- [📚 Intent and blueprint coverage](#-intent-and-blueprint-coverage)
- [📝 Dataset notes (Data Card)](#-dataset-notes-data-card)
- [📖 Citation](#-citation)

---

## ✨ What’s inside

TelcoAgent-Bench contains **three aligned assets**:

1. **`BLUEPRINTS/`**  
   Blueprint templates in YAML format. Each blueprint defines a telecom troubleshooting scenario family, including KPI constraints, scenario context, reference tool flow, and expected resolution logic.

2. **`TelcoAgent-Bench/`**  
   Benchmark samples in JSON format. Each sample contains a bilingual engineer–agent dialogue, a gold tool trajectory, flow alignment, and a gold final summary.

3. **`TelcoAgent-Metrics/`**  
   Evaluation artifacts in JSON format. These files store model predictions and benchmark scores for intent recognition, tool-flow alignment, resolution quality, and reliability.

---

## 🗂 Repository structure

```text
.
├── BLUEPRINTS/
│   └── <INTENT>/
│       ├── <BLUEPRINT_ID>.yaml
│       └── ...
├── TelcoAgent-Bench/
│   └── <INTENT>/
│       └── <BLUEPRINT_ID>/
│           ├── sample_0001.json
│           ├── sample_0002.json
│           └── ...
├── TelcoAgent-Metrics/
│   └── <MODEL_NAME>/
│       └── <INTENT>/
│           └── <BLUEPRINT_ID>/
│               ├── sample_0001.json
│               ├── sample_0002.json
│               └── ...
├── README.md
└── LICENSE
```

---

## 🔗 Alignment contract (1:1 mapping)

Each benchmark sample is derived from exactly one blueprint, and each evaluation file corresponds to exactly one benchmark sample.

```text
BLUEPRINTS/<INTENT>/<BLUEPRINT_ID>.yaml
        ↓
TelcoAgent-Bench/<INTENT>/<BLUEPRINT_ID>/sample_k.json
        ↓
TelcoAgent-Metrics/<MODEL_NAME>/<INTENT>/<BLUEPRINT_ID>/sample_k.json
```

This 1:1 mapping enables:

- reproducible scenario generation,
- exact tool-flow evaluation,
- blueprint-level aggregation, and
- reliability analysis across repeated scenario variants.

---

## 📦 Data formats

### A) Blueprint YAML spec

A blueprint defines one troubleshooting **scenario family** for a given intent. It constrains KPI ranges, scenario logic, tool ordering, and the expected resolution pattern.

#### Example

```yaml
intent: downlink_throughput_drop
blueprint_id: DTD_01
language_support: [en, ar]

scenario:
  category: ran_performance
  description: "Persistent downlink throughput degradation in a congested urban cell"

kpi_constraints:
  prb_utilization: [0.75, 0.95]
  dl_throughput_mbps: [4, 15]
  bler: [0.02, 0.07]

gold_tool_flow:
  - oss_query
  - kpi_timeseries
  - recommend_param_change

resolution_template:
  root_cause: "High resource utilization causing throughput degradation"
  corrective_action: "Recommend scheduler or parameter optimization"
  ticket_required: false
```

#### Main fields

- `intent`: troubleshooting intent label
- `blueprint_id`: unique blueprint identifier
- `language_support`: supported languages
- `scenario`: scenario category and description
- `kpi_constraints`: valid KPI sampling ranges
- `gold_tool_flow`: ordered reference tool sequence
- `resolution_template`: expected diagnosis and action structure

---

### B) Benchmark JSON spec (TelcoAgent-Bench)

A benchmark file stores one bilingual engineer–agent troubleshooting case.

#### Example

```json
{
  "sample_id": "DTD_01_0001",
  "intent": "downlink_throughput_drop",
  "blueprint_id": "DTD_01",
  "language": "en",
  "problem_statement": "Users in sector A report a significant drop in downlink throughput since this morning.",
  "conversation": [
    {
      "role": "engineer",
      "text": "We are observing degraded download speed in sector A."
    },
    {
      "role": "agent",
      "text": "I will first query the OSS to inspect cell KPIs."
    }
  ],
  "tool_calls": [
    "oss_query",
    "kpi_timeseries",
    "recommend_param_change"
  ],
  "flow_alignment": [
    {"turn_id": 2, "gold_step": 1, "tool": "oss_query"},
    {"turn_id": 4, "gold_step": 2, "tool": "kpi_timeseries"},
    {"turn_id": 6, "gold_step": 3, "tool": "recommend_param_change"}
  ],
  "gold_summary": {
    "en": "The cell shows high PRB utilization and reduced downlink throughput. A scheduler-related parameter adjustment is recommended.",
    "ar": "تظهر الخلية استخداماً مرتفعاً لموارد PRB مع انخفاض في معدل النقل الهابط. يُوصى بإجراء تعديل على إعدادات الجدولة."
  }
}
```

#### Main fields

- `sample_id`: unique sample identifier
- `intent`: gold troubleshooting intent
- `blueprint_id`: source blueprint
- `language`: primary sample language
- `problem_statement`: initial issue trigger
- `conversation`: engineer–agent interaction
- `tool_calls`: gold tool path
- `flow_alignment`: turn-to-step mapping
- `gold_summary`: expected bilingual final resolution

---

### C) Evaluation JSON spec (TelcoAgent-Metrics)

An evaluation file stores the model output and benchmark scores for one sample.

#### Example

```json
{
  "sample_id": "DTD_01_0001",
  "model_name": "qwen-3-8b",
  "predicted_intent": "downlink throughput issue due to congestion",
  "predicted_tool_calls": [
    "oss_query",
    "kpi_timeseries",
    "recommend_param_change"
  ],
  "predicted_summary": "The throughput drop is caused by heavy utilization in the affected cell. A parameter optimization action is recommended.",
  "scores": {
    "IRA": 0.94,
    "MSC": 1.00,
    "EAP": 1.00,
    "SAS": 1.00,
    "RA": 0.91
  }
}
```

#### Main fields

- `sample_id`: linked benchmark sample
- `model_name`: evaluated model
- `predicted_intent`: free-text predicted intent
- `predicted_tool_calls`: model-generated tool trajectory
- `predicted_summary`: final resolution summary
- `scores`: per-sample evaluation scores

---

## 🛠 Tool schema

TelcoAgent-Bench evaluates agents in a mixed tool environment composed of **core tools** and **distractor tools**.

### Core tools

| Tool | Description |
|---|---|
| `oss_query` | Retrieves RAN KPI details for a cell and time window |
| `kpi_timeseries` | Returns time-series values for a target KPI |
| `recommend_param_change` | Produces optimization or corrective parameter recommendations |
| `create_ticket` | Creates an OSS/NOC issue ticket with issue summary and actions |
| `push_config` | Simulates a configuration push |
| `neighbor_audit` | Checks neighboring cells for misconfiguration or anomalies |
| `coverage_map` | Generates coverage information for coverage-hole, beam, or interference analysis |

### Distractor tools

| Tool | Description |
|---|---|
| `subscriber_insight` | Retrieves subscriber usage profiles for a specific cell |
| `device_cap_lookup` | Returns UE/device capability information |
| `sla_policy_fetch` | Retrieves SLA compliance policies |
| `traffic_forecast` | Provides predicted traffic load |
| `complaint_trend_analysis` | Returns complaint and sentiment trends |
| `spectrum_license_info` | Retrieves spectrum licensing or regulatory information |

> Distractor tools are valid tools but are not required for solving the corresponding gold task.  
> They are used to test whether an agent can avoid unnecessary actions.

---

## 📏 Metrics schema (IRA / MSC / EAP / SAS / RA)

TelcoAgent-Bench evaluates each agent along multiple complementary dimensions.

### 1) IRA — Intent Recognition Accuracy
Measures semantic agreement between the predicted intent and the gold intent.

- free-text intent prediction is allowed,
- evaluated using embedding-based semantic similarity.

### 2) MSC — Mandatory Step Coverage
Measures whether the required gold actions appear in the correct order.

- based on ordered overlap with the gold tool path,
- rewards completion of mandatory troubleshooting steps.

### 3) EAP — Extra Action Penalty
Penalizes unnecessary extra tool calls.

- high EAP indicates efficient tool usage,
- low EAP indicates overuse of irrelevant tools.

### 4) SAS — Sequence Alignment Score
Combines process compliance and efficiency:

```text
SAS = MSC × EAP
```

A strong SAS indicates that the agent followed the correct ordered workflow while avoiding unnecessary tools.

### 5) RA — Resolution Accuracy
Measures semantic similarity between the predicted final summary and the gold final summary.

- evaluates reporting quality,
- reflects whether the final diagnosis and corrective action are correctly captured.

---

## 📘 Blueprint-level stability (BRS / GPC-0 / GPC-1 / SD)

TelcoAgent-Bench also evaluates **stability across repeated variants** of the same blueprint.

### GPC-0
Exact gold-path consistency.

- percentage of samples where the predicted tool path exactly matches the gold path.

### GPC-1
Near-match gold-path consistency.

- allows small deviations from the gold path,
- typically computed with edit-distance tolerance.

### SD — Sequence Dispersion
Measures variability across predicted tool sequences for samples generated from the same blueprint.

- low SD indicates stable behavior,
- high SD indicates inconsistent reasoning or tool use.

### BRS — Blueprint Reliability Score
A weighted reliability score that combines:

- exact consistency (`GPC-0`),
- tolerant consistency (`GPC-1`), and
- stability (`1 - SD`).

```text
BRS = α1 · GPC-0 + α2 · GPC-1 + α3 · (1 - SD)
```

where `α1 + α2 + α3 = 1`.

BRS is intended to measure whether an agent behaves **reliably and repeatably** across scenario variations belonging to the same blueprint family.

---

## 📚 Intent and blueprint coverage

The benchmark spans telecom troubleshooting scenarios across the following operational categories:

- **RAN Performance**
- **Coverage / Interference**
- **Mobility / Handover**
- **Resource Management**
- **Fault Detection**
- **5G Slicing**
- **Configuration / Optimization**

Each category is instantiated through structured blueprints that define KPI-constrained scenario families and reference troubleshooting flows.

---

## 📝 Dataset notes (Data Card)

- **Domain:** Telecom troubleshooting and operational workflows  
- **Languages:** English and Arabic  
- **Format:** Blueprint YAML, benchmark JSON, evaluation JSON  
- **Interaction type:** Simulated engineer–agent dialogues  
- **Evaluation focus:** Intent recognition, ordered tool use, final resolution quality, and blueprint-level reliability  
- **Intended use:** Research and benchmarking of multilingual telecom AI agents  
- **Not intended for:** Direct deployment in live operational environments without additional validation and safeguards  

---

## 📖 Citation

If you use this repository in your research, please cite the accompanying paper.

```bibtex
@misc{bariah2026telcoagentbench,
  title={TelcoAgent-Bench: A Multilingual Benchmark for Telecom AI Agents},
  author={Lina Bariah and Brahim Mefgouda and Farbod Tavakkoli and Enrique Molero and Louis Powell and M{\'e}rouane Debbah},
  year={2026},
  note={Manuscript}
}
```

---
