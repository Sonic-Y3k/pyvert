import json


class Config():
    VALID_FILE_EXTENSIONS = ['.mkv']
    SCAN_DIRECTORY = '/Users/tschoenbach/Downloads/Test'
    OUTPUT_DIRECTORY = '/tmp/output'
    VIDEO_CODEC = 'hevc_nvenc'
    AUDIO_CODEC = 'copy'
    SUBTITLE_CODEC = 'copy'
    AUTOCROP = True
    DECODER = 'h264_cuvid'
    VIDEO_OPTIONS = {
        'profile': 'main10',
        'preset': 'slow',
        'rc': 'vbr',
        'rc-lookahead': 32,
        'qmin': 15.0,
        'qmax': 25.0,
        'pix_fmt': 'yuv444p16le',
    }
    OUTPUT_FORMAT = 'mkv'
    AUDIO_OPTIONS = {}
    SUBTITLE_OPTIONS = {}
    HTTP_PORT = 80
    HTTP_HOST = '127.0.0.1'
    HTTP_ROOT = ''
    HTTP_ENVIRONMENT = ''
    INTERFACE = 'default'

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
        json.dump(self.get_all_variables(), file_handler, indent=4,
                  sort_keys=True)
