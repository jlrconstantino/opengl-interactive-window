# Dependências
import glfw
from typeutils import typeassert


# Exceções
class GLFWInitializationException(Exception):
    pass
class WindowCreationException(Exception):
    pass


class GLFWWindow:
    ''' Janela de contexto do GLFW '''

    @typeassert(int, int, str, int, int, _is_method=True)
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
            raise GLFWInitializationException()
        
        # Criação da janela
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE);
        window = glfw.create_window(width, height, title, monitor, share)
        if not window:
            glfw.terminate()
            raise WindowCreationException()
        glfw.make_context_current(window)