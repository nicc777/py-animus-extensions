import json
import copy


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


class Field:

    def __init__(self, name: str, value: object=None):
        self.name = name
        self.children = list()
        self.value = value

    def to_dict(self):
        if self.value is None:
            return {self.name: None}
        elif self.value.__class__.__name__ == 'Field':
            return {self.name: self.value.to_dict()}
        return {self.name: self.value}


def embed_field(dotted_name: str, value: object)->Field:
    field_names = dotted_name.split('.')
    if len(field_names) > 1:
        next_dotted_name = '.'.join(field_names[1:])
        field = Field(name=field_names[0], value=embed_field(dotted_name=next_dotted_name, value=value))
    else:
        field = Field(name=field_names[0], value=copy.deepcopy(field_data))
    return field


def merge_dicts(A: dict, B: dict)->dict:
    # FROM https://stackoverflow.com/questions/29241228/how-can-i-merge-two-nested-dictionaries-together (Vivek Sable)
    for i, j in B.items(): 
        if i in A:
            A[i].update(j)
        else:
            A[i] = j
    return A


final_template_data = dict()
for t_field_name, t_field_data in template_data.items():
    spec = copy.deepcopy(template_data[t_field_name])
    new_spec = dict()
    if isinstance(spec, dict):
        for field_name, field_data in spec.items():
            embedded_field = embed_field(dotted_name=field_name, value=copy.deepcopy(field_data))
            for k,v in embedded_field.to_dict().items():
                if k not in new_spec:
                    new_spec[k] = v
                else:
                    if isinstance(v, dict):
                        new_spec[k] = merge_dicts(A=new_spec[k], B=v)
                    else:
                        new_spec[k] = v
        final_template_data[t_field_name] = new_spec
    else:
        final_template_data[t_field_name] = t_field_data    
    
    
print(json.dumps(final_template_data))
