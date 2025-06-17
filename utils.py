# sequence format: (x/y), let's cap it at 10 reserved chars for safety -> 190
max_length = 190


def splitter(long_text: str, max_length: int = 190) -> list[str]:
    """
    Takes in a large block of text and chunks it into individual messages up to a max length, splitting on periods
    """
    sentences = long_text.split(".")
    sentences = [_ + "." for _ in sentences if _]  # add the periods back in

    chunks = []
    current_string = ""
    while sentences:  # still some remainint text
        next_sentence = sentences.pop(0)  # grab the next sentence off the front
        if len(current_string + next_sentence) < max_length:
            current_string += next_sentence  # keep adding since there's still room
        else:
            chunks.append(current_string)
            current_string = next_sentence
    chunks.append(current_string)  # add the last chunk
    chunks = [_.strip(".").strip() for _ in chunks if _]  # remove extra characters
    return chunks


def sequencer(packets: list[str]) -> list[str]:
    total = len(packets)
    newpackets = []
    for idx, packet in enumerate(packets):
        newpackets.append(packet + f" ({idx+1}/{total})")
    return newpackets


def format_time_left(seconds_left):
    days, rem = divmod(seconds_left, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{hours:02.0f}:{minutes:02.0f}:{seconds:02.0f}"
