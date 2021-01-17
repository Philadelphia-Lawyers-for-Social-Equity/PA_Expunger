from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
import mysql.connector
import os
import expunger.models
import logging


host = 'psle-db-mysql-nyc1-87996-do-user-5085894-0.a.db.ondigitalocean.com'
port = '25060'
database = 'defaultdb'
ssl_ca = '/path/to/ca-certificate.crt'  # put this secret somewhere

logger = logging.Logger(__name__)
logger.addHandler = logging.StreamHandler()
logger.setLevel(os.environ.get("LOGLEVEL", "WARNING"))


class Command(BaseCommand):
    def handle(self, *args, **options):
        # establish connection with MySQL
        try:
            user = os.environ.get("MYSQL_USER")
            pwd = os.environ.get("MYSQL_PWD")
            cnx = mysql.connector.connect(
                user=user,
                password=pwd,
                host=host,
                port=port,
                database=database,
                ssl_ca=ssl_ca,
                ssl_verify_cert=True)
            cursor = cnx.cursor()
        except mysql.connector.Error as err:
            logger.error("Failed to connect to %s, %s", host, str(err))

        batch_size = 5000
        query = "SELECT * FROM case_data ORDER BY id"
        cursor.execute(query)
        input_batch = cursor.fetchmany(size=batch_size)
        count = 0

        while len(input_batch) > 0 and count < 2:
            for result in input_batch:
                try:
                    expunger.models.DocketMetadata.objects.create(
                        external_mysql_id=result[0],
                        county_name=result[1],
                        docket_number=result[2],
                        filed_date=result[3],
                        last_name=result[4],
                        first_name=result[5],
                        middle_name=result[6],
                        city=result[7],
                        state=result[8],
                        zipcode=result[9],
                        offense_tracking_number=result[10],
                        gender_code=result[11],
                        race_code=result[12],
                        birthdate=result[13],
                        originating_offense_sequence=result[14],
                        statute_type=result[15],
                        statute_title=result[16],
                        statute_section=result[17],
                        statute_subsection=result[18],
                        inchoate_statute_title=result[19],
                        inchoate_statute_section=result[20],
                        inchoate_statute_subsection=result[21],
                        offense_disposition=result[22],
                        offense_date=result[23],
                        offense_disposition_date=result[24],
                        offense_description=result[25],
                        case_disposition=result[26],
                        case_disposition_date=result[27],
                        offense_grade=result[28],
                        disposing_judge=result[29]
                        )
                except IntegrityError as e:
                    print("already had %d, skipping" % result[0])
                    print("IntegrityError: ", e)
                except Exception as e:
                    print("ERROR! Failed to create object in postgres: ", e)

            input_batch = cursor.fetchmany(size=batch_size)
            count = count + 1

        cursor.fetchall()
        cursor.close()
        cnx.close()
