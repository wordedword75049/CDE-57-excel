k, b = 0, 0


def set_coefficients(bounds, part):
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
    indexes = []
    for i, word in enumerate(new_part):
        if word != '':
            indexes.append(i)
        if len(indexes) == 2:
            break

    global k, b
    y_0 = (float(bounds[indexes[0]]["top"]) + float(bounds[indexes[0]]["bottom"])) / 2
    y_1 = (float(bounds[indexes[1]]["top"]) + float(bounds[indexes[1]]["bottom"])) / 2

    v_0 = float(new_part[indexes[0]])
    v_1 = float(new_part[indexes[1]])
    k = (v_0 - v_1) \
        / (y_0 - y_1)
    b = v_1 - k * y_1

def get_value(y):
    return k * y + b