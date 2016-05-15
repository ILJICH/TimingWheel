from distutils.core import setup

from timingwheel import version

setup(
    name='timingwheel',
    packages=['timingwheel'],
    version=version,
    description='Timing Wheel algorithm implementation',
    author='Valentin Lupachev',
    author_email='iljich@iljich.name',
    url='https://github.com/ILJICH/TimingWheel/tarball/' + version,
)
