# These will be removed in APScheduler 4.0.
release = '3.3.1'
version_info = tuple(int(x) if x.isdigit() else x for x in release.split('.'))
version = __version__ = '.'.join(str(x) for x in version_info[:3])
