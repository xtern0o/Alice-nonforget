def check_line(line):
    negative_words = ["нет", "ни", "не"]
    negatives_count = line.lower().count("не")
    if negatives_count % 2 != 0:
        for word in negative_words:
            if word in line.lower():
                return True
        return False
    return False