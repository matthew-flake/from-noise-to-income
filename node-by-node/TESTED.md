# Test report / Raport z testów – 27 Oct 2026

**Machine / Komputer:** Windows, NVIDIA GeForce RTX 5060 8 GB VRAM, 32 GB RAM
**ComfyUI:** 0.39.0 (Python 3.12.10), frontend 1.53.10
**Models / Modele:** see MODELS.md (files kept in a `SDXL\` subfolder – picked from the loader list)

Every workflow was loaded from `workflows/ui` into the ComfyUI window and run with **Run** (UI format test),
and earlier sent through the `/prompt` endpoint from `workflows/api` (API format test).
Każdy workflow wczytano z `workflows/ui` do okna ComfyUI i uruchomiono przyciskiem Run, a wcześniej wysłano przez `/prompt` z `workflows/api`.

| Workflow | UI run | API run | Time (model in memory) | Output |
|---|---|---|---|---|
| W01_first_image | OK | OK | 16 s | 1024×1024 |
| W02_cfg_test | OK | OK | 32 s | 2528×832 strip |
| W03_img2img_denoise | OK | OK | 44 s | 4144×1024 strip |
| W04_inpainting_mask | OK | OK | 16 s | 1024×1024 |
| W05_outpainting_panorama | OK | OK | 25 s | 1856×768 |
| W06_upscale_2x | OK | OK | 10 s | 2048×2048 |
| W07_hires_fix | OK | OK | 42 s | 1248×1824 |
| W08_controlnet_canny | OK | OK | 19 s | 1024×1024 |
| W09_lora_comparison | OK | OK | 32 s | 2448×832 strip |
| W10_all_together | OK | OK | 45 s | 1280×1280 + 2560×2560 (re-tested 28 Oct 2026 after the prompt fix) |
| W11_series | OK | OK | 16 s | 832×1216 |
| scripts/series.py + topics.csv (6 topics × 1) | – | OK | 88 s total | 6 × 832×1216 |

Notes / Uwagi:
- W03: SDXL keeps the colours and light of the input photo even at denoise 0.75 – the strip shows it on purpose (chapter 6).
- W04: with denoise 0.8 the new lid came out copper (pulled by the wood colour) – the final file uses denoise 1.0 + `(matte black:1.2)`.
- series.py was first run against a local mock server (payload check), then the identical payloads were sent to ComfyUI.
- First run after starting ComfyUI is slower (model loading): add 20–60 s.
