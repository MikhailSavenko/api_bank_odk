import sqlite3

connection = sqlite3.connect('account_statement.db')

cursor = connection.cursor()

# amount - сумма платежа crAmount
cursor.execute('''
CREATE TABLE IF NOT EXISTS Payment(
               id INTEGER PRIMERY KEY,
               name TEXT,
               date TEXT,
               time TEXT,
               amount INTEGER,                                      
               account_number TEXT
)
''')



connection.commit()
connection.close()