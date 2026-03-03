from tcgPocket import TGCPocket
import json
import time


def formatDuration(seconds: float) -> str:
    seconds = int(seconds)
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    parts = []

    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")

    if minutes:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")

    parts.append(f"{secs} second{'s' if secs != 1 else ''}")

    if len(parts) > 1:
        return ", ".join(parts[:-1]) + " and " + parts[-1]
    else:
        return parts[0]


init_time = time.perf_counter()
filename = "pokemon_cards.json"


pocket = TGCPocket()


end_time = time.perf_counter()
print(f"Finished downloading cards to {filename}, total time: {
        formatDuration(end_time - init_time)}")

with open(filename, "w", encoding="utf-8") as file:
    json.dump(pocket.getCardDataSorted(), file, ensure_ascii=False, indent=4)
