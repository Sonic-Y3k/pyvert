import uuid
from converter import Converter
from converter.ffmpeg import FFMpegConvertError
from os.path import join, basename
from .helper import sizeof_fmt, seconds_hr
from . import logger


import pyvert


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
        logger.debug(' - UUID: {}'.format(self.UUID))
        """
        Status (0) = added
        Status (1) = scanned
        Status (2) = processing
        Status (3) = finished
        Status (4) = failed
        """
        self.STATUS = 0
        self.MEDIAINFO = self.COBJECT.probe(filename, posters_as_video=False)
        logger.debug(' - Size: {}'.format(sizeof_fmt(
                     self.MEDIAINFO['format']['size'])))
        logger.debug(' - Duration: {}'.format(seconds_hr(
                     self.MEDIAINFO['format']['duration'])))

        #if ('unknown' not in self.get_video_stream()['color_primaries']):
        #    logger.debug(' - Has HDR: Yes')
        #    self.HDR = True
        #else:
        #    logger.debug(' - Has HDR: No')
        #    self.HDR = False

        self.analyze()
        self.STATUS = 1

    def analyze(self):
        abc = self.COBJECT.analyze(self.FULLPATH, crop=True, audio_level=False,
                                   duration=20, start=60)

        try:
            for a in abc:
                try:
                    logger.debug('Analyze: {0:.2f}%'.format(float(a/20)*100))
                except TypeError:
                    pass

            self.CROP = a[2]
        except TypeError as e:
            logger.warning('Analyze failed in {}'.format(self.FULLPATH) +
                           ' with {}.'.format(e))
            self.CROP = '0:0:0:0'
        
        self.crop_correction()

    def crop_correction(self):
        """
        """
        crop_array = []
        for i in self.CROP.split(':'):
            crop_array.append(int(i))
        width = 0
        cwidth = 0
        height = 0
        cheight = 0
        for stream in self.MEDIAINFO['streams']:
            if stream['codec_type'] == 'video':
                logger.debug(' - Media Resolution: {0}x{1}'.format(
                             stream['width'], stream['height'],
                             crop_array[0], crop_array[1]))
                width = int(stream['width'])
                height = int(stream['height'])
                break

        logger.debug(' - Cropdetect res: {}'.format(self.CROP))
        if abs(width-4096) < 10 and abs(height-2160) < 10:
            cwidth = 4096
            if crop_array[3] <= 140:
                logger.debug(' - Guessed aspect ratio: 1.90:1')
                cheight = 2160
            elif 140 < crop_array[3] <= 300:
                logger.debug(' - Guessed aspect ratio: 2.39:1')
                cheight = 1716
        elif abs(width-3996) < 10 and abs(height-2160) < 10:
            cwidth = 3996
            if crop_array[3] <= 140:
                logger.debug(' - Guessed aspect ratio: 1.85:1')
                cheight = 2160
        elif abs(width-3840) < 10 and abs(height-2160) < 10:
            cwidth = 3840
            if crop_array[3] <= 120:
                logger.debug(' - Guessed aspect ratio: 16:9')
                cheight = 2160
            elif 120 < crop_array[3] <= 300:
                logger.debug(' - Guessed aspect ratio: 12:5')
                cheight = 1600
        elif abs(width-1920) < 10 and abs(height-1080) < 10:
            cwidth = 1920
            if crop_array[3] <= 10:
                logger.debug(' - Guessed aspect ratio: 16:9')
                cheight = 1080
            elif 10 < crop_array[3] <= 40:
                logger.debug(' - Guessed aspect ratio: 1.85:1')
                cheight = 1038
            elif 40 < crop_array[3] < 70:
                logger.debug(' - Guessed aspect ratio: 2:1')
                cheight = 960
            elif 80 < crop_array[3] <= 230:
                logger.debug(' - Guessed aspect ratio: 2.40:0')
                cheight = 800
            else:
                cheight = height
        else:
            cwidth = width
            cheight = height

        self.CROP = '{0}:{1}:{2}:{3}'.format(
                    cwidth,
                    cheight,
                    abs(width-cwidth),
                    round(abs(height-cheight)/2))
        logger.debug(' - Set crop to {0}'.format(self.CROP))

    def get_vcodec(self):
        """
        """
        return '{0}'.format(self.get_video_stream()['codec_name'])

    def get_video_stream(self):
        """
        """
        for stream in self.MEDIAINFO['streams']:
            if stream['codec_type'] == 'video':
                return stream
        return 'None'

    def timecode_to_sec(self, tc):
        """
        """
        if ':' in tc:
            timecode = 0
            for part in tc.split(':'):
               timecode = 60 * timecode + float(part)
        else:
            timecode = float(tc)
        
        return timecode

    def convert(self, outdir):
        """
        """
        infile = self.FULLPATH
        options = {}
        #if (self.HDR):
        if False:
            outfile = join(outdir, '{0}.{1}'.format(basename(infile), 'hevc'))
            options['format'] = 'hevc'
            options['video'] = pyvert.CONFIG.VIDEO_OPTIONS
            if pyvert.CONFIG.AUTOCROP:
                options['video']['crop'] = self.CROP

        else:
            outfile = join(outdir, basename(infile))
            options['format'] = pyvert.CONFIG.OUTPUT_FORMAT
            options['video'] = pyvert.CONFIG.VIDEO_OPTIONS
            options['video']['codec'] = pyvert.CONFIG.VIDEO_CODEC
            if pyvert.CONFIG.AUTOCROP:
                options['video']['crop'] = self.CROP
            options['audio'] = pyvert.CONFIG.AUDIO_OPTIONS
            options['audio']['codec'] = pyvert.CONFIG.AUDIO_CODEC
            options['subtitle'] = pyvert.CONFIG.SUBTITLE_OPTIONS
            options['subtitle']['codec'] = pyvert.CONFIG.SUBTITLE_CODEC
            options['map'] = []
            for stream in self.MEDIAINFO['streams']:
                if stream['codec_name'] not in' mjpeg':
                    options['map'].append(int(stream['index']))

        vcodec = self.get_vcodec()
        if pyvert.CONFIG.DECODER in ['cuvid']:
            if vcodec in ['h264', 'hevc', 'vc1']:
                options['decoder'] = {'codec': vcodec+'_cuvid'}
        options['max_muxing_queue_size'] = pyvert.CONFIG.MMQS
        
        for i in self.COBJECT.convert(infile, outfile, options):
            self.PERCENT = float(self.timecode_to_sec(i[2])/self.MEDIAINFO['format']['duration'])*100
        
        return True
