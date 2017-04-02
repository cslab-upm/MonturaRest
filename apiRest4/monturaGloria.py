import abc
class monturaGloria:
    __metaclass__ = abc.ABCMeta
    
    # Funciones necesarias
    @abc.abstractmethod
    def iniciarSerie(self):
        raise NotImplementedError('El metodo "iniciarSerie" no ha sido implementado')

    @abc.abstractmethod
    def getStatus(self):
        raise NotImplementedError('El metodo "getStatus" no ha sido implementado')

    @abc.abstractmethod
    def getRA(self):
        raise NotImplementedError('El metodo "getRA" no ha sido implementado')

    @abc.abstractmethod
    def getDec(self):
        raise NotImplementedError('El metodo "getDec" no ha sido implementado')

    @abc.abstractmethod
    def setSeguimiento(self, b):
        raise NotImplementedError('El metodo "setMovimiento" no ha sido implementado')

    @abc.abstractmethod
    def setTasaSeguimiento(self, tiempo):
        raise NotImplementedError('El metodo "setTasaMovimiento" no ha sido implementado')

    @abc.abstractmethod
    def setSlewRate(self, n):
        raise NotImplementedError('El metodo "SetSlewRate" no ha sido implementado')

    @abc.abstractmethod
    def getRA(self):
        raise NotImplementedError('El metodo "getRA" no ha sido implementado')

    @abc.abstractmethod
    def moverPorTiempo(self, direccion, tiempo):
        raise NotImplementedError('El metodo "moverPorTiempo" no ha sido implementado')

    @abc.abstractmethod
    def moverPorCoordenadas(self, tipo, coordenadas):
        raise NotImplementedError('El metodo "moverPorCoordenadas" no ha sido implementado')

    @abc.abstractmethod
    def moverHastaObjeto(self, objeto):
        raise NotImplementedError('El metodo "moverHastaObjeto" no ha sido implementado')

    @abc.abstractmethod
    def  moverAHome(self):
        raise NotImplementedError('El metodo "moverAHome" no ha sido implementado')

    @abc.abstractmethod
    def  setHome(self, home):
        raise NotImplementedError('El metodo setHome" no ha sido implementado')
    

