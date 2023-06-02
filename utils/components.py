# Dependências
from collections.abc import Sequence
import numpy as np
from utils.colors import rgb_black_color
from OpenGL.GL import GL_TRIANGLES


class OpenGLComponent:
    ''' Representa uma componente OpenGL '''

    ''' Atributos '''
    primitive:int
    vertices:Sequence
    model:Sequence

    def __init__(self, primitive:int, vertices:Sequence, model:Sequence = None):
        '''
        Inicialização da componente.

        Parâmetros:
        ----------
        primitive: int
            Primitiva de renderização do OpenGL
        vertices: Sequence
            Arranjo contendo os vértices.
        model: Sequence, default = None
            Matriz de modelo da componente. Caso nenhuma seja fornecida, 
            utilizará a matriz identidade.
        '''
        if model is None:
            model = np.identity(4)
        self.primitive = primitive
        self.vertices = vertices
        self.model = model
    
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
    vertices = []
    normals = []
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

        ### recuperando vertices
        if values[0] == 'vn':
            normals.append(values[1:4])

        ### recuperando coordenadas de textura
        elif values[0] == 'vt':
            texture_coords.append(values[1:3])

        ### recuperando faces 
        elif values[0] in ('usemtl', 'usemat'):
            material = values[1]
        elif values[0] == 'f':
            face = []
            face_texture = []
            face_normals = []
            for v in values[1:]:
                w = v.split('/')
                face.append(int(w[0]))
                face_normals.append(int(w[2]))
                if len(w) >= 2 and len(w[1]) > 0:
                    face_texture.append(int(w[1]))
                else:
                    face_texture.append(0)

            faces.append((face, face_texture, face_normals, material))

    model = {}
    model['vertices'] = vertices
    model['texture'] = texture_coords
    model['faces'] = faces
    model['normals'] = normals

    return model


class WaveFrontObject(OpenGLComponent):
    ''' Componente OpenGL para representação de objetos WaveFront '''

    def __init__(self, obj_filename:str, texture_filename:str, ka:float=1.0, kd:float=0.5, ks:float=0.5, ns:float=1.0):
        '''
        Inicialização da componente.

        Parâmetros:
        ----------
        obj_filename: str
            Caminho para o arquivo .obj.
        texture_filename: str
            Caminho para o arquivo de textura.
        ka: float, default = 1.0
            Coeficiente de reflexão ambiente.
        kd: float, default = 0.5
            Coeficiente de reflexão difusa.
        ks: float, default = 0.5
            Coeficiente de reflexão especular.
        ns: float, default = 1.0
            Expoente de reflexão especular.
        '''
        # Carregamento do modelo do objeto
        model = load_model_from_file(obj_filename)
        vertices = []
        texture_vertices = []
        normals_vertices = []
        for face in model['faces']:
            for vertice_id in face[0]: 
                vertices.append( model['vertices'][vertice_id-1] )
            for texture_id in face[1]:
                texture_vertices.append( model['texture'][texture_id-1] )
            for normal_id in face[2]:
                normals_vertices.append( model['normals'][normal_id-1] )
        
        # Inicialização da componente
        primitive = GL_TRIANGLES
        super().__init__(primitive, vertices)

        # Texturas
        self.texture_filename = texture_filename
        self.texture_vertices = texture_vertices

        # Vetores normais
        self.normals_vertices = normals_vertices

        # Controle de iluminação
        self.ka = ka
        self.kd = kd
        self.ks = ks
        self.ns = ns