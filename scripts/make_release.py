"""Build the free download pack for 'From Noise to Income'.

1. Copies the sample images from ComfyUI's output/book folder into ../samples
   as JPG (max 2048 px) - or PNG when the image has transparency - with ALL metadata removed
   (no embedded workflow, no user name, no paths), as promised in section 24.4 of the book,
2. copies the test input photos (output/book/_inputs) into ../inputs (metadata removed;
   files named like a trademark-lookalike test product, e.g. 'headphones', are skipped),
3. writes SHA256SUMS.txt for every file in the pack,
4. zips everything into ../../from-noise-to-income-pack-<version>.zip

Usage (Windows, ComfyUI-Easy-Install - uses ComfyUI's own Python, which has Pillow):
    path\\to\\python_embeded\\python.exe make_release.py "D:\\...\\ComfyUI\\output\\book" --version 2.1

Standard library + Pillow only. Nothing is uploaded anywhere. License: MIT, (c) Matthew Flake.
"""
import argparse, hashlib, os, shutil, sys, zipfile

MAX_PIXELS = 16_000_000  # larger images become JPG previews
# only the folders written by the v2 workflows (older test folders are skipped)
FOLDERS = set(['CH07_first', 'P01_botanical', 'P02_office_art', 'P03_pattern', 'P04_kidsbook', 'P05_maya', 'P06_campaign', 'P07_cosmetics', 'P08_set', 'P09_packaging', 'P10_slides', 'P11_rpg', 'P12_sandstone', 'P13_panorama', 'P14_zen', 'P15_product', 'P16_portfolio', 'P17_kdp_coloring', 'P18_etsy_clipart', 'P19_jp_nurie', 'P20_line_stickers']) | {"_inputs"}
RENAME = {"skincare": "product"}  # test photo name expected by P08 and P15
SKIP_INPUTS = {"headphones"}  # looked too much like a famous product - never ship it

PACK = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def latest_per_prefix(folder):
    """ComfyUI adds _00001_, _00002_ ... keep only the newest file per name prefix."""
    best = {}
    for f in os.listdir(folder):
        if not f.lower().endswith(".png"):
            continue
        prefix = f.rsplit("_", 2)[0]
        if prefix.startswith("seed_"):  # seed comparison tests, not samples
            continue
        p = os.path.join(folder, f)
        if prefix not in best or os.path.getmtime(p) > os.path.getmtime(best[prefix]):
            best[prefix] = p
    return sorted(best.values())


def copy_image(src, dst_dir):
    """Re-encode the image from pixels only, so no metadata (workflow, user, paths) survives."""
    from PIL import Image
    os.makedirs(dst_dir, exist_ok=True)
    name = os.path.basename(src).rsplit("_", 2)[0]
    is_input = dst_dir.endswith("inputs")
    if is_input:
        if name in SKIP_INPUTS:
            return "skipped " + src
        name = RENAME.get(name, name)
    with Image.open(src) as im:
        alpha = im.mode in ("RGBA", "LA") or "transparency" in im.info
        mode = "RGBA" if alpha else "RGB"
        clean = Image.frombytes(mode, im.size, im.convert(mode).tobytes())
        if is_input:
            out = os.path.join(dst_dir, name + ".png")
            clean.save(out)
            return out
        if clean.width * clean.height > MAX_PIXELS or not alpha:
            clean.thumbnail((2048, 2048))
        if alpha:
            out = os.path.join(dst_dir, name + ".png")
            clean.save(out)
        else:
            out = os.path.join(dst_dir, name + ".jpg")
            clean.save(out, quality=90)
        return out


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("book_output", help="ComfyUI output/book folder")
    ap.add_argument("--version", default="2.1")
    a = ap.parse_args()
    if not os.path.isdir(a.book_output):
        sys.exit("Folder not found: " + a.book_output)

    for sub in sorted(os.listdir(a.book_output)):
        src_dir = os.path.join(a.book_output, sub)
        if not os.path.isdir(src_dir) or sub not in FOLDERS:
            continue
        dst = os.path.join(PACK, "inputs" if sub == "_inputs" else os.path.join("samples", sub))
        for f in latest_per_prefix(src_dir):
            print("sample:", copy_image(f, dst))

    sums = []
    for root, _, files in os.walk(PACK):
        for f in sorted(files):
            p = os.path.join(root, f)
            rel = os.path.relpath(p, PACK).replace(os.sep, "/")
            if rel == "SHA256SUMS.txt" or "__pycache__" in rel:
                continue
            sums.append(f"{sha256(p)}  {rel}")
    with open(os.path.join(PACK, "SHA256SUMS.txt"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(sorted(sums, key=lambda s: s[66:])) + "\n")

    zpath = os.path.join(os.path.dirname(PACK), f"from-noise-to-income-pack-{a.version}.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED, strict_timestamps=False) as z:
        for root, _, files in os.walk(PACK):
            for f in files:
                p = os.path.join(root, f)
                if "__pycache__" in p:
                    continue
                z.write(p, os.path.join("from-noise-to-income", os.path.relpath(p, PACK)))
    print("\nZIP:", zpath, "\nSHA-256 of the zip:", sha256(zpath))


if __name__ == "__main__":
    main()
