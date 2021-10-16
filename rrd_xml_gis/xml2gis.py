# coding: utf-8
"""Модуль реализующий функцию преобразования xml-документа в какой-либо формат для ГИС"""
import glob
import logging
import os
try:
    import ogr
    import osr
except ImportError:
    from osgeo import ogr
    from osgeo import osr
from pyproj import __version__ as proj_version
from rrd_xml_parser.parser import ParserXML
from rrd_xml_parser.parsers.names import ATTRIBUTES
from rrd_xml_parser.parsers.exceptions import NotImplementedTypeError, NotImplementedValueError
from rrd_xml_gis import exceptions
from rrd_xml_gis.consts import DATASOURCE_FORMATS


logger = logging.getLogger(__name__)


def get_feature_srs(feature):
    """
    Получение системы координат для одного объекта

    :param Feature feature: экземпляр модели распарсенного объекта
    :return: система координат
    :rtype: osr.SpatialReference
    """
    if feature.srid:  # type: Feature
        try:
            head, tail = feature.srid[:5], str(abs(int(feature.srid[5:])))[:1]  # 1, 2, 11, 21, -1
            code = head + tail
        except Exception as e:
            # logger.exception(e)
            logger.debug('Ошибка формирования кода системы координат из {}'.format(feature.srid))
            return

        try:
            if int(proj_version.split('.')[0]) == 1:
                from pyproj import Proj
                prop_srs = Proj(init="rrdoc:{}".format(code)).definition_string()
            elif int(proj_version.split('.')[0]) == 2:
                from pyproj import CRS
                prop_srs = CRS("rrdoc:{}".format(code)).to_proj4()
        except Exception as e:
            logger.error("Ошибка инициализации системы координат по коду {}".format(code))
            return
        else:
            ogr_srs = osr.SpatialReference()
            ogr_srs.ImportFromProj4(prop_srs)
            ogr_srs.SetWellKnownGeogCS(osr.SRS_DN_WGS84)
            return ogr_srs


def get_srs(path):
    """
    Получение системы координат

    :param str path: путь до xml-документа
    :return: объект системы координат
    :rtype: osr.SpatialReference
    """
    parser = ParserXML()
    for feature in parser.parse(path):
        ogr_srs = get_feature_srs(feature)
        return ogr_srs


def python_to_org(layer_defn, feature, feature_real_fields):
    """
    Функция преобразования Feature полученной из парсера в Feature ogr

    :param org.FeatureDefn layer_defn: структура полей выходного файла
    :param feature: структура полученная из парсера
    :param dict[str] feature_real_fields: список имён атрибутов
    :return:
    """
    feature_new = ogr.Feature(layer_defn)  # type: ogr.Feature
    for f in feature_real_fields:
        try:
            if f == 'geometry':
                if not feature.geometry:
                    logger.debug('Пустая геометрия объекта. {}'.format(feature))
                    continue
                geometry = ogr.CreateGeometryFromWkt(feature.geometry)
                feature_new.SetGeometry(geometry)
            else:
                value = getattr(feature, f, None)
                if not value:
                    continue
                feature_new[feature_real_fields[f]] = str(value)
        except Exception as e:
            logger.error('Ошибка записи атрибута {} со значением {}'.format(f, getattr(feature, f, None)))
            logger.exception(e)
    return feature_new


def write_feature(layer, feature, empty):
    """
    Запись ogr Feature в ogr Layer

    :param ogr.Layer layer: OGR Layer
    :param ogr.Feature feature: ORG Feature
    :param bool empty: флаг указывающий выгружать ли объекты с пустой геометрией
    :return:
    """
    try:
        if empty or bool(feature.geometry()):
            layer.CreateFeature(feature)
    except ValueError as e:
        logger.error('Парсинге получен объект без геометрии. {}'.format(str(feature)))
    except Exception as e:
        logger.exception(e)


def xml2gis(path, filename_out, gis, object_type=None, empty=False, **kwargs):
    """
    Функция преобразования xml-документа в документ пригодный для открытия в ГИС

    :param str path: полный путь к xml-документу
    :param str filename_out: имя нового формируемого файла
    :param str gis: имя создаваемого драйвера OGR
    :param str object_type: тип выбираемого объекта из xml-документа
    :param bool empty: выгружать объекты с пустой геометрией
    :param dict[str] kwargs: дополнительные именованные аргументы
    :key str type_xml: тип xml-документа
    :key str version_xml: версия xml-документа
    :key str transform_to: СК для выходного файла
    :return: список путей до преобразованных документов
    :rtype: list[str]
    :raise DriverException: ошибка создания драйвера OGR

    """
    OGR_ENABLE_PARTIAL_REPROJECTION = os.environ.get('OGR_ENABLE_PARTIAL_REPROJECTION', None)
    os.environ['OGR_ENABLE_PARTIAL_REPROJECTION'] = 'True'

    result = []
    parse = ParserXML()
    try:
        feature_iterator = parse.parse(path,
                                       type_xml=kwargs.get('type_xml', None),
                                       version_xml=kwargs.get('version_xml', None))
    except NotImplementedTypeError as e:
        logger.error(str(e))
        return
    except NotImplementedValueError as e:
        logger.error(str(e))
        return
    except Exception as e:
        logger.error(str(e))
        return

    # Инициализация требуемого драйвера для сохранения данных
    driver = ogr.GetDriverByName(gis)  # type: ogr.Driver
    if driver is None:
        raise exceptions.DriverException('Неподдерживаемый драйвер. {}'.format(gis))

    datasource_format = DATASOURCE_FORMATS.get(gis, dict())
    output_filename = os.path.extsep.join(
        [filename_out, datasource_format.get('extension', driver.GetMetadata().get('DMD_EXTENSIONS', 'mif'))]
    )
    path_out = os.path.join(os.path.dirname(path), output_filename)

    # Создание источника данных (файла)
    datasource = driver.CreateDataSource(path_out)  # type: ogr.DataSource
    if datasource is None:
        raise exceptions.DatasourceException('Не удалось создать источник для записи.')

    # Получение СК для слоя из первого объекта
    layer_srs = get_srs(path)
    # Если задано перепроецирование в другую СК, то создаём новую СК для слоя
    transform_to = kwargs.get('transform_to', None)
    if transform_to:
        layer_srs = osr.SpatialReference()
        layer_srs.ImportFromEPSG(transform_to)

    layer = datasource.CreateLayer(os.path.splitext(os.path.basename(path))[0], srs=layer_srs, options=datasource_format.get('options', []))  # type: ogr.Layer
    real_fields = dict()  # type: dict
    for f in ATTRIBUTES:
        feature_type = ogr.wkbUnknown if f == 'geometry' else ogr.OFTString
        field = ogr.FieldDefn(f, feature_type)
        layer.CreateField(field)
        real_fields[f] = layer.schema[-1].name

    transformations = dict()  # type dict[int]
    layer_defn = layer.GetLayerDefn()  # type: ogr.FeatureDefn
    layer.StartTransaction()
    try:
        for feature in feature_iterator:
            if object_type and feature.type != object_type:
                continue
            ogr_feature = python_to_org(
                layer_defn=layer_defn,
                feature=feature,
                feature_real_fields=real_fields
            )
            if transform_to:
                feature_srs = get_feature_srs(feature)
                if feature_srs:
                    transformations[feature.srid] = osr.CoordinateTransformation(feature_srs, layer_srs)
                    ogr_feature.geometry().Transform(transformations[feature.srid])
            write_feature(layer=layer, feature=ogr_feature, empty=empty)
    finally:
        layer.CommitTransaction()
        layer.SyncToDisk()
        del layer
    datasource.SyncToDisk()
    datasource.Destroy()

    if OGR_ENABLE_PARTIAL_REPROJECTION is not None:
        os.environ['OGR_ENABLE_PARTIAL_REPROJECTION'] = OGR_ENABLE_PARTIAL_REPROJECTION

    for filename in glob.glob(os.path.splitext(path_out)[0] + '.*'):
        if os.path.splitext(filename)[1] == '.xml' or os.path.splitext(filename)[1] == '.zip':
            continue
        result.append(filename)
    return result
