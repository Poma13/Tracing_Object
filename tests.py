'''
new_dict = {}
for key in tracking_objs.keys():
    if not(tracking_objs[key] in new_dict.values()):
        new_dict[key] = tracking_objs[key]

    else:
        old_key = -1
        for k1 in new_dict.keys():
            if new_dict[k1] == tracking_objs[key] and k1 > key:
                old_key = k1
        if old_key != -1:
            del new_dict[old_key]
            new_dict[key] = tracking_objs[old_key]

tracking_objs = new_dict
'''
