# coding: utf-8
"""
Модуль для хранения предопределенных констант
"""
import os
try:
    import ogr
except ImportError:
    from osgeo import ogr

from pyproj import __version__ as proj_version

from rrd_xml_parser.parsers.names import NAMES

# Регистрация драйверов
ogr.RegisterAll()
ogr.UseExceptions()

# Регистрация дополнительной директории для файлов в проекциями
if int(proj_version.split('.')[0]) == 1:
    from pyproj import set_datapath, pyproj_datadir  # noqa
    set_datapath(os.path.join(os.path.dirname(__file__), 'data'))
elif int(proj_version.split('.')[0]) == 2:
    from pyproj.datadir import append_data_dir  # noqa
    append_data_dir(os.path.join(os.path.dirname(__file__), 'data'))

AVAILABLE_FORMATS = sorted([ogr.GetDriver(i).GetName() for i in range(ogr.GetDriverCount())])
"""Итератор доступных форматов для вывода"""

AVAILABLE_OBJECT_TYPES = sorted(['ALL', ] + list(set(NAMES.values())))
"""Итератор доступных типов объектов недвижимости"""

DATASOURCE_FORMATS = {
    'MapInfo File': dict(
        extension='mif',
        lang='en',
        replace=True,
        transform=False,
    ),
    'GeoJSON': dict(
        extension='geojson',
        lang='en',
        replace=False,
        transform=True,
        option=['ENCODING=UTF8', ]
    ),
    'ESRI Shapefile': dict(
        extension='shp',
        lang='en',
        replace=True,
        transform=False
    ),
    'KML': dict(
        extension='kml',
        lang='en',
        replace=True,
        transform=False
    ),
    'CSV': dict(
        extension='csv',
        lang='en',
        replace=False,
        transform=False
    )
}
