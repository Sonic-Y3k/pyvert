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
from .queue_element_config import ElementConfig

import pyvert

class QueueElement():
    COBJECT = Converter()
    HOBJECT = hdrpatcher()
    
    def __init__(self, filename):
        """ Inits a QueueElement

        Keyword Arguments:
        filename -- full path to a file
        """
        self.STATUS = 0
        self.PERCENT = 0.0
        self.HPERCENT = 0
        self.MPERCENT = 0
        self.FULLPATH = filename
        self.UUID = str(uuid.uuid4())
        self.CONFIG = ElementConfig()
        
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
        self.MOBJECT = MediaInfo.parse(filename)

        # checking for sps
        for t in self.MOBJECT.tracks:
            if t.track_type == 'Video' and t.format == 'HEVC':
                if hasattr(t, 'color_primaries') and hasattr(t, 'transfer_characteristics') and hasattr(t, 'matrix_coefficients'):
                    self.CONFIG.add_sps(t.color_primaries, t.transfer_characteristics, t.matrix_coefficients)
                
                if hasattr(t, 'mastering_display_luminance'):
                        self.CONFIG.add_sei(l=re.findall('\d+.\d+', t.mastering_display_luminance))
                        
                if hasattr(t, 'mastering_display_color_primaries'):
                    if 'BT.709' in t.mastering_display_color_primaries:
                        cwp = (15635, 16450)
                        cg = (15000, 30000)
                        cb = (7500, 3000)
                        cr = (32000, 16450)
                    elif 'BT.2020' in t.mastering_display_color_primaries:
                        cwp = (15635, 16450)
                        cg = (8500, 39850)
                        cb = (6550, 2300)
                        cr = (35400, 14600)
                    elif 'P3' in t.mastering_display_color_primaries:
                        cwp = (15635, 16450)
                        cg = (13250, 34500)
                        cb = (7500, 3000)
                        cr = (34000, 16000)
                    self.CONFIG.add_sei(wp=cwp, g=cg, b=cb, r=cr)
                
                if hasattr(t, 'maximum_content_light_level'):
                    try:
                        self.CONFIG.add_sei(mcll=re.findall('\d+', t.maximum_content_light_level))
                    except TypeError:
                        pass
                    
                if hasattr(t, 'maximum_frameaverage_light_level'):
                    try:
                        self.CONFIG.add_sei(mfll=re.findall('\d+', t.maximum_frameaverage_light_level))
                    except TypeError:
                        pass
        
        self.analyze()
        self.show()
        self.STATUS = 1

    def show(self):
        logger.debug('Adding \'{0}\''.format(basename(self.FULLPATH)))
        logger.debug(' - UUID: {}'.format(self.UUID))
        logger.debug(' - Size: {}'.format(sizeof_fmt(self.MEDIAINFO['format']['size'])))
        logger.debug(' - Duration: {}'.format(seconds_hr(self.MEDIAINFO['format']['duration'])))
        if self.CONFIG.has_hdr():
            logger.debug(' - HDR: Yes (SPS: {}, SEI: {})'.format(int(self.CONFIG.has_sps()), int(self.CONFIG.has_sps())))
        else:
            logger.debug(' - HDR: No')
        if self.CROP:
            logger.debug(' - CROP: {0}'.format(self.CROP))
        
    def analyze(self):
        abc = self.COBJECT.analyze(self.FULLPATH, crop=True, audio_level=False,
                                   duration=20, start=300)

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
                #logger.debug(' - Media Resolution: {0}x{1}'.format(
                #             stream['width'], stream['height'],
                #             crop_array[0], crop_array[1]))
                width = int(stream['width'])
                height = int(stream['height'])
                break

        if abs(width-4096) < 10 and abs(height-2160) < 10:
            cwidth = 4096
            if crop_array[3] <= 140:
                #logger.debug(' - Guessed aspect ratio: 1.90:1')
                cheight = 2160
            elif 140 < crop_array[3] <= 300:
                #logger.debug(' - Guessed aspect ratio: 2.39:1')
                cheight = 1716
        elif abs(width-3996) < 10 and abs(height-2160) < 10:
            cwidth = 3996
            if crop_array[3] <= 140:
                #logger.debug(' - Guessed aspect ratio: 1.85:1')
                cheight = 2160
        elif abs(width-3840) < 10 and abs(height-2160) < 10:
            cwidth = 3840
            if crop_array[3] <= 120:
                #logger.debug(' - Guessed aspect ratio: 16:9')
                cheight = 2160
            elif 120 < crop_array[3] <= 300:
                #logger.debug(' - Guessed aspect ratio: 12:5')
                cheight = 1600
        elif abs(width-1920) < 10 and abs(height-1080) < 10:
            cwidth = 1920
            if crop_array[3] <= 10:
                #logger.debug(' - Guessed aspect ratio: 16:9')
                cheight = 1080
            elif 10 < crop_array[3] <= 40:
                #logger.debug(' - Guessed aspect ratio: 1.85:1')
                cheight = 1038
            elif 40 < crop_array[3] < 70:
                #logger.debug(' - Guessed aspect ratio: 2:1')
                cheight = 960
            elif 80 < crop_array[3] <= 230:
                #logger.debug(' - Guessed aspect ratio: 2.40:0')
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
        
        self.CONFIG.add('map', [])
           
        # if we need to patch video stream for sps or sei packages
        if self.CONFIG.has_hdr():
            outfile = join(outdir, '{}.hevc'.format(self.UUID))
            self.CONFIG.add('format', 'hevc')
            for stream in self.MEDIAINFO['streams']:
                if 'mjpeg' not in stream['codec_name'] and 'video' in stream['codec_type']:
                    self.CONFIG.get('map').append(int(stream['index']))
                    continue
        else:
            outfile = join(outdir, '{}.{}'.format(self.UUID, pyvert.CONFIG.OUTPUT_FORMAT))
            self.CONFIG.add('format', pyvert.CONFIG.OUTPUT_FORMAT)
            self.CONFIG.add('audio', copy(pyvert.CONFIG.AUDIO_OPTIONS))
            self.CONFIG.get('audio')['codec'] = pyvert.CONFIG.AUDIO_CODEC
            self.CONFIG.add('subtitle', copy(pyvert.CONFIG.SUBTITLE_OPTIONS))
            self.CONFIG.get('subtitle')['codec'] = pyvert.CONFIG.SUBTITLE_CODEC
            
            for stream in self.MEDIAINFO['streams']:
                if 'mjpeg' not in stream['codec_name']:
                    self.CONFIG.get('map').append(int(stream['index']))

        self.CONFIG.add('max_muxing_queue_size', pyvert.CONFIG.MMQS)
        self.CONFIG.add('video', copy(pyvert.CONFIG.VIDEO_OPTIONS))
        self.CONFIG.get('video')['codec'] = pyvert.CONFIG.VIDEO_CODEC
        
        if pyvert.CONFIG.AUTOCROP:
            self.CONFIG.get('video')['crop'] = self.CROP
        
        
        if pyvert.CONFIG.DECODER in ['cuvid']:
            if vcodec in ['h264', 'hevc', 'vc1']:
                self.CONFIG.add('decoder', {'codec': vcodec+'_cuvid'})
        
        for i in self.COBJECT.convert(infile, outfile, self.CONFIG.gen_dict()):
            self.PERCENT = float(self.timecode_to_sec(i[2])/self.MEDIAINFO['format']['duration'])*100
        
        # if sps or sei present, now it's time to patch and remux
        if self.CONFIG.has_hdr():
            self.STATUS = 3
            houtfile = join(outdir, '{}_p.hevc'.format(self.UUID))
            
            self.HOBJECT.load(outfile)
            self.HOBJECT.process(0)
            
            if self.CONFIG.has_sei():
                self.HOBJECT.patch(sei=self.CONFIG.SEI)
            
            if self.CONFIG.has_sps():
                self.HOBJECT.patch(sps=self.CONFIG.SPS)
                
            for i in self.HOBJECT.write(houtfile):
                self.HPERCENT = i
            self.HOBJECT.close_streams()
            
            self.STATUS = 4
            m = MKVMerge()
            noutfile = join(outdir, '{}.{}'.format(self.UUID, pyvert.CONFIG.OUTPUT_FORMAT))
            options = {houtfile: ['-A', '-S'], infile: ['-D']}
            for i in m.merge([houtfile, infile], noutfile, options, self.CONFIG.get_hdr()):
                self.MPERCENT = i
            
            # remux successful, let's delete the temp file
            os.remove(houtfile)
            os.remove(outfile)
            outfile = noutfile
        
        # rename uuid.mkv
        x = 0
        while True:
            fn = '{}{}.{}'.format(os.path.splitext(basename(infile))[0], '_({})'.format(x) if x > 0 else '', pyvert.CONFIG.OUTPUT_FORMAT)
            fp = join(outdir, fn)
            if not Path(fp).exists():
                break
            x += 1
            
        os.rename(outfile, fp)
        return True
