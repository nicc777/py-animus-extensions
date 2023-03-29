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


def nest_data(current_dict: dict, key_dotted_notation: str, value: object)->dict:
    keys = key_dotted_notation.split('.')
    if len(keys) == 1:
        current_dict[key_dotted_notation] = value
        return current_dict
    idx = 0
    d = dict()
    last_key = ''
    while len(keys) > 0:
        idx += 1
        key = keys.pop()
        last_key = copy.deepcopy(key)
        if idx == 1:
            d[key] = value
        else:
            d[key] = d
    current_dict[last_key] = d
    return current_dict    

spec = template_data['spec']
dotted_key = 'source.type'
source_type_data = nest_data(current_dict=spec, key_dotted_notation=dotted_key, value=spec[dotted_key])
spec.pop(dotted_key)
template_data['spec'] = spec
print(json.dumps(template_data))


            

