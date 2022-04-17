import base64, json, ast
from django.core.files.base import ContentFile

class convert_string_to_list:
    @classmethod
    def convert_to_list(self, data):
        try:
            return_data = ast.literal_eval(data)
        except:
            qery_list = json.dumps(data)
            return_data = ast.literal_eval(qery_list)
        return return_data


class base_encoding:
    @classmethod
    def base64_file(self, data, name=None):
        print(data)
        _format, _img_str = data.split(';base64,')
        _name, ext = _format.split('/')
        if not name:
            name = _name.split(":")[-1]
        return ContentFile(base64.b64decode(_img_str), name='{}.{}'.format(name, ext))

