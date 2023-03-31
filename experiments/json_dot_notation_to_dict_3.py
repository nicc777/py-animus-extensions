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


class ComplexDict:

    def __init__(self):
        self.fields = list()

    def add_field(self, f: Field):
        found = False
        for current_field in self.fields:
            if current_field.name == f.name:
                current_field.children.append(f)
                current_field.value = None
                found = True
        if found is False:
            self.fields.append(f)

    def to_dict(self):
        d = dict()
        for field in self.fields:
            field_dict = field.to_dict()
            for k,v in field_dict.items():
                d[k] = v
        return d


def embed_field(dotted_name: str, value: object)->Field:
    field_names = dotted_name.split('.')
    if len(field_names) > 1:
        next_dotted_name = '.'.join(field_names[1:])
        field = Field(name=field_names[0], value=embed_field(dotted_name=next_dotted_name, value=value))
    else:
        field = Field(name=field_names[0], value=copy.deepcopy(field_data))
    return field


def add_data_to_dict(d: dict, data: object):
    pass



spec_dict = ComplexDict()
spec = template_data['spec']
new_spec = dict()
for field_name, field_data in spec.items():
    # spec_dict.fields.append(embed_field(dotted_name=field_name, value=copy.deepcopy(field_data)))
    embedded_field = embed_field(dotted_name=field_name, value=copy.deepcopy(field_data))
    print('embedded_field={}'.format(embedded_field.to_dict()))
    for k,v in embedded_field.to_dict().items():
        if k not in new_spec:
            new_spec[k] = v
        else:
            if isinstance(v, dict):
                new_spec[k] = {**new_spec[k], **v}
            else:
                new_spec[k] = v
    
template_data['spec'] = new_spec
print(json.dumps(template_data))
