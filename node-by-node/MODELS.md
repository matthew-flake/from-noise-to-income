# Models / Modele

Status checked on 26 October 2026. Always re-read the licence on the model page before you sell anything. Not legal advice.
Stan na 26.10.2026. Przed sprzedażą zawsze przeczytaj licencję na stronie modelu. To nie jest porada prawna.

| File / Plik | Folder `ComfyUI/models/...` | Used by / Używają | Licence / Licencja | Official source / Źródło |
|---|---|---|---|---|
| `sd_xl_base_1.0.safetensors` (~6.9 GB) | `checkpoints` | W01–W05, W07–W11 | CreativeML Open RAIL++-M (commercial use allowed, with use restrictions) | https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0 |
| `sd_xl_offset_example-lora_1.0.safetensors` (~50 MB) | `loras` | W09, W10 | CreativeML Open RAIL++-M | https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0 |
| `t2i-adapter-canny-sdxl-1.0.fp16.safetensors` (download `diffusion_pytorch_model.fp16.safetensors` and rename) | `controlnet` | W08, W10 | Apache 2.0 | https://huggingface.co/TencentARC/t2i-adapter-canny-sdxl-1.0 |
| `4x_NMKD-Siax_200k.pth` | `upscale_models` | W06, W10 | WTFPL | https://openmodeldb.info (search "NMKD Siax") |

The workflow files contain these download links, so recent ComfyUI versions usually offer to download missing files.
If your files live in subfolders (e.g. `checkpoints/SDXL/`), just pick them from the list in the loader node.

Pliki workflow zawierają adresy pobrania, więc nowsze ComfyUI zwykle samo proponuje pobranie brakujących modeli.
Jeśli trzymasz modele w podfolderach (np. `checkpoints/SDXL/`), wybierz plik z listy w węźle ładującym.

Alternative upscaler / zamiennik: Real-ESRGAN x4plus (BSD-3-Clause), https://github.com/xinntao/Real-ESRGAN/releases

All 11 workflows use **built-in ComfyUI nodes only** – no custom node packs required.
Wszystkie 11 workflowów używa **wyłącznie węzłów wbudowanych** – bez rozszerzeń.
