k, b = 0, 0

def parse_text(part):
    new_part = []
    for word in part:
        new_word = ""
        for i, char in enumerate(word):
            if char.isdigit():
                new_word += char
            else:
                if len(new_word):
                    if i != len(word) - 1:
                        if word[i].lower() == 'к':
                            new_word += '000'
                        elif word[i].lower() == 'м':
                            new_word += '0' * 6
                break
        if new_word != '':
            new_word = int(new_word)
        new_part.append(new_word)
    return new_part


def set_coefficients(lines, new_part):
    indexes = []
    for i, word in enumerate(new_part):
        if word != '':
            indexes.append(i)
        if len(indexes) == 2:
            break

    global k, b
    k = 2 * (new_part[indexes[0]] - new_part[indexes[1]])\
        /(lines[indexes[0]]["top"] + lines[indexes[0]]["bottom"] -
          lines[indexes[1]]["top"] - lines[indexes[1]]["bottom"])

    b = new_part[indexes[0]] - k * (lines[indexes[0]]["top"] + lines[indexes[0]]["bottom"])/2


def get_value(y):
    return k * y + b