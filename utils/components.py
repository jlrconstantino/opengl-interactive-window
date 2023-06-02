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
    model:Sequence

    def __init__(self, primitive:int, vertices:Sequence, color:Sequence = None, model:Sequence = None, line_width:float = 1.0):
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
        model: Sequence, default = None
            Matriz de modelo da componente. Caso nenhuma seja fornecida, 
            utilizará a matriz identidade.
        line_width: float, default = 1.0
            Espessura da linha a ser utilizada na renderização 
            do objeto.
        '''
        if color is None:
            color = rgb_black_color()
        if model is None:
            model = np.identity(4)
        elif len(color) != 4:
            raise ValueError("expected 'color' to have four dimensions")
        self.primitive = primitive
        self.vertices = vertices
        self.color = color
        self.model = model
        self.line_width = line_width
    
    def transform(self, matrix:Sequence):
        ''' 
        Realiza transformação dos vértices com base 
        em uma matriz de transformação fornecida. 
        '''
        self.vertices = np.dot(matrix, self.vertices)

    def __len__(self):
        ''' Retorna o número de vértices da componente. '''
        return len(self.vertices)


def load_model_from_file(filename):
    """Loads a Wavefront OBJ file. """
    objects = {}
    vertices = []
    texture_coords = []
    faces = []

    material = None

    # abre o arquivo obj para leitura
    for line in open(filename, "r"): ## para cada linha do arquivo .obj
        if line.startswith('#'): continue ## ignora comentarios
        values = line.split() # quebra a linha por espaço
        if not values: continue

        ### recuperando vertices
        if values[0] == 'v':
            vertices.append(values[1:4])

        ### recuperando coordenadas de textura
        elif values[0] == 'vt':
            texture_coords.append(values[1:3])

        ### recuperando faces 
        elif values[0] in ('usemtl', 'usemat'):
            material = values[1]
        elif values[0] == 'f':
            face = []
            face_texture = []
            for v in values[1:]:
                w = v.split('/')
                face.append(int(w[0]))
                if len(w) >= 2 and len(w[1]) > 0:
                    face_texture.append(int(w[1]))
                else:
                    face_texture.append(0)

            faces.append((face, face_texture, material))

    model = {}
    model['vertices'] = vertices
    model['texture'] = texture_coords
    model['faces'] = faces

    return model


class WaveFrontObject(OpenGLComponent):
    ''' Componente OpenGL para representação de objetos WaveFront '''

    def __init__(self, filename:str, color:Sequence = None):
        '''
        Inicialização da componente.

        Parâmetros:
        ----------
        filename: str
            Caminho para o arquivo .obj.
        color: Sequence, default = None
            Arranjo RGB com quatro dimensões. Caso nenhuma cor seja 
            fornecida, a cor preta será utilizada.
        '''
        model = load_model_from_file(filename)
        vertices = []
        for face in model['faces']:
            for vertice_id in face[0]: 
                vertices.append( model['vertices'][vertice_id-1] )
        primitive = GL_TRIANGLES
        super().__init__(primitive, vertices, color)