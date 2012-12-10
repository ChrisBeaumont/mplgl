from matplotlib.backend_bases import (RendererBase, FigureCanvasBase,
                                      GraphicsContextBase, Event, ShowBase)

from matplotlib.backends.backend_qt4 import (TimerQT, Show, FigureCanvasQT,
                                     FigureManagerQT)

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib.figure import Figure



def new_figure_manager(num, *args, **kwargs):
    FigureClass = kwargs.pop('FigureClass', Figure)
    fig = FigureClass(*args, **kwargs)
    return new_figure_manager_given_figure(num, fig)

def new_figure_manager_given_figure(num, figure):
    canvas = FigureCanvasQtOpenGL(figure)
    return FigureManagerQT(canvas, num)


class OpenGLRenderer(RendererBase):
    def __init__(self, w, h, dpi):
        RendererBase.__init__(self)
        self.width = w
        self.height = h
        self.dpi = dpi

    #required
    def draw_path(self, gc, path, transform, rgbFace=None):
        print 'rendering a path'

    def draw_image(self, gc, x, y, im):
        print 'an image'
        pass

    #def draw_text(self, gc, x, y, s, prop, angle, ismath=False, mtext=None):
    #    print 'text', s

    #def get_text_width_height_descent(self, s, prop, ismath):
    #    pass

    #recommended
    #def draw_markers(self, gc, marker_path, marker_trans, path,
    #                 trans, rgbFace=None):
    #    pass

    #def draw_path_collection(self, gc, master_transform, paths,
    #                         all_transforms, offsets, offsetTrans,
    #                         facecolors, edgecolors,
    #                         linewidths, linestyles, antialiaseds, urls,
    #                         offset_position):
    #   pass

    #def draw_quad_mesh(self, gc, master_transform, meshWidth,
    #                   meshHeight, coordinates, offsets, offsetTrans,
    #                   facecolors, antialiased, edgecolors):
    #    pass


class FigureCanvasOpenGL(FigureCanvasBase):
    def draw(self):
        renderer = self.get_renderer()
        self.figure.draw(self.renderer)

    def get_renderer(self):
        l, b, w, h = self.figure.bbox.bounds
        key = w, h, self.figure.dpi
        try: self._lastKey, self.renderer
        except AttributeError: need_new_renderer = True
        else: need_new_renderer = (self._lastKey != key)

        if need_new_renderer:
            self.renderer = OpenGLRenderer(w, h, self.figure.dpi)
            self._lastKey = key
        return self.renderer


if __name__ == "__main__":
    f = Figure()
    fc = FigureCanvasOpenGL(f)
    ax = f.add_subplot(111)
    lines, = ax.plot([1,2,3])
    ax.scatter([2,3,4], [3,4,5])
    im = ax.imshow([[1,2,3],[2,3,4],[3,4,5]])
    fc.draw()
