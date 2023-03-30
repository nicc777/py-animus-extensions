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
    pass


def merge_dicts(A: dict, B: dict)->dict:
    # FROM https://stackoverflow.com/questions/29241228/how-can-i-merge-two-nested-dictionaries-together (Vivek Sable)
    for i, j in B.items(): 
        if i in A:
            A[i].update(j)
        else:
            A[i] = j
    return A


spec = copy.deepcopy(template_data['spec'])
for dotted_key in list(spec.keys()):
    nested_data = nest_data(key_dotted_notation=dotted_key, value=spec[dotted_key])
    spec.pop(dotted_key)
    spec = merge_dicts(A=copy.deepcopy(spec), B=copy.deepcopy(nested_data))


template_data['spec'] = copy.deepcopy(spec)


print(json.dumps(template_data))




