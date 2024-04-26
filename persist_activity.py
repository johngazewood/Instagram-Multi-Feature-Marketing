import peewee
import config

marketing_db = peewee.SqliteDatabase(config.DATABASE_FILE_NAME)

class SavedComment(peewee.Model):
    text = peewee.CharField()
    hyperlink = peewee.CharField()
    class Meta:
        database = marketing_db
    def __str__(self):
        return f'{self.index} {self.hyperlink} : {self.text}'



marketing_db.connect()
# execute sql just to verify connection. if connection has not been established, execute_sql() will throw peewee.OperationalError
marketing_db.execute_sql('SELECT 1')
marketing_db.create_tables([SavedComment])