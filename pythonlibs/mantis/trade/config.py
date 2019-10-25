# coding: utf-8

from mantis.trade.types import ProductClass

DatabaseDefs= {
    ProductClass.Future: {
        'bars':'Ctp_Bar_{scale}',
        'ticks':'Ctp_Tick'
    }
}



__all__ = (DatabaseDefs,)