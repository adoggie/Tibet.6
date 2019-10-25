#coding:utf-8
import config

dbnames = [
    'Ctp_Bar_60','Ctp_Bar_30','Ctp_Bar_15',
'Ctp_Bar_5','Ctp_Bar_1',
           ]

for _ in dbnames:
    config.db_conn.drop_database(_)