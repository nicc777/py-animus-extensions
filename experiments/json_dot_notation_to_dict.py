import json
import copy


input_data = '''{
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

"""
The original_data2 transformed will now look like this:

{
    "kind": "ShellScript",
    "version": "v1",
    "metadata": {
        "name": "shell-script-v1-minimal",
        "skipDeleteAll": true
    },
    "spec": {
        "shellInterpreter": "sh",
        "source": {
            "type": "inLine",
            "value": "echo \"Not Yet Implemented\"",
            "test": {
                "alt1": "111",
                "alt2": "222"
            }
        }
    }
}
"""


input_data_converted = json.loads(input_data)        


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


output_data = dict()
for t_field_name, t_field_data in input_data_converted.items():
    if isinstance(t_field_data, dict):
        converted_t_field_data = dict()
        for field_name, field_data in t_field_data.items():
            embedded_field = embed_field(dotted_name=field_name, value=copy.deepcopy(field_data))
            for k,v in embedded_field.to_dict().items():
                if k not in converted_t_field_data:
                    converted_t_field_data[k] = v
                else:
                    if isinstance(v, dict):
                        converted_t_field_data[k] = merge_dicts(A=converted_t_field_data[k], B=v)
                    else:
                        converted_t_field_data[k] = v
        output_data[t_field_name] = converted_t_field_data
    else:
        output_data[t_field_name] = t_field_data    
    
    
print(json.dumps(output_data))
