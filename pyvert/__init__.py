import os
import threading
import datetime
from pyvert import logger, versioncheck, queue
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

SYS_ENCODING = None
QUIET = None
VERBOSE = None
CONFIG_DIR = None
DATA_DIR = None
FULL_PATH = None
PROG_DIR = None
LOG_DIR = None
CONFIG = None
COMMITS_BEHIND = 0
CURRENT_VERSION = None
CURRENT_VERSION = None
LATEST_VERSION = None
SIGNAL = None
SCHED = BackgroundScheduler()
SCHED_LOCK = threading.Lock()
QUEUE = queue.Queue()


def initialize_scheduler():
    with SCHED_LOCK:
        # check if scheduler should be started
        start_jobs = not len(SCHED.get_jobs())

        schedule_job(versioncheck.get_remote_version, 'Check GitHub' +
                     ' for updates', hours=1, minutes=9, seconds=0)

        schedule_job(QUEUE.scan, 'Scan files', hours=0, minutes=1,
                     seconds=0, args=[CONFIG.SCAN_DIRECTORY])

        # schedule_job(QUEUE.worker, 'Process files', hours=0, minutes=0,
        #             seconds=30)

        schedule_job(QUEUE.clean_ignore_list, 'Clean ignore list.',
                     hours=0, minutes=0, seconds=20)

        # start scheduler
        if start_jobs and len(SCHED.get_jobs()):
            try:
                SCHED.start()
            except Exception as e:
                logger.error(e)


def schedule_job(function, name, hours=0, minutes=0, seconds=0, args=None):
    """
    """
    job = SCHED.get_job(name)
    if job:
        if hours == 0 and minutes == 0 and seconds == 0:
            SCHED.remove_job(name)
            logger.info('Removed background task: {}'.format(
                        name))
        elif job.trigger.interval != datetime.timedelta(hours=hours,
                                                        minutes=minutes):
            SCHED.reschedule_job(name, trigger=IntervalTrigger(
                hours=hours, minutes=minutes, seconds=seconds), args=args)
            logger.info("Re-scheduled background task: %s", name)
    elif hours > 0 or minutes > 0 or seconds > 0:
        SCHED.add_job(function, id=name, trigger=IntervalTrigger(
            hours=hours, minutes=minutes, seconds=seconds), args=args)
        logger.info("Scheduled background task: %s", name)


def start():
    initialize_scheduler()


def sig_handler(signum=None, frame=None):
    if signum is not None:
        logger.info('Signal {} caught, saving and exiting...'.format(signum))
        shutdown()


def shutdown(restart=False, update=False):
    CONFIG.save_config_file(os.path.join(DATA_DIR, 'config.json'))

    if not restart and not update:
        logger.info('PyVert is shutting down...')

    if update:
        logger.info('PyVert is updating...')

    if restart:
        logger.info('PyVert is restarting...')

    os._exit(0)
