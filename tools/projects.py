"""All 20 companion workflows for 'From Noise to Income'. Run: python projects.py OUT_DIR"""
import json, os, sys
from wfgen import WF

Z_UNET, Z_CLIP, Z_VAE = "z_image_turbo_bf16.safetensors", "qwen_3_4b.safetensors", "ae.safetensors"
K_UNET, K_CLIP, K_VAE = "flux-2-klein-4b-fp8.safetensors", "qwen_3_4b.safetensors", "flux2-vae.safetensors"
UPSCALER = "4x_NMKD-Siax_200k.pth"

LIC_Z = ("MODELS (license category A — commercial use OK, checked Oct 2026):\n"
         "• Z-Image-Turbo — Apache 2.0 (Tongyi-MAI)\n• Qwen3-4B text encoder — Apache 2.0\n"
         "• ae.safetensors (FLUX.1 [schnell] VAE) — Apache 2.0\n"
         "8 GB VRAM: keep weight_dtype = fp8_e4m3fn. Re-check every LICENSE before you sell.")
LIC_K = ("MODELS (license category A — commercial use OK, checked Oct 2026):\n"
         "• FLUX.2 [klein] 4B — Apache 2.0 (Black Forest Labs). NOT the 9B or [dev] — those are non-commercial!\n"
         "• Qwen3-4B text encoder — Apache 2.0\n• FLUX.2 VAE — Apache 2.0")
LIC_UP = "• 4x NMKD-Siax 200k upscaler — WTFPL (OpenModelDB). Alternative: Real-ESRGAN x4plus (BSD-3)."
LIC_BG = ("• BiRefNet-general — MIT (node pack ComfyUI-RMBG, GPL-3.0 code).\n"
          "  Do NOT switch to RMBG-2.0 — CC BY-NC (non-commercial).")


# ---------- building blocks ----------
def z_models(wf, group="1 · Models"):
    u = wf.add("UNETLoader", "Load Z-Image-Turbo", group, unet_name=Z_UNET, weight_dtype="fp8_e4m3fn")
    c = wf.add("CLIPLoader", "Load text encoder (Qwen3-4B)", group, clip_name=Z_CLIP, type="lumina2")
    v = wf.add("VAELoader", "Load VAE", group, vae_name=Z_VAE)
    m = wf.add("ModelSamplingAuraFlow", "Model sampling (shift 3)", group, model=u[0], shift=3.0)
    return {"model": m[0], "clip": c[0], "vae": v[0]}


def z_t2i(wf, M, prompt, w, h, seed, group, col=0, label="", denoise=1.0, latent=None, steps=8):
    p = wf.add("CLIPTextEncode", f"Prompt{label}", group, col, text=prompt, clip=M["clip"])
    n = wf.add("ConditioningZeroOut", f"Negative (empty){label}", group, col, conditioning=p[0])
    if latent is None:
        latent = wf.add("EmptySD3LatentImage", f"Canvas {w}×{h}{label}", group, col, width=w, height=h, batch_size=1)[0]
    k = wf.add("KSampler", f"Sampler{label}", group, col, model=M["model"], seed=seed, steps=steps, cfg=1.0,
               sampler_name="res_multistep", scheduler="simple", positive=p[0], negative=n[0],
               latent_image=latent, denoise=denoise)
    d = wf.add("VAEDecode", f"Decode{label}", group, col, samples=k[0], vae=M["vae"])
    return d


def k_models(wf, group="1 · Models"):
    u = wf.add("UNETLoader", "Load FLUX.2 [klein] 4B", group, unet_name=K_UNET, weight_dtype="default")
    c = wf.add("CLIPLoader", "Load text encoder (Qwen3-4B)", group, clip_name=K_CLIP, type="flux2")
    v = wf.add("VAELoader", "Load FLUX.2 VAE", group, vae_name=K_VAE)
    return {"model": u[0], "clip": c[0], "vae": v[0]}


def k_gen(wf, K, prompt, group, seed, refs=(), size_from=None, w=1024, h=1024, col=0, label="", steps=4):
    """FLUX.2 [klein] 4B: text-to-image, or edit with 1–3 reference images (Set Reference Latent)."""
    p = wf.add("CLIPTextEncode", f"Instruction{label}", group, col, text=prompt, clip=K["clip"])
    cond = p[0]
    for i, r in enumerate(refs):
        e = wf.add("VAEEncode", f"Encode reference {i + 1}{label}", group, col, pixels=r, vae=K["vae"])
        cond = wf.add("ReferenceLatent", f"Set Reference Latent {i + 1}{label}", group, col, conditioning=cond, latent=e[0])[0]
    neg = wf.add("ConditioningZeroOut", f"Negative (empty){label}", group, col, conditioning=p[0])
    if size_from is not None:
        sz = wf.add("GetImageSize", f"Read size{label}", group, col, image=size_from)
        W, H = sz[0], sz[1]
    else:
        W, H = w, h
    lat = wf.add("EmptyFlux2LatentImage", f"Canvas{label}", group, col + 1, width=W, height=H, batch_size=1)
    sch = wf.add("Flux2Scheduler", f"Scheduler ({steps} steps){label}", group, col + 1, steps=steps, width=W, height=H)
    g = wf.add("CFGGuider", f"Guider (cfg 1){label}", group, col + 1, model=K["model"], positive=cond, negative=neg[0], cfg=1.0)
    s = wf.add("KSamplerSelect", f"Sampler type{label}", group, col + 1, sampler_name="euler")
    nz = wf.add("RandomNoise", f"Seed{label}", group, col + 1, noise_seed=seed)
    sa = wf.add("SamplerCustomAdvanced", f"Sample{label}", group, col + 1, noise=nz[0], guider=g[0], sampler=s[0], sigmas=sch[0], latent_image=lat[0])
    d = wf.add("VAEDecode", f"Decode{label}", group, col + 1, samples=sa[0], vae=K["vae"])
    return d


def prep_ref(wf, img, group, col=0, mp=1.0, label=""):
    return wf.add("ImageScaleToTotalPixels", f"Scale to ~{mp} MP{label}", group, col, image=img, upscale_method="lanczos",
                  megapixels=mp, resolution_steps=16)


def upscale4(wf, img, group, col=0):
    u = wf.add("UpscaleModelLoader", "Load upscaler", group, col, model_name=UPSCALER)
    return wf.add("ImageUpscaleWithModel", "Upscale ×4", group, col, upscale_model=u[0], image=img)


def save(wf, img, prefix, group, col=0, title="Save"):
    return wf.add("SaveImage", title, group, col, images=img, filename_prefix=prefix)


def offset_half(wf, img, size, group, col=0, label=""):
    """Wrap-around offset by half the tile (the 'offset & heal' trick) using only core nodes."""
    h2 = size // 2
    a = wf.add("ImageCrop", f"Left half{label}", group, col, image=img, width=h2, height=size, x=0, y=0)
    b = wf.add("ImageCrop", f"Right half{label}", group, col, image=img, width=h2, height=size, x=h2, y=0)
    hx = wf.add("ImageStitch", f"Swap halves (X){label}", group, col, image1=b[0], image2=a[0], direction="right",
                match_image_size=False, spacing_width=0, spacing_color="white")
    t = wf.add("ImageCrop", f"Top half{label}", group, col + 1, image=hx[0], width=size, height=h2, x=0, y=0)
    bo = wf.add("ImageCrop", f"Bottom half{label}", group, col + 1, image=hx[0], width=size, height=h2, x=0, y=h2)
    return wf.add("ImageStitch", f"Swap halves (Y){label}", group, col + 1, image1=bo[0], image2=t[0], direction="down",
                  match_image_size=False, spacing_width=0, spacing_color="white")


def cross_mask(wf, size, band, group, col=0):
    base = wf.add("SolidMask", "Empty mask", group, col, value=0.0, width=size, height=size)
    v = wf.add("SolidMask", "Vertical seam band", group, col, value=1.0, width=band, height=size)
    h = wf.add("SolidMask", "Horizontal seam band", group, col, value=1.0, width=size, height=band)
    m1 = wf.add("MaskComposite", "Add vertical band", group, col, destination=base[0], source=v[0], x=size // 2 - band // 2, y=0, operation="add")
    return wf.add("MaskComposite", "Add horizontal band", group, col, destination=m1[0], source=h[0], x=0, y=size // 2 - band // 2, operation="add")


def tile3x3(wf, img, group, col=0):
    r1 = wf.add("ImageStitch", "Row: 2 tiles", group, col, image1=img, image2=img, direction="right", match_image_size=False, spacing_width=0, spacing_color="white")
    r2 = wf.add("ImageStitch", "Row: 3 tiles", group, col, image1=r1[0], image2=img, direction="right", match_image_size=False, spacing_width=0, spacing_color="white")
    c1 = wf.add("ImageStitch", "2 rows", group, col, image1=r2[0], image2=r2[0], direction="down", match_image_size=False, spacing_width=0, spacing_color="white")
    return wf.add("ImageStitch", "3 rows = 3×3 preview", group, col, image1=c1[0], image2=r2[0], direction="down", match_image_size=False, spacing_width=0, spacing_color="white")


def seamless_heal(wf, M, img, size, prompt, seed, group):
    off = offset_half(wf, img, size, group, col=0)
    mask = cross_mask(wf, size, 160, group, col=2)
    enc = wf.add("VAEEncode", "Encode offset tile", group, 2, pixels=off[0], vae=M["vae"])
    nm = wf.add("SetLatentNoiseMask", "Only repaint the seam cross", group, 2, samples=enc[0], mask=mask[0])
    return z_t2i(wf, M, prompt, size, size, seed, group, col=3, label=" (heal)", denoise=0.7, latent=nm[0])


def alpha_cutout(wf, img, group, col=0, sensitivity=1.0):
    """Transparent PNG: BiRefNet (MIT) returns RGBA directly when background = Alpha."""
    return wf.add("BiRefNetRMBG", "Remove background (BiRefNet)", group, col, image=img, model="BiRefNet-general",
                  sensitivity=sensitivity, mask_blur=0, mask_offset=0, invert_output=False, refine_foreground=True,
                  unload_model=False, background="Alpha", background_color="#222222")


def bw_lineart(wf, img, group, col=0, threshold=0.6):
    """Pure black & white line art for print: threshold the luminance (no grey, no speckles)."""
    m = wf.add("ImageToMask", "Take luminance", group, col, image=img, channel="red")
    t = wf.add("ThresholdMask", f"Threshold {threshold}", group, col, mask=m[0], value=threshold)
    return wf.add("MaskToImage", "Pure black & white", group, col, mask=t[0])


def place_on_page(wf, img, page_w, page_h, margin, group, col=0, color=16777215, label="page"):
    inner_w, inner_h = page_w - 2 * margin, page_h - 2 * margin
    fit = wf.add("ResizeAndPadImage", f"Fit into safe area {inner_w}×{inner_h}", group, col, image=img, target_width=inner_w,
                 target_height=inner_h, padding_color="white", interpolation="lanczos")
    page = wf.add("EmptyImage", f"White {label} {page_w}×{page_h}", group, col, width=page_w, height=page_h, batch_size=1, color=color)
    return wf.add("ImageCompositeMasked", "Place artwork with margins", group, col, destination=page[0], source=fit[0], x=margin, y=margin, resize_source=False)


# ---------- projects ----------
def P01():
    wf = WF("P01", "Botanical poster set (6 posters, 2:3, print-ready)")
    M = z_models(wf)
    wf.note(LIC_Z + "\n" + LIC_UP, "1 · Models", title="Licenses")
    g = "2 · Prompt & generate"
    wf.note("Change ONLY the {plant} part between runs: monstera leaf, eucalyptus branch, fern frond, olive branch, "
            "ginkgo leaves, palm leaf. Keep the seed fixed while you tune the style.", g, title="How to use")
    img = z_t2i(wf, M, "minimalist botanical line art poster, a single monstera leaf, thin black ink lines, "
                "off-white paper background, generous negative space, centered composition, elegant, no text",
                832, 1248, 1001, g)
    save(wf, img[0], "book/P01_botanical/preview", g, 1, "Save preview (832×1248)")
    g3 = "3 · Upscale for print"
    up = upscale4(wf, img[0], g3)
    wf.note("Result: 3328×4992 px = 30×45 cm at ~282 DPI or 20×30 cm at 420 DPI. Crop A-sizes (1:1.41) in any editor "
            "or with an Image Crop node.", g3, title="Print sizes")
    save(wf, up[0], "book/P01_botanical/print", g3, 1, "Save print file")
    return wf


def P02():
    wf = WF("P02", "Large wall art for offices & cafés (100×150 cm)")
    M = z_models(wf)
    wf.note(LIC_Z + "\n" + LIC_UP, "1 · Models", title="Licenses")
    g = "2 · Generate"
    wf.note("Colour variants: keep the SAME seed and change only the palette words, e.g. 'sage green and cream', "
            "'deep navy and gold'.", g, title="Variants")
    img = z_t2i(wf, M, "large abstract landscape wall art, layered soft rolling hills, warm terracotta and sand tones, "
                "subtle paper grain texture, calm minimal atmosphere, gallery quality, no text",
                832, 1248, 2002, g)
    save(wf, img[0], "book/P02_wallart/preview", g, 1, "Save preview")
    g3 = "3 · Upscale ×4 → ×2"
    up = upscale4(wf, img[0], g3)
    big = wf.add("ImageScaleBy", "Resize ×2 (lanczos)", g3, 0, image=up[0], upscale_method="lanczos", scale_by=2.0)
    wf.note("6656×9984 px ≈ 113×169 cm at 150 DPI — enough for a large print seen from 2–3 m. Ask the print shop for "
            "their file format and colour profile; convert to CMYK in their RIP or a free editor (Krita/GIMP).", g3, 1, "Print notes")
    save(wf, big[0], "book/P02_wallart/print_150dpi", g3, 1, "Save large print file")
    return wf


def P03():
    wf = WF("P03", "Seamless pattern tile (textile & paper) + 3×3 preview")
    M = z_models(wf)
    wf.note(LIC_Z + "\nNo custom nodes needed — the seamless trick uses only core nodes.", "1 · Models", title="Licenses")
    g = "2 · Generate tile"
    prompt = ("seamless repeating pattern, small scattered lemons and green leaves, flat vector illustration, "
              "limited palette: cream, olive, mustard, even spacing, textile print, no text")
    img = z_t2i(wf, M, prompt, 1024, 1024, 3003, g)
    g3 = "3 · Offset & heal the seams"
    wf.note("The tile is shifted by half its size (with wrap-around), so the hidden edges meet in the middle as a cross. "
            "Only that cross is repainted (denoise 0.7). The outer edges now repeat perfectly.", g3, 1, "How it works")
    healed = seamless_heal(wf, M, img[0], 1024, prompt, 3004, g3)
    g4 = "4 · Save tile & 3×3 check"
    save(wf, healed[0], "book/P03_pattern/tile", g4, 0, "Save seamless tile")
    prev = tile3x3(wf, healed[0], g4, 1)
    save(wf, prev[0], "book/P03_pattern/preview_3x3", g4, 2, "Save 3×3 preview")
    return wf


def P04():
    wf = WF("P04", "Children's book illustrations — character sheet → scenes")
    K = k_models(wf)
    wf.note(LIC_K + "\nOne model family for both steps keeps RAM use low (8 GB VRAM / 32 GB RAM tested).", "1 · Models", title="Licenses")
    g = "2 · Character sheet"
    sheet = k_gen(wf, K, "Character sheet of a small red fox wearing a yellow scarf and round glasses: front view, side view and "
                  "back view standing next to each other, children's book illustration, soft watercolor texture, warm pastel "
                  "palette, plain white background, consistent proportions, no text.", g, 4004, w=1344, h=768, label=" (sheet)")
    save(wf, sheet[0], "book/P04_kidsbook/character_sheet", g, 2, "Save character sheet")
    g4 = "3 · Scene from the sheet"
    wf.note("FLUX.2 [klein] 4B reads the character sheet as a reference and keeps the fox the same. Write one scene per run; "
            "leave the top third empty for the book text.", g4, 0, "How to use")
    ref = prep_ref(wf, sheet[0], g4, 0)
    scene = k_gen(wf, K, "Use the fox from the reference image (same yellow scarf, same round glasses, same watercolor style). "
                  "The fox is reading a book under a big oak tree on a sunny meadow, children's book illustration, soft watercolor, "
                  "warm pastel palette, simple background, empty sky in the top third for text.",
                  g4, 4005, refs=[ref[0]], w=1088, h=1360, col=1)
    save(wf, scene[0], "book/P04_kidsbook/scene", g4, 3, "Save scene")
    return wf


def P05():
    wf = WF("P05", "Brand mascot — one character, many scenes (+ transparent PNG)")
    K = k_models(wf)
    wf.note(LIC_K + "\n" + LIC_BG, "1 · Models", title="Licenses")
    g = "2 · Mascot design"
    m = k_gen(wf, K, "Friendly bakery mascot character: a round smiling bread bun with small arms and legs, wearing a tiny baker "
              "hat, two-color design teal and orange, flat vector style, thick clean outline, full body, front view, plain white "
              "background, no text.", g, 5005, w=1024, h=1024, label=" (mascot)")
    save(wf, m[0], "book/P05_mascot/mascot", g, 2, "Save mascot")
    cut = alpha_cutout(wf, m[0], g, 2)
    save(wf, cut[0], "book/P05_mascot/mascot_transparent", g, 2, "Save transparent PNG")
    g4 = "3 · Scene with the same mascot"
    ref = prep_ref(wf, m[0], g4, 0)
    sc = k_gen(wf, K, "The same bread bun mascot from the reference image (same teal and orange colors, same baker hat, same "
               "flat vector style) is happily carrying a tray of fresh croissants in a cozy bakery, flat vector illustration, "
               "clean outline, simple warm background.", g4, 5006, refs=[ref[0]], w=1024, h=1024, col=1)
    save(wf, sc[0], "book/P05_mascot/scene", g4, 3, "Save scene")
    return wf


def P06():
    wf = WF("P06", "Consistent brand image series (style guide in a prompt)")
    M = z_models(wf)
    wf.note(LIC_Z, "1 · Models", title="Licenses")
    g = "2 · Style guide + subject"
    wf.note("STYLE (never change): editorial photo style, soft natural window light, muted palette of cream, forest green "
            "and brass, clean composition, lots of negative space.\nSUBJECTS (change one per run): ceramic cup on a wooden "
            "table / hands holding fresh herbs / linen napkin and cutlery / teapot on a tray.", g, title="Style guide")
    img = z_t2i(wf, M, "ceramic tea cup on a wooden table, editorial photo style, soft natural window light, muted palette "
                "of cream, forest green and brass, clean composition, lots of negative space, no text, no logo",
                1024, 1024, 6006, g, col=1)
    save(wf, img[0], "book/P06_brandseries/image", g, 2, "Save")
    return wf


def P07():
    wf = WF("P07", "Social media pack for a local business (1:1, 4:5, 9:16 + headline)")
    M = z_models(wf)
    wf.note(LIC_Z, "1 · Models", title="Licenses")
    base = ("calm physiotherapy treatment room interior, soft daylight, green plants, light wood, clean modern style, "
            "empty space on the left for text, no text, no people")
    out = {}
    for i, (lab, w, h, col) in enumerate([("1:1", 1024, 1024, 0), ("4:5", 896, 1120, 1), ("9:16", 720, 1280, 2)]):
        g = f"{i + 2} · Format {lab}"
        out[lab] = z_t2i(wf, M, base, w, h, 7007, g, label=f" {lab}")
        save(wf, out[lab][0], f"book/P07_social/{lab.replace(':', 'x')}", g, 1, f"Save {lab}")
    g = "5 · Headline (optional)"
    wf.note("Draw Text Overlay is a core node — quick headlines without Canva/Photoshop. For brand fonts and precise "
            "layout, finish in a free editor (Photopea, GIMP, Krita).", g, title="Text")
    t = wf.add("TextOverlay", "Headline", g, 0, images=out["1:1"][0], text="Back pain? Book a free check-up",
               font_size=6.0, color="#ffffff", position="bottom", align="center", outline=True)
    save(wf, t[0], "book/P07_social/1x1_headline", g, 1, "Save with headline")
    return wf


def P08():
    wf = WF("P08", "New backgrounds for product photos (product pixels stay 100% original)")
    K = k_models(wf)
    wf.note(LIC_K + "\n" + LIC_BG, "1 · Models", title="Licenses")
    g = "2 · Product photo"
    wf.note("Load the client's product photo (any background). The product is cut out with BiRefNet and pasted back on top "
            "at the end, so labels and logos are never redrawn by AI.", g, title="How to use")
    li = wf.add("LoadImage", "Product photo", g, 0, image="product.png")
    sc = prep_ref(wf, li[0], g, 1)
    cut = alpha_cutout(wf, sc[0], g, 1)
    g3 = "3 · New scene (FLUX.2 klein edit)"
    gen = k_gen(wf, K, "Place this exact product on a bright scandinavian kitchen countertop, morning light from a window on "
                "the left, soft natural shadows, blurred background with plants, professional product photography. Keep "
                "the product unchanged.", g3, 8008, refs=[sc[0]], size_from=sc[0], col=0)
    g4 = "4 · Paste original product back"
    comp = wf.add("ImageCompositeMasked", "Original product on top", g4, 0, destination=gen[0], source=sc[0], x=0, y=0,
                  resize_source=False, mask=cut[1])
    save(wf, comp[0], "book/P08_product_bg/kitchen", g4, 1, "Save scene")
    return wf


def P09():
    wf = WF("P09", "Packaging concepts (keep the jar, try new labels)")
    K = k_models(wf)
    wf.note(LIC_K, "1 · Models", title="Licenses")
    g = "2 · Packaging photo or sketch"
    li = wf.add("LoadImage", "Jar / box photo", g, 0, image="jar.png")
    sc = prep_ref(wf, li[0], g, 0)
    g3 = "3 · Label concept"
    wf.note("FLUX.2 [klein] keeps the shape of the jar from the reference — no depth map needed. Short brand names render "
            "well; check spelling and redo the final logo by hand (or with a designer).", g3, 0, "Tip")
    out = k_gen(wf, K, "Keep this exact glass jar shape and camera angle. Add a minimalist kraft paper label with a small "
                "hand-drawn bee illustration and the words \"WILD MEADOW HONEY\" in an elegant serif font, golden honey inside, "
                "studio product shot, soft light, plain light background.", g3, 9011, refs=[sc[0]], size_from=sc[0], col=1)
    save(wf, out[0], "book/P09_packaging/concept", g3, 3, "Save concept")
    return wf


def P10():
    wf = WF("P10", "Presentation & campaign visuals (16:9 metaphors)")
    M = z_models(wf)
    wf.note(LIC_Z, "1 · Models", title="Licenses")
    g = "2 · Metaphor 16:9"
    wf.note("Metaphor list: teamwork = paper boats tied together; growth = seedling in a cracked pot; security = "
            "lighthouse in calm sea; speed = paper plane trail. Keep the palette words identical.", g, title="Ideas")
    img = z_t2i(wf, M, "conceptual illustration of teamwork, several paper boats connected by a red thread on calm water, "
                "calm blue and coral palette, soft 3d paper craft style, empty space on the right for a slide title, no text",
                1344, 768, 10010, g, col=1)
    save(wf, img[0], "book/P10_slides/metaphor", g, 2, "Save")
    return wf


def P11():
    wf = WF("P11", "2D game asset pack — icons on transparent background")
    M = z_models(wf)
    wf.note(LIC_Z + "\n" + LIC_BG, "1 · Models", title="Licenses")
    g = "2 · Item"
    wf.note("Keep the style ending identical for all 40 items: sword, shield, key, map, potion, coins, book, scroll, gem…",
            g, title="Item list")
    img = z_t2i(wf, M, "single fantasy potion bottle with purple liquid, game item icon, hand-painted style, thick dark outline, "
                "centered, isolated on plain white background, no text", 1024, 1024, 11011, g, col=1)
    g3 = "3 · Transparent PNG 512 px"
    cut = alpha_cutout(wf, img[0], g3, 0)
    small = wf.add("ImageScale", "Resize to 512×512", g3, 0, image=cut[0], upscale_method="lanczos", width=512, height=512, crop="disabled")
    save(wf, small[0], "book/P11_gameassets/potion", g3, 1, "Save icon (RGBA)")
    return wf


def P12():
    wf = WF("P12", "Seamless material textures + depth map")
    M = z_models(wf)
    wf.note(LIC_Z + "\n• Depth Anything V2 SMALL (vits) — Apache 2.0. Base/Large are CC BY-NC — do not use for paid work.",
            "1 · Models", title="Licenses")
    g = "2 · Texture"
    prompt = ("top-down orthographic photo of weathered oak wood planks, even flat lighting, no shadows, high detail "
              "texture, seamless material, no text")
    img = z_t2i(wf, M, prompt, 1024, 1024, 12012, g)
    g3 = "3 · Make it seamless"
    healed = seamless_heal(wf, M, img[0], 1024, prompt, 12013, g3)
    g4 = "4 · Save + depth map + 3×3 check"
    save(wf, healed[0], "book/P12_textures/oak_albedo", g4, 0, "Save texture")
    d = wf.add("DepthAnythingV2Preprocessor", "Depth map (V2 Small)", g4, 0, image=healed[0], ckpt_name="depth_anything_v2_vits.pth", resolution=1024)
    save(wf, d[0], "book/P12_textures/oak_depth", g4, 1, "Save depth map")
    prev = tile3x3(wf, healed[0], g4, 2)
    save(wf, prev[0], "book/P12_textures/oak_preview_3x3", g4, 2, "Save 3×3 preview")
    return wf


def P13():
    wf = WF("P13", "Reframe & repair photos (outpaint square → 16:9, remove defects)")
    K = k_models(wf)
    wf.note(LIC_K + "\n• LaMa — Apache 2.0 (Lama Remover node from ComfyUI-RMBG).", "1 · Models", title="Licenses")
    g = "2 · Photo & repair"
    wf.note("Right-click the Load Image node → Open in MaskEditor and paint over small defects (dust, cables, a sign). "
            "Lama Remover fills them. With an empty mask nothing is changed.", g, title="Repair")
    li = wf.add("LoadImage", "Client photo (square)", g, 0, image="cafe.png")
    sc = wf.add("ImageScale", "Normalise to 1024×1024", g, 0, image=li[0], upscale_method="lanczos", width=1024, height=1024, crop="center")
    mi = wf.add("MaskToImage", "Painted mask → image", g, 1, mask=li[1])
    ms = wf.add("ImageScale", "Mask to 1024×1024", g, 1, image=mi[0], upscale_method="bilinear", width=1024, height=1024, crop="center")
    mk = wf.add("ImageToMask", "Image → mask", g, 1, image=ms[0], channel="red")
    fixed = wf.add("AILab_LamaRemover", "Remove painted defects (LaMa)", g, 2, images=sc[0], masks=mk[0], removal_strength=230, edge_smoothness=8, unload_model=True)
    g3 = "3 · Extend to 16:9"
    pad = wf.add("ImagePadForOutpaint", "Add 400 px left & right", g3, 0, image=fixed[0], left=400, top=0, right=400, bottom=0, feathering=0)
    gen = k_gen(wf, K, "Extend this photo to the left and right: fill the plain grey areas with a natural continuation of the "
                "same bright cafe interior, matching wooden tables, plants, warm daylight and perspective. Do not change the "
                "middle of the photo.", g3, 13013, refs=[pad[0]], w=1824, h=1024, col=1)
    g4 = "4 · Keep the original centre"
    comp = wf.add("ImageCompositeMasked", "Paste original centre back", g4, 0, destination=gen[0], source=fixed[0], x=400, y=0, resize_source=False)
    save(wf, comp[0], "book/P13_reframe/cafe_16x9", g4, 1, "Save 16:9")
    return wf


def P14():
    wf = WF("P14", "Niche collection made in batches (template for batch.py)")
    M = z_models(wf)
    wf.note(LIC_Z, "1 · Models", title="Licenses")
    g = "2 · Template"
    wf.note("This file is driven by scripts/batch.py + topics.csv (export: Workflow → Export (API)). The script replaces "
            "the prompt of node 'Prompt', the seed of 'Sampler' and the prefix of 'Save'. Upscale only the winners with P01 "
            "group 3.", g, title="Batch")
    img = z_t2i(wf, M, "antique style map of an imaginary island, hand-drawn coastline, compass rose, sepia ink on aged paper, "
                "nautical decorations, sea monsters in the margins, no readable text", 832, 1248, 14014, g, col=1)
    save(wf, img[0], "book/P14_batch/island_map", g, 2, "Save")
    return wf


def P15():
    wf = WF("P15", "One product, many variants (colourways & backgrounds)")
    K = k_models(wf)
    wf.note(LIC_K, "1 · Models", title="Licenses")
    g = "2 · Base design"
    li = wf.add("LoadImage", "Base product design", g, 0, image="tote.png")
    sc = prep_ref(wf, li[0], g, 0)
    variants = [("forest_green", "Change only the colour of the bag to forest green. Keep the print, shape, light and background identical."),
                ("beach", "Keep the bag exactly the same and place it on a sunny beach with soft sand and turquoise sea in the background."),
                ("navy_gold", "Change the bag colour to deep navy and the lemon print to gold foil. Keep everything else identical.")]
    for i, (slug, instr) in enumerate(variants):
        gg = f"{i + 3} · Variant: {slug}"
        out = k_gen(wf, K, instr, gg, 15015 + i, refs=[sc[0]], size_from=sc[0], label=f" {i + 1}")
        save(wf, out[0], f"book/P15_variants/{slug}", gg, 2, f"Save {slug}")
    return wf


def P16():
    wf = WF("P16", "Portfolio contact sheet (no models needed)")
    g = "1 · Four best works"
    wf.note("Pick your 4 best finished images (any size). The sheet is built with core nodes only — no AI model, "
            "so it runs on any computer.", g, title="How to use")
    imgs = [wf.add("LoadImage", f"Work {i + 1}", g, i // 2, image=f"portfolio_{i + 1}.png") for i in range(4)]
    sq = [wf.add("ImageScale", f"Square crop {i + 1}", g, 2, image=im[0], upscale_method="lanczos", width=800, height=800, crop="center") for i, im in enumerate(imgs)]
    g2 = "2 · Layout"
    r1 = wf.add("ImageStitch", "Row 1", g2, 0, image1=sq[0][0], image2=sq[1][0], direction="right", match_image_size=False, spacing_width=24, spacing_color="white")
    r2 = wf.add("ImageStitch", "Row 2", g2, 0, image1=sq[2][0], image2=sq[3][0], direction="right", match_image_size=False, spacing_width=24, spacing_color="white")
    grid = wf.add("ImageStitch", "2×2 grid", g2, 0, image1=r1[0], image2=r2[0], direction="down", match_image_size=False, spacing_width=24, spacing_color="white")
    t = wf.add("TextOverlay", "Your name & service", g2, 1, images=grid[0], text="Your Name — AI-assisted illustration & product visuals",
               font_size=3.0, color="#ffffff", position="bottom", align="center", outline=True)
    save(wf, t[0], "book/P16_portfolio/contact_sheet", g2, 1, "Save sheet")
    return wf


# ---------- new projects for Amazon (EN) and Japan ----------
def P17():
    wf = WF("P17", "Amazon KDP 'Bold & Easy' large-print coloring page (8.5×11 in, with bleed)")
    M = z_models(wf)
    wf.note(LIC_Z + "\n" + LIC_UP + "\nKDP: tick 'AI-generated' for images in the content questionnaire.", "1 · Models", title="Licenses")
    g = "2 · Line art"
    wf.note("Bold & Easy = thick outlines, big simple shapes, no tiny details — for seniors, beginners and relaxed colouring. "
            "One theme per book (cozy cafe, farm animals, seasons…), 40–50 pages.", g, title="Niche")
    img = z_t2i(wf, M, "bold and easy coloring book page for adults, a cute cat sleeping in a cozy armchair with a cup of tea and "
                "a potted plant, very thick clean black outlines, large simple shapes, no shading, no grey, no hatching, pure "
                "white background, black and white line art, no text", 896, 1168, 17017, g, col=1)
    g3 = "3 · Print page 2588×3375 px (300 DPI)"
    up = upscale4(wf, img[0], g3, 0)
    bw = bw_lineart(wf, up[0], g3, 1, 0.6)
    page = place_on_page(wf, bw[0], 2588, 3375, 150, g3, 2)
    wf.note("8.5×11 in + 0.125 in bleed = 8.625×11.25 in → 2588×3375 px at 300 DPI. Artwork stays inside a 150 px "
            "(0.5 in) safe margin. Export the pages to one PDF (Krita, GIMP, or img2pdf).", g3, 2, "KDP specs")
    save(wf, page[0], "book/P17_kdp_coloring/page", g3, 3, "Save page")
    return wf


def P18():
    wf = WF("P18", "Etsy clipart bundle — transparent PNG, 4096 px")
    M = z_models(wf)
    wf.note(LIC_Z + "\n" + LIC_UP + "\n" + LIC_BG, "1 · Models", title="Licenses")
    g = "2 · Clipart element"
    wf.note("One theme, ~20 elements (lemon slice, whole lemon, leaf, blossom, jug…). Same style words in every prompt. "
            "Sell as a ZIP + commercial-use licence PDF, disclose AI in the listing.", g, title="Bundle")
    img = z_t2i(wf, M, "watercolor clipart of a single lemon slice with two green leaves, hand-painted, soft edges, vibrant "
                "yellow, isolated on plain white background, centered, no shadow, no text", 1024, 1024, 18018, g, col=1)
    g3 = "3 · Cut out & upscale"
    cut = alpha_cutout(wf, img[0], g3, 0)
    up = upscale4(wf, img[0], g3, 1)
    mi = wf.add("MaskToImage", "Mask → image", g3, 2, mask=cut[1])
    mu = wf.add("ImageScale", "Mask to 4096 px", g3, 2, image=mi[0], upscale_method="bilinear", width=4096, height=4096, crop="disabled")
    m2 = wf.add("ImageToMask", "Image → mask", g3, 2, image=mu[0], channel="red")
    inv = wf.add("InvertMask", "Invert (alpha convention)", g3, 2, mask=m2[0])
    rgba = wf.add("JoinImageWithAlpha", "4096 px with transparency", g3, 3, image=up[0], alpha=inv[0])
    save(wf, rgba[0], "book/P18_etsy_clipart/lemon_slice", g3, 3, "Save PNG (RGBA)")
    return wf


def P19():
    wf = WF("P19", "Amazon.co.jp adult coloring book 大人の塗り絵 — seasonal flowers & wagara (A4)")
    M = z_models(wf)
    wf.note(LIC_Z + "\n" + LIC_UP + "\nKDP (also amazon.co.jp): disclose AI-generated content.", "1 · Models", title="Licenses")
    g = "2 · Line art"
    wf.note("Japanese buyers love seasonal themes (桜 sakura, 紫陽花 hydrangea, 紅葉 autumn leaves, 椿 camellia) and "
            "traditional patterns (青海波 seigaiha, 麻の葉 asanoha, 七宝 shippo). Fine lines, medium detail, calm mood.", g, title="Niche (JP)")
    img = z_t2i(wf, M, "adult coloring book page, cherry blossom branches over a traditional japanese seigaiha wave pattern, "
                "elegant fine clean black outlines, medium detail, balanced composition, no shading, no grey, pure white "
                "background, black and white line art, no text", 880, 1248, 19019, g, col=1)
    g3 = "3 · A4 page with bleed 2519×3583 px"
    up = upscale4(wf, img[0], g3, 0)
    bw = bw_lineart(wf, up[0], g3, 1, 0.55)
    page = place_on_page(wf, bw[0], 2519, 3583, 150, g3, 2)
    wf.note("A4 (8.27×11.69 in) + 0.125 in bleed = 8.395×11.94 in → 2519×3583 px at 300 DPI; safe margin 150 px. "
            "Print one-sided pages (blank backs) so markers don't bleed through.", g3, 2, "KDP specs")
    save(wf, page[0], "book/P19_jp_nurie/page", g3, 3, "Save page")
    return wf


def P20():
    wf = WF("P20", "LINE sticker set — original kawaii character (370×320 px, transparent)")
    M = z_models(wf)
    wf.note(LIC_Z + "\n" + LIC_BG + "\nLINE Creators Market: original characters only, no logos or famous characters. "
            "Check the current review guidelines before you submit.", "1 · Models", title="Licenses")
    g = "2 · Sticker pose"
    wf.note("Keep the character description identical and change only the pose/emotion: waving, thank you bow, OK sign, "
            "sleepy, crying, happy jump, heart, ganbatte fist… A set is 8, 16, 24, 32 or 40 stickers.", g, title="Poses")
    img = z_t2i(wf, M, "cute chibi kawaii sticker of an original fluffy white sheep character with a pink scarf, waving hello "
                "happily, big sparkling eyes, thick dark outline, simple flat colors, white sticker border, full body, "
                "isolated on plain white background, no text", 1024, 1024, 20020, g, col=1)
    g3 = "3 · LINE format 370×320 + 10 px margin"
    cut = alpha_cutout(wf, img[0], g3, 0)
    fit = wf.add("ResizeAndPadImage", "Fit 350×300 (RGB)", g3, 1, image=img[0], target_width=350, target_height=300, padding_color="white", interpolation="lanczos")
    mi = wf.add("MaskToImage", "Mask → image", g3, 1, mask=cut[1])
    fitm = wf.add("ResizeAndPadImage", "Fit 350×300 (mask)", g3, 1, image=mi[0], target_width=350, target_height=300, padding_color="black", interpolation="lanczos")
    can = wf.add("EmptyImage", "White 370×320", g3, 2, width=370, height=320, batch_size=1, color=16777215)
    canm = wf.add("EmptyImage", "Black 370×320", g3, 2, width=370, height=320, batch_size=1, color=0)
    rgb = wf.add("ImageCompositeMasked", "Place with 10 px margin", g3, 2, destination=can[0], source=fit[0], x=10, y=10, resize_source=False)
    mm = wf.add("ImageCompositeMasked", "Place mask with 10 px margin", g3, 2, destination=canm[0], source=fitm[0], x=10, y=10, resize_source=False)
    m2 = wf.add("ImageToMask", "Image → mask", g3, 3, image=mm[0], channel="red")
    inv = wf.add("InvertMask", "Invert (alpha convention)", g3, 3, mask=m2[0])
    rgba = wf.add("JoinImageWithAlpha", "Sticker with transparency", g3, 3, image=rgb[0], alpha=inv[0])
    save(wf, rgba[0], "book/P20_line_stickers/01_hello", g3, 3, "Save sticker PNG")
    return wf


def CH07():
    wf = WF("CH07", "Your first workflow — five nodes (chapter 7)")
    g = "Five nodes"
    wf.note("The simplest workflow there is: one all-in-one checkpoint (SDXL base 1.0, CreativeML Open RAIL++-M, "
            "commercial use allowed with a list of prohibited uses). Change the prompt, keep the rest, press Run.", g, title="Read me")
    ck = wf.add("CheckpointLoaderSimple", "1 · Load Checkpoint", g, 1, ckpt_name="sd_xl_base_1.0.safetensors")
    p = wf.add("CLIPTextEncode", "2a · Positive prompt", g, 1, text="minimalist botanical line art, single monstera leaf, thin black ink lines, off-white background, generous negative space, centered poster composition", clip=ck[1])
    n = wf.add("CLIPTextEncode", "2b · Negative prompt", g, 1, text="text, watermark, signature, frame, clutter, blurry", clip=ck[1])
    l = wf.add("EmptyLatentImage", "3 · Empty Latent 832×1216", g, 2, width=832, height=1216, batch_size=1)
    k = wf.add("KSampler", "4 · KSampler", g, 2, model=ck[0], seed=42, steps=28, cfg=6.0, sampler_name="dpmpp_2m", scheduler="karras", positive=p[0], negative=n[0], latent_image=l[0], denoise=1.0)
    d = wf.add("VAEDecode", "5a · VAE Decode", g, 3, samples=k[0], vae=ck[2])
    save(wf, d[0], "book/CH07_first/botanical", g, 3, "5b · Save Image")
    return wf


ALL = [CH07, P01, P02, P03, P04, P05, P06, P07, P08, P09, P10, P11, P12, P13, P14, P15, P16, P17, P18, P19, P20]

FILE_NAMES = {
    "CH07": "CH07_first_workflow_sdxl",
    "P01": "P01_botanical_poster_set", "P02": "P02_large_wall_art", "P03": "P03_seamless_pattern",
    "P04": "P04_childrens_book_illustrations", "P05": "P05_brand_mascot", "P06": "P06_brand_image_series",
    "P07": "P07_social_media_pack", "P08": "P08_product_new_background", "P09": "P09_packaging_concepts",
    "P10": "P10_presentation_visuals", "P11": "P11_game_asset_icons", "P12": "P12_seamless_textures_depth",
    "P13": "P13_reframe_and_repair", "P14": "P14_batch_niche_collection", "P15": "P15_product_variants",
    "P16": "P16_portfolio_contact_sheet", "P17": "P17_kdp_bold_easy_coloring", "P18": "P18_etsy_clipart_bundle",
    "P19": "P19_amazon_jp_nurie_coloring", "P20": "P20_line_stickers",
}

if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(os.path.join(out, "ui"), exist_ok=True)
    os.makedirs(os.path.join(out, "api"), exist_ok=True)
    for f in ALL:
        wf = f()
        name = FILE_NAMES[wf.code]
        with open(os.path.join(out, "ui", name + ".json"), "w", encoding="utf-8") as fh:
            json.dump(wf.ui(), fh, ensure_ascii=False, indent=1)
        with open(os.path.join(out, "api", name + ".api.json"), "w", encoding="utf-8") as fh:
            json.dump(wf.api(), fh, ensure_ascii=False, indent=1)
        print(wf.code, len(wf.nodes), "nodes")
