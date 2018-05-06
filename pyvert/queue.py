from threading import RLock
from os import path, walk, stat
from time import time
import re
import pyvert
from pyvert import config, logger, queue_element, hdr
from json.decoder import JSONDecodeError

queue_lock = RLock()


class Queue():
    queue = None
    ignore = None
    active = None

    def __init__(self):
        """
        """
        self.queue = []
        self.ignore = []
        self.active = 0

    def gffd(self, directory, recursive=True):
        """ Scans directory for new files

        Keyword arguments:
        directory -- a path to a directory
        recursive -- recursive search
        """
        result = []
        if path.isdir(directory):
            #logger.debug('Starting scan in directory \'{}\''.format(
            #              directory))
            for root, directories, filenames in walk(directory):
                directories.sort()
                for filename in sorted(filenames):
                    temp_fullpath = path.join(root, filename)
                    if temp_fullpath not in self.ignore:
                        result.append(temp_fullpath)
        return result

    def get_index_from_queue(self, element):
        """ Returns the index for a given element
            by a element from that queue

        Keyword Arguments:
        element -- a element from queue
        """
        return self.queue.index(element)

    def get(self, index):
        """ Returns a element from queue by id

        Keyword Arguments:
        index -- index for a element
        """
        with queue_lock:
            if (index >= 0) and (index < len(self.queue)):
                return self.queue[index]
            else:
                return None

    def modify(self, qindex, argument, value):
        """ Modifies element in queue
        """
        with queue_lock:
            # qindex = self.get_index_from_queue(element)
            if qindex >= 0:
                try:
                    setattr(self.queue[qindex], argument, value)
                except Exception as e:
                    logger.error(e) 
            else:
                logger.error('Element not in queue')

    def get_next_to_work(self):
        """ Returns the index of that element
            that is next to process
        """
        result = -1
        with queue_lock:
            for index, element in enumerate(self.queue):
                if element.STATUS == 1:
                    return index
        return result

    def get_active_idx(self):
        """
        """
        result = []
        with queue_lock:
            for index, element in enumerate(self.queue):
                if 2 <= element.STATUS <= 4:
                    result.append(index)
        return result

    def scan(self, directory):
        """ Scans directory for new files
        """
        #logger.debug('Starting scan in directory \'{}\''.format(directory))
        filenames = self.gffd(directory)
        for temp_fullpath in filenames:
            try:
                if self.scan_time_modified(temp_fullpath) and \
                   self.scan_file_extension(temp_fullpath) and \
                   self.scan_output_directory(temp_fullpath) and \
                   self.scan_size(temp_fullpath):
                    temp_file = None
                    logger.debug('Adding \'{0}\''.format(
                                 path.basename(temp_fullpath)))
                    temp_file = queue_element.QueueElement(temp_fullpath)
                    with queue_lock:
                        self.queue.append(temp_file)
                        self.ignore.append(temp_fullpath)
            except FileNotFoundError as e:
                logger.error('\'{}\' throws \'{}\''.format(
                                 temp_fullpath, e))
            except JSONDecodeError as e:
                logger.error('failed to parse mediainfo ' +
                             'from \'{}\''.format(temp_fullpath))
            finally:
                """"""
        #logger.debug('Finishing scan in directory \'{}\''.format(
        #             directory))

    def scan_time_modified(self, filename, t=30):
        """ Checks if file was at least modified t seconds ago

        Keyword arguments:
        filename -- fullpath to a file to check
        t -- minimum seconds since last file modification
        """
        check_query = (abs(time() - path.getmtime(filename)) > t)
        return check_query

    def scan_file_extension(self, filename):
        """ Checks for valid file extension

        Keyword arguments:
        filename -- fullpath to a file to check
        """
        check_query = (path.splitext(filename)[1] in
                       pyvert.CONFIG.VALID_FILE_EXTENSIONS)
        return check_query

    def scan_output_directory(self, filename):
        """ Checks if directory is within our output directory

        Keyword arguments:
        filename -- fullpath to a file to check
        """
        check_query = (pyvert.CONFIG.OUTPUT_DIRECTORY not in filename)
        return check_query

    def scan_size(self, filename, minimum=1048576):
        """ Checks if file is big enough

        Keyword arguments:
        filename -- fullpath to a file to check
        minimum -- minimum filesize to compare with
        """
        check_query = (stat(filename).st_size > minimum)
        return check_query

    def clean_ignore_list(self):
        """ Remove invalid entries from ignore list
        """
        #logger.debug('Starting cleaning of ignore list')
        with queue_lock:
            old_len = len(self.ignore)
            for i in self.ignore:
                if not path.exists(i):
                    self.ignore.remove(i)
            new_len = len(self.ignore)

            if new_len < old_len:
                logger.debug('Removed {} items from ignore list.'.format(
                             abs(old_len - new_len)))
        #logger.debug('Finished cleaning of ignore list')

    def worker(self):
        """ lets work on queue
        """
        if self.active < pyvert.CONFIG.CONCURRENT_JOBS:
            idx = self.get_next_to_work()
            if idx >= 0:
                with queue_lock:
                    logger.debug('Setting ID #{} to active'.format(idx))
                    self.active += 1
                    self.modify(idx, 'STATUS', 2)
                element = self.get(idx)
                try:
                    element.convert(pyvert.CONFIG.OUTPUT_DIRECTORY)
                except Exception as e:
                    element.STATUS = 6
                    logger.debug('Conversion failed with {}'.format(e))
                    return
                with queue_lock:
                    logger.debug('Setting ID #{} to finished'.format(idx))
                    self.active -= 1
                    self.modify(idx, 'STATUS', 5)
        
        for i in self.get_active_idx():
            p = self.get(i)
            if p.STATUS == 2:
                cutted_percent = "{0:.2f}".format(p.PERCENT)
                logger.debug('[{}] Progress: {}%'.format(i, cutted_percent))
            elif p.STATUS == 3:
                logger.debug('[{}] HDR Progress: {}%'.format(i, p.HPERCENT))
            elif p.STATUS == 4:
                logger.debug('[{}] Remux Progress: {}%'.format(i, p.MPERCENT))
