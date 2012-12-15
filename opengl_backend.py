from functools import partial
from contextlib import contextmanager
from time import time

from matplotlib.backend_bases import (RendererBase, FigureCanvasBase,
                                      GraphicsContextBase, Event, ShowBase)

from matplotlib.backends.backend_qt4 import (TimerQT, Show, FigureCanvasQT,
                                     FigureManagerQT, show,
                                     NavigationToolbar2QT)

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from OpenGL import GL, GLU
from PyQt4.QtOpenGL import QGLWidget
from PyQt4.QtGui import QApplication, QMainWindow
from PyQt4 import QtCore

import numpy as np
import sys
from fps import fps

from glutil import (_apply_transform, check_gl_errors,
                    render_path, render_marker)


class OpenGLRenderer(RendererBase):

    def __init__(self, w, h, dpi):
        RendererBase.__init__(self)
        self.width = w
        self.height = h
        self.dpi = dpi
        self._draw_stack = []

    def clear(self):
        self._draw_stack = []

    @check_gl_errors
    @fps
    def display(self):
        print "draw stack size: %i" % len(self._draw_stack)
        for render_call in self._draw_stack:
            render_call()

    def draw_path(self, gc, path, transform, rgbFace=None):
        self._draw_stack.append(partial(render_path,
                                        gc, path, transform, rgbFace))

    #def draw_image(self, gc, x, y, im):
        #print 'an image'
        #pass

    #def draw_text(self, gc, x, y, s, prop, angle, ismath=False, mtext=None):
    #    print 'text', s

    #def get_text_width_height_descent(self, s, prop, ismath):
    #    pass

    #recommended
    def draw_markers(self, gc, marker_path, marker_trans, path,
                     trans, rgbFace=None):
        self._draw_stack.append(partial(render_marker, gc, marker_path,
                                        marker_trans, path,
                                        trans, rgbFace))

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


class FigureCanvasQTOpenGL(QGLWidget, FigureCanvasQT):

    def draw(self):
        renderer = self.get_renderer()
        self.figure.draw(self.renderer)
        self.update()

    def get_renderer(self):
        l, b, w, h = self.figure.bbox.bounds
        key = w, h, self.figure.dpi
        try: self._lastKey, self.renderer
        except AttributeError: need_new_renderer = True
        else: need_new_renderer = (self._lastKey != key)

        if need_new_renderer:
            self.renderer = OpenGLRenderer(w, h, self.figure.dpi)
            self._lastKey = key
        self.renderer.clear()
        return self.renderer

    def initializeGL(self):
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glDisable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_VERTEX_PROGRAM_POINT_SIZE)
        GL.glDisable(GL.GL_DITHER)
        GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
        GL.glClearColor(0, 0, 0, 0)

    def drawRectangle(self, rect):
        pass

    def paintGL(self):
        t0 = time()
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        self.renderer.display()
        print 'render time: %ims' % ((time() - t0) * 1000)
        print 'paintEnd'

    def resizeGL(self, w, h):
        print w, h
        self.width = int(w)
        self.height = int(h)
        GL.glViewport(0, 0, w, h)
        self._set_projections()

    def _set_projections(self):
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, self.width, 0, self.height, -10, 10)

        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GLU.gluLookAt(0, 0, 4, 0, 0, 0, 0, 1, 0)

    def __init__(self, figure):
        FigureCanvasQT.__init__(self, figure)
        QGLWidget.__init__(self)
        self.drawRect = False
        self.rect = []
        self.blitbox = None
        self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)

    def drawRectangle(self, rect):
        pass

    def paintEvent(self, e):
        """
        Copy the image from the Agg canvas to the qt.drawable.
        In Qt, all drawing should be done inside of here when a widget is
        shown onscreen.
        """
        QGLWidget.paintEvent(self, e)


if __name__ == "__main__":
    import sys

    app = QApplication([''])
    mw = QMainWindow()


    f = Figure()

    if '--old' not in sys.argv:
        fc = FigureCanvasQTOpenGL(f)
    else:
        fc = FigureCanvasQTAgg(f)

    ax = f.add_subplot(111)

    sz = 10**6
    x = np.random.normal(0, 1, sz)
    y = np.random.normal(0, 1, sz)
    lines, = ax.plot(x, y, 'o', alpha=.1)
    lines2, = ax.plot(x, np.sin(x), 'ro', alpha = .2)

    tb = NavigationToolbar2QT(fc, None)

    mw.setCentralWidget(fc)
    mw.addToolBar(tb)

    mw.show()
    show.mainloop()
