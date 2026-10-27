# Test report - v2, 26 October 2026

Environment: Windows 11, ComfyUI 0.39.0, NVIDIA GeForce RTX 5060 8 GB VRAM, 32 GB RAM.
Each workflow was queued through the ComfyUI API in its API version and run end-to-end with real models
(P17-P20 unchanged since the 23 October run). Times are per run with models loaded; Z-Image and
FLUX.2 [klein] families were run in separate batches with models unloaded in between (POST /free).

Local file names differed from the official ones only by folder; Z-Image-Turbo was tested with the FP8 file
`z-image-turbo-fp8-e4m3fn.safetensors` (same model as the official BF16 file loaded as fp8_e4m3fn).

Fixes found during testing:
- P06 and P10: prompts that mentioned a "headline" produced garbled pseudo-text. Both prompts now ask for a
  completely text-free image; P10 sets the real title with the core Draw Text Overlay node.
- Draw Text Overlay accepts position "top" or "bottom" only.

| Workflow | Result | Time | Output |
|---|---|---|---|
| CH07 | OK | 19 s | 896 x 1120 |
| P01 | OK | 25 s | 896 x 1120 + 3584 x 4480 |
| P02 | OK | 34 s | 1248 x 832 + 4x + 2x (9984 x 6656) |
| P03 | OK | 32 s | 1024 tile + 3072 3x3 preview |
| P04 | OK | 24 s | 1344 x 768 + 5376 x 3072 |
| P05 | OK | 61 s | 1344 x 768 sheet + 6 scenes 864 x 1152 |
| P06 | OK | 19 s | 896 x 1120 (text-free) |
| P07 | OK | 48 s | 896 x 1120, 720 x 1280, 1024 x 1024 + headline story |
| P08 | OK | 22 s | 896 x 1120 set + product on set |
| P09 | OK | 16 s | 864 x 1152 |
| P10 | OK | 16 s | 1344 x 768 + titled slide |
| P11 | OK | 17 s | 1024 RGBA + 256 icon |
| P12 | OK | 31 s | 1024 texture, depth map, 3072 preview |
| P13 | OK | 16 s | 1792 x 768 panorama |
| P14 | OK | 16 s | 832 x 1248 (6 subjects via batch.py) |
| P15 | OK | 54 s | 6 x 896 x 1120 |
| P16 | OK | 16 s | 1344 x 768 + title line |
| P17 | OK | 25 s | 2588 x 3375 page |
| P18 | OK | 27 s | 4096 x 4096 RGBA |
| P19 | OK | 25 s | 2519 x 3583 page |
| P20 | OK | 19 s | 370 x 320 RGBA |

Contact sheet of the results: `docs/results.jpg`.

## Pack 2.1 - re-test on 26 October 2026 (same PC: ComfyUI 0.39.0, RTX 5060 8 GB, 32 GB RAM)

Queued through the ComfyUI API from the 2.1 files, outputs saved to output/book/test2_1/.

| Test | Result | Time | Notes |
|---|---|---|---|
| P09 with the 2.0 text-free sentence (seed 9901) | partly | 20.4 s | faint pseudo-letters still on the box |
| P09 final prompt (box sentence + gold plaque), seed 9901 | OK | 16.2 s | box clean; tiny engraved mark on the bottle base |
| P09 final prompt, seed 9902 | OK | 13.7 s | box clean |
| P09 final prompt, seed 9903 | fail | 13.7 s | small pseudo-text on a white box - try another seed |
| P15 with inputs/product.png (unbranded jar) | OK | 57.6 s | 6 looks; shape, lid and blank label kept, no logos added (time includes model loading after /free) |
| batch.py -> P14, 2 topics (bamboo, crane_lake) | OK | 16.1 / 16.4 s | files bamboo_1, crane_lake_1 |
| batch.py -> P01, 1 topic (lotus) | OK | 24.6 s | files lotus_1 + lotus_1_print (3584 x 4480) |
| Node check: all 44 node types in the 21 UI files | OK | - | present in ComfyUI 0.39.0; only BiRefNetRMBG, AILab_LamaRemover (ComfyUI-RMBG) and DepthAnythingV2Preprocessor (controlnet_aux) are custom; Draw Text Overlay is core |

Other 2.1 changes:
- batch.py finds every Save Image node and names all output files; multi-scene workflows (P05, P07, P08, P13, P15)
  stop with a clear message. Also tested against a mock server with all 21 API workflows.
- make_release.py re-encodes samples and inputs without metadata and never ships a 'headphones' input.
- inputs/product.png and inputs/landscape.png are the original 1024 x 1024 and 1344 x 768 test photos.
