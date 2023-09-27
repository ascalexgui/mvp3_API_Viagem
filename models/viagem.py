from sqlalchemy import Column, String, Integer, DateTime, Float, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Union

from models import Base


class Viagem(Base):

     __tablename__ = 'viagem'

    # O nome de uma coluna também pode ter no banco um nome diferente
    # como é apresentado aqui no caso da Produto.id que no banco será 
    # prod_catalog.pk_prod, o sufixo pk está sendo utilizado para 
    # indicar que é uma chave primária

    # Adaptando para o meu negócio
    # O nome de uma coluna também pode ter no banco um nome diferente
    # como é apresentado aqui no caso da Viagem.id que no banco será 
    # viagem.pk_viagem, o sufixo pk está sendo utilizado para 
    # indicar que é uma chave primária

     id = Column("pk_viagem", Integer, primary_key=True)

    # Supondo que os atributos seguintes já estejam em conformidade
    # com o menemônico adotado pela empresa, então não há necessidade
    # de fazer a definição de um "nome" de coluna diferente.

     cidade = Column(String(140)) 
     descricao = Column(String(2000))
     qtd_dias = Column(Integer) 
     ano = Column(Integer)
     mes = Column(String(20))


     def __init__(self, cidade, descricao, qtd_dias, ano, mes):
        """
        Cria uma viagem

        Arguments:
            cidade: local da viagem ( estamos restringindo apenas para cidades brasileiras)
            descricao: descrição da viagem
            qtd_dias: duração da viagem em dias
            ano: qual o ano da viagem
            mes: qual o mês da viagem ( janeiro, fevereiro, março, ...)
        """
        self.cidade = cidade
        self.descricao = descricao
        self.qtd_dias = qtd_dias
        self.ano = ano
        self.mes = mes
       
      
     def to_dict(self):
        """
        Retorna a representação em dicionário do Objeto Produto.
        """
        return{
            "id": self.id,
            "cidade": self.cidade,
            "descricao": self.descricao,
            "qtd_dias": self.qtd_dias,
            "ano": self.ano,
            "mes": self.mes,
        }

     def __repr__(self):
        """
        Retorna uma representação da Viagem em forma de texto.
        """
        return f"Product(id={self.id}, cidade='{self.cidade}', descricao={self.descricao}, qtd_dias={self.qtd_dias},ano='{self.ano}',mes='{self.mes}')"

