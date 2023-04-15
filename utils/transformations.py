# Dependências
from numpy import array, float32, cos, sin

def translate2D(tx:float, ty:float):
    '''
    Retorna uma matriz de translação bidimensional 
    considerando coordenadas homogêneas.

    Parâmetros:
    ----------
    tx: float
        Translação da abscissa.
    ty: float
        Translação da ordenada.
    '''
    return array([
        [1.0, 0.0,  tx], 
        [0.0, 1.0,  ty], 
        [0.0, 0.0, 1.0],
    ], dtype=float32)


def scale2D(sx:float, sy:float):
    '''
    Retorna uma matriz de escala bidimensional 
    considerando coordenadas homogêneas.

    Parâmetros:
    ----------
    sx: float
        Escala da abscissa.
    sy: float
        Escala da ordenada.
    '''
    return array([
        [ sx, 0.0, 0.0], 
        [0.0,  sy, 0.0], 
        [0.0, 0.0, 1.0],
    ], dtype=float32)


def relative_scale2D(sx:float, sy:float, x0:float = 0.0, y0:float = 0.0):
    '''
    Retorna uma matriz de escala bidimensional 
    com ponto de referência considerando 
    coordenadas homogêneas.

    Parâmetros:
    ----------
    sx: float
        Escala da abscissa.
    sy: float
        Escala da ordenada.
    x0: float, default = 0.0
        Abscissa do ponto de referência.
    y0: float, default = 0.0
        Ordenada do ponto de referência.
    '''
    return array([
        [ sx, 0.0, x0*(1.0-sx)], 
        [0.0,  sy, y0*(1.0-sy)], 
        [0.0, 0.0,         1.0],
    ], dtype=float32)


def rotate2D(t:float):
    '''
    Retorna uma matriz de rotação bidimensional 
    considerando coordenadas homogêneas.

    Parâmetros:
    ----------
    t: float
        Ângulo de rotação em radianos.
    '''
    c = cos(t)
    s = sin(t)
    return array([
        [ +c,  -s, 0.0], 
        [ +s,  +c, 0.0], 
        [0.0, 0.0, 1.0],
    ], dtype=float32)


def relative_rotate2D(t:float, x0:float = 0.0, y0:float = 0.0):
    '''
    Retorna uma matriz de rotação bidimensional 
    com ponto de referência considerando 
    coordenadas homogêneas.

    Parâmetros:
    ----------
    t: float
        Ângulo de rotação em radianos.
    x0: float, default = 0.0
        Abscissa do ponto de referência.
    y0: float, default = 0.0
        Ordenada do ponto de referência.
    '''
    c = cos(t)
    s = sin(t)
    return array([
        [ +c,  -s, x0 - x0*c + y0*s], 
        [ +s,  +c, y0 - y0*c - x0*s], 
        [0.0, 0.0,              1.0],
    ], dtype=float32)


def translate3D(tx:float, ty:float, tz:float = 1.0):
    '''
    Retorna uma matriz de translação tridimensional 
    considerando coordenadas homogêneas.

    Parâmetros:
    ----------
    tx: float
        Translação da abscissa.
    ty: float
        Translação da ordenada.
    tz: float, default = 1.0
        Translação da cota.
    '''
    return array([
        [1.0, 0.0, 0.0,  tx], 
        [0.0, 1.0, 0.0,  ty], 
        [0.0, 0.0, 1.0,  tz],
        [0.0, 0.0, 0.0, 1.0],
    ], dtype=float32)


def scale3D(sx:float, sy:float, sz:float = 1.0):
    '''
    Retorna uma matriz de escala tridimensional 
    considerando coordenadas homogêneas.

    Parâmetros:
    ----------
    sx: float
        Escala da abscissa.
    sy: float
        Escala da ordenada.
    sz: float, default = 1.0
        Escala da cota.
    '''
    return array([
        [ sx, 0.0, 0.0, 0.0], 
        [0.0,  sy, 0.0, 0.0], 
        [0.0, 0.0,  sz, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ], dtype=float32)


def xrotate3D(t:float):
    '''
    Retorna uma matriz de rotação tridimensional 
    no eixo das abscissas considerando coordenadas 
    homogêneas.

    Parâmetros:
    ----------
    t: float
        Ângulo de rotação em radianos.
    '''
    c = cos(t)
    s = sin(t)
    return array([
        [1.0, 0.0, 0.0, 0.0], 
        [0.0,  +c,  -s, 0.0], 
        [0.0,  +s,  +c, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ], dtype=float32)


def yrotate3D(t:float):
    '''
    Retorna uma matriz de rotação tridimensional 
    no eixo das ordenadas considerando coordenadas 
    homogêneas.

    Parâmetros:
    ----------
    t: float
        Ângulo de rotação em radianos.
    '''
    c = cos(t)
    s = sin(t)
    return array([
        [ +c, 0.0,  +s, 0.0], 
        [0.0, 1.0, 0.0, 0.0], 
        [ -s, 0.0,  +c, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ], dtype=float32)


def zrotate3D(t:float):
    '''
    Retorna uma matriz de rotação tridimensional 
    no eixo das cotas considerando coordenadas 
    homogêneas.

    Parâmetros:
    ----------
    t: float
        Ângulo de rotação em radianos.
    '''
    c = cos(t)
    s = sin(t)
    return array([
        [ +c,  -s, 0.0, 0.0], 
        [ +s,  +c, 0.0, 0.0], 
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ], dtype=float32)