# Dependências
from numpy import hstack
from numpy.random import normal

def rgb_random_color(opacity=1.0):
    ''' Gera uma cor RGB aleatória com opacidade opcional '''
    return hstack([normal(0.0, 1.0, size=3), (opacity)])


def rgb_black_color(opacity=1.0):
    ''' Retorna uma tupla RGB, com opacidade, para a coloração preta '''
    return (0.0, 0.0, 0.0, opacity)


def rgb_white_color(opacity=1.0):
    ''' Retorna uma tupla RGB, com opacidade, para a coloração branca '''
    return (1.0, 1.0, 1.0, opacity)