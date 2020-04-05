def get_text_between(text, begin, end):
    start = text.index(begin) + len(begin)
    end = text.index(end, start)
    return text[start:end]
