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


class ComplexDict:

    def __init__(self):
        self.fields = list()


def embed_field(dotted_name: str, value: object)->Field:
    field_names = field_name.split('.')
    if len(field_names) > 1:
        next_dotted_name = '.'.join(field_names[1:])
        field = Field(name=field_name, value=embed_field(dotted_name=next_dotted_name, value=value))
    else:
        field = Field(name=field_name, value=copy.deepcopy(field_data))
    return field


spec_dict = ComplexDict()
spec = template_data['spec']
for field_name, field_data in spec.items():
    field_names = field_name.split('.')
    if len(field_names) > 1:
        spec_dict.fields.append(embed_field(dotted_name=field_name, value=copy.deepcopy(field_data)))
    else:
        spec_dict.fields.append(Field(name=field_name, value=copy.deepcopy(field_data)))
    

