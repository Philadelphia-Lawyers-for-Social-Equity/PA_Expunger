from datetime import date
import logging
import os
import pymysql
import re
import sys

from django.db import connection as django_connection

from django.core.management.base import BaseCommand
import pa_court_archive.models as m

host = 'psle-db-mysql-nyc1-87996-do-user-5085894-0.a.db.ondigitalocean.com'
port = 25060
database = 'defaultdb'

batch_size = 5000

# copy your cert to platform/src/mysql_cert.pem
ssl_ca = os.path.join(os.environ.get('APPDIR'), 'mysql_cert.pem')

logger = logging.getLogger("django")
logger.addHandler = logging.StreamHandler()
logger.setLevel(os.environ.get("DJANGO_LOG_LEVEL", "INFO"))


reverse_race_code = {x.label: x.name for x in m.RaceCode}


class Command(BaseCommand):
    def handle(self, *args, **options):

        cnx = get_connection()
        cursor = cnx.cursor(pymysql.cursors.DictCursor)

        with ArchiveQueue(batch_size) as aq:

            for row in retrieve_all_rows(cursor):
                aq.handle_row(row)

        # Clear the connection
        cursor.fetchall()
        cursor.close()
        cnx.close()


class ArchiveQueue:
    """Provide queueing / batching on django inserts."""

    def __init__(self, batch_size):
        self.total = 0
        self.batch_size = batch_size
        self._initialize_queues()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.clear_queues()

    def _initialize_queues(self):
        self.batch_count = 0

        self.arrestee_inserts = []
        self.arrestee_params = []

        self.case_inserts = []
        self.case_params = []

        self.arrestee_case_inserts = []
        self.arrestee_case_params = []

        self.docket_params = dict()

        self.offense_inserts = []
        self.offense_params = []

    def queue_arrestee(self, row):
        """Queue SQL values for an Arrestee based on originating db row."""

        if row["LastName"] is None:
            return

        if row["GenderCode"] is None:
            gender_code = None
        else:
            try:
                gender_code = m.GenderCode(row["GenderCode"][0])
            except ValueError:
                logger.warning("Invalid gender code: %s", row["GenderCode"])
                gender_code = None

        if row["RaceCode"] is None:
            race_code = None
        else:
            try:
                race_code = reverse_race_code[row["RaceCode"]]
            except ValueError:
                logger.warning("Invalid race code: %s", row["RowCode"])
                race_code = None

        self.arrestee_inserts.append("(%s, %s, %s, %s, %s, %s)")
        self.arrestee_params += [
            row["FirstName"], row["MiddleName"], row["LastName"],
            gender_code, race_code, parse_date_string(row["BirthDate"])]

    def queue_case(self, row):
        """Queue SQL values for a Case based on originating db row."""

        if row["OffenseTrackingNumber"] is None:
            return

        self.case_inserts.append("(%s, %s, %s, %s, %s, %s, %s, %s, %s)")
        self.case_params += [
            row["OffenseTrackingNumber"],
            parse_date_string(row["FiledDate"]),
            row["City"],
            row["CountyName"],
            row["State"],
            fix_zip_code(row["ZipCode"]),
            row["CaseDisposition"],
            parse_date_string(row["CaseDispositionDate"]),
            row["DisposingJudge"]
        ]

    def queue_arrestee_case(self, row):
        """
        Queue SQL values to link Arrestee, Case based on originating db row.
        """
        if row["LastName"] is None:
            return

        if row["OffenseTrackingNumber"] is None:
            return

        birth_date = parse_date_string(row["BirthDate"])

        arrestee_select = \
            "(SELECT id FROM pa_court_archive_arrestee WHERE %s AND %s AND %s AND %s)" % (
                self.value_selector("first_name", row["FirstName"]),
                self.value_selector("middle_name", row["MiddleName"]),
                self.value_selector("last_name", row["LastName"]),
                self.value_selector("birth_date", birth_date))

        case_select = "(SELECT id FROM pa_court_archive_case WHERE otn = %s)"

        self.arrestee_case_inserts.append(
            "(%s, %s)" % (arrestee_select, case_select))

        for param in [row["FirstName"], row["MiddleName"], row["LastName"], birth_date]:
            if param is not None:
                self.arrestee_case_params.append(param)

        self.arrestee_case_params.append(row["OffenseTrackingNumber"])

    def queue_docket(self, row):
        """Queue a docket from the row."""
        if row["DocketNumber"] is None:
            return

        docket_number = row["DocketNumber"]
        otn = row["OffenseTrackingNumber"]

        if docket_number not in self.docket_params:
            self.docket_params[docket_number] = otn

        elif self.docket_params[docket_number] is None:
            self.docket_params[docket_number] = otn

    def queue_offense(self, row):
        """Queue the offense from the source database row."""

        if row["OffenseDescription"] is None:
            return

        if row["DocketNumber"] is None:
            return

        if row["StatuteType"] is None:
            statute_type = None
        else:
            try:
                statute_type = m.StatuteType(row["StatuteType"][0])
            except ValueError:
                logger.warn("Invalid StatuteType %s", row["StatuteType"])
                statute_type = None

        self.offense_inserts.append(
            "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "
            "(SELECT id FROM pa_court_archive_docket WHERE docket_number = %s))"
        )

        for x in [
            row["OffenseDisposition"],
            parse_date_string(row["OffenseDate"]),
            parse_date_string(row["OffenseDispositionDate"]),
            row["OffenseDescription"],
            row["OriginatingOffenseSequence"],
            statute_type,
            row["StatuteTitle"],
            row["StatuteSection"],
            row["StatuteSubSection"],
            row["InchoateStatuteTitle"],
            row["InchoateStatuteSection"],
            row["InchoateStatuteSubSection"],
            row["OffenseGrade"],
            row["DocketNumber"]
        ]:
            self.offense_params.append(x)

    def clear_queues(self):
        """Clear queued items."""

        self.clear_arrestee_queue()
        self.clear_case_queue()
        self.clear_arrestee_case_queue()
        self.clear_docket_queue()
        self.clear_offense_queue()

        logger.debug("Queue cleared, total %d rows so far.", self.total)
        self._initialize_queues()

    def clear_arrestee_queue(self):
        if len(self.arrestee_inserts) < 1:
            return

        query = """INSERT INTO pa_court_archive_arrestee
            (first_name, middle_name, last_name, gender_code, race_code, birth_date)
            VALUES %s
            ON CONFLICT DO NOTHING""" % (",".join(self.arrestee_inserts))

        with django_connection.cursor() as cursor:
            cursor.execute(query, self.arrestee_params)

    def clear_case_queue(self):
        if len(self.case_inserts) < 1:
            return

        query = """INSERT INTO pa_court_archive_case
            (otn, filed_date, city, county, state, zip, disposition, disposition_date, disposing_judge)
            VALUES %s
            ON CONFLICT DO NOTHING""" % (",".join(self.case_inserts))

        with django_connection.cursor() as cursor:
            cursor.execute(query, self.case_params)

    def clear_arrestee_case_queue(self):
        if len(self.arrestee_case_inserts) < 1:
            return

        query = """INSERT INTO pa_court_archive_case_arrestees
            (arrestee_id, case_id)
            VALUES %s
            ON CONFLICT DO NOTHING""" % (",".join(self.arrestee_case_inserts))

        with django_connection.cursor() as cursor:
            cursor.execute(query, self.arrestee_case_params)

    def clear_docket_queue(self):
        if len(self.docket_params) < 1:
            return

        inserts = []
        params = []

        for docket_number, otn in self.docket_params.items():

            if otn is None:
                inserts.append("(%s, NULL)")
                params.append(docket_number)
            else:
                inserts.append("(%s, (SELECT id FROM pa_court_archive_case WHERE otn = %s))")
                params.append(docket_number)
                params.append(otn)

        query = """INSERT INTO pa_court_archive_docket
            (docket_number, case_id)
            VALUES %s
            ON CONFLICT DO NOTHING
            """ % (",".join(inserts))

        with django_connection.cursor() as cursor:
            cursor.execute(query, params)

    def clear_offense_queue(self):
        if len(self.offense_inserts) < 1:
            return

        query = """INSERT INTO pa_court_archive_offense
        (disposition, date, disposition_date, description,
         originating_sequence, statute_type, statute_title, statute_section,
         statute_subsection, inchoate_statute_title, inchoate_statute_section,
         inchoate_statute_subsection, grade, docket_id)
        VALUES %s
        ON CONFLICT DO NOTHING
        """ % (",".join(self.offense_inserts))

        with django_connection.cursor() as cursor:
            cursor.execute(query, self.offense_params)

    def handle_row(self, row):
        """Bring in a new row from the originating database."""
        self.total += 1
        self.batch_count += 1

        self.queue_arrestee(row)
        self.queue_case(row)
        self.queue_arrestee_case(row)
        self.queue_docket(row)
        self.queue_offense(row)

        if self.batch_count >= self.batch_size:
            self.clear_queues()

    @staticmethod
    def value_selector(name, val):
        """Produce "name = %s" or "name IS NULL" string for a sql selector."""

        if val is None:
            return "%s IS NULL" % name

        return f"{name} = %s"


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


def parse_date_string(ds):
    """Clean up a date string, or reject it."""

    if ds is None:
        return

    ds = ds[:10]
    match = re.match(r"\d{4}-\d{2}-\d{2}", ds)

    if match is None:
        return

    year, month, day = [int(x) for x in ds.split("-")]
    return date(year, month, day)


def fix_zip_code(zc):
    """Clean up a zip code, or reject it."""

    if zc is None:
        return

    if type(zc) is float or type(zc) is int:
        zc = str(int(zc))

    if len(zc) < 4 or len(zc) > 10:
        logger.warn("Invalid zipcode %s", zc)
        return

    if len(zc) == 4:
        return "0%s" % zc

    if len(zc) == 5:
        return zc

    if "-" in zc:
        return zc

    return "%s-%s" % (zc[:5], zc[5:])


def retrieve_all_rows(cursor):
    """Generate all rows from the MySQL database cursor."""
    query = "SELECT count(*) FROM case_data"
    cursor.execute(query)
    total = cursor.fetchone()["count(*)"]
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
