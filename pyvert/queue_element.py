import uuid
import re
import os
from pathlib import Path
from copy import copy
from converter import Converter
from converter.ffmpeg import FFMpegConvertError
from os.path import join, basename
from .helper import sizeof_fmt, seconds_hr
from . import logger
from mkvmerge import MKVMerge
from hevc_hdr_patcher import hdrpatcher
from pymediainfo import MediaInfo

import pyvert

class QueueConfig():
    def __init__(self, sps, sei, config):
        self.SPS = sps
        self.SEI = sei
        self.CONFIG = config
        
    def getc(self, name):
        return getattr(self, name)
        
    def setc(self, name, value):
        setattr(self, name, value)

class QueueElement():
    FULLPATH = None
    STATUS = None
    PERCENT = 0.0
    HPERCENT = 0
    MPERCENT = 0
    MEDIAINFO = None
    UUID = None
    COBJECT = Converter()
    HOBJECT = hdrpatcher()
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
        Status (2) = processing_ffmpeg
        Status (3) = processing_hdrpatch
        Status (4) = processing_merge
        Status (5) = finished
        Status (6) = failed
        """
        self.STATUS = 0
        self.MEDIAINFO = self.COBJECT.probe(filename, posters_as_video=False)
        logger.debug(' - Size: {}'.format(sizeof_fmt(
                     self.MEDIAINFO['format']['size'])))
        logger.debug(' - Duration: {}'.format(seconds_hr(
                     self.MEDIAINFO['format']['duration'])))

        self.MOBJECT = MediaInfo.parse(filename)
        # checking for sps
        for t in self.MOBJECT.tracks:
            if t.track_type == 'Video' and t.format == 'HEVC':
                if hasattr(t, 'color_primaries') and hasattr(t, 'transfer_characteristics') and hasattr(t, 'matrix_coefficients'):
                    logger.debug(' - Has SPS: Yes')
                    self.SPS = {}
                    self.SPS['colour_primaries'] = t.color_primaries
                    self.SPS['transfer_characteristics'] = t.transfer_characteristics
                    self.SPS['matrix_coeffs'] = t.matrix_coefficients
                if hasattr(t, 'mastering_display_luminance') and hasattr(t, 'mastering_display_color_primaries'):
                    logger.debug(' - Has SEI_0: Yes')
                    self.SEI = {}
                    mdl = re.findall('\d+.\d+', t.mastering_display_luminance)
                    self.SEI['L'] = (int(mdl[1])*10000, int(float(mdl[0])*10000))
                    
                    if 'BT.709' in t.mastering_display_color_primaries:
                        self.SEI['WP'] = (15635, 16450)
                        self.SEI['G'] = (15000, 30000)
                        self.SEI['B'] = (7500, 3000)
                        self.SEI['R'] = (32000, 16450)
                    elif 'BT.2020' in t.mastering_display_color_primaries:
                        self.SEI['WP'] = (15635, 16450)
                        self.SEI['G'] = (8500, 39850)
                        self.SEI['B'] = (6550, 2300)
                        self.SEI['R'] = (35400, 14600)
                    elif 'P3' in t.mastering_display_color_primaries:
                        self.SEI['WP'] = (15635, 16450)
                        self.SEI['G'] = (13250, 34500)
                        self.SEI['B'] = (7500, 3000)
                        self.SEI['R'] = (34000, 16000)
                if hasattr(t, 'maximum_content_light_level') and hasattr(t, 'maximum_frameaverage_light_level'):
                    logger.debug(' - Has SEI_1: Yes')
                    self.SEI['MDPC'] = int(re.findall('\d+', t.maximum_content_light_level)[0])
                    self.SEI['MDL'] = int(re.findall('\d+', t.maximum_frameaverage_light_level)[0])

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
        vcodec = self.get_vcodec()
        options = {self.UUID: {}}
        options['map'] = []
        
        
        
        # if we need to patch video stream for sps or sei packages
        if hasattr(self, 'SPS') or hasattr(self, 'SEI'):
            logger.debug('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
            outfile = join(outdir, '{}.hevc'.format(self.UUID))
            options['format'] = 'hevc'
            for stream in self.MEDIAINFO['streams']:
                if 'mjpeg' not in stream['codec_name'] and 'video' in stream['codec_type']:
                    options['map'].append(int(stream['index']))
                    #continue
        else:
            self.SPS = self.SEI = {}
            outfile = join(outdir, '{}.{}'.format(self.UUID, pyvert.CONFIG.OUTPUT_FORMAT))
            options['format'] = pyvert.CONFIG.OUTPUT_FORMAT
            options['audio'] = copy(pyvert.CONFIG.AUDIO_OPTIONS)
            options['subtitle'] = copy(pyvert.CONFIG.SUBTITLE_OPTIONS)
            options['audio']['codec'] = pyvert.CONFIG.AUDIO_CODEC
            options['subtitle']['codec'] = pyvert.CONFIG.SUBTITLE_CODEC
            for stream in self.MEDIAINFO['streams']:
                if 'mjpeg' not in stream['codec_name']:
                    options['map'].append(int(stream['index']))

        options['max_muxing_queue_size'] = pyvert.CONFIG.MMQS            
        options['video'] = copy(pyvert.CONFIG.VIDEO_OPTIONS)
        options['video']['codec'] = pyvert.CONFIG.VIDEO_CODEC
        
        if pyvert.CONFIG.AUTOCROP:
            options['video']['crop'] = self.CROP
        
        
        if pyvert.CONFIG.DECODER in ['cuvid']:
            if vcodec in ['h264', 'hevc', 'vc1']:
                options['decoder'] = {'codec': vcodec+'_cuvid'}
        
        for i in self.COBJECT.convert(infile, outfile, options):
            self.PERCENT = float(self.timecode_to_sec(i[2])/self.MEDIAINFO['format']['duration'])*100
        
        # if sps or sei present, now it's time to patch and remux
        if len(self.SPS) > 0 or len(self.SEI) > 0:
            self.STATUS = 3
            houtfile = join(outdir, '{}_p.hevc'.format(self.UUID))
            
            
            self.HOBJECT.load(outfile)
            self.HOBJECT.patch(sei=self.SEI, sps=self.SPS)
            for i in self.HOBJECT.write(houtfile):
                self.HPERCENT = i
            self.HOBJECT.close_streams()
            
            self.STATUS = 4
            m = MKVMerge()
            noutfile = join(outdir, '{}.{}'.format(self.UUID, pyvert.CONFIG.OUTPUT_FORMAT))
            options = {houtfile: ['-A', '-S'], infile: ['-D']}
            for i in m.merge([houtfile, infile], noutfile, options):
                self.MPERCENT = i
            
            # remux successful, let's delete the temp file
            os.remove(houtfile)
            os.remove(outfile)
            outfile = noutfile
        
        # rename uuid.mkv
        x = 0
        while True:
            fn = '{}{}.{}'.format(os.path.splitext(basename(infile))[0], x if x > 0 else '', pyvert.CONFIG.OUTPUT_FORMAT)
            fp = join(outdir, fn)
            if not Path(fp).exists():
                break
            x += 1
            
        os.rename(outfile, fp)
        return True
