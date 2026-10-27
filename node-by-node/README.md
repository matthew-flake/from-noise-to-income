# Węzeł po węźle / Node by Node – companion pack (edition 10.26)

**PL.** Bezpłatne materiały do książki *Węzeł po węźle. ComfyUI od pierwszego obrazu do własnego workflow* (Matthew Flake, wydanie 10.26, październik 2026). Bez konta, bez e-maila.

**EN.** Free companion files for the book *Node by Node* (Polish edition: *Węzeł po węźle*), edition 10.26. No account, no e-mail.

![Results / Wyniki](docs/results.jpg)

## Start in 3 steps / Start w 3 krokach
1. Download the models listed in `MODELS.md` into `ComfyUI/models/...` / Pobierz modele z `MODELS.md`.
2. Copy `inputs/*.png` to `ComfyUI/input` / Skopiuj obrazy z `inputs` do `ComfyUI/input`.
3. Drag a file from `workflows/ui` onto the ComfyUI window and click **Run** / Przeciągnij plik z `workflows/ui` na okno ComfyUI i kliknij **Run**.

## Contents / Zawartość
| Folder | What / Co |
|---|---|
| `workflows/ui` | 11 workflows – drag & drop (built-in nodes only) / 11 workflowów do przeciągnięcia (tylko węzły wbudowane) |
| `workflows/api` | the same in API format for scripts / to samo w formacie API |
| `inputs` | exercise images / obrazy do ćwiczeń |
| `scripts` | `series.py` + `topics.csv` – batch series (chapter 15) / seria jednym poleceniem |
| `materials` | checklists, notes template, licence register, brief and offer templates (`*_en.md` English, `*_pl.md` Polish) / checklisty i szablony |
| `docs/graphs` | screenshots of every graph / zrzuty każdego grafu |
| `samples` | test results as PNG with embedded workflow / wyniki testów z workflow w metadanych |
| `TESTED.md` | test report (RTX 5060 8 GB) / raport z testów |

| # | File | Chapter / Rozdział |
|---|---|---|
| W01 | [first_image](workflows/ui/W01_first_image.json) · [graph](docs/graphs/W01_graph.jpg) | 3 |
| W02 | [cfg_test](workflows/ui/W02_cfg_test.json) · [graph](docs/graphs/W02_graph.jpg) | 5 |
| W03 | [img2img_denoise](workflows/ui/W03_img2img_denoise.json) · [graph](docs/graphs/W03_graph.jpg) | 6 |
| W04 | [inpainting_mask](workflows/ui/W04_inpainting_mask.json) · [graph](docs/graphs/W04_graph.jpg) | 7 |
| W05 | [outpainting_panorama](workflows/ui/W05_outpainting_panorama.json) · [graph](docs/graphs/W05_graph.jpg) | 7 |
| W06 | [upscale_2x](workflows/ui/W06_upscale_2x.json) · [graph](docs/graphs/W06_graph.jpg) | 8 |
| W07 | [hires_fix](workflows/ui/W07_hires_fix.json) · [graph](docs/graphs/W07_graph.jpg) | 8 |
| W08 | [controlnet_canny](workflows/ui/W08_controlnet_canny.json) · [graph](docs/graphs/W08_graph.jpg) | 10 |
| W09 | [lora_comparison](workflows/ui/W09_lora_comparison.json) · [graph](docs/graphs/W09_graph.jpg) | 11 |
| W10 | [all_together](workflows/ui/W10_all_together.json) · [graph](docs/graphs/W10_graph.jpg) | 13 |
| W11 | [series](workflows/ui/W11_series.json) · [graph](docs/graphs/W11_graph.jpg) | 15 |

Integrity: `SHA256SUMS.txt`. Licences: see `LICENSE.md`. Workflows and scripts – MIT. Models are not included.
Not affiliated with Comfy Org or Stability AI.
