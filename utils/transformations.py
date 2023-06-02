# Dependências
from numpy import array, float32, dot, cos, sin
from collections.abc import Sequence

def translate(tx:float, ty:float, tz:float = 1.0, origin:Sequence = None):
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
    origin: Sequence, default = None
        Matriz ao qual multiplicar a transformação.
    '''
    matrix = array([
        [1.0, 0.0, 0.0,  tx], 
        [0.0, 1.0, 0.0,  ty], 
        [0.0, 0.0, 1.0,  tz],
        [0.0, 0.0, 0.0, 1.0],
    ], dtype=float32)
    if origin is None:
        return matrix
    return dot(origin, matrix)


def scale(sx:float, sy:float, sz:float = 1.0, origin:Sequence = None):
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
    origin: Sequence, default = None
        Matriz ao qual multiplicar a transformação.
    '''
    matrix = array([
        [ sx, 0.0, 0.0, 0.0], 
        [0.0,  sy, 0.0, 0.0], 
        [0.0, 0.0,  sz, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ], dtype=float32)
    if origin is None:
        return matrix
    return dot(origin, matrix)


def xrotate(t:float, origin:Sequence = None):
    '''
    Retorna uma matriz de rotação tridimensional 
    no eixo das abscissas considerando coordenadas 
    homogêneas.

    Parâmetros:
    ----------
    t: float
        Ângulo de rotação em radianos.
    origin: Sequence, default = None
        Matriz ao qual multiplicar a transformação.
    '''
    c = cos(t)
    s = sin(t)
    matrix = array([
        [1.0, 0.0, 0.0, 0.0], 
        [0.0,  +c,  -s, 0.0], 
        [0.0,  +s,  +c, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ], dtype=float32)
    if origin is None:
        return matrix
    return dot(origin, matrix)


def yrotate(t:float, origin:Sequence = None):
    '''
    Retorna uma matriz de rotação tridimensional 
    no eixo das ordenadas considerando coordenadas 
    homogêneas.

    Parâmetros:
    ----------
    t: float
        Ângulo de rotação em radianos.
    origin: Sequence, default = None
        Matriz ao qual multiplicar a transformação.
    '''
    c = cos(t)
    s = sin(t)
    matrix = array([
        [ +c, 0.0,  +s, 0.0], 
        [0.0, 1.0, 0.0, 0.0], 
        [ -s, 0.0,  +c, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ], dtype=float32)
    if origin is None:
        return matrix
    return dot(origin, matrix)


def zrotate(t:float, origin:Sequence = None):
    '''
    Retorna uma matriz de rotação tridimensional 
    no eixo das cotas considerando coordenadas 
    homogêneas.

    Parâmetros:
    ----------
    t: float
        Ângulo de rotação em radianos.
    origin: Sequence, default = None
        Matriz ao qual multiplicar a transformação.
    '''
    c = cos(t)
    s = sin(t)
    matrix = array([
        [ +c,  -s, 0.0, 0.0], 
        [ +s,  +c, 0.0, 0.0], 
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ], dtype=float32)
    if origin is None:
        return matrix
    return dot(origin, matrix)


def relative_zrotate(t:float, x0:float=0.0, y0:float=0.0, z0:float=0.0, origin:Sequence = None):
    '''
    Retorna uma matriz de rotação tridimensional, 
    relativa a um ponto de referência, no eixo das 
    cotas considerando coordenadas homogêneas.

    Parâmetros:
    ----------
    t: float
        Ângulo de rotação em radianos.
    origin: Sequence, default = None
        Matriz ao qual multiplicar a transformação.
    '''
    matrix = dot(
        translate(x0, y0, z0), 
        dot(
            zrotate(t),
            translate(-x0, -y0, -z0)
        )
    )
    if origin is None:
        return matrix
    return dot(origin, matrix)