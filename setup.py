import io
from setuptools import setup, find_packages

with io.open('VERSION', 'r') as fd:
    VERSION = fd.read().rstrip()

requires = (
    'nextgisweb>=4.0.0.dev5',
    'rrd-xml-parser>=1.0.0'
)

entry_points = {
    'nextgisweb.packages': [
        'nextgisweb_rosreestr = nextgisweb_rosreestr:pkginfo',
    ],
    'nextgisweb.amd_packages': [
        'nextgisweb_rosreestr = nextgisweb_rosreestr:amd_packages',
    ],
}


setup(
    name='nextgisweb_rosreestr',
    version=VERSION,
    description="",
    long_description="",
    classifiers=[],
    keywords='',
    author='',
    author_email='',
    url='',
    license='',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    python_requires=">2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, <4",
    install_requires=requires,
    entry_points=entry_points,
)
