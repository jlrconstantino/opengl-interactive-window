# Dependências
import glfw
from collections import defaultdict


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
        stare: int
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

        # Eventos de tecla
        def key_event(window, key, scancode, action, mods):
            for callback in self.key_callbacks[key]:
                callback(action)
        glfw.set_key_callback(window, key_event)

        # Eventos de clique
        def mouse_event(window,button,action,mods):
            for callback in self.mouse_callbacks[button]:
                callback(action)
        glfw.set_mouse_button_callback(window,mouse_event)
    

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
            Deve apresentar único parâmetro referente à 
            ação realizada na tecla.
        '''
        try:
            key = getattr(glfw, "KEY_{}".format(key.upper()))
            self.key_callbacks[key].append(callback)
        except:
            raise UnknownKeyError()
    

    def add_mouse_callback(self, button:int, callback):
        ''' 
        Adiciona um callback aos eventos de um botão 
        de mouse específico.

        Parâmetros:
        ----------
        button: int
            Código do botão. Por exemplo, 0 para o botão 
            esquerdo, e 1 para o direito.
        callback: function
            Função de callback para a tecla correspondente. 
            Deve apresentar único parâmetro referente à 
            ação realizada na tecla.
        '''
        self.mouse_callbacks[button].append(callback)


    def display(self):
        '''
        Ativa a visualização da janela enquanto 
        essa não for encerrada. Ao final, termina 
        o processamento da biblioteca GLFW.
        '''
        # Habilitação da janela
        window = self.window
        glfw.show_window(self.window)
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