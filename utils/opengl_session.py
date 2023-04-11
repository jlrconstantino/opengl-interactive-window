# Dependências
from OpenGL.GL import *

# Exceções
class VertexShaderException(Exception):
    pass
class FragmentShaderException(Exception):
    pass
class ProgramBuildException(Exception):
    pass


class OpenGLSession:
    ''' Sessão de um programa OpenGL. '''


    def __init__(self):
        '''
        '''

        # Código C para manipulação e transformação dos vértices
        vertex_code = """
            attribute vec3 position;
            uniform mat4 mat_transformation;
            void main(){
                gl_Position = mat_transformation * vec4(position, 1.0);
            }
        """

        # Código C para manipulação e transformação das cores dos fragmentos
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
            
        # Faz do programa atual o padrão
        glUseProgram(program)