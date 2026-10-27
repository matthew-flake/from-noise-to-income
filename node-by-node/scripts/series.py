"""Series runner for "Węzeł po węźle" / "Node by Node" (chapter 15).

Sends one ComfyUI workflow (API format) many times, once per row of a CSV file,
with a new random seed for every image.

Made for W11_series.api.json, but works with any single-prompt workflow whose nodes are titled
"Prompt" (positive prompt), "Sampler" (the KSampler) and has a Save Image node.
Your own workflow: title the nodes like that and use Workflow > Export (API).

Usage (ComfyUI must be running):
    python series.py ../workflows/api/W11_series.api.json topics.csv --per-topic 2

Output: ComfyUI/output/node_by_node/W11/<slug>_<n>_00001_.png

Standard library only. No data leaves your computer: the script talks to
http://127.0.0.1:8188 (change with --server). License: MIT, (c) Matthew Flake.
"""
import argparse, copy, csv, json, os, random, sys, urllib.error, urllib.request


def by_title(wf, *titles):
    return [nid for nid, n in wf.items() if n.get("_meta", {}).get("title") in titles]


def by_class(wf, *classes):
    return [nid for nid, n in wf.items() if n.get("class_type") in classes]


def find_prompt(wf):
    hits = by_title(wf, "Prompt")
    if not hits:
        hits = [nid for nid in by_class(wf, "CLIPTextEncode")
                if "positive prompt" in wf[nid].get("_meta", {}).get("title", "").lower()]
    if len(hits) != 1:
        sys.exit("This workflow has no single node titled 'Prompt' (it is probably a multi-scene workflow).\n"
                 "Run it from the ComfyUI window, or title your prompt node 'Prompt' and export again (Export (API)).")
    return hits[0]


def find_seed(wf):
    hits = by_title(wf, "Sampler", "Seed") or by_class(wf, "KSampler", "RandomNoise")
    if len(hits) != 1:
        sys.exit("Could not find exactly one sampler/seed node - title it 'Sampler' and export again.")
    return hits[0]


def save_names(wf):
    """Map every SaveImage node to a suffix, e.g. 'peony' -> '', 'peony_print' -> 'print'."""
    saves = by_class(wf, "SaveImage")
    if not saves:
        sys.exit("No Save Image node found.")
    bases = [os.path.basename(wf[s]["inputs"]["filename_prefix"]) for s in saves]
    common = os.path.commonprefix(bases)
    if common not in bases:
        common = common[:common.rfind("_") + 1] if "_" in common else ""
    return {s: (b[len(common):].strip("_"), os.path.dirname(wf[s]["inputs"]["filename_prefix"]))
            for s, b in zip(saves, bases)}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("workflow", help="workflow in API format (*.api.json)")
    ap.add_argument("csv", help="CSV with columns slug,subject")
    ap.add_argument("--per-topic", type=int, default=2, help="images per subject (default 2)")
    ap.add_argument("--server", default="http://127.0.0.1:8188")
    a = ap.parse_args()

    with open(a.workflow, encoding="utf-8") as f:
        base = json.load(f)
    if not all(isinstance(v, dict) and "class_type" in v for v in base.values()):
        sys.exit("This is not an API-format workflow. Use the files in workflows/api, or Workflow > Export (API).")
    p, s, saves = find_prompt(base), find_seed(base), save_names(base)
    seed_key = "seed" if "seed" in base[s]["inputs"] else "noise_seed"

    with open(a.csv, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows or not {"slug", "subject"} <= set(rows[0]):
        sys.exit("The CSV needs two columns: slug,subject")

    for row in rows:
        for i in range(a.per_topic):
            wf = copy.deepcopy(base)
            wf[p]["inputs"]["text"] = row["subject"]
            wf[s]["inputs"][seed_key] = random.randint(0, 2**32 - 1)
            for nid, (suffix, folder) in saves.items():
                name = f"{row['slug']}_{i + 1}" + (f"_{suffix}" if suffix else "")
                wf[nid]["inputs"]["filename_prefix"] = f"{folder}/{name}" if folder else name
            req = urllib.request.Request(a.server + "/prompt", data=json.dumps({"prompt": wf}).encode("utf-8"),
                                         headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req) as r:
                    print(row["slug"], i + 1, json.loads(r.read())["prompt_id"])
            except urllib.error.URLError as e:
                sys.exit(f"Cannot reach ComfyUI at {a.server} - is it running? ({e})")


if __name__ == "__main__":
    main()
