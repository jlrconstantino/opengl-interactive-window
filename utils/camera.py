# Dependências
import glm
import numpy as np
from math import cos, sin

class Camera:
    ''' Câmera de visualização 3D para ser utilizada com o OpenGL '''

    # Atributos de controle
    active = False

    # Atributos de configuração
    speed = 0.0
    sensitivity = 0.0
    last_xpos = 0.0
    last_ypos = 0.0
    yaw = 0.0
    pitch = 0.0

    # Atributos posicionais
    position = None
    front = None
    up = None

    def __init__(
        self, 
        speed:float = 0.2, 
        sensitivity:float = 0.3,
        last_xpos:float = 0.0, 
        last_ypos:float = 0.0,
        yaw:float = -90.0, 
        pitch:float = 0.0,
        position:list = None
    ):
        ''' Inicialização da câmera '''
        
        # Atributos de controle
        self.active = True

        # Atributos de configuração
        self.speed = speed
        self.sensitivity = sensitivity
        self.last_xpos = last_xpos
        self.last_ypos = last_ypos
        self.yaw = yaw
        self.pitch = pitch

        # Atributos posicionais
        if position is None:
            position = (0.0,  0.0,  1.0)
        self.position = glm.vec3(*position)
        self.front = glm.vec3(0.0,  0.0, -1.0);
        self.up = glm.vec3(0.0,  1.0,  0.0)
    
    def move_forward(self, *_):
        ''' Mover para frente caso ativa '''
        if self.active == True:
            self.position += self.speed * self.front
    
    def move_right(self, *_):
        ''' Mover para a direita caso ativa '''
        if self.active == True:
            self.position += self.speed * glm.normalize(glm.cross(self.front, self.up))
    
    def move_backward(self, *_):
        ''' Mover para trás caso ativa '''
        if self.active == True:
            self.position -= self.speed * self.front

    def move_left(self, *_):
        ''' Mover para a esquerda caso ativa '''
        if self.active == True:
            self.position -= self.speed * glm.normalize(glm.cross(self.front, self.up))
    
    def move_front(self, xpos, ypos):
        ''' Movimentação do fronte de visão via cursor do mouse '''

        # Obtenção dos offsets
        xoffset = self.sensitivity * (xpos - self.last_xpos)
        yoffset = self.sensitivity * (self.last_ypos - ypos)
        
        # Atualizações
        self.last_xpos = xpos
        self.last_ypos = ypos
        self.yaw += xoffset
        self.pitch += yoffset

        # Controle de intervalo do pitch
        if self.pitch >= 90.0: 
            self.pitch = 90.0
        elif self.pitch <= -90.0: 
            self.pitch = -90.0

        # Atualização da visão
        front = glm.vec3()
        front.x = cos(glm.radians(self.yaw)) * cos(glm.radians(self.pitch))
        front.y = sin(glm.radians(self.pitch))
        front.z = sin(glm.radians(self.yaw)) * cos(glm.radians(self.pitch))
        self.front = glm.normalize(front)
    
    @property
    def view(self):
        return np.array (
            glm.lookAt (
                self.position, 
                self.position + self.front, 
                self.up
            )
        )


class RestrictedCamera(Camera):
    ''' Câmera com restrições de posição '''

    def __init__(
        self, 
        *, 
        min_xpos:float = -1000.0, 
        max_xpos:float = 1000.0, 
        min_ypos:float = -1000.0, 
        max_ypos:float = 1000.0,
        min_zpos:float = -1000.0, 
        max_zpos:float = 1000.0,
        **kwargs
    ):
        # Inicialização da classe pai
        super().__init__(**kwargs)

        # Posições em x
        self.min_xpos = min_xpos
        self.max_xpos = max_xpos

        # Posições em y
        self.min_ypos = min_ypos
        self.max_ypos = max_ypos

        # Posições em z
        self.min_zpos = min_zpos
        self.max_zpos = max_zpos
    
    def check_position(self):
        x, y, z = self.position
        if x < self.min_xpos or x > self.max_xpos:
            return False
        if y < self.min_ypos or y > self.max_ypos:
            return False
        if z < self.min_zpos or z > self.max_zpos:
            return False
        return True
    
    def move_forward(self, *_):
        ''' Mover para frente caso ativa '''
        x, y, z = self.position
        super().move_forward()
        if self.check_position() == False:
            self.position = glm.vec3(x,y,z)
    
    def move_right(self, *_):
        ''' Mover para a direita caso ativa '''
        x, y, z = self.position
        super().move_right()
        if self.check_position() == False:
            self.position = glm.vec3(x,y,z)
    
    def move_backward(self, *_):
        ''' Mover para trás caso ativa '''
        x, y, z = self.position
        super().move_backward()
        if self.check_position() == False:
            self.position = glm.vec3(x,y,z)

    def move_left(self, *_):
        ''' Mover para a esquerda caso ativa '''
        x, y, z = self.position
        super().move_left()
        if self.check_position() == False:
            self.position = glm.vec3(x,y,z)