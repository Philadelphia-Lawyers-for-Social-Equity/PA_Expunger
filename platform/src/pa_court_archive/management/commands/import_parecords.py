import logging
import os
import pymysql
import sys

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError


import pa_court_archive.models

host = 'psle-db-mysql-nyc1-87996-do-user-5085894-0.a.db.ondigitalocean.com'
port = 25060
database = 'defaultdb'

batch_size = 5000

# copy your cert to platform/src/mysql_cert.pem
ssl_ca = os.path.join(os.environ.get('APPDIR'), 'mysql_cert.pem')

logger = logging.getLogger("django")
logger.addHandler = logging.StreamHandler()
logger.setLevel(os.environ.get("LOGLEVEL", "INFO"))


class Command(BaseCommand):
    def handle(self, *args, **options):

        cnx = get_connection()
        cursor = cnx.cursor()

        for row in retrieve_all_rows(cursor):
            make_parecord(row)

        cursor.fetchall()
        cursor.close()
        cnx.close()


def get_connection():
    """Get the MySQl connection."""

    connection_args = {
        "user": os.environ.get("MYSQL_USER"),
        "password": os.environ.get("MYSQL_PASS"),
        "host": host,
        "port": port,
        "database": database,
        "ssl_ca": ssl_ca,
        "ssl_verify_cert": True
    }

    logger.debug("connection arguments: %s", connection_args)

    try:
        cnx = pymysql.connect(**connection_args)
    except pymysql.Error as err:
        logger.error("Failed to connect to %s, %s", host, str(err))
        sys.exit(1)

    return cnx


def make_parecord(row):
    """Produce the PaRecord from the source database row."""
    try:
        pa_court_archive.models.PaRecord.objects.create(
            external_mysql_id=row[0],
            county_name=row[1],
            docket_number=row[2],
            filed_date=row[3],
            last_name=row[4],
            first_name=row[5],
            middle_name=row[6],
            city=row[7],
            state=row[8],
            zipcode=row[9],
            offense_tracking_number=row[10],
            gender_code=row[11],
            race_code=row[12],
            birthdate=row[13],
            originating_offense_sequence=row[14],
            statute_type=row[15],
            statute_title=row[16],
            statute_section=row[17],
            statute_subsection=row[18],
            inchoate_statute_title=row[19],
            inchoate_statute_section=row[20],
            inchoate_statute_subsection=row[21],
            offense_disposition=row[22],
            offense_date=row[23],
            offense_disposition_date=row[24],
            offense_description=row[25],
            case_disposition=row[26],
            case_disposition_date=row[27],
            offense_grade=row[28],
            disposing_judge=row[29]
            )
    except IntegrityError:
        logger.warn("already had %d, skipping" % row[0])


def retrieve_all_rows(cursor):
    """Generate all rows from the MySQL database cursor."""
    query = "SELECT count(*) FROM case_data"
    cursor.execute(query)
    total = cursor.fetchone()[0]
    count = 0

    while count < total:

        # pymysql library goofs if you specify the correct %d label
        query = "SELECT * FROM case_data ORDER BY id LIMIT %s offset %s"
        cursor.execute(query, (batch_size, count))

        for i in range(cursor.rowcount):
            row = cursor.fetchone()
            count += 1

            if row is None:
                logger.warn("expected %d results, but finished with %d",
                            cursor.rowcount, count)
                return

            yield row
        logger.debug("retrieved %d rows so far", count)

    logger.debug("finished retrieving %d rows", count)
