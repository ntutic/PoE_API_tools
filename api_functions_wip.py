def mod_key_values(db, keys, txts, mods):
    '''
    keys = list of mod keys
    txts = lits of mod texts
    mods = DataFrame of mods with 'key' (index), 'txt' and 'values'
    '''

    digit = False
    first_val = True
    dic_txts = {}
    for mod in txts:
        dic_txts[mod] = {'mod_clean': '', 'value1': '', 'value2': ''}
        for i, char in enumerate(mod):  
            if char.isnumeric() or char == '.':
                if not digit:
                    mod[i] = '#'
                    digit = True
                    if first_val:
                        dic_txts[mod]['value1'] += char
                    else:
                        dic_txts[mod]['value2'] += char
                elif digit:
                    mod[i] = ''
                    if first_val:
                        dic_txts[mod]['value1'] += char
                    else:
                        dic_txts[mod]['value2'] += char
            else:
                if digit:
                    first_val = False
                    digit = False
        dic_txts[mod]['mod_clean'] = ''.join(mod)
        dic_txts[mod]['value1'] = int(dic_txts[mod]['value1'])
        dic_txts[mod]['value2'] = int(dic_txts[mod]['value2'])
        dic_txts[mod]['key'] = db.mods_id.loc[mod_clean, type_]['id'].values[0]

    for key in keys:
        if not mods[key]['values']:
            dic += {mods[key]['id']}
        else:
            pass#mod for mod in mods if mod == 
    
    return dic