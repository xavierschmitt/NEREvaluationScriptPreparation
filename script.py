import sys


def _file_to_tab(file):
    tab = []
    for line in file:
        line = line.rstrip('\r\n')
        features = line.split()
        if len(features) == 0:
            tab.append([''])
        else:
            tab.append(features)
    return tab

def print_exp(tab, tag):

    if tag != "O" and tag != "I-PER" and tag != "I-LOC" and tag != "I-ORG":
        pass

    print(' '.join([str(x) for x in tab]) + ' ' + tag)


def _find_shift(gold_tab, result_tab, id_gold, id_result):

    shift_id_gold = 0
    shift_id_result = 0

    gold = gold_tab[id_gold][0]
    result = result_tab[id_result][0]

    if result_tab[id_result][0] == result_tab[id_result][1]: # case on spacy
        return 0, 1

    if len(gold) > 0 and len(result) > 0 and gold[0] != result[0]:
        if result == gold_tab[id_gold + 1][0]: # shifting gold
            return 1, 0
        elif gold == result_tab[id_result + 1][0]: # shifting result
            return 0, 1
        elif result in gold_tab[id_gold + 1][0] \
                or gold_tab[id_gold + 1][0] in result\
                and result[0] == gold_tab[id_gold + 1][0][0]: # shifting gold start same as result
            shift_id_gold += 1
            gold = gold_tab[id_gold + 1][0]
        elif gold in result_tab[id_result + 1][0]\
                or result_tab[id_result + 1][0] in gold\
                and gold[0] == result_tab[id_result + 1][0][0]:
            shift_id_result += 1
            result = result_tab[id_result + 1][0]

    while True:

        if len(gold) > 0 and len(result) > 0:
            car_gold = gold[0]
            car_result = result[0]

            try:
                car_gold[0].decode("utf-8")  # Case with spacy and gmb
            except:
                gold = gold[1:]

            try:
                car_result[0].decode("utf-8")
            except:
                result = result[1:]

            if car_gold == car_result: # first caractere matche
                gold = gold[1:]
                result = result[1:]
            elif len(gold) > 1 and car_result == gold[1]: # second gold match (add on result)
                gold = gold[2:]
                result = result[1:]
            elif len(result) > 1 and result[1] == car_gold: # second result match ( delete on result)
                gold = gold[1:]
                result = result[2:]
            elif len(gold) == 1 and gold == '':
                shift_id_gold += 1
                token_to_be_added = gold_tab[id_gold + shift_id_gold][0]
                if token_to_be_added == '-DOCSTART-':
                    shift_id_gold += 1
                    token_to_be_added = gold_tab[id_gold + shift_id_gold][0]
                gold += token_to_be_added
            elif len(result) == 1 and result == '':
                shift_id_result += 1
                result += result_tab[id_result + shift_id_result][0]
            elif len(gold) > 1 and len(result) == 1 and gold[1] == result_tab[id_result + shift_id_result + 1][0][0]:
                result = result[1:]
                shift_id_result += 1
                result += result_tab[id_result + shift_id_result][0]
            else:
                raise Exception

        elif len(gold) == 0 and len(result) == 0:
            return shift_id_gold + 1, shift_id_result + 1
        elif len(gold) == 0:
            shift_id_gold += 1
            token_to_be_added = gold_tab[id_gold + shift_id_gold][0]
            while token_to_be_added == '-DOCSTART-' or token_to_be_added == '':
                shift_id_gold += 1
                token_to_be_added = gold_tab[id_gold + shift_id_gold][0]
            gold += token_to_be_added

        elif len(result) == 0:
            shift_id_result += 1
            token = result_tab[id_result + shift_id_result]
            token_to_be_added = result_tab[id_result + shift_id_result][0]

            while True:
                if len(token) == 1 or token_to_be_added == '':
                    shift_id_result += 1
                    token = result_tab[id_result + shift_id_result]
                    token_to_be_added = result_tab[id_result + shift_id_result][0]
                else:
                    try:
                        token_to_be_added[0].decode("utf-8")  # Case with spacy and gmb
                        break
                    except:
                        shift_id_result += 1
                        token = result_tab[id_result + shift_id_result]
                        token_to_be_added = result_tab[id_result + shift_id_result][0]

            result += result_tab[id_result + shift_id_result][0]


def add_result_to_gold(gold_tab, result_tab):

    id_gold = 0
    id_result = 0
    errors = 0

    nb_token_gold = len(gold_tab)
    nb_token_result = len(result_tab)

    while id_gold < nb_token_gold:

        # if id_gold == 10000:
        #     print "<attention>"

        gold_token = gold_tab[id_gold]

        if id_result < nb_token_result:
            result_token = result_tab[id_result]
        else:
            result_token = result_tab[id_result - 1]

        # if no tags
        if len(result_token) == 1:
            result_token[0] = ''

        if gold_token[0] == '':
            print
            if result_token[0] == '':
                id_result += 1
            id_gold += 1
            continue
        elif result_token[0] == '':
            id_result += 1
            continue
        elif gold_token[0] == '-DOCSTART-':
            print_exp(gold_token, 'O')
            id_gold += 1
            continue
        elif gold_token[0] == result_token[0]:
            print_exp(gold_token, result_token[-1])
            id_result += 1
            id_gold += 1
            continue
        else:
            shift_id_gold = 0
            shift_id_result = 0
            try:
                # find next match
                shift_id_gold, shift_id_result = _find_shift(gold_tab, result_tab, id_gold, id_result)
            except:
                # case that happen with gate and gmb: gate add a line with a new word
                if gold_tab[id_gold][0] == result_tab[id_result + 1 ][0]:
                    shift_id_gold = 0
                    shift_id_result = 1
                else:
                    shift_id_gold = 1
                    shift_id_result = 1

            # Print
            for i in range(0, shift_id_gold):
                temp_gold_token = gold_tab[id_gold + i]
                if temp_gold_token[0] != '':
                    print_exp(temp_gold_token, 'O')

            errors += 1
            id_gold += shift_id_gold
            id_result += shift_id_result


def merge_files(gold_file, result_file):

    gold_tab = _file_to_tab(gold_file)
    result_tab = _file_to_tab(result_file)

    try:
        add_result_to_gold(gold_tab, result_tab)
    except:
        pass

# Open the results
def main(argv):

    with open(sys.argv[1]) as gold_file:
        with open(sys.argv[2]) as result_file:
            merge_files(gold_file, result_file)


if __name__ == '__main__':
    sys.exit(main(sys.argv))


