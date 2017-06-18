import json


class Config():
    TEST = "abc"
    ABCD = ['a', 'b', 'c', 1]
    DEFG = {'a': 2}

    def __init__(self):
        """
        """

    def get_all_variables(self):
        result = {}
        attrs = [attr for attr in dir(self) 
                 if not callable(getattr(self, attr))
                 and not attr.startswith("__")]
        for att in attrs:
            result[att] = getattr(self, att)

        return result

    def load_config_file(self, conf_file):
        """
        """
        file_handler = open(conf_file, 'r')
        attrs = json.load(file_handler)
        for attr in attrs:
            setattr(self, attr, attrs[attr])

    def save_config_file(self, conf_file):
        """
        """
        file_handler = open(conf_file, 'w')
        json.dump(self.get_all_variables(), file_handler)
