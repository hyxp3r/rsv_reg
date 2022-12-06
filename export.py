import pandas as pd
import psycopg2

conn = psycopg2.connect(
                        dbname = 'rsv_prod',
                        user = 'ermakov',
                        password = 'hyxper1337W',
                        host = '127.0.0.1'
                        )


df_1 = pd.read_sql('select * from day_1', conn)
df_2 = pd.read_sql('select * from day_1', conn)

df_1.to_excel('day_1.xlsx')
df_2.to_excel('day_2.xlsx')