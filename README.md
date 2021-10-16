# rrd-xml-gis

## Описание
Утилита предназанчена для конвертации xml-документов в различные ГИС-форматы

## Использование
Утилита rrd-xml-gis содержит модуль `xml2gis` реализующий функцию `xml2gis` которая принимает путь к xml-документу,
ORG CODE формата преобразования и дополнительные необязательные ключевые аргументы.

```python
from rrd_utils.utils import rrd_file_iterator
from rrd_xml_gis.xml2gis import xml2gis

for file_ in rrd_file_iterator('<шаблон для поиска файлов>'):
    print(xml2gis(file_, ogr_code='MapInfo File'))
```

### Поддерживаемые типы и версии документов
* Кадастровая выписка о земельном участке:
    * **KVZU**: urn://x-artefacts-rosreestr-ru/outgoing/kvzu/7.0.1

* Кадастровый паспорт на земельный участок:
    * **KPZU**: urn://x-artefacts-rosreestr-ru/outgoing/kvzu/6.0.1

* Кадастровый план территории: 
    * **KPT**: urn://x-artefacts-rosreestr-ru/outgoing/kpt/10.0.1
    * **extract_cadastral_plan_territory**: extract_cadastral_plan_territory 

* Выписка из ЕГРН об объекте недвижимости:
    * **extract_about_property_land**: extract_about_property_land

* Выписка из ЕГРН об основных характеристиках и зарегистрированных правах на объект недвижимости:
    * **extract_base_params_land**: extract_base_params_land
