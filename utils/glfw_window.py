# Dependências
import glfw
from collections import defaultdict
import numpy as np
import glm


# Exceções
class GLFWInitializationError(Exception):
    pass
class WindowCreationError(Exception):
    pass
class UnknownKeyError(Exception):
    pass


class GLFWWindow:
    ''' Janela de contexto do GLFW '''

    ''' Atributos '''
    window = None
    key_callbacks = None
    mouse_callbacks = None
    cursor_callbacks = None
    initial_cursor_pos = None
    projection = None

    def __init__(self, width:int, height:int, title:str = "", *, monitor:int = None, share:int = None):
        ''' 
        Inicialização do contexto. 

        Parâmetros:
        ----------
        width: int
            Largura da janela em pixels
        height: int
            Altura da janela em pixels
        title: str
            Título da janela
        monitor: int
            Monitor a ser utilizado. Por padrão, utiliza o atualmente ativo.
        share: int
            Diretiva de compartilhamento.
        '''

        # Inicialização do GLFW
        if not glfw.init():
            raise GLFWInitializationError()
        
        # Criação da janela
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE);
        window = glfw.create_window(width, height, title, monitor, share)
        if not window:
            glfw.terminate()
            raise WindowCreationError()
        glfw.make_context_current(window)

        # Registro dos atributos
        self.window = window
        self.key_callbacks = defaultdict(list)
        self.mouse_callbacks = defaultdict(list)
        self.cursor_callbacks = []
        self.initial_cursor_pos = (width/2, height/2)

        # Projeção de tela
        self.projection = np.array (
            glm.perspective (
                glm.radians(45.0),  # fovy
                width/height,       # aspect
                0.1,                # near
                1000.0              # far
            )
        )

        # Eventos de tecla
        def key_event(window, key, scancode, action, mods):
            for callback in self.key_callbacks[key]:
                callback(key, action)
        glfw.set_key_callback(window, key_event)

        # Eventos de clique
        def mouse_event(window,button,action,mods):
            for callback in self.mouse_callbacks[button]:
                callback(button, action)
        glfw.set_mouse_button_callback(window,mouse_event)

        # Eventos de ponteiro de mouse
        def cursor_event(window, xpos, ypos):
            for callback in self.cursor_callbacks:
                callback(xpos, ypos)
        glfw.set_cursor_pos_callback(window, cursor_event)
    

    def add_key_callback(self, key:str, callback):
        ''' 
        Adiciona um callback aos eventos de uma tecla 
        específica.

        Parâmetros:
        ----------
        key: str
            String referente à tecla, por exemplo, 
            "A" e "PAUSE".
        callback: function
            Função de callback para a tecla correspondente. 
            Deve apresentar dois parâmetros: um referente à 
            tecla pressionada, e outro referente à
            ação realizada nessa tecla.
        '''
        try:
            key = getattr(glfw, "KEY_{}".format(key.upper()))
            self.key_callbacks[key].append(callback)
        except:
            raise UnknownKeyError()
    

    def add_mouse_callback(self, button:str, callback):
        ''' 
        Adiciona um callback aos eventos de uma tecla 
        específica do mouse.

        Parâmetros:
        ----------
        button: str
            String referente à tecla, por exemplo, 
            "LEFT" e "RIGHT".
        callback: function
            Função de callback para a tecla correspondente. 
            Deve apresentar dois parâmetros: um referente à 
            tecla pressionada, e outro referente à
            ação realizada nessa tecla.
        '''
        try:
            button = getattr(glfw, "MOUSE_BUTTON_{}".format(button.upper()))
            self.mouse_callbacks[button].append(callback)
        except:
            raise UnknownKeyError()
    

    def add_cursor_callback(self, callback):
        ''' 
        Adiciona um callback aos eventos de movimentação 
        do cursor sobre a tela.

        Parâmetros:
        ----------
        callback: function
            Função de callback. Deve apresentar dois 
            parâmetros: xpos e ypos nesta ordem.
        '''
        self.cursor_callbacks.append(callback)
        

    def display(self):
        '''
        Ativa a visualização da janela enquanto 
        essa não for encerrada. Ao final, termina 
        o processamento da biblioteca GLFW.
        '''
        # Habilitação da janela
        window = self.window
        glfw.show_window(self.window)
        glfw.set_cursor_pos(window, *self.initial_cursor_pos)
        try:

            # Enquanto não encerrá-la, itera
            while not glfw.window_should_close(self.window):

                # Processa os eventos da biblioteca
                glfw.poll_events()

                # Entrega o fluxo de controle
                yield

                # Realiza a troca de buffers CPU-GPU
                glfw.swap_buffers(window)

        # Encerra a biblioteca
        finally:
            glfw.terminate()