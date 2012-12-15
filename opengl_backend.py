from functools import partial
from contextlib import contextmanager

from matplotlib.backend_bases import (RendererBase, FigureCanvasBase,
                                      GraphicsContextBase, Event, ShowBase)

from matplotlib.backends.backend_qt4 import (TimerQT, Show, FigureCanvasQT,
                                     FigureManagerQT)

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from OpenGL import GL, GLU, GLUT
import numpy as np
import sys

from fps import fps

def _apply_transform(transform):
    v = transform.to_values()
    GL.glMultMatrixf([v[0], v[1], 0., 0.,
                      v[2], v[3], 0., 0.,
                      0., 0., 1., 0.,
                      v[4], v[5], 0., 1.])

#def new_figure_manager(num, *args, **kwargs):
#    FigureClass = kwargs.pop('FigureClass', Figure)
#    fig = FigureClass(*args, **kwargs)
#    return new_figure_manager_given_figure(num, fig)

#def new_figure_manager_given_figure(num, figure):
#    canvas = FigureCanvasQtOpenGL(figure)
#    return FigureManagerQT(canvas, num)

GLUT.glutInit([''])
GLUT.glutInitDisplayMode(GLUT.GLUT_RGB | GLUT.GLUT_DOUBLE)
GLUT.glutInitWindowSize(640, 480)
GLUT.glutCreateWindow("MPL Test")
GLUT.glutDisplayFunc(lambda: None)
GLUT.glutReshapeFunc(lambda w,h: None)

def check_gl_errors(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        assert GL.glGetError() == GL.GL_NO_ERROR
        return result
    return wrapper


def render_path(gc, path, transform, rgbFace):
        GL.glLoadIdentity()
        _apply_transform(transform)
        GL.glVertexPointerf(path.vertices)

        ###update transform
        #GL.glVertexPointerf(path.vertices)
        npt = path.vertices.shape[0]

        #render the face
        if rgbFace is not None:
            GL.glColor3f(*rgbFace[0:3])
            GL.glDrawArrays(GL.GL_POLYGON, 0, npt)

        #render the path
        if gc.get_linewidth() != 0.0:
            GL.glLineWidth(gc.get_linewidth())
            GL.glColor3f(*gc.get_rgb()[0:3])
            GL.glDrawArrays(GL.GL_LINE_LOOP, 0, npt)

        #render the hatch
        hatch = gc.get_hatch_path()
        if hatch is not None:
            print 'render hatch'

def render_marker(gc, marker_path, marker_trans, path,
                  transform, rgbFace):

    GL.glLoadIdentity()
    _apply_transform(transform)

    npt = path.vertices.shape[0]

    GL.glVertexPointerf(path.vertices)
    GL.glPointSize(3)

    if rgbFace is not None:
        GL.glColor3f(*rgbFace[0:3])
        GL.glDrawArrays(GL.GL_POINTS, 0, npt)


class OpenGLRenderer(RendererBase):

    def __init__(self, w, h, dpi):
        RendererBase.__init__(self)
        self.width = w
        self.height = h
        self.dpi = dpi
        self._opengl_init()
        self._draw_stack = []

    def _opengl_init(self):
        GL.glEnable(GL.GL_VERTEX_PROGRAM_POINT_SIZE)
        GL.glDisable(GL.GL_DITHER)
        GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
        GLUT.glutDisplayFunc(self.display)
        GLUT.glutReshapeFunc(self.reshape)
        GLUT.glutIdleFunc(self.display)


    @check_gl_errors
    @fps
    def display(self):

        for render_call in self._draw_stack:
            render_call()

        GLUT.glutSwapBuffers()


    @check_gl_errors
    def _set_projections(self):
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, self.width, 0, self.height, -10, 10)

        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GLU.gluLookAt(0, 0, 4, 0, 0, 0, 0, 1, 0)


    @check_gl_errors
    def reshape(self, w, h):
        GL.glViewport(0, 0, w, h)
        self._set_projections()

    #required
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
    #ax.axis('off')
    sz = 10**6
    x = np.random.normal(0, 1, sz)
    y = np.random.normal(0, 1, sz)
    lines, = ax.plot(x, y, 'o')
    fc.draw()
    GLUT.glutMainLoop()
