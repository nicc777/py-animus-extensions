import json
import copy

template_data = {
    "kind": "ShellScript",
    "version": "v1",
    "metadata": {
        "name": "shell-script-v1-minimal",
        "skipDeleteAll": True
    },
    "spec": {
        "shellInterpreter": "sh",
        "source.type": "inLine",
        "source.value": "echo \"Not Yet Implemented\""
    }
}


def add_parent_key_to_dict(current_dict: dict, parent_key: str):
    new_dict = dict()
    new_dict[parent_key] = current_dict
    return new_dict


def nest_data(key_dotted_notation: str, value: object)->dict:
    keys = key_dotted_notation.split('.')
    idx = 0
    d = dict()
    last_key = ''
    while len(keys) > 0:
        idx += 1
        key = keys.pop()
        # print('idx={}   len(keys)={}'.format(idx, len(keys)))
        last_key = copy.deepcopy(key)
        if idx == 1:
            d[key] = value
            if len(keys) > 1:
                d = add_parent_key_to_dict(current_dict=d, parent_key=keys[-1])
        else:
            d = add_parent_key_to_dict(current_dict=d, parent_key=key)
            if len(keys) > 1:
                d = add_parent_key_to_dict(current_dict=d, parent_key=keys[-1])
        # print('* d={}'.format(d))
    print('-> d={}'.format(d))
    return d


def merge_dicts(d1: dict, d2: dict)->dict:
    for k, v in d2.items():
        if k in d1:
            d1 = {**d1[k], **d2[k]}
        else:
            d1[k] = v
    return d1


spec = copy.deepcopy(template_data['spec'])
for dotted_key in list(spec.keys()):
    data_dict = nest_data(key_dotted_notation=dotted_key, value=spec[dotted_key])
    print('source_type_data={}'.format(data_dict))
    spec.pop(dotted_key)
    spec = merge_dicts(d1=spec, d2=data_dict)

template_data['spec'] = copy.deepcopy(spec)


print(json.dumps(template_data))




