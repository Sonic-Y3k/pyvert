import json


class Config():
    VALID_FILE_EXTENSIONS = ['.mkv']
    SCAN_DIRECTORY = '/Users/tschoenbach/Downloads/Test'
    OUTPUT_DIRECTORY = '/tmp/output'
    VIDEO_CODEC = 'hevc_vaapi'
    AUDIO_CODEC = 'copy'
    SUBTITLE_CODEC = 'copy'
    AUTOCROP = True
    DECODER = ''
    VIDEO_OPTIONS = {
        'aspect_filters': 'format=p010,hwupload',
        'vprofile': 2,
        'qp': 20.0,
        'pix_fmt': 'vaapi_vld',
    }
    OUTPUT_FORMAT = 'mkv'
    AUDIO_OPTIONS = {}
    SUBTITLE_OPTIONS = {}
    HTTP_PORT = 8080
    HTTP_HOST = '127.0.0.1'
    HTTP_ROOT = ''
    HTTP_ENVIRONMENT = ''
    INTERFACE = 'default'
    MMQS = 4000  # max_muxing_queue_size
    CONCURRENT_JOBS = 1

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
