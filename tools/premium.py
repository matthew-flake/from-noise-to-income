"""Premium P01-P16 (v2): prompts from the author's prompt sheet, best category-A model per task."""
from wfgen import WF
from projects import (z_models, z_t2i, k_models, k_gen, prep_ref, upscale4, save, seamless_heal, tile3x3,
                      alpha_cutout, LIC_Z, LIC_K, LIC_UP, LIC_BG)

NEG_SDXL = ("low quality, blurry, pixelated, poorly composed, distorted proportions, malformed objects, duplicated elements, "
            "inconsistent perspective, unnatural lighting, excessive saturation, muddy colors, compression artifacts, unwanted text, "
            "watermark, signature, random letters, fake logos, recognizable trademarks, recognizable copyrighted characters, "
            "imitation of existing commercial artwork, visible image borders, unfinished details")


def J(*parts):
    return " ".join(p.strip() for p in parts)


P1_SPECIES = ["peony", "magnolia", "eucalyptus", "iris", "fern", "dahlia"]
P1 = J("Create an original, exquisite botanical fine-art illustration featuring {x}.",
       "A meticulously composed botanical specimen with elegant stems, delicate flowers, organically arranged leaves, intricate natural veins, and subtle variations in botanical structure.",
       "Traditional watercolor painting combined with delicate hand-drawn ink details, translucent pigment layers, natural paper grain, sophisticated muted sage green, dusty olive, warm ivory, and subtle earthy tones.",
       "Elegant archival botanical illustration aesthetic, exceptional artistic craftsmanship, balanced vertical composition, beautiful negative space, intricate details, premium printable wall art, timeless interior decoration.",
       "Original composition, no artist signatures, no typography, no logos, no watermarks. Portrait orientation, 4:5 aspect ratio.")
P2 = J("Create an original monumental contemporary abstract artwork suitable for an elegant modern corporate office.",
       "Flowing organic geometric shapes, sculptural plaster textures, layered mineral pigments, architectural forms, sophisticated interplay between matte and subtly reflective surfaces.",
       "Refined warm ivory, sandstone beige, soft terracotta, muted taupe, and restrained metallic champagne-gold accents.",
       "Tactile surfaces, realistic plaster relief, subtle imperfections, delicate material transitions, beautiful asymmetrical balance, controlled visual rhythm.",
       "The artwork should communicate elegance, confidence, creativity, and architectural sophistication.",
       "Museum-quality abstract fine art, carefully controlled composition, exceptional surface detail, visually striking but harmonious.",
       "Flat front-facing artwork filling the entire frame, without a surrounding room, furniture, or picture frame.",
       "Original abstract design, no recognizable existing artworks, no signatures, no typography, no logos. Landscape orientation, 3:2 aspect ratio.")
P3 = J("Create an original sophisticated seamless repeating geometric pattern inspired by classical decorative geometry.",
       "Elegant interlocking arches, stylized fan-shaped elements, rhythmic curves, refined symmetrical ornamentation, precise geometric construction.",
       "Deep emerald green, warm ivory, muted jade, and subtle antique-brass color accents.",
       "Perfectly balanced motif distribution, consistent decorative line thickness, clean edges, excellent visual rhythm, harmonious spacing.",
       "Premium decorative surface design suitable for wallpaper, luxury packaging, textile printing, and stationery.",
       "Flat two-dimensional artwork, no perspective, no shadows, no photographic objects, no fabric mockup.",
       "Design the geometric elements to connect continuously across all four tile boundaries.",
       "Original ornament design, no recognizable branded patterns, no typography, no logos, no watermarks. Square format.")
P4 = J("Create an original enchanting children's picture-book illustration.",
       "A small curious red fox with bright amber eyes, soft orange fur, a fluffy tail, and a distinctive hand-knitted teal scarf discovers a magical woodland clearing.",
       "The fox stands beside enormous softly glowing mushrooms while tiny golden fireflies float through the air.",
       "Ancient trees, delicate flowers, lush moss, whimsical forest vegetation, and warm sunlight filtering gently through the leaves.",
       "Expressive character design, charming proportions, emotional storytelling, delicate watercolor washes combined with textured gouache brushwork.",
       "A harmonious palette of forest green, warm amber, muted teal, dusty peach, and soft gold.",
       "Beautifully composed illustration with gentle depth, atmospheric perspective, intricate environmental details, and a magical but comforting atmosphere.",
       "Reserve an uncluttered area in the upper-right portion for future story text.",
       "Original fictional character and environment, no existing franchise characters, no artist signatures, no typography, no logos. Landscape orientation, 16:9.")
MAYA = J("Maya, a 25-year-old fictional female explorer, premium stylized three-dimensional animated adventure character:",
         "short curly auburn hair, warm amber eyes, small freckles across the nose, expressive oval face, friendly confident smile,",
         "athletic but natural body proportions, mustard-yellow utility jacket, dark teal adventure backpack, charcoal cargo trousers, tan leather hiking boots.",
         "Distinctive recognizable silhouette, high-quality 3D materials, detailed fabric textures, natural facial expressions, beautiful cinematic lighting.",
         "Original fictional character, no resemblance to celebrities or existing animated characters, no logos, no typography.")
MAYA_SCENES = [
    ("station", "Maya arrives at a beautiful historic railway station at sunrise, carrying a folded adventure map."),
    ("rainforest", "Maya explores a mysterious tropical rainforest filled with enormous plants and glowing insects."),
    ("temple", "Maya discovers an ancient fictional sandstone temple surrounded by desert dunes at sunset."),
    ("mountain", "Maya stands on a snowy mountain ridge while dramatic clouds move across the valley."),
    ("city", "Maya walks through an imaginative futuristic city illuminated by colorful architectural lights."),
    ("ocean", "Maya watches a golden sunset from a quiet ocean cliff after completing her adventure."),
]
P6 = J("Create an original premium visual advertising campaign concept for a fictional sustainable technology company.",
       "A magnificent translucent emerald glass sphere floats above a dark sculptural stone surface.",
       "Inside the glass sphere is a miniature thriving ecosystem containing delicate plants, tiny trees, moss-covered terrain, and glowing energy pathways.",
       "Beautiful optical refraction, realistic transparent glass, controlled reflections, subtle gold-colored energy streams.",
       "Deep forest-green surroundings, sophisticated bronze highlights, soft cinematic rim lighting, subtle atmospheric depth.",
       "An elegant visual metaphor for innovation, nature, renewable energy, and environmental responsibility.",
       "Exceptional commercial art direction, photorealistic materials, dramatic yet refined composition, luxury editorial visual language.",
       "Generous calm negative space in the upper part of the frame.",
       "Original concept and composition, no existing company branding, no trademarks, no watermarks. Completely text-free image: no letters, no words, no characters, no signage. Portrait orientation, 4:5.")
P7 = J("Create an original luxury skincare advertising photograph featuring an entirely fictional, unbranded cosmetic serum bottle.",
       "Elegant matte-black glass bottle with a sculptural champagne-gold metallic cap.",
       "The bottle floats above a polished black-marble podium surrounded by subtle golden light reflections.",
       "Dramatic professional studio lighting, controlled highlights, deep charcoal background, refined shadows, subtle atmospheric haze.",
       "Photorealistic glass and metallic materials, sophisticated premium product photography, elegant minimalist composition.",
       "Strong product-centered visual hierarchy, beautiful contrast, carefully balanced negative space suitable for later advertising typography.",
       "Extremely polished commercial aesthetic, high-end beauty campaign art direction, realistic optical reflections and natural material behavior.",
       "Original generic packaging design, blank label, no recognizable product shapes associated with existing brands, no text, no logos, no trademarks.")
P8 = J("Create an original photorealistic luxury product photography environment.",
       "A beautifully sculpted natural travertine stone podium occupies the central foreground.",
       "Elegant Mediterranean-inspired architectural surfaces, warm limestone walls, soft ivory plaster, delicate olive branches, natural stone textures.",
       "Beautiful late-afternoon sunlight enters from the upper-left side, creating gentle architectural shadows.",
       "Warm beige, ivory, sandstone, and muted olive color palette.",
       "Professional commercial photography, realistic surface imperfections, subtle depth of field, excellent shadow consistency.",
       "Sophisticated minimalist art direction suitable for skincare, fragrance, jewelry, or premium lifestyle products.",
       "The central podium must remain completely empty and clearly visible for future product compositing.",
       "No bottles, no products, no people, no furniture, no typography, no logos. Original environment and architectural arrangement. Portrait orientation, 4:5.")
P9 = J("Create an original award-worthy luxury fragrance packaging design for a fictional premium perfume brand.",
       "A beautifully sculpted deep-emerald glass perfume bottle with a distinctive architectural silhouette.",
       "The bottle features elegant geometric proportions, luxurious transparent glass, a heavy brushed champagne-gold cap, and a plain polished gold plaque without any engraving.",
       "Beside the bottle stands a matching premium rigid presentation box decorated only with delicate original botanical embossing; the front of the box is plain and blank, with no lettering, no monogram and no printed band.",
       "The packaging communicates mystery, nature, craftsmanship, and sophisticated elegance.",
       "Dark cinematic studio environment with subtle moss, natural stone, and understated organic decorative elements.",
       "Exceptional realistic glass refraction, polished metallic highlights, physically convincing materials, professional studio lighting.",
       "Visually striking premium product presentation, carefully controlled composition, exquisite commercial art direction.",
       "Completely original bottle geometry and packaging concept, no resemblance to existing identifiable fragrance packaging, no existing brand names, no logos, no trademarks. Completely text-free image: no letters, no words, no characters, no signage. Portrait orientation, 3:4.")
PR_P10 = J("Create an original breathtaking futuristic renewable energy visualization for a professional corporate presentation.",
        "A luminous transparent globe floats above an interconnected sustainable energy landscape.",
        "The landscape contains realistic solar photovoltaic farms, elegant wind turbines, modular battery energy storage installations, and modern electrical infrastructure.",
        "Beautiful flowing cyan and electric-blue energy pathways visually connect the individual technologies.",
        "Deep midnight-navy environment, cinematic volumetric lighting, sophisticated reflections, atmospheric depth.",
        "The scene symbolizes intelligent electricity networks, technological innovation, energy transformation, and a sustainable future.",
        "Premium three-dimensional visualization, physically plausible materials, realistic architectural scale, exceptional lighting and composition.",
        "Place the main visual elements in the right two-thirds of the image. Leave the left third clean, empty and relatively dark.",
        "Original concept, no corporate logos, no trademarks, no technical labels. Completely text-free image: no letters, no words, no characters, no signage. Landscape orientation, 16:9.")
P11_ITEMS = ["enchanted crystal sword", "ancient magical spellbook", "glowing phoenix-inspired amulet",
             "ornamental healing potion", "legendary engraved shield", "mysterious golden treasure key"]
PR_P11 = J("Create an original premium fantasy role-playing game inventory asset. ITEM: {x}.",
        "Exquisite hand-painted digital illustration, carefully designed fantasy craftsmanship, intricate ornamental details, elegant stylized proportions.",
        "Rich magical materials, polished metal, carved gemstones, aged leather, engraved decorative surfaces, subtle luminous energy.",
        "A sophisticated palette of sapphire blue, deep violet, antique gold, and muted silver.",
        "Beautifully defined silhouette, consistent object scale, crisp painterly edges, excellent readability at small icon sizes.",
        "Professional high-quality game inventory asset with detailed surface textures and controlled lighting.",
        "Single centered isolated object, generous empty margins, simple uniform plain white background suitable for later background removal.",
        "No environment, no hands, no characters, no floor, no interface, no typography, no logos.",
        "Completely original fantasy item design, no references to existing games or fictional franchises. Square format.")
PR_P12 = J("Create an original ultra-detailed photorealistic natural sandstone surface texture.",
        "Fine mineral grains, delicate sedimentary formations, tiny pores, subtle geological imperfections, natural erosion marks.",
        "Realistic warm-beige, muted taupe, pale sandstone, and soft earthy color variations.",
        "Physically plausible mineral surface characteristics, extraordinary microtexture detail, consistent material scale.",
        "Uniform neutral diffuse illumination across the entire surface. Orthographic top-down material capture, flat surface, no perspective distortion.",
        "The texture must cover the entire image continuously without borders. No directional sunlight, no strong shadows, no decorative objects, no architectural elements.",
        "Natural realistic sandstone material suitable for architectural visualization and game development. Design for seamless tiling across opposite image boundaries.",
        "Original material pattern, no typography, no logos, no watermarks. Square format.")
PR_P13 = J("Extend the supplied original landscape image into a breathtaking ultra-wide cinematic panorama. Fill the plain grey areas on the left and right.",
        "Continue the visible landscape naturally beyond the existing image boundaries: majestic rugged alpine mountain peaks, a pristine turquoise glacial lake, subtle morning mist, natural vegetation, atmospheric perspective.",
        "Beautiful golden sunrise illuminating the mountain slopes with warm directional light. Highly realistic geological formations, natural reflections in the lake, subtle clouds.",
        "Match the original image's horizon line, perspective, camera position, lens characteristics, color temperature, lighting direction, and photographic grain.",
        "Create seamless visual transitions between the existing image and newly generated areas. Preserve the original image content in the middle without alteration.",
        "Professional landscape photography, natural color grading. Do not introduce recognizable buildings, people, text, logos, or artificial landmarks.")
P14_SCENES = ["mountains and a rising sun", "a bamboo forest in morning mist", "a solitary pine tree above a valley",
              "a quiet mountain waterfall", "minimalist coastal cliffs", "moonlit mountain silhouettes"]
PR_P14 = J("Create an original sophisticated minimalist wall-art illustration inspired by traditional East Asian ink painting principles and contemplative natural landscapes.",
        "Subject: {x}, with a magnificent muted vermilion sun or moon and elegant layers of mist.",
        "Expressive organic black-ink brushstrokes, delicate tonal transitions, subtle handmade-paper texture.",
        "Warm ivory background, deep charcoal brushwork, restrained vermilion accents, exceptional visual balance.",
        "Refined asymmetry, graceful negative space, calm meditative atmosphere, subtle natural imperfections.",
        "Beautiful abstracted silhouettes, soft atmospheric depth, exquisite paper grain, elegant minimalist composition.",
        "Timeless decorative fine art suitable for contemporary interiors and coordinated premium printable collections.",
        "Original brushwork, original composition, no copying of historical or contemporary artworks, no artist signatures, no calligraphy, no typography, no logos. Portrait orientation, 2:3.")
P15_BASE = J("Create a world-class premium commercial product photograph of the product from the reference image.",
             "Preserve the exact visible geometry, proportions, materials, color, functional components, and distinctive physical characteristics of the product.",
             "Present the product as the central hero object. {x}",
             "Polished commercial photography, physically plausible reflections and shadows, strong visual hierarchy, premium material realism,",
             "generous clean negative space for future marketing typography. Do not invent new product features, logos, trademarks or branding.")
P15_VARIANTS = [
    ("midnight_blue", "Sophisticated futuristic studio, deep midnight-blue environment, elegant cobalt-blue rim lighting, volumetric light beams, subtle haze."),
    ("champagne", "Warm champagne luxury studio, soft golden light, satin backdrop, refined warm reflections."),
    ("neon", "Futuristic violet and cyan neon environment, glossy reflective floor, dramatic colored rim lights."),
    ("daylight", "Natural daylight lifestyle environment, light oak desk by a window, soft morning sun, plants softly out of focus."),
    ("white_arch", "Minimalist white architectural studio, curved white walls, soft diffused light, gentle shadows."),
    ("charcoal", "Dramatic charcoal-black premium campaign, single hard key light, deep shadows, subtle smoke."),
]
PR_P16 = J("Create an original visually extraordinary hero image for a professional creative design portfolio specializing in AI-assisted commercial visual production.",
        "A sophisticated artistic composition combining translucent sculptural glass, elegant architectural geometry, polished metallic surfaces, and beautifully arranged abstract dimensional forms.",
        "Rich charcoal, warm ivory, refined champagne-gold, and subtle deep-green color accents. Masterful interplay of realistic materials and imaginative visual design.",
        "Exceptional cinematic lighting, intricate reflections, sophisticated volumetric depth, restrained atmospheric effects.",
        "Premium contemporary editorial art direction, carefully balanced visual hierarchy. Elegant negative space on the left reserved for a future portfolio title.",
        "No imitation of existing design studios, no recognizable branded elements, no third-party logos, no signatures, no typography, no watermarks. Landscape orientation, 16:9.")

TIP_VARIANTS = "Variations: change only the {what} in the prompt, keep the seed while you tune the style, then change seeds for alternatives."


def P01():
    wf = WF("P01", "Botanical fine-art poster collection (4:5, print-ready)")
    M = z_models(wf)
    wf.note(LIC_Z + "\n" + LIC_UP, "1 · Models", title="Licenses")
    g = "2 · Prompt & generate"
    wf.note("Six coordinated posters: replace 'peony' with " + ", ".join(P1_SPECIES[1:]) + ". " + TIP_VARIANTS.format(what="species"), g, title="Collection")
    img = z_t2i(wf, M, P1.format(x="a peony"), 896, 1120, 1101, g, col=1)
    save(wf, img[0], "book/P01_botanical/peony", g, 2, "Save preview")
    g3 = "3 · Upscale for print"
    up = upscale4(wf, img[0], g3)
    wf.note("3584 × 4480 px = 12 × 15 in at 300 DPI, or 16 × 20 in at 224 DPI.", g3, 1, "Print sizes")
    save(wf, up[0], "book/P01_botanical/peony_print", g3, 1, "Save print file")
    return wf


def P02():
    wf = WF("P02", "Large-scale abstract office art (3:2, up to 66 × 44 in)")
    M = z_models(wf)
    wf.note(LIC_Z + "\n" + LIC_UP, "1 · Models", title="Licenses")
    g = "2 · Generate"
    img = z_t2i(wf, M, P2, 1248, 832, 2201, g, col=1)
    save(wf, img[0], "book/P02_office_art/preview", g, 2, "Save preview")
    g3 = "3 · Upscale ×4 → ×2"
    up = upscale4(wf, img[0], g3)
    big = wf.add("ImageScaleBy", "Resize ×2 (lanczos)", g3, 0, image=up[0], upscale_method="lanczos", scale_by=2.0)
    wf.note("9984 × 6656 px ≈ 66 × 44 in at 150 DPI - wall size, viewed from a few steps away. Ask the print shop for format and colour profile.", g3, 1, "Print notes")
    save(wf, big[0], "book/P02_office_art/print_150dpi", g3, 1, "Save large print file")
    return wf


def P03():
    wf = WF("P03", "Seamless luxury geometric pattern + 3×3 check")
    M = z_models(wf)
    wf.note(LIC_Z + "\nCore nodes only.", "1 · Models", title="Licenses")
    g = "2 · Generate tile"
    img = z_t2i(wf, M, P3, 1024, 1024, 3301, g)
    g3 = "3 · Offset & heal the seams"
    wf.note("The tile is shifted by half (wrap-around) so its edges meet in the middle; only that cross is repainted (denoise 0.7).", g3, 1, "How it works")
    healed = seamless_heal(wf, M, img[0], 1024, P3, 3302, g3)
    g4 = "4 · Save tile & 3×3 check"
    save(wf, healed[0], "book/P03_pattern/tile", g4, 0, "Save seamless tile")
    prev = tile3x3(wf, healed[0], g4, 1)
    save(wf, prev[0], "book/P03_pattern/preview_3x3", g4, 2, "Save 3×3 preview")
    return wf


def P04():
    wf = WF("P04", "Magical children's book illustration (16:9, space for text)")
    M = z_models(wf)
    wf.note(LIC_Z + "\n" + LIC_UP, "1 · Models", title="Licenses")
    g = "2 · Illustration"
    wf.note("Keep the fox description word for word in every page prompt (amber eyes, teal hand-knitted scarf). For pages that must match a "
            "reference exactly, use the reference-image technique from P05.", g, title="Consistency")
    img = z_t2i(wf, M, P4, 1344, 768, 4401, g, col=1)
    save(wf, img[0], "book/P04_kidsbook/clearing", g, 2, "Save page")
    g3 = "3 · Print size"
    up = upscale4(wf, img[0], g3)
    save(wf, up[0], "book/P04_kidsbook/clearing_print", g3, 1, "Save print file (5376 × 3072)")
    return wf


def P05():
    wf = WF("P05", "Consistent character in six scenes (Maya)")
    K = k_models(wf)
    wf.note(LIC_K + "\nFLUX.2 [klein] reads the character sheet as a reference image, so Maya keeps her face, hair and clothes in every scene.", "1 · Models", title="Licenses")
    g = "2 · Character sheet"
    sheet = k_gen(wf, K, J("Character turnaround sheet:", MAYA, "Front view, three-quarter view and side view standing next to each other, full body, neutral light grey studio background."),
                  g, 5501, w=1344, h=768, label=" (sheet)")
    save(wf, sheet[0], "book/P05_maya/sheet", g, 2, "Save sheet")
    ref = prep_ref(wf, sheet[0], g, 2)
    for i, (slug, scene) in enumerate(MAYA_SCENES):
        gg = f"{i + 3} · Scene {i + 1}: {slug}"
        out = k_gen(wf, K, J("Use the character from the reference image: keep exactly the same face, hairstyle, clothing colors, backpack and proportions.",
                             "SCENE:", scene, "Premium stylized 3D animated film still, cinematic lighting, portrait orientation."),
                    gg, 5510 + i, refs=[ref[0]], w=864, h=1152, label=f" {i + 1}")
        save(wf, out[0], f"book/P05_maya/{i + 1}_{slug}", gg, 2, f"Save {slug}")
    return wf


def P06():
    wf = WF("P06", "Premium sustainable-technology brand campaign")
    M = z_models(wf)
    wf.note(LIC_Z, "1 · Models", title="Licenses")
    g = "2 · Key visual"
    img = z_t2i(wf, M, P6, 896, 1120, 6601, g, col=1)
    save(wf, img[0], "book/P06_campaign/key_visual", g, 2, "Save")
    return wf


def P07():
    wf = WF("P07", "Luxury cosmetic social campaign (4:5 feed, 9:16 story, 1:1)")
    M = z_models(wf)
    wf.note(LIC_Z, "1 · Models", title="Licenses")
    out = {}
    for i, (lab, w, h, extra) in enumerate([("4:5", 896, 1120, "Portrait orientation, 4:5."), ("9:16", 720, 1280, "Tall vertical story format, 9:16, extra space above the product."),
                                             ("1:1", 1024, 1024, "Square format, bottle slightly left of center.")]):
        g = f"{i + 2} · Format {lab}"
        out[lab] = z_t2i(wf, M, J(P7, extra), w, h, 7701, g, label=f" {lab}")
        save(wf, out[lab][0], f"book/P07_cosmetics/{lab.replace(':', 'x')}", g, 1, f"Save {lab}")
    g = "5 · Headline (optional)"
    wf.note("Variations: change camera angle, product position, background colour, lighting direction, podium geometry or decor. "
            "Draw Text Overlay adds a quick headline; brand fonts belong in a free editor.", g, title="Variations & text")
    t = wf.add("TextOverlay", "Headline", g, 0, images=out["9:16"][0], text="RADIANCE, REFINED", font_size=5.0, color="#E8D9B0",
               position="top", align="center", outline=False)
    save(wf, t[0], "book/P07_cosmetics/9x16_headline", g, 1, "Save story with headline")
    return wf


def P08():
    wf = WF("P08", "Mediterranean product-photography set + your product placed on the podium")
    K = k_models(wf)
    wf.note(LIC_K + "\n" + LIC_BG, "1 · Models", title="Licenses")
    g = "2 · Empty set (background)"
    bg = k_gen(wf, K, P8, g, 8801, w=896, h=1120, label=" (set)")
    save(wf, bg[0], "book/P08_set/empty_set", g, 2, "Save empty set")
    g3 = "3 · Your product"
    wf.note("Load a product photo on a plain background. BiRefNet cuts it out so the model sees only the product.", g3, title="How to use")
    li = wf.add("LoadImage", "Product photo", g3, 0, image="product.png")
    sc = prep_ref(wf, li[0], g3, 0)
    cut = wf.add("BiRefNetRMBG", "Cut out on white", g3, 1, image=sc[0], model="BiRefNet-general", sensitivity=1.0, mask_blur=0, mask_offset=0,
                 invert_output=False, refine_foreground=True, unload_model=False, background="Color", background_color="#FFFFFF")
    g4 = "4 · Place product on the podium"
    out = k_gen(wf, K, J("Place the product from the second reference image standing in the center of the empty travertine podium in the first reference image.",
                         "Keep the scene, architecture, sunlight direction and colors of the first image. Keep the product exactly as it is: same shape, material, color and markings.",
                         "Add a natural contact shadow consistent with the late-afternoon light from the upper left. Professional product photography."),
                g4, 8802, refs=[bg[0], cut[0]], w=896, h=1120, label=" (place)")
    save(wf, out[0], "book/P08_set/product_on_set", g4, 2, "Save product shot")
    return wf


def P09():
    wf = WF("P09", "Luxury perfume packaging concept")
    M = z_models(wf)
    wf.note(LIC_Z + "\nConcept only: final logo, label text and legal copy are designed by a human.", "1 · Models", title="Licenses")
    g = "2 · Concept"
    img = z_t2i(wf, M, P9, 864, 1152, 9901, g, col=1)
    save(wf, img[0], "book/P09_packaging/concept", g, 2, "Save concept")
    return wf


def P10():
    wf = WF("P10", "Futuristic renewable-energy presentation visual (16:9)")
    M = z_models(wf)
    wf.note(LIC_Z, "1 · Models", title="Licenses")
    g = "2 · Slide visual"
    img = z_t2i(wf, M, PR_P10, 1344, 768, 10101, g, col=1)
    save(wf, img[0], "book/P10_slides/energy", g, 2, "Save clean")
    g3 = "3 · Slide headline (replaces a layout app)"
    t = wf.add("TextOverlay", "Headline", g3, 0, images=img[0], text="THE GRID, REIMAGINED", font_size=6.0, color="#FFFFFF",
               position="top", align="left", outline=False)
    save(wf, t[0], "book/P10_slides/energy_title", g3, 1, "Save slide")
    return wf


def P11():
    wf = WF("P11", "Fantasy RPG asset collection (transparent icons)")
    M = z_models(wf)
    wf.note(LIC_Z + "\n" + LIC_BG, "1 · Models", title="Licenses")
    g = "2 · Item"
    wf.note("Six assets: replace the ITEM with " + ", ".join(P11_ITEMS[1:]) + ". Same seed and style words = one consistent set.", g, title="Collection")
    img = z_t2i(wf, M, PR_P11.format(x=P11_ITEMS[0]), 1024, 1024, 11101, g, col=1)
    g3 = "3 · Transparent PNG"
    cut = alpha_cutout(wf, img[0], g3, 0)
    save(wf, cut[0], "book/P11_rpg/sword_1024", g3, 1, "Save 1024 RGBA")
    small = wf.add("ImageScale", "Icon 256×256", g3, 1, image=cut[0], upscale_method="lanczos", width=256, height=256, crop="disabled")
    save(wf, small[0], "book/P11_rpg/sword_icon256", g3, 2, "Save icon")
    return wf


def P12():
    wf = WF("P12", "Photorealistic seamless sandstone texture + depth map")
    M = z_models(wf)
    wf.note(LIC_Z + "\n• Depth Anything V2 SMALL (vits) - Apache 2.0. Base/Large are CC BY-NC - do not use for paid work.", "1 · Models", title="Licenses")
    g = "2 · Texture"
    img = z_t2i(wf, M, PR_P12, 1024, 1024, 12201, g)
    g3 = "3 · Make it seamless"
    healed = seamless_heal(wf, M, img[0], 1024, PR_P12, 12202, g3)
    g4 = "4 · Save + depth + 3×3 check"
    save(wf, healed[0], "book/P12_sandstone/albedo", g4, 0, "Save texture")
    d = wf.add("DepthAnythingV2Preprocessor", "Depth map (V2 Small)", g4, 0, image=healed[0], ckpt_name="depth_anything_v2_vits.pth", resolution=1024)
    save(wf, d[0], "book/P12_sandstone/depth", g4, 1, "Save depth map")
    prev = tile3x3(wf, healed[0], g4, 2)
    save(wf, prev[0], "book/P12_sandstone/preview_3x3", g4, 2, "Save 3×3 preview")
    return wf


def P13():
    wf = WF("P13", "Cinematic landscape outpainting (16:9 → 21:9)")
    K = k_models(wf)
    wf.note(LIC_K + "\n• LaMa - Apache 2.0 (optional defect removal).", "1 · Models", title="Licenses")
    g = "2 · Photo & repair"
    wf.note("Optional: paint small defects in the Mask Editor of Load Image - LaMa removes them. Empty mask = no change.", g, title="Repair")
    li = wf.add("LoadImage", "Landscape photo (16:9)", g, 0, image="landscape.png")
    sc = wf.add("ImageScale", "Normalise to 1344×768", g, 0, image=li[0], upscale_method="lanczos", width=1344, height=768, crop="center")
    mi = wf.add("MaskToImage", "Painted mask → image", g, 1, mask=li[1])
    ms = wf.add("ImageScale", "Mask to 1344×768", g, 1, image=mi[0], upscale_method="bilinear", width=1344, height=768, crop="center")
    mk = wf.add("ImageToMask", "Image → mask", g, 1, image=ms[0], channel="red")
    fixed = wf.add("AILab_LamaRemover", "Remove painted defects (LaMa)", g, 2, images=sc[0], masks=mk[0], removal_strength=230, edge_smoothness=8, unload_model=True)
    g3 = "3 · Extend to 21:9"
    pad = wf.add("ImagePadForOutpaint", "Add 224 px left & right", g3, 0, image=fixed[0], left=224, top=0, right=224, bottom=0, feathering=0)
    gen = k_gen(wf, K, PR_P13, g3, 13301, refs=[pad[0]], w=1792, h=768, col=1)
    g4 = "4 · Keep the original centre + upscale"
    comp = wf.add("ImageCompositeMasked", "Paste original centre back", g4, 0, destination=gen[0], source=fixed[0], x=224, y=0, resize_source=False)
    save(wf, comp[0], "book/P13_panorama/panorama_21x9", g4, 1, "Save 21:9")
    return wf


def P14():
    wf = WF("P14", "Minimalist Zen wall-art collection (2:3, batch template)")
    M = z_models(wf)
    wf.note(LIC_Z + "\n" + LIC_UP, "1 · Models", title="Licenses")
    g = "2 · Template"
    wf.note("Driven by scripts/batch.py + topics.csv (export: Workflow → Export (API)). Six subjects: " + "; ".join(P14_SCENES) + ".", g, title="Batch")
    img = z_t2i(wf, M, PR_P14.format(x=P14_SCENES[0]), 832, 1248, 14401, g, col=1)
    save(wf, img[0], "book/P14_zen/mountains_sun", g, 2, "Save")
    return wf


def P15():
    wf = WF("P15", "Premium product visualisation - six studio looks from one photo")
    K = k_models(wf)
    wf.note(LIC_K, "1 · Models", title="Licenses")
    g = "2 · Product reference"
    wf.note("Load a clean photo of the real product (test photo: inputs/product.png, an unbranded jar). Only markings that are really on the product may appear in the result. Never use a product designed to look like a famous brand.", g, title="How to use")
    li = wf.add("LoadImage", "Product photo", g, 0, image="product.png")
    sc = prep_ref(wf, li[0], g, 0)
    for i, (slug, look) in enumerate(P15_VARIANTS):
        gg = f"{i + 3} · Look: {slug}"
        out = k_gen(wf, K, P15_BASE.format(x=look), gg, 15501 + i, refs=[sc[0]], w=896, h=1120, label=f" {i + 1}")
        save(wf, out[0], f"book/P15_product/{i + 1}_{slug}", gg, 2, f"Save {slug}")
    return wf


def P16():
    wf = WF("P16", "Portfolio hero image + title")
    M = z_models(wf)
    wf.note(LIC_Z, "1 · Models", title="Licenses")
    g = "2 · Hero image"
    img = z_t2i(wf, M, PR_P16, 1344, 768, 16601, g, col=1)
    save(wf, img[0], "book/P16_portfolio/hero", g, 2, "Save hero")
    g3 = "3 · Title (optional)"
    t = wf.add("TextOverlay", "Portfolio title", g3, 0, images=img[0], text="YOUR NAME  ·  AI-ASSISTED VISUAL PRODUCTION", font_size=3.5,
               color="#EDE6D6", position="bottom", align="left", outline=False)
    save(wf, t[0], "book/P16_portfolio/hero_title", g3, 1, "Save hero with title")
    return wf


def CH07():
    wf = WF("CH07", "Your first workflow - five nodes (chapter 7)")
    g = "Five nodes"
    wf.note("The simplest workflow there is: one all-in-one checkpoint (SDXL base 1.0, CreativeML Open RAIL++-M, "
            "commercial use allowed with a list of prohibited uses). Change the prompt, keep the rest, press Run.", g, title="Read me")
    ck = wf.add("CheckpointLoaderSimple", "1 · Load Checkpoint", g, 1, ckpt_name="sd_xl_base_1.0.safetensors")
    p = wf.add("CLIPTextEncode", "2a · Positive prompt", g, 1, text=P1.format(x="a magnolia branch"), clip=ck[1])
    n = wf.add("CLIPTextEncode", "2b · Negative prompt", g, 1, text=NEG_SDXL, clip=ck[1])
    l = wf.add("EmptyLatentImage", "3 · Empty Latent 896×1120", g, 2, width=896, height=1120, batch_size=1)
    k = wf.add("KSampler", "4 · KSampler", g, 2, model=ck[0], seed=42, steps=30, cfg=6.0, sampler_name="dpmpp_2m", scheduler="karras", positive=p[0], negative=n[0], latent_image=l[0], denoise=1.0)
    d = wf.add("VAEDecode", "5a · VAE Decode", g, 3, samples=k[0], vae=ck[2])
    save(wf, d[0], "book/CH07_first/magnolia", g, 3, "5b · Save Image")
    return wf
