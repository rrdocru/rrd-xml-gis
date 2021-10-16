# coding: utf-8
import logging
from rrd_xml_gis import consts
from rrd_xml_gis.xml2gis import xml2gis

logger = logging.getLogger(__name__)


def createParser():
    """
        Объявление параметров командной строки

    :return: объект с определенными параметрами
    :rtype: argparse.ArgumentParser
    """
    import argparse  # noqa
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--input',
                        help='Паттрен пути для поиска файлов',
                        type=str,
                        required=True
                        )
    parser.add_argument('-o', '--output',
                        help='Путь для сохранения файлов',
                        type=str)
    parser.add_argument('-f', '--formats',
                        help='Формат для преобразования исходных xml-документов',
                        type=str,
                        nargs='*',
                        default=['MapInfo File', ],
                        choices=consts.AVAILABLE_FORMATS
                        )
    parser.add_argument('-t', '--transform_to',
                        help='Система координат для результирующего файла',
                        type=int,
                        required=False,
                        )
    parser.add_argument('--includes',
                        help='Выгружаемые типы объектов',
                        type=str,
                        nargs='*',
                        default=['ALL', ],
                        choices=consts.AVAILABLE_OBJECT_TYPES
                        )
    parser.add_argument('-s', '--split',
                        help='Разделять файлы по типам объектов',
                        action='store_true')
    parser.add_argument('-e', '--empty',
                        help='Выгружать объекты с пустой геометрией',
                        action='store_true')
    return parser


def main():
    """Основная процедура для запуска"""
    import os  # noqa
    import shutil  # noqa
    from rrd_utils.utils import rrd_file_iterator_with_origin_name  # noqa

    def _save_result(results, name_to_save, path_to_save):
        os.makedirs(path_to_save, exist_ok=True)
        for result in results:
            file_to_save = os.path.join(path_to_save, name_to_save + os.path.splitext(result)[1])
            if os.path.exists(file_to_save) and result != file_to_save:
                os.remove(file_to_save)
            shutil.move(result, file_to_save)

    parser = createParser()
    args = parser.parse_args()
    logger.info('Старт обработки документов.')

    for xml, origin in rrd_file_iterator_with_origin_name(args.input):
        logger.info(origin)
        for format_gis in args.formats:
            logger.debug(format_gis)
            origin_name = os.path.splitext(os.path.split(origin)[1])[0]
            path_to_save = args.output or os.path.dirname(origin)
            filename_out = os.path.splitext(os.path.basename(origin_name))[0]
            if 'ALL' in args.includes:
                logger.debug('ALL')
                try:
                    result = xml2gis(path=xml, filename_out=filename_out, gis=format_gis, empty=args.empty, transform_to=args.transform_to)
                except Exception as e:
                    logger.exception(e)
                else:
                    _save_result(result, origin_name, path_to_save)
            else:
                for object_type in args.objects:
                    logger.debug(object_type)
                    try:
                        result = xml2gis(path=xml,
                                         filename_out=filename_out,
                                         gis=format_gis,
                                         object_type=object_type,
                                         empty=args.empty,
                                         transform_to=args.transform_to)
                    except Exception as e:
                        logger.exception(e)
                    else:
                        _save_result(result, origin_name, path_to_save)
    logger.info('Завершение обработки документов.')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
