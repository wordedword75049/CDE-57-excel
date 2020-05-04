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