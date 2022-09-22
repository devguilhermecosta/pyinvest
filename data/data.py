try:
    import sys
    import os
    
    sys.path.append(
        os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                '../modulos'
            )
        )
    )
except Exception as error:
    print(f'{error}')
    
    
from os import renames
import sqlite3 as sq
from .exceptions import AtivoJaCadastradoError, AtivoNaoCadastradoError, SaldoInsuficienteError
from .exceptions import QuantidadeInsuficienteError
from .metodos_sql import MetodosSqlRF, MetodosSqlRV
from ativos.fiis import Fiis
from ativos.acoes import Acao
from ativos.renda_fixa import RendaFixa
from ativos.tesouro_direto import TesouroDireto
from ativos.reserva_emergencia import ReservaEmergencia


class RepositorioRendaVariavel(MetodosSqlRV):
    def cadastrar_ativo(self, ativo: Acao | Fiis) -> int | None:
        """       
        Param: ativo: Object -> Acao | Fiis
        
        Raise: AtivoJaCadastradoError
              
        return 0 or None
        """
        if self._existe_ativo(ativo.codigo):
            raise AtivoJaCadastradoError('Ativo já cadastrado.')
        else:
            self.acao_sql_cadastrar_ativo(ativo)
            return 0
    
    def comprar(self, ativo: Fiis | Acao, qtde: int, pu: float) -> int | None:
        """
        Param: ativo: Object -> Acao | Fiis
        Param: qtde: int
        Param: pu: float
        
        Raise: AtivoNaoCadastradoError
        
        return 0 or None
        """      
        if not self._existe_ativo(ativo.codigo):
            raise AtivoNaoCadastradoError('Ativo não cadastrado')
        else:
            self.acao_aql_comprar_ativo(ativo, qtde, pu)
            return 0        
            
    def vender(self, ativo: Acao | Fiis, qtde: int, pu: float) -> int | None:
        """
        Param: ativo: Object -> Acao | Fiis
        Param: qtde: int
        Param: pu: float
        
        Raise: AtivoNaoCadastradoError, QuantidadeInsuficienteError
        
        return 0 or None
        """
        if not self._existe_ativo(ativo.codigo):
            raise AtivoNaoCadastradoError('Ativo não cadastrado')
        elif not self._quantidade_suficiente(ativo):
            raise QuantidadeInsuficienteError('Quantidade insuficiente para venda') 
        else:
            self.acao_sql_vender(ativo, qtde, pu)
            return 0
      
    def deletar(self, ativo: Acao | Fiis) -> int:
        """
        Param: ativo: Object -> Acao | Fiis
        
        Raise: AtivoNaoCadastradoError
        
        return 0 or None
        """
        if not self._existe_ativo(ativo.codigo):
            raise AtivoNaoCadastradoError('Ativo não cadastrado')
        else:
            self.acao_sql_deletar_ativo(ativo)
            return 0

    def alterar_dados(self, ativo: Acao | Fiis, nome: str, codigo: str) -> int | None:
        """       
        Param: ativo: Object -> Acao | Fiis
        Param: nome: str
        Param: codigo: str
        
        Raise: AtivoNaoCadastradoError  
           
        return 0 or None
        """
        if not self._existe_ativo(ativo.codigo):
            raise AtivoNaoCadastradoError('Ativo não cadastrado')
        else:
            self.acao_sql_alterar_dados(ativo, nome, codigo)
            return 0

    def acertar_quantidade(self, ativo: Acao | Fiis, qtde: int) -> int | None:
        """
        Param: ativo: Object -> Acao | Fiis
        Param: qtde: int
        
        Raise: AtivoNaoCadastradoError
        
        return 0 or None
        """
        if not self._existe_ativo(ativo.codigo):
            raise AtivoNaoCadastradoError('Ativo não cadastrado')
        else:
            self.acao_sql_acertar_quantidade(ativo, qtde)
            return 0

    def acertar_preco_unit(self, ativo: Acao | Fiis, pu: float) -> int | None:
        """        
        Param: ativo: Object -> Acao | Fiis
        Param: pu: float
        
        Raise: AtivoNaoCadastradoError
        
        return 0 or None
        """
        if not self._existe_ativo(ativo.codigo):
            raise AtivoNaoCadastradoError('Ativo não cadastrado')
        else:
            self.acao_sql_acertar_preco_unit(ativo, pu)            
            return 0
    

class RepositorioRendaFixa(MetodosSqlRF):      
    def cadastrar_ativo(self, ativo: RendaFixa | TesouroDireto | ReservaEmergencia) -> int | None:
        """
        Param: ativo: Object -> RendaFixa | TesouroDireto | ReservaEmergencia  
        
        Raise: AtivoJaCadastradoError   
        
        return 0 or None
        """        
        if self._existe(ativo):
            raise AtivoJaCadastradoError('Ativo já cadastrado')
        else:
            self.acao_sql_insert(ativo)
        return 0
    
    def comprar(self,
                ativo: RendaFixa | TesouroDireto | ReservaEmergencia,
                qtde: int,
                valor: float) -> int:
        """
        Param: ativo: Object -> RendaFixa | TesouroDireto | ReservaEmergencia
        Param: qtde: int
        Param: valor: float
        
        Raise: AtivoNaoCadastradoError
        
        return int -> -1 se não comprado ou 0 se comprado
        """
        resultado: int = -1
        if not self._existe(ativo):
            raise AtivoNaoCadastradoError('Ativo não cadastrado')
        else:
            self.acao_sql_comprar(ativo, qtde, valor)
            resultado = 0
        return resultado
    
    def resgatar(self,
                 ativo: RendaFixa | TesouroDireto | ReservaEmergencia,
                 qtde: int,
                 valor: float) -> int | None:
        """
        Param: ativo: Object -> RendaFixa | TesouroDireto | ReservaEmergencia
        Param: qtde: int
        Param: valor: float
        
        Raise: AtivoNaoCadastradoError, SaldoInsuficienteError
        
        return 0 or None
        """
        if not self._existe(ativo):
            raise AtivoNaoCadastradoError('Ativo não cadastrado')
        elif self.acao_sql_get_saldo(ativo) <= 0:
            raise SaldoInsuficienteError('Saldo insuficiente para resgate')
        else:
            self.acao_sql_alterar_saldo_apos_resgate(ativo, qtde, valor)
            return 0
        
    def alterar_dados_ativo(self,
                             ativo: RendaFixa | TesouroDireto | ReservaEmergencia,
                             nome: str,
                             data_resgate: str,
                             data_vencimento: str,
                             rentabilidade: str) -> int | None:
        """
        Param: ativo: Object -> RendaFixa | TesouroDireto | ReservaEmergencia
        Param: nome: str
        Param: data_resgate: str
        Param: data_vencimento: str
        Param: rentabilidade: str
        
        Raise: AtivoNaoCadastradoError
        
        return 0 or None
        """
        if not self._existe(ativo):
            raise AtivoNaoCadastradoError('Ativo não cadastrado')
        else:
            self.acao_sql_alterar_dados(ativo, nome, data_resgate, data_vencimento, rentabilidade)           
            return 0
        
    def acertar_valor_aplicado(self,
                               ativo: RendaFixa | TesouroDireto | ReservaEmergencia,
                               valor: float) -> int | None:
        """
        Param: ativo: Object -> RendaFixa | TesouroDireto | ReservaEmergencia
        Param: valor: float
        
        Raise: AtivoNaoCadastradoError
        
        return 0 or None
        """
        if not self._existe(ativo):
            raise AtivoNaoCadastradoError('Ativo não cadastrado')
        else:
            self.acao_sql_acertar_valor_aplicado(ativo, valor)
            return 0
        
    def deletar_ativo(self, ativo: RendaFixa | TesouroDireto | ReservaEmergencia) -> int | None:
        """
        Param: ativo: Object -> RendaFixa | TesouroDireto | ReservaEmergencia
            
        Raise: AtivoNaoCadastradoError
        
        return 0 or None
        """
        if not self._existe(ativo):
            raise AtivoNaoCadastradoError('Ativo não cadastrado')
        else:
            self.acao_sql_deletar_ativo(ativo)
            return 0
