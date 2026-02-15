class Queue:
    """Implementação do TDA Queue baseada em List"""
    
    def __init__(self, sourceCollection = None):
        """ Define o estado inicial de self com sourceCollection """
        self._itens = list()
        self._size = 0
        if sourceCollection:
            for item in sourceCollection:
                self.add(item)

    @property
    def itens(self):
        return self._itens

    # def remove_specific(self, item):
    #     for value in self._itens:
    #         if value == item:
    #             self._itens.

    # metodos gerais de coleção
    def is_empty(self):
        """ Retorna True se len(self) é 0, senão False """
        return len(self) == 0

    def __len__(self):
        """ Retorna o numero de elementos da queue """
        return self._size

    def __str__(self):
        """ Retorna a representação em string de self """
        return str(self._itens) + " :  " + str(self._size) + " elementos"

    def clear(self):
        """ Torna o self vazio"""
        self._itens = list()
        self._size = 0

    def __iter__(self):
        """ Suporta a iteração sobre self """
        return None

    # metodos especificos da fila

    def peek(self):
        """ Retorna o item que está na frente de self.
             precondição: self não é vazio."""
        if self.is_empty():
            raise KeyError(" queue is empty")
        else:
            return self._itens[0]

    def add(self, item):
        """ Acrescenta item a self no fim
            pos-condição: item foi acrescentado a self """
        self._itens.append(item)
        self._size += 1

    def pop(self):
        """ Remove elemento do topo de self e retorna esse elemento.
             precondição: self não é vazio.
             pos-condição: item foi removido de self """
        if self.is_empty():
            raise KeyError(" queue is empty")
        else:
            self._size -= 1
            return self._itens.pop(0)

    def remove(self, element):
        if self.is_empty():
            raise KeyError(" queue is empty")
        else:
            self._size -= 1
            print('Item removido da fila.')
            return self._itens.remove(element)

