import sqlalchemy as db

engine = db.create_engine('sqlite:///my_account_statement.db')
conn = engine.connect()


metadata = db.MetaData()
payment = db.Table('Payment', metadata, autoload_with=engine)

insertion_query = payment.insert().values([
    {'name': 'Быков Василий Геннадьевич', 'date': '2018-06-15', 'time': '15:39:08.885+03:00', 'amount': '1000.00', 'account_number': '144945576'},
    {'name': 'Курёзин Петр Михайлович', 'date': '2018-06-15', 'time': '12:39:08.885+03:00', 'amount': '2000.00', 'account_number': '144942346'}
])

conn.execute(insertion_query)

conn.commit()
