# Dependências
from collections.abc import Sequence
from numpy import identity, array
from pywavefront import Wavefront

class WaveFrontMaterialController:
    ''' Classe de controle de acesso às características de um material WaveFront '''

    def __init__(self, name, material, model, ka, kd, ks, ns):
        ''' Inicialização a partir de um material '''

        # Nome da componente
        self.name = name

        # Matriz model (guarda a referência)
        self.model = model

        # Controle de iluminação
        self.ka = ka
        self.kd = kd
        self.ks = ks
        self.ns = ns

        # Listas de vértices
        textures = []
        normals = []
        vertices = []

        # Dados
        FACE_SIZE = 8
        mv = material.vertices

        # Aquisição e separação dos vértices; formato "T2F_N3F_V3F"
        for idx in range(0, len(mv), FACE_SIZE):

            # T2F
            textures.append(mv[idx])
            textures.append(mv[idx+1])

            # N3F
            normals.append(mv[idx+2])
            normals.append(mv[idx+3])
            normals.append(mv[idx+4])

            # V3F
            vertices.append(mv[idx+5])
            vertices.append(mv[idx+6])
            vertices.append(mv[idx+7])

        # Armazenamento dos vértices
        self.textures = array(textures).reshape(-1,2)
        self.normals = array(normals).reshape(-1,3)
        self.vertices = array(vertices).reshape(-1,3)

        # Armazenamento do caminho da textura
        self.texture_filepath = material.texture._path



class WaveFrontObject:
    ''' Componente OpenGL para representação de objetos WaveFront '''

    def __init__(self, 
                 obj_filename:str, 
                 model:Sequence = None,
                 ka:float=1.0, 
                 kd:float=0.5, 
                 ks:float=0.5, 
                 ns:float=1.0):
        '''
        Inicialização da componente.

        Parâmetros:
        ----------
        obj_filename: str
            Caminho para o arquivo .obj.
        model: Sequence, default = None
            Matriz de modelo da componente. Caso nenhuma seja fornecida, 
            utilizará a matriz identidade.
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
        scene = Wavefront(obj_filename, collect_faces=True)
        
        # Matriz Model
        if model is None:
            model = identity(4)
        self.model = model

        # Extração dos materiais
        self.materials = [
            WaveFrontMaterialController(name, material, self.model, ka, kd, ks, ns) 
            for name, material in scene.materials.items()
        ]

    def set_model(self, value):
        ''' Atualização da matriz Model '''
        self.model = value
        for mt in self.materials:
            mt.model = value
        
            