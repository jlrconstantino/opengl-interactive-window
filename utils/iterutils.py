# Dependências
from collections import Iterable

def flatten(items:Iterable):
    '''
    Permite a iteração mista entre elementos iteráveis 
    e não iteráveis. Por exemplo, a coleção [1,[2,3], 
    [4,[5,6]]] seria iterada como [1,2,3,4,5,6].

    Parâmetros:
    ----------
    items: Iterable
        Coleção iterável de elementos.
    '''
    for item in items:
        if isinstance(item, Iterable):
            yield from flatten(item)
        else:
            yield item