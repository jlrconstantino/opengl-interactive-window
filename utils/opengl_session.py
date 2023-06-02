# Dependências
import numpy as np
import ctypes
from OpenGL.GL import *
from collections.abc import Sequence
from utils.glfw_window import GLFWWindow
from utils.components import OpenGLComponent
from utils.typeutils import check_type
from utils.iterutils import flatten
from utils.colors import rgb_white_color


# Exceções
class VertexShaderException(Exception):
    pass
class FragmentShaderException(Exception):
    pass
class ProgramBuildException(Exception):
    pass
class UninitializedBufferException(Exception):
    pass


class OpenGLSession:
    ''' 
    Sessão de um programa OpenGL. 
    Requer um contexto GLFW para funcionar.
    Ao ser evocado, compilará e inicializará 
    o programa OpenGL, assim como seus códigos 
    de vértices e de fragmentos.
    Após registrar os diferentes componentes 
    por meio do método "add_components", utilize 
    o método "process_buffers" para realizar o 
    processamento dos buffers necessários para 
    a renderização de tais componentes.
    '''

    ''' Atributos '''
    components = None
    program = None
    color_buffer = None
    model_buffer = None
    view_buffer = None
    projection_buffer = None

    def __init__(self, window:GLFWWindow) -> None:
        '''
        Parâmetros:
        ----------
        window: GLFWWindow
            Janela de contexto do GLFW. Utilizado para garantir
            inicialização prévia do módulo.
        '''
        # Verifica os argumentos fornecidos
        check_type(window, "window", GLFWWindow)

        # Código C para manipulação e transformação dos vértices
        vertex_code = """

            // Vetor de posições
            attribute vec3 position;

            // Matrizes de modelo, visão e projeção
            uniform mat4 model;
            uniform mat4 view;
            uniform mat4 projection;

            // Programa principal
            void main(){
                gl_Position = projection * view * model * vec4(position,1.0);
            } 
        """

        # Código C para manipulação e transformação dos fragmentos
        fragment_code = """
            uniform vec4 color;
            void main(){
                gl_FragColor = color;
            }
        """

        # Requisição de programa e de slots da GPU
        program  = glCreateProgram()
        vertex   = glCreateShader(GL_VERTEX_SHADER)
        fragment = glCreateShader(GL_FRAGMENT_SHADER)

        # Associação dos shaders
        glShaderSource(vertex, vertex_code)
        glShaderSource(fragment, fragment_code)

        # Compilação do shader de vértices
        glCompileShader(vertex)
        if not glGetShaderiv(vertex, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(vertex).decode()
            raise VertexShaderException(error)
        
        # Compilação do shader de fragmentos
        glCompileShader(fragment)
        if not glGetShaderiv(fragment, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(fragment).decode()
            raise FragmentShaderException(error)

        # Associação dos shaders compilados ao programa principal
        glAttachShader(program, vertex)
        glAttachShader(program, fragment)

        # Construção do programa
        glLinkProgram(program)
        if not glGetProgramiv(program, GL_LINK_STATUS):
            error = glGetProgramInfoLog(program)
            raise ProgramBuildException(error)
            
        # Faz do programa atual o inicializado anteriormente
        glUseProgram(program)
        self.program = program

        # Inicialização das componentes
        self.components = list()
    

    def enable_polygon_mode(self):
        ''' Ativa o modo poligonal '''
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    

    def add_component(self, component:OpenGLComponent):
        ''' Registra um novo componente '''
        self.components.append(component)

    
    def add_components(self, components:Sequence):
        ''' Registra uma nova coleção de componentes '''
        for cp in flatten(components):
            self.add_component(cp)
    

    def clear_components(self):
        ''' 
        Remove todas as componentes atualmente associadas 
        à sessão do OpenGL. No processo, os buffers são 
        destruídos. Logo, processe-os novamente antes de 
        realizar uma nova renderização.
        '''
        self.components = list()
        self.color_buffer = None
    

    def _get_vertices(self):
        ''' Retorna os vértices que integram todos os componentes '''
        flatten_vertices = np.vstack([cp.vertices for cp in self.components])
        vertices = np.zeros(len(flatten_vertices), [("position", np.float32, 3)])
        vertices["position"] = flatten_vertices
        return vertices
    

    def process_buffers(self):
        ''' Realiza o processamento dos buffers do OpenGL '''

        # Requisição e associação de slot de buffer da gpu
        buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, buffer)

        # Envio dos vértices à GPU
        vertices = self._get_vertices()
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_DYNAMIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, buffer)

        # Stride e offset do buffer
        stride = vertices.strides[0]
        offset = ctypes.c_void_p(0)

        # Associação das posições do GLSL ao buffer
        loc_position = glGetAttribLocation(self.program, "position")
        glEnableVertexAttribArray(loc_position)
        glVertexAttribPointer(loc_position, 3, GL_FLOAT, False, stride, offset)

        # Aquisição dos buffers de controle
        self.color_buffer = glGetUniformLocation(self.program, "color")
        self.model_buffer = glGetUniformLocation(self.program, "model")
        self.view_buffer = glGetUniformLocation(self.program, "view")
        self.projection_buffer = glGetUniformLocation(self.program, "projection")
        
        # Para 3D
        glEnable(GL_DEPTH_TEST)
    

    def clear(self):
        ''' Limpa a janela da sessão atual '''
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(1.0, 1.0, 1.0, 1.0)
    

    def _render_component(self, num_rendered_vertices, cp):
        ''' Renderiza um objeto e retorna a quantia de vértices dele '''

        # Quantia de vértices da componente
        num_vertices = len(cp)

        # Aplicação da coloração e da forma da componente
        glUniform4f(self.color_buffer, *cp.color)
        glLineWidth(cp.line_width)
        glDrawArrays(cp.primitive, num_rendered_vertices, num_vertices)

        return num_vertices


    def render(self):
        ''' Renderiza todos os componentes registrados na sessão '''

        # Verificação de bufferização
        if self.color_buffer is None:
            raise UninitializedBufferException("use process_buffers() before rendering")

        # Quantia de vértices renderizados
        num_rendered_vertices = 0

        # Iteração ao longo das componentes
        for cp in flatten(self.components):

            # Aplicação da transformação e renderização
            glUniformMatrix4fv(self.model_buffer, 1, GL_TRUE, cp.model)
            num_rendered_vertices += self._render_component(num_rendered_vertices, cp)
    
    
    def view(self, matrix:Sequence = None):
        ''' Envia uma matriz de visão à GPU '''
        if matrix is None:
            matrix = np.identity(4)
        glUniformMatrix4fv(self.view_buffer, 1, GL_TRUE, matrix)
    

    def projection(self, matrix:Sequence = None):
        ''' Envia uma matriz de projeção à GPU '''
        if matrix is None:
            matrix = np.identity(4)
        glUniformMatrix4fv(self.projection_buffer, 1, GL_TRUE, matrix)