"""Example workflows for the book "Węzeł po węźle" / "Node by Node" (edition 10.26).
Run:  python node_by_node.py OUTPUT_DIR      (writes ui/ and api/)
Author: Matthew Flake. Workflow files: MIT licence.
All on-canvas text (node titles, groups, notes, save prefixes) is in English on purpose:
the screenshots are reused in the English edition."""
import json, os, sys
import wfgen
from wfgen import WF

CKPT = "sd_xl_base_1.0.safetensors"
LORA = "sd_xl_offset_example-lora_1.0.safetensors"
CNET = "t2i-adapter-canny-sdxl-1.0.fp16.safetensors"
UPS = "4x_NMKD-Siax_200k.pth"
HF_SDXL = "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/"
wfgen.MODEL_URLS.update({
    CKPT: (HF_SDXL + CKPT, "checkpoints"),
    LORA: (HF_SDXL + LORA, "loras"),
    CNET: ("https://huggingface.co/TencentARC/t2i-adapter-canny-sdxl-1.0/resolve/main/diffusion_pytorch_model.fp16.safetensors", "controlnet"),
})

OUT = "node_by_node"
NEG = "text, watermark, logo, signature, blurry, low quality, deformed, extra objects"
LIC = ("LICENCES (as of 26 Oct 2026 - check before selling):\n"
       "- SDXL base 1.0: CreativeML Open RAIL++-M - commercial use allowed, with a list of prohibited uses.\n"
       "Not legal advice.")
LIC_UP = "- 4x NMKD-Siax 200k: WTFPL (OpenModelDB). Alternative: Real-ESRGAN x4plus (BSD-3)."
INFO = lambda code, desc: {"description": f"Node by Node / Węzeł po węźle (ed. 10.26) - {code}: {desc}",
                           "license": "MIT (workflow file). Models have their own licences - see MODELS.md."}


def base(wf, g, col=0):
    return wf.add("CheckpointLoaderSimple", "Load Checkpoint (SDXL)", g, col, ckpt_name=CKPT)


def prompts(wf, clip, text, g, col=1, neg=NEG):
    p = wf.add("CLIPTextEncode", "Prompt", g, col, text=text, clip=clip)
    n = wf.add("CLIPTextEncode", "Negative prompt", g, col, text=neg, clip=clip)
    return p, n


def sampler(wf, model, p, n, latent, g, col, seed, steps=28, cfg=6.0, denoise=1.0, title="Sampler"):
    return wf.add("KSampler", title, g, col, model=model, seed=seed, steps=steps, cfg=cfg,
                  sampler_name="dpmpp_2m", scheduler="karras", positive=p, negative=n,
                  latent_image=latent, denoise=denoise)


def save(wf, img, prefix, g, col, title="Save"):
    return wf.add("SaveImage", title, g, col, images=img, filename_prefix=f"{OUT}/{prefix}")


def stitch(wf, images, g, col, label="Stitch"):
    cur = images[0]
    for i, nxt in enumerate(images[1:]):
        cur = wf.add("ImageStitch", f"{label} {i + 1}", g, col, image1=cur, image2=nxt, direction="right",
                     match_image_size=True, spacing_width=16, spacing_color="white")[0]
    return cur


def W01():
    wf = WF("W01", "First image (text to image)")
    g = "Text to image"
    wf.note("Chapter 3. Seven nodes worth knowing by heart.\n"
            "Change only the text in Prompt and click Run. Output: ComfyUI/output/node_by_node/W01.\n\n" + LIC, g)
    ck = base(wf, g)
    p, n = prompts(wf, ck[1], "realistic product photo of a matte black ceramic coffee mug on a dark slate surface, "
                   "soft studio lighting, subtle reflections, centered composition, clean minimal background", g)
    l = wf.add("EmptyLatentImage", "Canvas 1024x1024", g, 2, width=1024, height=1024, batch_size=1)
    k = sampler(wf, ck[0], p[0], n[0], l[0], g, 2, seed=101)
    d = wf.add("VAEDecode", "VAE Decode", g, 3, samples=k[0], vae=ck[2])
    save(wf, d[0], "W01/mug", g, 3)
    return wf


def W02():
    wf = WF("W02", "CFG test: 4 / 7 / 10 in one run")
    g = "CFG comparison"
    wf.note("Chapter 5. Same prompt, same seed, three CFG values side by side.\n"
            "Change one thing at a time - here only CFG. Output: one comparison strip.\n\n" + LIC, g)
    ck = base(wf, g)
    p, n = prompts(wf, ck[1], "watercolor illustration of a red fox sitting in autumn leaves, soft morning light, "
                   "warm palette, white paper background", g)
    l = wf.add("EmptyLatentImage", "Canvas 832x832", g, 1, width=832, height=832, batch_size=1)
    imgs = []
    for cfg in (4.0, 7.0, 10.0):
        k = sampler(wf, ck[0], p[0], n[0], l[0], g, 2, seed=202, cfg=cfg, title=f"Sampler CFG {cfg:g}")
        imgs.append(wf.add("VAEDecode", f"Decode CFG {cfg:g}", g, 3, samples=k[0], vae=ck[2])[0])
    save(wf, stitch(wf, imgs, g, 4), "W02/cfg_4_7_10", g, 4)
    return wf


def W03():
    wf = WF("W03", "Img2img: three denoise levels side by side")
    g = "Img2img"
    wf.note("Chapter 6. Input image -> VAE Encode -> three KSamplers with denoise 0.35 / 0.55 / 0.75.\n"
            "Same prompt and seed - only denoise changes. Strip: original | 0.35 | 0.55 | 0.75.\n"
            "Input file: jar.png (pack folder inputs) -> copy to ComfyUI/input.\n\n" + LIC, g)
    ck = base(wf, g)
    im = wf.add("LoadImage", "Input image", g, 0, image="jar.png")
    p, n = prompts(wf, ck[1], "glossy terracotta ceramic cosmetic jar with a light oak lid, standing on a travertine "
                   "pedestal, warm sunset light, long soft shadows, editorial product photography", g)
    e = wf.add("VAEEncode", "VAE Encode", g, 2, pixels=im[0], vae=ck[2])
    imgs = [im[0]]
    for dn in (0.35, 0.55, 0.75):
        k = sampler(wf, ck[0], p[0], n[0], e[0], g, 2, seed=303, denoise=dn, title=f"Sampler denoise {dn:g}")
        imgs.append(wf.add("VAEDecode", f"Decode {dn:g}", g, 3, samples=k[0], vae=ck[2])[0])
    save(wf, stitch(wf, imgs, g, 4), "W03/denoise_035_055_075", g, 4)
    return wf


def W04():
    wf = WF("W04", "Inpainting with a regular model: new lid")
    g = "Inpainting"
    wf.note("Chapter 7. We change ONLY the jar lid.\n"
            "Regular model (SDXL base) + Set Latent Noise Mask + denoise 1.0 (the mask protects the rest).\n"
            "Image Composite Masked pastes the new part into the original, so everything else stays pixel-identical.\n"
            "Files: jar.png and jar_lid_mask.png (white = change). To draw your own mask: right-click Load Image ->\n"
            "Open in MaskEditor, then connect the MASK output of Load Image instead.\n\n" + LIC, g)
    ck = base(wf, g)
    im = wf.add("LoadImage", "Photo", g, 0, image="jar.png")
    mi = wf.add("LoadImage", "Mask (white = change)", g, 0, image="jar_lid_mask.png")
    m = wf.add("ImageToMask", "Image to mask", g, 1, image=mi[0], channel="red")
    gm = wf.add("GrowMask", "Grow mask 12 px", g, 1, mask=m[0], expand=12, tapered_corners=True)
    p, n = prompts(wf, ck[1], "(matte black:1.2) metal screw lid on a frosted glass cosmetic jar, black lid, smooth "
                   "surface, soft studio light, product photography", g, col=1)
    e = wf.add("VAEEncode", "VAE Encode", g, 2, pixels=im[0], vae=ck[2])
    nm = wf.add("SetLatentNoiseMask", "Set Latent Noise Mask", g, 2, samples=e[0], mask=gm[0])
    k = sampler(wf, ck[0], p[0], n[0], nm[0], g, 2, seed=404, denoise=1.0)
    d = wf.add("VAEDecode", "VAE Decode", g, 3, samples=k[0], vae=ck[2])
    c = wf.add("ImageCompositeMasked", "Paste masked area only", g, 3, destination=im[0], source=d[0], x=0, y=0,
               resize_source=False, mask=gm[0])
    save(wf, c[0], "W04/new_lid", g, 3)
    return wf


def W05():
    wf = WF("W05", "Outpainting: from 16:9 to a panorama")
    g = "Outpainting"
    wf.note("Chapter 7 (outpainting). Pad Image for Outpainting adds empty strips and creates the mask.\n"
            "Here we use VAE Encode (for Inpainting): it fills the mask with neutral grey,\n"
            "so it needs denoise 1.0 (with lower values you get a grey patch).\n"
            "File: lake.png (pack folder inputs).\n\n" + LIC, g)
    ck = base(wf, g)
    im = wf.add("LoadImage", "Landscape 1344x768", g, 0, image="lake.png")
    pad = wf.add("ImagePadForOutpaint", "Add 256 px left and right", g, 1, image=im[0], left=256, top=0, right=256,
                 bottom=0, feathering=64)
    p, n = prompts(wf, ck[1], "wide panoramic photo of a calm mountain lake at golden hour, pine forest on both shores, "
                   "soft mist, natural colors", g, col=1)
    e = wf.add("VAEEncodeForInpaint", "VAE Encode (for Inpainting)", g, 2, pixels=pad[0], vae=ck[2], mask=pad[1],
               grow_mask_by=16)
    k = sampler(wf, ck[0], p[0], n[0], e[0], g, 2, seed=505, denoise=1.0)
    d = wf.add("VAEDecode", "VAE Decode", g, 3, samples=k[0], vae=ck[2])
    save(wf, d[0], "W05/panorama", g, 3)
    return wf


def W06():
    wf = WF("W06", "Model upscale: clean 2x for print")
    g = "Upscale"
    wf.note("Chapter 8. 4x model + scale by 0.5 = a clean 2x without artificial sharpening.\n"
            "Input: any finished image (e.g. the W01 result). Fix first, enlarge last.\n\n" + LIC_UP, g)
    im = wf.add("LoadImage", "Image to enlarge", g, 0, image="jar.png")
    um = wf.add("UpscaleModelLoader", "Load Upscale Model", g, 0, model_name=UPS)
    up = wf.add("ImageUpscaleWithModel", "Upscale Image (Using Model)", g, 1, upscale_model=um[0], image=im[0])
    sc = wf.add("ImageScaleBy", "Scale down to 2x", g, 1, image=up[0], upscale_method="lanczos", scale_by=0.5)
    save(wf, sc[0], "W06/product_2x", g, 2)
    return wf


def W07():
    wf = WF("W07", "Hi-res fix: second pass in latent space")
    g = "Hi-res fix"
    wf.note("Chapter 8. First an image at the model's native size (about 1 MP),\n"
            "then Upscale Latent By 1.5 and a second KSampler at denoise 0.5 adds detail.\n"
            "Why not 1248x1824 straight away? The model would start repeating objects.\n\n" + LIC, g)
    ck = base(wf, g)
    p, n = prompts(wf, ck[1], "cozy reading nook by a large window, rainy evening, warm lamp light, wooden shelves full of "
                   "books, knitted blanket, cinematic interior photography", g)
    l = wf.add("EmptyLatentImage", "Canvas 832x1216", g, 2, width=832, height=1216, batch_size=1)
    k1 = sampler(wf, ck[0], p[0], n[0], l[0], g, 2, seed=707, title="Sampler (pass 1)")
    d1 = wf.add("VAEDecode", "Decode pass 1", g, 2, samples=k1[0], vae=ck[2])
    wf.add("PreviewImage", "Preview pass 1", g, 2, images=d1[0])
    up = wf.add("LatentUpscaleBy", "Upscale Latent By 1.5", g, 3, samples=k1[0], upscale_method="nearest-exact", scale_by=1.5)
    k2 = sampler(wf, ck[0], p[0], n[0], up[0], g, 3, seed=707, steps=20, denoise=0.5, title="Sampler (pass 2)")
    d2 = wf.add("VAEDecode", "VAE Decode", g, 4, samples=k2[0], vae=ck[2])
    save(wf, d2[0], "W07/hires", g, 4)
    return wf


def W08():
    wf = WF("W08", "ControlNet Canny: same shape, new material")
    g = "ControlNet"
    wf.note("Chapter 10. Canny (built-in node) extracts the edges of the photo, and T2I-Adapter Canny SDXL\n"
            "keeps the new image on the same outline.\n"
            "strength 0.8, end 0.8 - the model is free for the last 20% of steps and refines texture better.\n"
            "Model: TencentARC t2i-adapter-canny-sdxl-1.0 (Apache 2.0) -> ComfyUI/models/controlnet.\n\n" + LIC, g)
    ck = base(wf, g)
    im = wf.add("LoadImage", "Reference photo", g, 0, image="jar.png")
    cn = wf.add("Canny", "Canny (edges)", g, 1, image=im[0], low_threshold=0.2, high_threshold=0.5)
    wf.add("PreviewImage", "Edge map preview", g, 1, images=cn[0])
    cl = wf.add("ControlNetLoader", "Load ControlNet Model", g, 0, control_net_name=CNET)
    p, n = prompts(wf, ck[1], "hand-made stoneware jar with a speckled cream glaze and a brushed copper lid, on a linen "
                   "cloth, soft daylight from a window, artisan product photography", g, col=1)
    ap = wf.add("ControlNetApplyAdvanced", "Apply ControlNet", g, 2, positive=p[0], negative=n[0], control_net=cl[0],
                image=cn[0], strength=0.8, start_percent=0.0, end_percent=0.8, vae=ck[2])
    l = wf.add("EmptyLatentImage", "Canvas 1024x1024", g, 2, width=1024, height=1024, batch_size=1)
    k = sampler(wf, ck[0], ap[0], ap[1], l[0], g, 3, seed=808)
    d = wf.add("VAEDecode", "VAE Decode", g, 3, samples=k[0], vae=ck[2])
    save(wf, d[0], "W08/canny", g, 3)
    return wf


def W09():
    wf = WF("W09", "LoRA: without and with LoRA side by side")
    g = "LoRA"
    wf.note("Chapter 11. Same seed, two passes: without LoRA and with LoRA (strength 0.8).\n"
            "LoRA: sd_xl_offset_example-lora_1.0 from the official SDXL repository (Open RAIL++-M) -\n"
            "deeper blacks and stronger contrast. File -> ComfyUI/models/loras.\n"
            "Always compare with the no-LoRA version, otherwise you don't know what it did.\n\n" + LIC, g)
    ck = base(wf, g)
    lo = wf.add("LoraLoader", "Load LoRA (0.8)", g, 0, model=ck[0], clip=ck[1], lora_name=LORA,
                strength_model=0.8, strength_clip=0.8)
    text = ("night street food market lit by paper lanterns, steam rising from a noodle stall, "
            "cinematic photography, deep shadows, warm highlights")
    l = wf.add("EmptyLatentImage", "Canvas 1216x832", g, 1, width=1216, height=832, batch_size=1)
    pa = wf.add("CLIPTextEncode", "Prompt (no LoRA)", g, 1, text=text, clip=ck[1])
    na = wf.add("CLIPTextEncode", "Negative (no LoRA)", g, 1, text=NEG, clip=ck[1])
    pb = wf.add("CLIPTextEncode", "Prompt (LoRA)", g, 2, text=text, clip=lo[1])
    nb = wf.add("CLIPTextEncode", "Negative (LoRA)", g, 2, text=NEG, clip=lo[1])
    ka = sampler(wf, ck[0], pa[0], na[0], l[0], g, 3, seed=909, title="Sampler (no LoRA)")
    kb = sampler(wf, lo[0], pb[0], nb[0], l[0], g, 3, seed=909, title="Sampler (LoRA)")
    da = wf.add("VAEDecode", "Decode (no LoRA)", g, 4, samples=ka[0], vae=ck[2])
    db = wf.add("VAEDecode", "Decode (LoRA)", g, 4, samples=kb[0], vae=ck[2])
    save(wf, stitch(wf, [da[0], db[0]], g, 4, "No LoRA | LoRA"), "W09/no_lora_vs_lora", g, 4)
    return wf


def W10():
    wf = WF("W10", "All together: LoRA + ControlNet + hi-res + upscale")
    g1, g2, g3 = "1 - Models", "2 - Generation", "3 - Finishing"
    wf.note("Chapter 13. Every layer has one job:\n"
            "- LoRA (0.6): contrast and mood\n- ControlNet Canny (0.7): product shape from the photo\n"
            "- weight 1.4 + 'white jar' in the negative: keeps the porcelain black\n"
            "- second pass (hi-res, denoise 0.45): detail\n- 4x model + scale down: print file.\n"
            "Test layers one by one: bypass a node (Ctrl+B) and compare.\n\n" + LIC + "\n" + LIC_UP, g1)
    ck = base(wf, g1)
    lo = wf.add("LoraLoader", "Load LoRA (0.6)", g1, 0, model=ck[0], clip=ck[1], lora_name=LORA,
                strength_model=0.6, strength_clip=0.6)
    cl = wf.add("ControlNetLoader", "Load ControlNet Model", g1, 0, control_net_name=CNET)
    um = wf.add("UpscaleModelLoader", "Load Upscale Model", g1, 0, model_name=UPS)
    im = wf.add("LoadImage", "Reference photo", g2, 0, image="jar.png")
    cn = wf.add("Canny", "Canny", g2, 0, image=im[0], low_threshold=0.2, high_threshold=0.5)
    p, n = prompts(wf, lo[1], "(polished black porcelain jar:1.4), plain smooth jar without label, gold lid, luxury skincare "
                   "packaging, on a wet black marble surface, dramatic rim light, dark moody studio, high-end advertising photography",
                   g2, col=1, neg="white jar, white porcelain, label, lettering, " + NEG)
    ap = wf.add("ControlNetApplyAdvanced", "Apply ControlNet", g2, 1, positive=p[0], negative=n[0], control_net=cl[0],
                image=cn[0], strength=0.7, start_percent=0.0, end_percent=0.8, vae=ck[2])
    l = wf.add("EmptyLatentImage", "Canvas 1024x1024", g2, 2, width=1024, height=1024, batch_size=1)
    k1 = sampler(wf, lo[0], ap[0], ap[1], l[0], g2, 2, seed=1114, title="Sampler (pass 1)")
    up = wf.add("LatentUpscaleBy", "Upscale Latent By 1.25", g3, 0, samples=k1[0], upscale_method="nearest-exact", scale_by=1.25)
    k2 = sampler(wf, lo[0], ap[0], ap[1], up[0], g3, 0, seed=1114, steps=20, denoise=0.45, title="Sampler (pass 2)")
    d = wf.add("VAEDecode", "VAE Decode", g3, 1, samples=k2[0], vae=ck[2])
    save(wf, d[0], "W10/campaign_1280", g3, 1, title="Save 1280")
    u = wf.add("ImageUpscaleWithModel", "Upscale 4x", g3, 2, upscale_model=um[0], image=d[0])
    s = wf.add("ImageScaleBy", "Scale down to 2560 px", g3, 2, image=u[0], upscale_method="lanczos", scale_by=0.5)
    save(wf, s[0], "W10/campaign_2560", g3, 2, title="Save 2560")
    return wf


def W11():
    wf = WF("W11", "Series: one workflow, many topics (for series.py)")
    g = "Series"
    wf.note("Chapter 15. Workflow for batch work. Nodes are titled Prompt / Sampler / Save,\n"
            "so scripts/series.py can swap the topic and seed for every row of topics.csv.\n"
            "By hand: type a topic in Prompt and set Batch count next to the Run button.\n\n" + LIC, g)
    ck = base(wf, g)
    p, n = prompts(wf, ck[1], "minimalist flat vector illustration of a hot air balloon over rolling hills, "
                   "pastel palette, plenty of empty space, clean background", g)
    l = wf.add("EmptyLatentImage", "Canvas 832x1216", g, 2, width=832, height=1216, batch_size=1)
    k = sampler(wf, ck[0], p[0], n[0], l[0], g, 2, seed=1212)
    d = wf.add("VAEDecode", "VAE Decode", g, 3, samples=k[0], vae=ck[2])
    save(wf, d[0], "W11/series", g, 3)
    return wf


ALL = [W01, W02, W03, W04, W05, W06, W07, W08, W09, W10, W11]
NAMES = {"W01": "W01_first_image", "W02": "W02_cfg_test", "W03": "W03_img2img_denoise",
         "W04": "W04_inpainting_mask", "W05": "W05_outpainting_panorama", "W06": "W06_upscale_2x",
         "W07": "W07_hires_fix", "W08": "W08_controlnet_canny", "W09": "W09_lora_comparison",
         "W10": "W10_all_together", "W11": "W11_series"}
DESC = {"W01": "first image", "W02": "CFG test", "W03": "img2img denoise scale", "W04": "inpainting with a mask",
        "W05": "outpainting", "W06": "2x upscale", "W07": "hi-res fix", "W08": "ControlNet Canny",
        "W09": "LoRA without/with", "W10": "complete workflow", "W11": "batch series"}

if __name__ == "__main__":
    out = sys.argv[1]
    for sub in ("ui", "api"):
        os.makedirs(os.path.join(out, sub), exist_ok=True)
    for f in ALL:
        wf = f()
        n = NAMES[wf.code]
        json.dump(wf.ui(info=INFO(wf.code, DESC[wf.code])), open(os.path.join(out, "ui", n + ".json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        json.dump(wf.api(), open(os.path.join(out, "api", n + ".api.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print(wf.code, len(wf.nodes))
