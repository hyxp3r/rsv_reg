import psycopg2
import os

conn = psycopg2.connect(
                        dbname = os.environ.get("dbname"),
                        user = os.environ.get("user"),
                        password = os.environ.get("password"),
                        host = os.environ.get("host")
                        )

cursor = conn.cursor()

count_sprav = {

    'day_1':
{
    'Веревочный парк': 33,
    'Тур в пещеры "Царская тропа"': 18,
    'Рафтинг': 45
},
    'day_2':
{
    'Веревочный парк': 33,
    'Тур в пещеры "Царская тропа"': 45,
    'Рафтинг': 18

}
}

def count(data):

    for dateTime in count_sprav:
        if dateTime == data['typeDate']:
            for k, v in count_sprav[dateTime].items():
                if k == data['typeApplication']:
                    itog = v
   

    cursor.execute(f"select count(id) from {data['typeDate']} where application = '{data['typeApplication']}'")
    records = cursor.fetchone()[0]
     
    text_1 = ''
    text_2 = ''

    if (data['timeDate'] == 'Дневное' and records >= itog) or (data['timeDate'] == 'Вечернее' and records >= 12):
 
        cursor.execute(f'''select application, fact - count(id) from day_1 where 
        time = '{data['timeDate']}' group by application, fact order by application''')
        records_day_1 = cursor.fetchall()
        cursor.execute(f'''select application, fact - count(id) from day_2 where 
        time = '{data['timeDate']}' group by application, fact order by application''')
        records_day_2 = cursor.fetchall()

        for record in records_day_1:
          
            text_1 = text_1 + record[0] + ':' + ' ' + '<b>' + str(record[1]) + '</b>'+ '\n'

        for record in records_day_2:
            
            text_2 = text_2 + record[0] + ':' + ' ' + '<b>' + str(record[1]) + '</b>'+ '\n'

    return text_1, text_2

def day_write_offline(data):

    cursor.execute(f'''INSERT INTO {data['typeDate']}  (lastname, name, application, telegram_id, fact, time) 
        VALUES (%s, %s, %s, %s, %s, %s);''',
        (data['lastname'], data['name'], data['typeApplication'], data['id'], data['fact'], data['timeDate']))
    conn.commit()

def day_write_online(data):

    cursor.execute(f'''INSERT INTO {data['typeDate']} (lastname, name, application, telegram_id, question, fact, time) 
    VALUES (%s, %s, %s, %s, %s, %s, %s);''',
    (data['lastname'], data['name'], data['typeApplication'], data['id'], str(data['question']), data['fact'],
    data['timeDate']))
    conn.commit()
    

def checkID(data):

    cursor.execute(f'''select CONCAT(lastname, ' ' ,name), application from {data['typeDate']} where 
        {data['id']} = telegram_id and time = '{data['timeDate']}' ''')
    records = cursor.fetchall()

    return(records)




        
