from django.core.management.base import BaseCommand, CommandError
import mysql.connector, os
# from expunger.models import DocketMetadata

class Command(BaseCommand):
    def handle(self, *args, **options):
        print("hello world")

        # (figure out where we were)

        # establish connection with MySQL
        user = os.environ.get("MYSQL_USER")
        pwd = os.environ.get("MYSQL_PWD")
        cnx = mysql.connector.connect(user=user, password=pwd,
                              host='psle-db-mysql-nyc1-87996-do-user-5085894-0.a.db.ondigitalocean.com',
                              port='25060',
                              database='defaultdb',
                              ssl_ca='/Users/apple/.ssh/plse',
                              ssl_verify_cert=True)
        cnx.close()

        # fetch chunk of data from MySQL

        # transform data into django model structure

        # save to django database