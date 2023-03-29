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
        print('idx={}   len(keys)={}'.format(idx, len(keys)))
        last_key = copy.deepcopy(key)
        if idx == 1:
            d[key] = value
        else:
            d = add_parent_key_to_dict(current_dict=d, parent_key=key)
        print('* d={}'.format(d))
    return d


for dotted_key in ('source.type', 'source.value', ):
    #dotted_key = 'source.type'
    spec = template_data['spec']
    source_type_data = nest_data(key_dotted_notation=dotted_key, value=spec[dotted_key])
    print('source_type_data={}'.format(source_type_data))
    template_data['spec'].pop(dotted_key)
    template_data['spec'] = {**template_data['spec'], **source_type_data}

print(json.dumps(template_data))


            

