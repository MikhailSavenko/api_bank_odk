import sqlalchemy as db

engine = db.create_engine('sqlite:///my_account_statement.db')

conn = engine.connect()
metadata = db.MetaData()

payment = db.Table('Payment', metadata,
                   db.Column('id', db.Integer, primary_key=True),
                   db.Column('name', db.Text),
                   db.Column('date', db.Text),
                   db.Column('time', db.Text),
                   db.Column('amount', db.Integer), 
                   db.Column('account_number', db.Text),
                  )


payment.create(engine)
conn.close()

