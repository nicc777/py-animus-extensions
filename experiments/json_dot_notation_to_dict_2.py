import json
import copy


# WORKING
original_data1 = '''{
    "kind": "ShellScript",
    "version": "v1",
    "metadata": {
        "name": "shell-script-v1-minimal",
        "skipDeleteAll": true
    },
    "spec": {
        "shellInterpreter": "sh",
        "source.type": "inLine",
        "source.value": "echo \\"Not Yet Implemented\\""
    }
}
'''

# FIXME  NOT WORKING YET
original_data2 = '''{
    "kind": "ShellScript",
    "version": "v1",
    "metadata": {
        "name": "shell-script-v1-minimal",
        "skipDeleteAll": true
    },
    "spec": {
        "shellInterpreter": "sh",
        "source.type": "inLine",
        "source.value": "echo \\"Not Yet Implemented\\"",
        "source.test.alt1": "111",
        "source.test.alt2": "222"
    }
}
'''


template_data = json.loads(original_data2)


def add_parent_key_to_dict(current_dict: dict, parent_key: str):
    new_dict = dict()
    new_dict[parent_key] = current_dict
    return new_dict


def nest_data(key_dotted_notation: str, value: object)->dict:
    final_dict = dict()
    keys = key_dotted_notation.split('.')
    mapped_keys = dict()
    idx = 0
    for key in keys:
        mapped_keys[idx] = key
        idx += 1
    indexes = list(mapped_keys.keys())
    indexes.sort(reverse=True)
    last_key = mapped_keys[indexes.pop(0)]
    final_dict[last_key] = value
    for idx in indexes:
        key_name = mapped_keys[idx]
        temp_dict = copy.deepcopy(final_dict)
        final_dict = dict()
        final_dict[key_name] = temp_dict
    return final_dict


def merge_dicts(A: dict, B: dict)->dict:
    # FROM https://stackoverflow.com/questions/29241228/how-can-i-merge-two-nested-dictionaries-together (Vivek Sable)
    for i, j in B.items(): 
        if i in A:
            A[i].update(j)
        else:
            A[i] = j
    return A


spec = copy.deepcopy(template_data['spec'])
final_spec = dict()
for dotted_key in list(spec.keys()):
    current_value = spec[dotted_key]
    nested_data = nest_data(key_dotted_notation=dotted_key, value=spec[dotted_key])

    nested_data_base_key = list(nested_data.keys())[0]
    if dotted_key != nested_data_base_key:
        if nested_data_base_key not in final_spec:
            final_spec[nested_data_base_key] = nested_data[nested_data_base_key]
        else:
            current_dict = copy.deepcopy(final_spec[nested_data_base_key])
            final_spec[nested_data_base_key] = {**current_dict, **nested_data[nested_data_base_key]}
    else:
        final_spec[dotted_key] = current_value

    # spec.pop(dotted_key)
    # spec = merge_dicts(A=copy.deepcopy(spec), B=copy.deepcopy(nested_data))
template_data['spec'] = copy.deepcopy(final_spec)


# template_data['spec'] = copy.deepcopy(spec)


print(json.dumps(template_data))




