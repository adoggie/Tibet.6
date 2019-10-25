# coding: utf-8

from mantis.fundamental.nosql.mongo import Connection
from mantis.fanbei.smartvision import model
from mantis.fundamental.parser.yamlparser import YamlConfigParser
from mantis.fundamental.utils.timeutils import timestamp_current
from mantis.fundamental.utils.useful import object_assign

def get_database():
    db = Connection('smartvision').db
    return db

model.get_database = get_database

def init_database():
    data = YamlConfigParser('./init-data.yaml').props

    get_database().HomeGarden.remove()
    _ = model.HomeGarden.get_or_new()
    _.assign( data.get('garden'))
    _.save()

    get_database().Building.remove()
    for r in data.get('building_list'):
        _ = model.Building()
        _.assign(r)
        _.save()

    get_database().InnerBox.remove()
    for r in data.get('innerbox_list'):
        _ = model.InnerBox()
        _.assign(r)
        _.save()

    get_database().OuterBox.remove()
    for r in data.get('outerbox_list'):
        _ = model.OuterBox()
        _.assign(r)
        _.save()

    get_database().PropertyCallApp.remove()
    for r in data.get('propcallapp_list'):
        _ = model.PropertyCallApp()
        _.assign(r)
        _.save()

    get_database().SentryApp.remove()
    for r in data.get('sentryapp_list'):
        _ = model.SentryApp()
        _.assign(r)
        _.save()


init_database()


