from pathlib import Path
from collections import defaultdict
import json

MODELS = [
    ("llama3:8b",          ["llama3:8b"]),
    ("qwen2:5:7b",         ["qwen2", "5:7b"]),
    ("granite3:1-moe:3b",  ["granite3", "1-moe:3b"]),
    ("granite3:3:8b",      ["granite3", "3:8b"]),
    ("gemma3:4b",          ["gemma3:4b"]),
    ("qwen3:8b",           ["qwen3:8b"]),
    ("qwen:7b",            ["qwen:7b"]),
    ("mistral:7b",         ["mistral:7b"]),
]

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.loads(f.read())

def get_nested(d, path, default=None):
    cur = d
    for k in path.split("."):
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur

def get_tool_pred_seq(d, model_path, lang):
    cur = d.get("Tool", {}).get("Predict", {})
    for k in model_path:
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    if not isinstance(cur, dict):
        return None
    return cur.get(lang, None)

def add_issue(bucket_counts, bucket_examples, key, fp, show_examples):
    bucket_counts[key] += 1
    if len(bucket_examples[key]) < show_examples:
        bucket_examples[key].append(str(fp))

def audit_all(eval_root: Path, show_examples=3):
    eval_files = sorted(eval_root.rglob("*.json"))
    total = 0

    missing = defaultdict(int)
    empty = defaultdict(int)
    examples_missing = defaultdict(list)
    examples_empty = defaultdict(list)

    for fp in eval_files:
        try:
            d = load_json(fp)
        except Exception:
            continue
        total += 1

        # =========================
        # QUERY
        # =========================
        for lang in ("En", "Ar"):
            v = get_nested(d, f"Query.{lang}", None)
            if v is None:
                add_issue(missing, examples_missing, f"Query.{lang}", fp, show_examples)
            elif isinstance(v, str) and not v.strip():
                add_issue(empty, examples_empty, f"Query.{lang}", fp, show_examples)

        # =========================
        # INTENT (ground truth)
        # =========================
        # Your structure has: Intent.GroundTruthKey, Intent.GroundTruthLabel, Intent.GroundTruth
        for k in ("Intent.GroundTruthKey", "Intent.GroundTruthLabel", "Intent.GroundTruth"):
            v = get_nested(d, k, None)
            if v is None:
                add_issue(missing, examples_missing, k, fp, show_examples)
            elif isinstance(v, str) and not v.strip():
                add_issue(empty, examples_empty, k, fp, show_examples)

        # =========================
        # INTENT predictions + scores (per model)
        # Handles your nested keys like qwen2 -> 5:7b
        # We'll check only if the model key exists in that file; otherwise count as missing for that model.
        # =========================
        for model_name, model_path in MODELS:
            # intent predict with list
            ip_en = get_nested(d, f"Intent.Predict.WithList.{'.'.join(model_path)}.En", None)
            ip_ar = get_nested(d, f"Intent.Predict.WithList.{'.'.join(model_path)}.Ar", None)
            if ip_en is None: add_issue(missing, examples_missing, f"Intent.Predict.WithList.{model_name}.En", fp, show_examples)
            elif isinstance(ip_en, str) and not ip_en.strip(): add_issue(empty, examples_empty, f"Intent.Predict.WithList.{model_name}.En", fp, show_examples)
            if ip_ar is None: add_issue(missing, examples_missing, f"Intent.Predict.WithList.{model_name}.Ar", fp, show_examples)
            elif isinstance(ip_ar, str) and not ip_ar.strip(): add_issue(empty, examples_empty, f"Intent.Predict.WithList.{model_name}.Ar", fp, show_examples)

            # intent score with list
            sc_en = get_nested(d, f"Intent.Score.WithList.{'.'.join(model_path)}.En", None)
            sc_ar = get_nested(d, f"Intent.Score.WithList.{'.'.join(model_path)}.Ar", None)
            if sc_en is None: add_issue(missing, examples_missing, f"Intent.Score.WithList.{model_name}.En", fp, show_examples)
            if sc_ar is None: add_issue(missing, examples_missing, f"Intent.Score.WithList.{model_name}.Ar", fp, show_examples)

        # =========================
        # TOOLS: GroundTruth + Predict per model/lang
        # =========================
        gt = get_nested(d, "Tool.GroundTruth", None)
        if gt is None:
            add_issue(missing, examples_missing, "Tool.GroundTruth", fp, show_examples)
        elif isinstance(gt, list) and len(gt) == 0:
            add_issue(empty, examples_empty, "Tool.GroundTruth", fp, show_examples)

        for model_name, model_path in MODELS:
            for lang in ("En", "Ar"):
                v = get_tool_pred_seq(d, model_path, lang)
                if v is None:
                    add_issue(missing, examples_missing, f"Tool.Predict.{model_name}.{lang}", fp, show_examples)
                elif isinstance(v, list) and len(v) == 0:
                    add_issue(empty, examples_empty, f"Tool.Predict.{model_name}.{lang}", fp, show_examples)

        # =========================
        # RESOLUTION: GroundTruth + Predict + Score
        # =========================
        for lang in ("En", "Ar"):
            vgt = get_nested(d, f"Resolution.GroundTruth.{lang}", None)
            if vgt is None:
                add_issue(missing, examples_missing, f"Resolution.GroundTruth.{lang}", fp, show_examples)
            elif isinstance(vgt, str) and not vgt.strip():
                add_issue(empty, examples_empty, f"Resolution.GroundTruth.{lang}", fp, show_examples)

        for model_name, model_path in MODELS:
            for lang in ("En", "Ar"):
                vp = get_nested(d, f"Resolution.Predict.{'.'.join(model_path)}.{lang}", None)
                if vp is None:
                    add_issue(missing, examples_missing, f"Resolution.Predict.{model_name}.{lang}", fp, show_examples)
                elif isinstance(vp, str) and not vp.strip():
                    add_issue(empty, examples_empty, f"Resolution.Predict.{model_name}.{lang}", fp, show_examples)

                vs = get_nested(d, f"Resolution.Score.{'.'.join(model_path)}.{lang}", None)
                if vs is None:
                    add_issue(missing, examples_missing, f"Resolution.Score.{model_name}.{lang}", fp, show_examples)

    print("Eval root:", eval_root)
    print("Total readable JSON files:", total)

    print("\n================ MISSING KEYS ================")
    for k, c in sorted(missing.items(), key=lambda x: -x[1]):
        if c > 0:
            print(f"{k}: {c}")
            for ex in examples_missing[k]:
                print("  ex:", ex)

    print("\n================ EMPTY VALUES ================")
    for k, c in sorted(empty.items(), key=lambda x: -x[1]):
        if c > 0:
            print(f"{k}: {c}")
            for ex in examples_empty[k]:
                print("  ex:", ex)

root = Path(__file__).resolve().parent
EVAL_ROOT = root / "Evaluation"
audit_all(EVAL_ROOT, show_examples=3)