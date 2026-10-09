# This config is loaded by Minecraft Overviewer, so several names used below
# (worlds, renders, Base, EdgeLines, etc.) are supplied by Overviewer itself.
# flake8: noqa: F821,F401
# pylint: disable=undefined-variable
# type: ignore

# Regarding `global`, see:
# https://docs.overviewer.org/en/latest/signs/#filter-functions
global html, SIGN_IDS, _sign_lines
import html
import os


SIGN_IDS = {"Sign", "sign", "minecraft:sign", "minecraft:hanging_sign"}


def playerIcons(poi):
    if poi["id"] == "Player":
        poi["icon"] = "https://overviewer.org/avatar/{}".format(poi["EntityId"])
        return "Last known location for {}".format(poi["EntityId"])


def _sign_lines(poi):
    if "Text1" in poi:
        plain_lines = [poi.get(key, "") for key in ["Text1", "Text2", "Text3", "Text4"]]
        return [(line, html.escape(line)) for line in plain_lines if line.strip()]

    lines = []
    for side_name in ["front_text", "back_text"]:
        side = poi.get(side_name, {})
        plain_lines = side.get("messages", [])
        html_lines = side.get("messagesHtml", [html.escape(line) for line in plain_lines])
        lines.extend(
            (plain_line, html_line)
            for plain_line, html_line in zip(plain_lines, html_lines)
            if plain_line.strip()
        )
    return lines


# Only render signs containing the filter string. If the filter string is blank,
# render all signs. Output uses messagesHtml because sign text is player-provided.
def signFilter(poi):
    import os

    if poi.get("id") not in SIGN_IDS:
        return None

    lines = _sign_lines(poi)
    sign_filter = os.environ.get("RENDER_SIGNS_FILTER", "-- RENDER --")
    hide_filter = os.environ.get("RENDER_SIGNS_HIDE_FILTER", "true").lower() == "true"
    render_all_signs = len(sign_filter) == 0

    if not render_all_signs and not any(sign_filter in plain_line for plain_line, _ in lines):
        return None

    if hide_filter and not render_all_signs:
        lines = [(plain_line, html_line) for plain_line, html_line in lines if plain_line != sign_filter]

    joiner = os.environ.get("RENDER_SIGNS_JOINER", "<br />")
    return joiner.join(html_line for _, html_line in lines)


worlds["minecraft"] = "/home/minecraft/server/"
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
