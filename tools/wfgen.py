"""Tiny builder that writes the same ComfyUI graph in two formats:
UI format (drag & drop into ComfyUI) and API format (for scripts / the /prompt endpoint).
Author of the generated workflows: Matthew Flake. Code: MIT."""
import json, uuid
from schema import S

GROUP_COLORS = ["#3f789e", "#8a6d3b", "#4b7f52", "#7d4b8a", "#a1544f", "#4f7d8a", "#6b6b3b", "#5a5a8a"]
NOTE_COLOR, NOTE_BG = "#432", "#653"

HF_Z = "https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/"
HF_K = "https://huggingface.co/Comfy-Org/flux2-klein-4B/resolve/main/split_files/"
MODEL_URLS = {
    "z_image_turbo_bf16.safetensors": (HF_Z + "diffusion_models/z_image_turbo_bf16.safetensors", "diffusion_models"),
    "qwen_3_4b.safetensors": (HF_Z + "text_encoders/qwen_3_4b.safetensors", "text_encoders"),
    "ae.safetensors": (HF_Z + "vae/ae.safetensors", "vae"),
    "flux-2-klein-4b-fp8.safetensors": ("https://huggingface.co/black-forest-labs/FLUX.2-klein-4b-fp8/resolve/main/flux-2-klein-4b-fp8.safetensors", "diffusion_models"),
    "flux2-vae.safetensors": (HF_K + "vae/flux2-vae.safetensors", "vae"),
}


class Node:
    def __init__(self, g, nid, ntype, title, group, col, values, links, mode=0):
        self.g, self.id, self.type, self.title, self.group, self.col = g, nid, ntype, title, group, col
        self.values, self.links, self.mode = values, links, mode

    def __getitem__(self, slot):
        return (self, slot)


class WF:
    def __init__(self, code, name, author="Matthew Flake"):
        self.code, self.name, self.author = code, name, author
        self.nodes, self.groups = [], []  # groups: (title, desc)

    def group(self, title):
        if title not in self.groups:
            self.groups.append(title)
        return title

    def add(self, ntype, title=None, group=None, col=0, mode=0, **kw):
        if ntype not in S:
            raise KeyError(ntype)
        ins, _ = S[ntype]
        values, links = {}, {}
        names = {i[0] for i in ins}
        for k, v in kw.items():
            if k not in names:
                raise KeyError(f"{ntype}.{k}")
            if isinstance(v, tuple):
                links[k] = v
            else:
                values[k] = v
        for (n, kind, typ, ctl, default) in ins:
            if kind == "W" and n not in values:
                if default is None and n not in links:
                    raise ValueError(f"{ntype}.{n} needs a value")
                values[n] = default
        n = Node(self, len(self.nodes) + 1, ntype, title or ntype, group, col, values, links, mode)
        if group:
            self.group(group)
        self.nodes.append(n)
        return n

    def note(self, text, group, col=0, title="Read me"):
        return self.add("Note", title=title, group=group, col=col, text=text)

    # ---------------- API format ----------------
    def api(self, rename=None):
        rename = rename or {}
        out = {}
        for n in self.nodes:
            if n.type == "Note" or n.mode != 0:
                continue
            inputs = {}
            for (k, kind, typ, ctl, d) in S[n.type][0]:
                if k in n.links:
                    src, slot = n.links[k]
                    inputs[k] = [str(src.id), slot]
                elif kind == "W" and k in n.values:
                    v = n.values[k]
                    inputs[k] = rename.get(v, v) if isinstance(v, str) else v
            out[str(n.id)] = {"class_type": n.type, "inputs": inputs, "_meta": {"title": n.title}}
        return out

    # ---------------- UI format ----------------
    def ui(self, info=None):
        # sizes
        def size(n):
            ins = S[n.type][0]
            rows = len([i for i in ins if i[1] == "L" or i[0] in n.links]) + len([i for i in ins if i[1] == "W"])
            rows += len(S[n.type][1])
            w = 340
            h = 46 + 24 * max(rows, 1)
            if n.type == "Note":
                lines = sum(max(1, len(l) // 44 + 1) for l in n.values["text"].split("\n"))
                w, h = 380, 30 + 17 * lines
            if n.type == "CLIPTextEncode":
                w, h = 420, 220
            if n.type in ("SaveImage", "PreviewImage"):
                w, h = 360, 380
            if n.type == "LoadImage":
                w, h = 340, 360
            if n.type == "TextOverlay":
                w, h = 360, 260
            return [w, h]

        # layout: groups left->right; inside each group columns, nodes stacked
        x0, gap, pad, top = 0, 70, 30, 60
        pos, gbox = {}, {}
        for gi, gname in enumerate(self.groups):
            members = [n for n in self.nodes if n.group == gname]
            cols = sorted({n.col for n in members})
            cx = x0 + pad
            gh = 0
            for c in cols:
                cy = top + 40
                cw = 0
                for n in [m for m in members if m.col == c]:
                    s = size(n)
                    pos[n.id] = ([cx, cy], s)
                    cy += s[1] + 50
                    cw = max(cw, s[0])
                gh = max(gh, cy - top)
                cx += cw + 40
            gw = cx - x0 - 40 + pad
            gbox[gname] = [x0, top - 10, gw, gh + 10]
            x0 += gw + gap
        # links
        links, lid = [], 0
        out_links = {}  # (node, slot) -> [ids]
        in_link = {}    # (node, name) -> id
        for n in self.nodes:
            ins = S[n.type][0]
            sock = [i for i in ins if i[1] == "L" or i[0] in n.links]
            for ti, (k, kind, typ, ctl, d) in enumerate(sock):
                if k in n.links:
                    src, slot = n.links[k]
                    lid += 1
                    otype = S[src.type][1][slot][1]
                    links.append([lid, src.id, slot, n.id, ti, otype])
                    out_links.setdefault((src.id, slot), []).append(lid)
                    in_link[(n.id, k)] = lid
        nodes = []
        for order, n in enumerate(self.nodes):
            ins, outs = S[n.type]
            inputs = []
            for (k, kind, typ, ctl, d) in ins:
                if kind == "L" or k in n.links:
                    e = {"name": k, "type": typ if typ != "COMBO" else "COMBO", "link": in_link.get((n.id, k))}
                    if kind == "W":
                        e["widget"] = {"name": k}
                    inputs.append(e)
            outputs = []
            for si, (oname, otype) in enumerate(outs):
                outputs.append({"name": oname, "type": otype, "links": out_links.get((n.id, si), []), "slot_index": si})
            wv = []
            for (k, kind, typ, ctl, d) in ins:
                if kind == "W":
                    wv.append(n.values.get(k))
                    if ctl:
                        wv.append("fixed")
            if n.type == "LoadImage":
                wv.append("image")
            p, s = pos[n.id]
            nd = {"id": n.id, "type": n.type, "pos": p, "size": s, "flags": {}, "order": order, "mode": n.mode,
                  "inputs": inputs, "outputs": outputs, "title": n.title,
                  "properties": {"Node name for S&R": n.type}, "widgets_values": wv}
            if n.type == "Note":
                nd["color"], nd["bgcolor"] = NOTE_COLOR, NOTE_BG
                nd["properties"] = {}
            models = []
            for v in n.values.values():
                if isinstance(v, str) and v in MODEL_URLS:
                    url, folder = MODEL_URLS[v]
                    models.append({"name": v, "url": url, "directory": folder})
            if models:
                nd["properties"]["models"] = models
            nodes.append(nd)
        groups = []
        for gi, gname in enumerate(self.groups):
            groups.append({"id": gi + 1, "title": gname, "bounding": gbox[gname], "color": GROUP_COLORS[gi % len(GROUP_COLORS)],
                           "font_size": 24, "flags": {}})
        return {
            "id": str(uuid.uuid5(uuid.NAMESPACE_URL, "from-prompt-to-product/" + self.code)),
            "revision": 0, "last_node_id": len(self.nodes), "last_link_id": lid,
            "nodes": nodes, "links": links, "groups": groups, "config": {},
            "extra": {"ds": {"scale": 0.6, "offset": [40, 40]},
                      "info": dict({"name": f"{self.code} {self.name}", "author": self.author,
                                    "description": f"Companion workflow for the book 'From Noise to Income' — {self.code}.",
                                    "license": "MIT (workflow file). Model files keep their own licenses — see README."}, **(info or {}))},
            "version": 0.4,
        }
