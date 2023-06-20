# Dependências
import numpy as np
from PIL import Image
import ctypes
from OpenGL.GL import *
from collections.abc import Sequence
from utils.glfw_window import GLFWWindow
from utils.components import WaveFrontObject
from utils.typeutils import check_type
from utils.iterutils import flatten


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

    ''' Atributos de controle '''
    components = None
    program = None
    clear_color = None
    buffered = False

    ''' Buffers de matriz '''
    model_buffer = None
    view_buffer = None
    projection_buffer = None
    
    ''' Buffers de iluminação '''
    light_buffer = None
    ka_buffer = None
    kd_buffer = None
    ks_buffer = None
    ns_buffer = None

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

            // Para manipulação de texturas
            attribute vec2 texture_coord;
            varying vec2 out_texture;

            // Para manipulação de normais
            attribute vec3 normals;
            varying vec3 out_normal;
        
            // Para manipulação de fragmentos
            varying vec3 out_fragPos;
            
            // Matrizes de modelo, visão e projeção
            uniform mat4 model;
            uniform mat4 view;
            uniform mat4 projection;        
            
            // Programa principal
            void main(){
                gl_Position = projection * view * model * vec4(position,1.0);
                out_texture = vec2(texture_coord);
                out_fragPos = vec3(model * vec4(position, 1.0));
                out_normal = vec3(model * vec4(normals, 1.0));            
            }
        """

        # Código C para manipulação e transformação dos fragmentos
        fragment_code = """
            // Posição e coloração da luz
            uniform vec3 lightPos;
            vec3 lightColor = vec3(1.0, 1.0, 1.0);
            
            // Parâmetros da iluminação ambiente e difusa
            uniform float ka;   // Coeficiente de reflexão ambiente
            uniform float kd;   // Coeficiente de reflexão difusa
            
            // Parâmetros da iluminação especular
            uniform vec3 viewPos;   // Define coordenadas com a posição da câmera/observador
            uniform float ks;       // Coeficiente de reflexão especular
            uniform float ns;       // Expoente de reflexão especular
            
            // Parâmetros recebidos do vertex shader
            varying vec2 out_texture;
            varying vec3 out_normal;
            varying vec3 out_fragPos;
            uniform sampler2D samplerTexture;
            
            // Programa principal
            void main(){
            
                // Cálculo de reflexão ambiente
                vec3 ambient = ka * lightColor;             
            
                // Cálculo de reflexão difusa
                vec3 norm = normalize(out_normal); // normaliza vetores perpendiculares
                vec3 lightDir = normalize(lightPos - out_fragPos); // direcao da luz
                float diff = max(dot(norm, lightDir), 0.0); // verifica limite angular (entre 0 e 90)
                vec3 diffuse = kd * diff * lightColor; // iluminacao difusa
                
                // Cálculo de reflexão especular
                vec3 viewDir = normalize(viewPos - out_fragPos); // direcao do observador/camera
                vec3 reflectDir = normalize(reflect(-lightDir, norm)); // direcao da reflexao
                float spec = pow(max(dot(viewDir, reflectDir), 0.0), ns);
                vec3 specular = ks * spec * lightColor;             
                
                // Aplicação do modelo de iluminação
                vec4 texture = texture2D(samplerTexture, out_texture);
                vec4 result = vec4((ambient + diffuse + specular),1.0) * texture; // aplica iluminacao
                gl_FragColor = result;
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
        self.materials = list()

        # Ativação do uso de texturas 2D
        glEnable(GL_TEXTURE_2D)

        # Para controle de bufferização
        self.buffered = False

        # Cor de limpeza da tela
        self.clear_color = (0.0, 0.0, 0.0, 1.0)
    

    def enable_polygon_mode(self):
        ''' Ativa o modo poligonal '''
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    

    def add_component(self, component:WaveFrontObject):
        ''' Registra um novo componente '''
        for material in component.materials:
            self.materials.append(material)

    
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
        self.materials = list()
        self.buffered = False

    
    def _load_texture_from_file(self, idx, filename):
        ''' Carrega uma imagem de textura '''

        # Associação por ID
        glBindTexture(GL_TEXTURE_2D, idx)

        # Parâmetros de textura
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        # Processamento da imagem
        img = Image.open(filename)
        img_width = img.size[0]
        img_height = img.size[1]
        image_data = img.tobytes("raw", "RGB", 0, -1)

        # Associação da imagem
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img_width, img_height, 0, GL_RGB, GL_UNSIGNED_BYTE, image_data)
    

    def _get_vertices(self):
        ''' Retorna os vértices que integram todos os componentes '''
        flatten_vertices = np.vstack([mt.vertices for mt in self.materials])
        vertices = np.zeros(len(flatten_vertices), [("position", np.float32, 3)])
        vertices["position"] = flatten_vertices
        return vertices
    

    def _get_texture_vertices(self):
        ''' Retorna os vértices de textura que integram todos os componentes '''
        flatten_vertices = np.vstack([mt.textures for mt in self.materials])
        textures = np.zeros(len(flatten_vertices), [("position", np.float32, 2)])
        textures["position"] = flatten_vertices
        return textures


    def _get_normals_vertices(self):
        ''' Retorna os vértices das normais que integram todos os componentes '''
        flatten_vertices = np.vstack([mt.normals for mt in self.materials])
        normals = np.zeros(len(flatten_vertices), [("position", np.float32, 3)])
        normals["position"] = flatten_vertices
        return normals


    def process_buffers(self):
        ''' Realiza o processamento dos buffers do OpenGL '''

        # Requisição de três slots de buffer da GPU 
        # (vértices dos polígonos, das texturas e das normais)
        buffer = glGenBuffers(3)

        # Envio dos vértices à GPU
        vertices = self._get_vertices()
        glBindBuffer(GL_ARRAY_BUFFER, buffer[0])
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_DYNAMIC_DRAW)

        # Stride e offset do buffer
        stride = vertices.strides[0]
        offset = ctypes.c_void_p(0)

        # Associação das posições do GLSL ao buffer de vértices
        loc_position = glGetAttribLocation(self.program, "position")
        glEnableVertexAttribArray(loc_position)
        glVertexAttribPointer(loc_position, 3, GL_FLOAT, False, stride, offset)

        # Geração e carregamento das texturas
        glGenTextures(len(self.materials))
        for idx, mt in enumerate(self.materials):
            self._load_texture_from_file(idx, mt.texture_filepath)

        # Envio dos vértices de textura à GPU
        textures = self._get_texture_vertices()
        glBindBuffer(GL_ARRAY_BUFFER, buffer[1])
        glBufferData(GL_ARRAY_BUFFER, textures.nbytes, textures, GL_STATIC_DRAW)

        # Stride do buffer de texturas
        stride = textures.strides[0]

        # Associação das posições do GLSL ao buffer de texturas
        loc_texture_coord = glGetAttribLocation(self.program, "texture_coord")
        glEnableVertexAttribArray(loc_texture_coord)
        glVertexAttribPointer(loc_texture_coord, 2, GL_FLOAT, False, stride, offset)

        # Envio dos vértices das normais à GPU
        normals = self._get_normals_vertices()
        glBindBuffer(GL_ARRAY_BUFFER, buffer[2])
        glBufferData(GL_ARRAY_BUFFER, normals.nbytes, normals, GL_STATIC_DRAW)

        # Stride do buffer de normais
        stride = normals.strides[0]

        # Associação das posições do GLSL ao buffer de vetores normais
        loc_normals_coord = glGetAttribLocation(self.program, "normals")
        glEnableVertexAttribArray(loc_normals_coord)
        glVertexAttribPointer(loc_normals_coord, 3, GL_FLOAT, False, stride, offset)

        # Aquisição dos buffers de controle das matrizes
        self.model_buffer = glGetUniformLocation(self.program, "model")
        self.view_buffer = glGetUniformLocation(self.program, "view")
        self.projection_buffer = glGetUniformLocation(self.program, "projection")

        # Aquisição dos buffers de controle de iluminação
        self.ka_buffer = glGetUniformLocation(self.program, "ka")
        self.kd_buffer = glGetUniformLocation(self.program, "kd")
        self.ks_buffer = glGetUniformLocation(self.program, "ks")
        self.ns_buffer = glGetUniformLocation(self.program, "ns")
        self.light_buffer = glGetUniformLocation(self.program, "lightPos")
        
        # z-buffer
        glEnable(GL_DEPTH_TEST)

        # Flag de bufferização
        self.buffered = True
    

    def clear(self):
        ''' Limpa a janela da sessão atual '''
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(*self.clear_color)
    

    def _render_component(self, idx, num_rendered_vertices, mt):
        ''' Renderiza um objeto e retorna a quantia de vértices dele '''

        # Quantia de vértices da componente
        num_vertices = len(mt.vertices)

        # Controle de iluminação
        glUniform1f(self.ka_buffer, mt.ka)
        glUniform1f(self.kd_buffer, mt.kd)
        glUniform1f(self.ks_buffer, mt.ks)
        glUniform1f(self.ns_buffer, mt.ns)

        # Modelo, textura e desenho dos polígonos
        glUniformMatrix4fv(self.model_buffer, 1, GL_TRUE, mt.model)
        glBindTexture(GL_TEXTURE_2D, idx)
        glDrawArrays(GL_TRIANGLES, num_rendered_vertices, num_vertices)

        return num_vertices


    def move_light(self, tx, ty, tz):
        ''' Movimenta a luz para a posição desejada '''
        glUniform3f(self.light_buffer, tx, ty, tz)


    def render(self):
        ''' Renderiza todos os componentes registrados na sessão '''

        # Verificação de bufferização
        if self.buffered is False:
            raise UninitializedBufferException("use process_buffers() before rendering")

        # Quantia de vértices renderizados
        num_rendered_vertices = 0

        # Renderização das componentes
        for idx, mt in enumerate(flatten(self.materials)):
            num_rendered_vertices += self._render_component(idx, num_rendered_vertices, mt)
    
    
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