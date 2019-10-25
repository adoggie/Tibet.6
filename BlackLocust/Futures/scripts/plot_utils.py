#conding:utf-8

#---- matplotlib initializing ----
import matplotlib as mpl
from matplotlib.font_manager import FontProperties
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.dates import DateFormatter
plt.switch_backend('agg')
title_font = FontProperties(family='YouYuan', size=18)
mpl.rcParams['axes.unicode_minus'] = False


def export_png_base64(fig):
    import StringIO
    import base64
    s = StringIO.StringIO()
    canvas=FigureCanvasAgg(fig)
    canvas.print_png(s)
    s.seek(0)
    data = "data:image/png;base64,"
    data += base64.encodestring(s.getvalue())
    s.close()
    return data