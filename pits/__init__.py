################################################################################
# pits --- Point In Time Storage
################################################################################
import re, gzip, builtins
import datetime as dt
from pathlib import Path
from contextlib import contextmanager


def goto(spec=None):
    return PointInTimeFile(spec)


@contextmanager
def open(spec, *args, **kw):
    pit = PointInTimeFile()
    with pit.open(spec, *args, **kw) as f:
        try:
            yield f
        finally:
            return


class PointInTimeFile:
    def __init__(self, pit_spec=None):
        self.pit = self.parse_time_point(pit_spec)
        self.filename = None


    def is_gzipped(self):
        if not self.filename:
            return False
        with builtins.open(self.filename, 'rb') as f:
            return f.read(2) == b'\x1f\x8b'


    @staticmethod
    def parse_time_point(spec):
        if spec is None:
            return dt.datetime.now()
        if not isinstance(spec, str):
            raise TypeError('spec should be string')
        s = re.sub(r'[^0-9]', '', spec)
        if len(s) < 8:
            raise ValueError('invalid spec {spec}')
        year = int(s[:4])
        mon = int(s[4:6])
        day = int(s[6:8])
        
        if len(s) >= 10:
            hh = len(s) >= 10 and int(s[ 8:10]) or 0
            mm = len(s) >= 12 and int(s[10:12]) or 0
            ss = len(s) >= 14 and int(s[12:14]) or 0
        else:
            hh, mm, ss = (23, 59, 59)
        return dt.datetime(year, mon, day, hh, mm, ss)


    @property
    def format(self):
        return '%Y.%m.%d-%H:%M:%S'


    @contextmanager
    def open(self, spec, *args, **kw):
        path = Path(spec).expanduser()
        kwargs = {key: val for key, val in kw.items() if key != 'gzip'}
        mode = args and args[0] or kw.get('mode', '')

        # writing
        if 'w' in mode:
            if path.is_file():
                raise RuntimeError(f'{path} should be a directory')
            path.mkdir(parents=True, exist_ok=True)
            self.filename = path / self.pit.strftime(self.format)
            fopen = kw.get('gzip', False) and gzip.open or builtins.open
            with fopen(self.filename, *args, **kwargs) as f:
                try:
                    yield f
                finally:
                    pass
            return

        # reading
        if not path.exists():
            raise FileNotFoundError(f'{path} not found')
        if not path.resolve().is_dir():
            raise RuntimeError(f'{path} is not a directory')
        # sort file names from latest to earliest
        for f in sorted(path.iterdir(), reverse=True):
            try:
                if self.pit >= dt.datetime.strptime(f.name, self.format):
                    self.filename = f
                    break
            except:
                continue
        if not self.filename:
            raise RuntimeError(f'No PIT file found for {self.pit} under {path}')
        fopen = gzip.open if self.is_gzipped() else builtins.open
        with fopen(self.filename, *args, **kwargs) as f:
            try:
                yield f
            finally:
                pass


### pits/__init__.py ends here
