# Models used by the workflows

All model files below have licenses that allow commercial use of the generated images
(category **A** in the book). Status checked on 26 October 2026 - always re-read the
LICENSE file on the model page before you sell anything. This is not legal advice.

The workflow files contain these download links, so recent ComfyUI versions usually offer to
download missing files (official repositories only). If yours doesn't, download them by hand from
the links below into the folder shown. Nothing is bundled in this pack.

| File | Put it in `ComfyUI/models/...` | Used by | License | Official source |
|---|---|---|---|---|
| `z_image_turbo_bf16.safetensors` (~12 GB, loaded as fp8 on 8 GB VRAM) | `diffusion_models` | P01-P04, P06, P07, P09-P12, P14, P16-P20 | Apache 2.0 | https://huggingface.co/Comfy-Org/z_image_turbo |
| `qwen_3_4b.safetensors` (~8 GB, text encoder) | `text_encoders` | all Z-Image and FLUX.2 [klein] workflows | Apache 2.0 | https://huggingface.co/Comfy-Org/z_image_turbo (also in Comfy-Org/flux2-klein-4B) |
| `ae.safetensors` (VAE, FLUX.1 [schnell]) | `vae` | Z-Image workflows | Apache 2.0 | https://huggingface.co/Comfy-Org/z_image_turbo |
| `flux-2-klein-4b-fp8.safetensors` (~4 GB) | `diffusion_models` | P05, P08, P13, P15 | Apache 2.0 | https://huggingface.co/black-forest-labs/FLUX.2-klein-4b-fp8 |
| `flux2-vae.safetensors` | `vae` | FLUX.2 [klein] workflows | Apache 2.0 | https://huggingface.co/Comfy-Org/flux2-klein-4B |
| `4x_NMKD-Siax_200k.pth` | `upscale_models` | P01, P02, P04, P17-P19 | WTFPL | https://openmodeldb.info (search "NMKD Siax") |
| `sd_xl_base_1.0.safetensors` (optional) | `checkpoints` | CH07 | CreativeML Open RAIL++-M | https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0 |

Downloaded automatically by node packs on first use:

| Model | Node pack (license) | Used by | Model license |
|---|---|---|---|
| BiRefNet-general | ComfyUI-RMBG (GPL-3.0) | P08, P11, P18, P20 | MIT |
| LaMa | ComfyUI-RMBG (GPL-3.0) | P13 | Apache 2.0 |
| Depth Anything V2 **Small** (`depth_anything_v2_vits.pth`) | comfyui_controlnet_aux (Apache 2.0) | P12 | Apache 2.0 |

Do NOT swap in: FLUX.2 [klein] **9B**, FLUX.1/FLUX.2 [dev], BRIA RMBG-2.0,
Depth Anything V2 Base/Large - their licenses are non-commercial.

Alternative upscaler: Real-ESRGAN x4plus (BSD-3-Clause),
https://github.com/xinntao/Real-ESRGAN/releases - pick it in the "Load upscaler" node.
