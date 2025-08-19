# Minecraft.py
from collections import Counter

def normalize_action(line: str):
    """
    Convert a raw log line into a normalized action string for grouping.
    """
    line = line.lower()

    if "broke" in line:
        # Extract block type
        try:
            block_name = line.split("broke ")[1].split(" at ")[0]
            return f"broke {block_name}"
        except IndexError:
            return "broke unknown block"

    elif "placed" in line:
        try:
            block_name = line.split("placed ")[1].split(" at ")[0]
            return f"placed {block_name}"
        except IndexError:
            return "placed unknown block"

    elif "attacked" in line:
        try:
            mob_name = line.split("attacked ")[1]
            return f"attacked {mob_name}"
        except IndexError:
            return "attacked unknown mob"

    elif "took" in line:
        try:
            mob_name = line.split("from ")[1]
            return f"took damage from {mob_name}"
        except IndexError:
            return "took damage from unknown"

    elif "died" in line:
        return "died"

    elif "respawned" in line:
        return "respawned"

    elif "completed advancement" in line:
        try:
            adv_name = line.split("completed advancement: ")[1]
            return f"advancement {adv_name}"
        except IndexError:
            return "advancement unknown"

    return None

def group_actions(lines: list[str]):
    """
    Takes raw log lines, normalizes them, and counts occurrences by action type.
    Returns a Counter dictionary.
    """
    normalized = [normalize_action(line) for line in lines if normalize_action(line)]
    return Counter(normalized)
