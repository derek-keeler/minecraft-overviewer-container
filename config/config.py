# This config variable is loaded into the upstream Minecraft Overviewer project,
# so it contains undefined variables and some `import` lines.
# flake8: noqa: F821,F401
# pylint: disable=undefined-variable
# type: ignore

# Regarding `global`, see
# https://docs.overviewer.org/en/latest/signs/#filter-functions
global html
import html
import os


def playerIcons(poi):
    if poi["id"] == "Player":
        poi["icon"] = "https://overviewer.org/avatar/{}".format(poi["EntityId"])
        return "Last known location for {}".format(poi["EntityId"])


# Only render the signs with the filter string in them. If filter string is
# blank or unset, render all signs. Lines are joined with a configurable string.
def signFilter(poi):
    # Because of how Overviewer reads this file, we must "import os" again here.
    import os

    # Only render signs with this function
    if poi["id"] in ["sign", "minecraft:sign"]:
        if 'Text1' in poi:
            text_lines = [line for line in [poi['Text1'], poi['Text2'], poi['Text3'], poi['Text4']] if line.strip()]
            print("Found pre-1.20 sign")
        else:
            # v1.20+ sign filter
            text_lines = []
            front_text = poi.get('front_text', {})
            back_text = poi.get('back_text', {})
            
            text_lines.extend(line for line in front_text.get('messages', []) if line.strip())
            text_lines.extend(line for line in back_text.get('messages', []) if line.strip())
            print("found post-1.20 sign")

        sign_filter = os.environ["RENDER_SIGNS_FILTER"]
        #hide_filter = os.environ["RENDER_SIGNS_HIDE_FILTER"] == "true"
        hide_filter = True
        
        # Determine if we should render this sign
        render_all_signs = len(sign_filter) == 0
        render_this_sign = sign_filter in text_lines
        print(f"render_all_signs={render_all_signs}, render_this_sign={render_this_sign}")

        if render_all_signs or render_this_sign:
            print(f"Rending sign with text [{'/n'.join(text_lines)}]")
            # If the user wants to strip the filter string, we do that here. Only
            # do this if sign_filter isn't blank.
            if hide_filter and not render_all_signs:
                print('hiding the filter...')
                text_lines = list(filter(lambda l: l != sign_filter, text_lines))

            # return html.escape(os.environ["RENDER_SIGNS_JOINER"].join(text_lines))
            return html.escape("\n".join(text_lines))

worlds["minecraft"] = "/home/minecraft/server/world"
outputdir = "/home/minecraft/render/"

markers = [
    dict(name="Players", filterFunction=playerIcons),
    dict(name="Signs", filterFunction=signFilter),
]

renders["day"] = {
    "title": "Day",
    "dimension": "overworld",
    "markers": markers,
    "rendermode": "smooth_lighting",
    "world": "minecraft",
}

renders["night"] = {
    "title": "Night",
    "dimension": "overworld",
    "markers": markers,
    "rendermode": "smooth_night",
    "world": "minecraft",
}

renders["nether"] = {
    "title": "Nether",
    "dimension": "nether",
    "markers": markers,
    "rendermode": "nether_smooth_lighting",
    "world": "minecraft",
}

renders["end"] = {
    "title": "End",
    "dimension": "end",
    "markers": markers,
    "rendermode": [Base(), EdgeLines(), SmoothLighting(strength=0.5)],
    "world": "minecraft",
}

renders["overlay_biome"] = {
    "title": "Biome Coloring Overlay",
    "dimension": "overworld",
    "overlay": ["day"],
    "rendermode": [ClearBase(), BiomeOverlay()],
    "world": "minecraft",
}

renders["overlay_mobs"] = {
    "title": "Mob Spawnable Areas Overlay",
    "dimension": "overworld",
    "overlay": ["day"],
    "rendermode": [ClearBase(), SpawnOverlay()],
    "world": "minecraft",
}

renders["overlay_slime"] = {
    "title": "Slime Chunk Overlay",
    "dimension": "overworld",
    "overlay": ["day"],
    "rendermode": [ClearBase(), SlimeOverlay()],
    "world": "minecraft",
}
