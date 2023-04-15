# Dependências
from collections.abc import Sequence
import numpy as np
from utils.colors import rgb_black_color
from OpenGL.GL import (
    GL_POINT, GL_POINTS, 
    GL_LINE, GL_LINES, GL_LINE_LOOP, GL_LINE_STRIP, 
    GL_TRIANGLES, GL_TRIANGLE_STRIP, GL_TRIANGLE_FAN, 
)


class OpenGLComponent:
    ''' Representa uma componente OpenGL '''

    ''' Atributos '''
    primitive:int
    vertices:Sequence
    color:Sequence

    def __init__(self, primitive:int, vertices:Sequence, color:Sequence = None):
        '''
        Inicialização da componente.

        Parâmetros:
        ----------
        primitive: int
            Primitiva de renderização do OpenGL
        vertices: Sequence
            Arranjo contendo os vértices.
        color: Sequence, default = None
            Arranjo RGB com quatro dimensões. Caso nenhuma cor seja 
            fornecida, a cor preta será utilizada.
        '''
        if color is None:
            color = rgb_black_color()
        elif len(color) != 4:
            raise ValueError("expected 'color' to have four dimensions")
        self.primitive = primitive
        self.vertices = vertices
        self.color = color
    
    def transform(self, matrix:Sequence):
        ''' 
        Realiza transformação dos vértices com base 
        em uma matriz de transformação fornecida. 
        '''
        self.vertices = np.dot(matrix, self.vertices)

    def __len__(self):
        ''' Retorna o número de vértices da componente. '''
        return len(self.vertices)


class Points(OpenGLComponent):
    ''' Componente OpenGL para representação de pontos '''

    def __init__(self, vertices:Sequence, color:Sequence = None):
        '''
        Inicialização da componente.

        Parâmetros:
        ----------
        vertices: Sequence
            Arranjo contendo os vértices.
        color: Sequence, default = None
            Arranjo RGB com quatro dimensões. Caso nenhuma cor seja 
            fornecida, a cor preta será utilizada.
        '''
        primitive = GL_POINT if len(vertices) == 1 else GL_POINTS
        super().__init__(primitive, vertices, color)


class Lines(OpenGLComponent):
    ''' Componente OpenGL para representação de linhas '''

    def __init__(self, vertices:Sequence, color:Sequence = None, *, mode:str = None):
        '''
        Inicialização da componente.

        Parâmetros:
        ----------
        vertices: Sequence
            Arranjo contendo os vértices.
        color: Sequence, default = None
            Arranjo RGB com quatro dimensões. Caso nenhuma cor seja 
            fornecida, a cor preta será utilizada.
        mode: str, default = None
            Indica o modo de renderização. Caso não seja fornecido, 
            utilizará GL_LINES para renderizar linhas a cada dois 
            vértices; caso seja "strip", utilizará encadeamento via 
            GL_LINE_STRIP; caso seja "loop", fará um circuito fechado 
            de linhas por meio da primitiva GL_LINE_LOOP.
        '''
        primitive = GL_LINES
        if len(vertices) == 1:
            primitive = GL_LINE
        elif mode is not None: 
            if mode == "strip":
                primitive = GL_LINE_STRIP
            elif mode == "loop":
                primitive = GL_LINE_LOOP
        super().__init__(primitive, vertices, color)
    

class Triangles(OpenGLComponent):
    ''' Componente OpenGL para representação de triângulos '''

    def __init__(self, vertices:Sequence, color:Sequence = None, *, mode:str = None):
        '''
        Inicialização da componente.

        Parâmetros:
        ----------
        vertices: Sequence
            Arranjo contendo os vértices.
        color: Sequence, default = None
            Arranjo RGB com quatro dimensões. Caso nenhuma cor seja 
            fornecida, a cor preta será utilizada.
        mode: str, default = None
            Indica o modo de renderização. Caso não seja fornecido, 
            utilizará GL_TRIANGLES para renderizar triângulos a cada 
            três vértices; caso seja "strip", utilizará encadeamento via 
            GL_TRIANGLE_STRIP; caso seja "fan", fará um circuito fechado 
            de triângulos por meio da primitiva GL_TRIANGLE_FAN.
        '''
        primitive = GL_TRIANGLES
        if mode is not None: 
            if mode == "strip":
                primitive = GL_TRIANGLE_STRIP
            elif mode == "fan":
                primitive = GL_TRIANGLE_FAN
        super().__init__(primitive, vertices, color)


class Rectangle(OpenGLComponent):
    ''' Componente OpenGL para representação de um retângulo '''

    def __init__(self, width:float, height:float, x0:float = 0.0, y0:float = 0.0, color:Sequence = None):
        '''
        Inicialização da componente.

        Parâmetros:
        ----------
        width: float
            Comprimento do retângulo.
        height: float
            Altura do retângulo.
        x0: float, default = 0.0
            Coordenada x da origem do retângulo.
        y0: float, default = 0.0
            Coordenada y da origem do retângulo.
        color: Sequence, default = None
            Arranjo RGB com quatro dimensões. Caso nenhuma cor seja 
            fornecida, a cor preta será utilizada.
        '''
        # Para os cálculos
        w = width/2.0
        h = height/2.0

        # Obtenção dos vértices
        vertices = np.array([
            [x0+w, y0+h], 
            [x0+w, y0-h], 
            [x0-w, y0-h], 
            [x0-w, y0+h], 
            [x0+w, y0+h], # Para formar o retângulo via STRIP
        ], dtype=np.float32)

        # Construção da componente
        super().__init__(GL_TRIANGLE_STRIP, vertices, color)


class Square(Rectangle):
    ''' Componente OpenGL para representação de um quadrado '''

    def __init__(self, side:float, x0:float = 0.0, y0:float = 0.0, color:Sequence = None):
        '''
        Inicialização da componente.

        Parâmetros:
        ----------
        side: float
            Tamanho do lado do quadrado.
        x0: float, default = 0.0
            Coordenada x da origem do quadrado.
        y0: float, default = 0.0
            Coordenada y da origem do quadrado.
        color: Sequence, default = None
            Arranjo RGB com quatro dimensões. Caso nenhuma cor seja 
            fornecida, a cor preta será utilizada.
        '''
        super().__init__(side, side, x0, y0, color)

    
class Circle(OpenGLComponent):
    ''' Componente OpenGL para representação de um círculo '''

    def __init__(self, x0:float = 0.0, y0:float = 0.0, radius:float = 1.0, num_vertices:int = 64, color:Sequence = None):
        '''
        Inicialização da componente.

        Parâmetros:
        ----------
        x0: float, default = 0.0
            Dimensão x do vértice de origem.
        y0: float, default = 0.0
            Dimensão y do vértice de origem.
        radius: float, default = 1.0
            Raio do círculo.
        num_vertices: int, default = 64
            Quantia de vértices desejados.
        color: Sequence, default = None
            Arranjo RGB com quatro dimensões. Caso nenhuma cor seja 
            fornecida, a cor preta será utilizada.
        '''
        # Discretização dos ângulos do círculo
        angles = np.linspace(start=2*np.pi/num_vertices, stop=2*np.pi, num=num_vertices)

        # Construção dos vértices
        x = x0 + np.cos(angles) * radius
        y = y0 + np.sin(angles) * radius
        vertices = tuple(zip(x, y))
        
        # Inicialização da componente principal
        super().__init__(GL_TRIANGLE_FAN, vertices, color)


class OpenGLComponentCompound:
    ''' Conjunto de componentes do OpenGL '''

    def __init__(self, components):
        '''
        Inicialização do conjunto de componentes.

        Parâmetros:
        ----------
        components: array-like
            Lista de componentes que comporão o conjunto.
        '''
        self.components = list()
        self.components.extend(components)
        self.transformation = np.array([[1.0, 0.0, 0.0, 0.0], 
                                        [0.0, 1.0, 0.0, 0.0], 
                                        [0.0, 0.0, 1.0, 0.0], 
                                        [0.0, 0.0, 0.0, 1.0]], np.float32)
    
    @property
    def vertices(self):
        return np.vstack([cp.vertices for cp in self.components])