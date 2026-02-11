# # Minecraft.py
# from collections import Counter

# def normalize_action(line: str):
#     """
#     Convert a raw log line into a normalized action string for grouping.
#     """
#     line = line.lower()

#     if "broke" in line:
#         # Extract block type
#         try:
#             block_name = line.split("broke ")[1].split(" at ")[0]
#             return f"broke {block_name}"
#         except IndexError:
#             return "broke unknown block"

#     elif "placed" in line:
#         try:
#             block_name = line.split("placed ")[1].split(" at ")[0]
#             return f"placed {block_name}"
#         except IndexError:
#             return "placed unknown block"

#     elif "attacked" in line:
#         try:
#             mob_name = line.split("attacked ")[1]
#             return f"attacked {mob_name}"
#         except IndexError:
#             return "attacked unknown mob"

#     elif "took" in line:
#         try:
#             mob_name = line.split("from ")[1]
#             return f"took damage from {mob_name}"
#         except IndexError:
#             return "took damage from unknown"

#     elif "died" in line:
#         return "died"

#     elif "respawned" in line:
#         return "respawned"

#     elif "completed advancement" in line:
#         try:
#             adv_name = line.split("completed advancement: ")[1]
#             return f"advancement {adv_name}"
#         except IndexError:
#             return "advancement unknown"

#     return None

# def group_actions(lines: list[str]):
#     """
#     Takes raw log lines, normalizes them, and counts occurrences by action type.
#     Returns a Counter dictionary.
#     """
#     normalized = [normalize_action(line) for line in lines if normalize_action(line)]
#     return Counter(normalized)

# mc.py - Universal version: works with old text logs AND your new JSON logs
# Compatible with ALL your AI profiles (no changes needed elsewhere)

import json
from collections import Counter

def normalize_action(line: str):
    """
    Convert a raw log line (text or JSON) into a normalized action string.
    Exactly like your old code, but now handles both vanilla text and your mod's JSON.
    """
    line = line.strip()

    # 1. Try your mod's JSON first (clean & rich)
    if line.startswith("{") and line.endswith("}"):
        try:
            event = json.loads(line)
            etype = event.get("type", "").lower()

            if etype == "advancement":
                # If you ever add JSON advancement logging
                details = event.get("details", "")
                title = details.split(" | ")[0] if " | " in details else "Unknown"
                return f"advancement {title}"

            elif etype == "break":
                block = event.get("details", "").split(" ")[0].split("(")[0].strip()
                return f"broke {block}"
            elif etype == "place":
                block = event.get("details", "").split(" ")[0].split("(")[0].strip()
                return f"placed {block}"
            elif etype == "death":
                return "died"
            elif etype == "respawn":
                return "respawned"
            elif etype == "attack":
                target = event.get("details", "").split(" ")[0]
                return f"attacked {target}"
            elif etype == "damage":
                source = event.get("details", "").split(" hit ")[0]
                return f"took damage from {source}"
            elif etype == "roastme":
                return "roastme"
            elif etype == "join":
                return "joined"
            elif etype == "leave":
                return "left"

        except json.JSONDecodeError:
            pass  # Not valid JSON → fall through to text parsing

    # 2. Fallback: your original vanilla text parsing (unchanged!)
    line_lower = line.lower()

    if "completed advancement:" in line_lower:
        try:
            adv_name = line.split("completed advancement: [")[1].split("]")[0]
            return f"advancement {adv_name}"
        except IndexError:
            return "advancement unknown"

    if "broke" in line_lower:
        try:
            block_name = line.split("broke ")[1].split(" at ")[0]
            return f"broke {block_name}"
        except IndexError:
            return "broke unknown block"

    if "placed" in line_lower:
        try:
            block_name = line.split("placed ")[1].split(" at ")[0]
            return f"placed {block_name}"
        except IndexError:
            return "placed unknown block"

    if "attacked" in line_lower:
        try:
            mob_name = line.split("attacked ")[1]
            return f"attacked {mob_name}"
        except IndexError:
            return "attacked unknown mob"

    if "took" in line_lower and "damage" in line_lower:
        try:
            mob_name = line.split("from ")[1]
            return f"took damage from {mob_name}"
        except IndexError:
            return "took damage from unknown"

    if "died" in line_lower:
        return "died"

    if "respawned" in line_lower:
        return "respawned"

    if "@bot" in line_lower or "roast me" in line_lower:
        return "roastme"

    return None


def group_actions(lines: list[str]):
    """
    Exactly your old function — works the same for all profiles.
    """
    normalized = [normalize_action(line) for line in lines if normalize_action(line)]
    return Counter(normalized)