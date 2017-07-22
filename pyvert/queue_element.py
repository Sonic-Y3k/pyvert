import uuid
from converter import Converter
from os.path import join, basename


class QueueElement():
    FULLPATH = None
    STATUS = None
    PERCENT = 0.0
    MEDIAINFO = None
    UUID = None
    COBJECT = Converter()
    CROP = None

    def __init__(self, filename):
        """ Inits a QueueElement

        Keyword Arguments:
        filename -- full path to a file
        """
        self.FULLPATH = filename
        self.UUID = str(uuid.uuid4())
        """
        Status (0) = added
        Status (1) = scanned
        Status (2) = processing
        Status (3) = finished
        Status (4) = failed
        """
        self.STATUS = 0
        self.MEDIAINFO = self.COBJECT.probe(filename, posters_as_video=False)
        self.analyze()
        self.STATUS = 1

    def analyze(self):
        s = round(self.MEDIAINFO['format']['duration'] / 2)
        abc = self.COBJECT.analyze(self.FULLPATH, crop=True, audio_level=False,
                                   duration=s)
        for a in abc:
            pass

        self.CROP = a[2]

    def convert(self, outdir):
        """
        """
        infile = self.FULLPATH
        outfile = join(outdir, basename(infile))
        options = {
            'format': 'mkv',
            'audio': {
                'codec': 'copy'
            },
            'video': {
                'codec': 'nvenc_hevc',
                'profile': 'main10',
                'preset': 'slow',
                'rc': 'vbr',
                'crop': self.CROP,
                'rc-lookahead': 32,
                'pix_fmt': 'yuv444p16le'
            },
            'map': 0,
            'decoder': {
                'codec': 'hevc_cuvid'
            }
        }
        return self.COBJECT.convert(infile, outfile, options)
