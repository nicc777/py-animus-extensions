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
        elif self.__class__.__name__ == 'Field':
            return {self.name: self.value.to_dict()}
        return {self.name: self.value}


class ComplexDict:

    def __init__(self):
        self.fields = list()

    def to_dict(self):
        d = dict()
        for field in self.fields:
            d[field.name] = d.to_dict()
        return d


def embed_field(dotted_name: str, value: object)->Field:
    field_names = dotted_name.split('.')
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
    
template_data['spec'] = spec_dict.to_dict()
print(json.dumps(template_data))
