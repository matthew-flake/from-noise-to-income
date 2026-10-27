"""Build all 21 workflows (UI + API). Usage: python build.py OUT_DIR"""
import json, os, sys
import premium as p
from projects import P17, P18, P19, P20

ALL = [p.CH07, p.P01, p.P02, p.P03, p.P04, p.P05, p.P06, p.P07, p.P08, p.P09, p.P10, p.P11, p.P12, p.P13, p.P14, p.P15, p.P16, P17, P18, P19, P20]
NAMES = {
    "CH07": "CH07_first_workflow_sdxl", "P01": "P01_botanical_fine_art_posters", "P02": "P02_abstract_office_art",
    "P03": "P03_seamless_luxury_pattern", "P04": "P04_childrens_book_illustration", "P05": "P05_consistent_character_six_scenes",
    "P06": "P06_brand_campaign_key_visual", "P07": "P07_luxury_cosmetic_social_pack", "P08": "P08_product_set_and_placement",
    "P09": "P09_perfume_packaging_concept", "P10": "P10_renewable_energy_slide", "P11": "P11_rpg_asset_icons",
    "P12": "P12_seamless_sandstone_texture", "P13": "P13_cinematic_panorama_outpaint", "P14": "P14_zen_wall_art_batch",
    "P15": "P15_product_six_studio_looks", "P16": "P16_portfolio_hero", "P17": "P17_kdp_bold_easy_coloring",
    "P18": "P18_etsy_clipart_bundle", "P19": "P19_amazon_jp_nurie_coloring", "P20": "P20_line_stickers",
}
if __name__ == "__main__":
    out = sys.argv[1]
    for sub in ("ui", "api"):
        os.makedirs(os.path.join(out, sub), exist_ok=True)
    for f in ALL:
        wf = f()
        n = NAMES[wf.code]
        json.dump(wf.ui(), open(os.path.join(out, "ui", n + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        json.dump(wf.api(), open(os.path.join(out, "api", n + ".api.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(wf.code, len(wf.nodes))
