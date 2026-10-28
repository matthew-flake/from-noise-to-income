# From Noise to Income — companion pack

Free workflows, templates, sample images and scripts for the book **"From Noise to Income: The ComfyUI Handbook"**
by Matthew Flake (20 tested ComfyUI projects to create and sell AI images legally).

*Unofficial guide. ComfyUI and Comfy are trademarks of Comfy Org. This pack and the book are independent
publications and are not authorised, sponsored or endorsed by Comfy Org.*

## Download

- **Everything at once:** click the green **Code** button above → **Download ZIP**, or open **Releases** on the right
  and download the latest version.
- After unzipping, you can check every file against `SHA256SUMS.txt` (see *Is it safe?* below).
- No account, no email, no tracking.

## Looking for *Node by Node* / *Węzeł po węźle*?

The companion pack for the beginner book *Node by Node. ComfyUI from Your First Image to Your Own Workflow* (Polish edition: *Węzeł po węźle*) now has its own repository: **https://github.com/matthew-flake/node-by-node**

## What's inside

```
workflows/ui/      21 workflows - drag & drop a .json file onto the ComfyUI window
workflows/api/     the same workflows in API format - for scripts/batch.py and automation
templates/         business_templates.xlsx (product and service calculators, license register, QC sheet,
                   demand tests) + brief, offer, product description and checklists (Markdown)
scripts/           batch.py + topics.csv (chapter 22), make_release.py (builds this pack)
samples/           result images (added by make_release.py, metadata removed) + previews/ (small JPGs)
inputs/            test photos: product.png (P08, P15) and landscape.png (P13) - AI-generated, free for practice
docs/results.jpg   contact sheet of the sample results
MODELS.md          every model file, its folder, license and official download link
SHA256SUMS.txt     checksums of every file in the pack
```

No model files are included. Every loader node carries the official download link, so recent ComfyUI
versions usually offer to download anything that is missing (from the publishers' own repositories).
If a model is not offered, download it by hand - `MODELS.md` lists every file, link and target folder.

## Quick start

1. Install ComfyUI (desktop app or portable, version 0.39 or newer).
2. Drag `workflows/ui/P01_botanical_fine_art_posters.json` onto the ComfyUI window.
3. If ComfyUI lists missing models, download them (links in the dialog and in `MODELS.md`).
4. Press **Run**. The result appears in `ComfyUI/output/book/P01_botanical/`.

Workflows that use your own photo (P08 product, P13 landscape, P15 product) start with a **Load Image** node -
pick your own file, or a test photo from `inputs/` (copy it into `ComfyUI/input` first).

## The workflows

| # | File | What it makes | Models | Extra node pack | Time* |
|---|---|---|---|---|---|
| CH07 | `CH07_first_workflow_sdxl.json` | Your first 5-node workflow: magnolia print, universal negative | SDXL base 1.0 | - | 19 s |
| P01 | `P01_botanical_fine_art_posters.json` | Botanical fine-art print + 4x print file (6 species) | Z-Image-Turbo, 4x NMKD-Siax | - | 25 s |
| P02 | `P02_abstract_office_art.json` | Abstract office art, 4x + 2x for large canvas | Z-Image-Turbo, 4x NMKD-Siax | - | 34 s |
| P03 | `P03_seamless_luxury_pattern.json` | Seamless luxury pattern + 3x3 preview | Z-Image-Turbo | - | 32 s |
| P04 | `P04_childrens_book_illustration.json` | Children's book spread (fox in a clearing) + 4x | Z-Image-Turbo, 4x NMKD-Siax | - | 24 s |
| P05 | `P05_consistent_character_six_scenes.json` | Character sheet + the same character in 6 scenes | FLUX.2 [klein] 4B | - | 61 s |
| P06 | `P06_brand_campaign_key_visual.json` | Text-free campaign key visual (glass ecosystem) | Z-Image-Turbo | - | 19 s |
| P07 | `P07_luxury_cosmetic_social_pack.json` | Cosmetic hero shot in 4:5, 9:16, 1:1 + headline | Z-Image-Turbo | - | 48 s |
| P08 | `P08_product_set_and_placement.json` | Mediterranean product set + your product placed on it | FLUX.2 [klein] 4B, BiRefNet | ComfyUI-RMBG | 22 s |
| P09 | `P09_perfume_packaging_concept.json` | Perfume bottle and box packaging concept (text-free) | Z-Image-Turbo | - | 16 s |
| P10 | `P10_renewable_energy_slide.json` | 16:9 slide visual + title set by a text node | Z-Image-Turbo | - | 16 s |
| P11 | `P11_rpg_asset_icons.json` | Fantasy RPG item, transparent PNG + 256 px icon (6 items) | Z-Image-Turbo, BiRefNet | ComfyUI-RMBG | 17 s |
| P12 | `P12_seamless_sandstone_texture.json` | Seamless sandstone texture + depth map | Z-Image-Turbo, Depth Anything V2 Small | comfyui_controlnet_aux | 31 s |
| P13 | `P13_cinematic_panorama_outpaint.json` | 16:9 photo extended to a 21:9 panorama | FLUX.2 [klein] 4B, LaMa | ComfyUI-RMBG | 16 s |
| P14 | `P14_zen_wall_art_batch.json` | Zen ink wall art - template for batch.py | Z-Image-Turbo | - | 16 s |
| P15 | `P15_product_six_studio_looks.json` | Your product in 6 studio looks (test photo: product.png) | FLUX.2 [klein] 4B | - | 54 s |
| P16 | `P16_portfolio_hero.json` | Portfolio hero image + title line | Z-Image-Turbo | - | 16 s |
| P17 | `P17_kdp_bold_easy_coloring.json` | Amazon KDP coloring page, 8.5x11 in + bleed | Z-Image-Turbo, 4x NMKD-Siax | - | 25 s |
| P18 | `P18_etsy_clipart_bundle.json` | Etsy clipart, 4096 px transparent PNG | Z-Image-Turbo, 4x NMKD-Siax, BiRefNet | ComfyUI-RMBG | 27 s |
| P19 | `P19_amazon_jp_nurie_coloring.json` | Amazon.co.jp adult coloring page, A4 + bleed | Z-Image-Turbo, 4x NMKD-Siax | - | 25 s |
| P20 | `P20_line_stickers.json` | LINE sticker 370 x 320 px, transparent | Z-Image-Turbo, BiRefNet | ComfyUI-RMBG | 19 s |

\* Tested on 26 October 2026 (P17-P20: 23 October): ComfyUI 0.39.0, Windows 11, NVIDIA GeForce RTX 5060 8 GB VRAM, 32 GB RAM, fp8 model files.
Performance and memory needs vary with your setup; with less system RAM, close other programs or use the cloud.
Times are per run with models already loaded; the first run of a model family adds its loading time.
On 8 GB VRAM run the Z-Image and FLUX.2 [klein] workflows in separate sessions or press "Free model and node cache"
between them - keeping both families in memory at once can exceed 32 GB RAM.

## Batch runs

`scripts/batch.py` queues one workflow many times from a CSV list (chapter 22). It works with the single-prompt
workflows CH07, P01-P04, P06, P09-P12, P14 and P16-P20. Multi-scene workflows (P05, P07, P08, P13, P15) have
several prompts or need your photo - run them from the ComfyUI window.

15 of the 21 workflows use only nodes built into ComfyUI. The others need one of two popular packs from the
ComfyUI registry (install them with ComfyUI Manager): **ComfyUI-RMBG** (1038lab, GPL-3.0) and
**comfyui_controlnet_aux** (Fannovel16, Apache 2.0).

## Can ComfyUI replace Photoshop?

For raster work - yes, for most of it: generating, background removal, object removal, outpainting,
product sets and placement, six studio looks from one product photo, draft text overlays, 4x upscaling for print, seamless patterns, B/W coloring pages,
cropping and contact sheets are all in this pack. Keep a free editor (Krita, GIMP, Inkscape, Scribus)
for vector logos, precise typography, book layout and CMYK/ICC preparation.

## Is it safe?

- Only open formats: JSON, Markdown, CSV, XLSX templates (no macros), PNG/JPG and short Python scripts
  (batch.py uses the standard library only; tools/ rebuilds the workflows). No installers, no executables, no model weights.
- Check any file against `SHA256SUMS.txt`:
  Windows `certutil -hashfile <file> SHA256` - macOS/Linux `shasum -a 256 <file>`.
- `batch.py` only talks to your own ComfyUI at `http://127.0.0.1:8188`.
- Sample images are re-encoded from pixels with all metadata removed - no embedded workflow, user names,
  disk paths or location data. To see how an image was made, drag the workflow JSON onto ComfyUI.

## Licenses

- Workflows, scripts and templates: **MIT** (see `LICENSE`) - use them in commercial projects too.
- Sample images: **CC BY-NC 4.0** (see `samples/LICENSE.md`) - study and share with credit, do not resell.
- Models: their own licenses (see `MODELS.md`). All models used here allow commercial use of the outputs
  as of October 2026. Re-check before you sell. Platforms (Amazon KDP, Etsy, LINE) require you to disclose AI use.

Questions and fixes: open an issue in this repository.
