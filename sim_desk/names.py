# encoding: UTF-8
from utils import  logger
try:
    from objectmaphelper import *

    greenHouse_Application_QQuickWindowQmlImpl = {"title": "GreenHouse Application", "type": "QQuickWindowQmlImpl", "unnamed": 1, "visible": True}
    greenHouse_Application_root_Item = {"container": greenHouse_Application_QQuickWindowQmlImpl, "id": "root", "type": "Item", "unnamed": 1, "visible": True}

except Exception as err:
    logger.warn("names import error, %s" % err)