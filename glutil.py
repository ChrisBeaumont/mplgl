from OpenGL import GL, GLU
import numpy as np

def _apply_transform(transform):
    v = transform.to_values()
    GL.glMultMatrixf([v[0], v[1], 0., 0.,
                      v[2], v[3], 0., 0.,
                      0., 0., 1., 0.,
                      v[4], v[5], 0., 1.])

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
        if len(rgbFace) == 4:
            r, g, b, a = rgbFace
        else:
            r, g, b = rgbFace
            a = gc.get_alpha()

        GL.glColor4f(r, g, b, a)
        GL.glDrawArrays(GL.GL_POLYGON, 0, npt)

        #render the path
    if gc.get_linewidth() != 0.0:
        GL.glLineWidth(gc.get_linewidth())
        GL.glColor4f(*gc.get_rgb())
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
        r, g, b = rgbFace
        a = gc.get_alpha()
        GL.glColor4f(r, g, b, a)
        GL.glDrawArrays(GL.GL_POINTS, 0, npt)
