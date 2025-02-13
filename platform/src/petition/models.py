import dateparser
import enum


class Address:
    def __init__(self, street1, city, state, zipcode, street2=None):
        self.street1 = street1
        self.street2 = street2
        self.city = city
        self.state = state
        self.zipcode = zipcode

    @staticmethod
    def from_dict(data):
        return Address(
            data["street1"], data["city"], data["state"], data["zipcode"],
            street2=data.get("street2", None))

    def __repr__(self):
        return f"Address('{self.street1}', '{self.city}', '{self.state}', '{self.zipcode}', street2='{self.street2}')"

    def __str__(self):
        """Provide string representation"""

        if self.street2 is None or self.street2.strip() == "":
            return f"{self.street1}\n{self.city}, {self.state} {self.zipcode}"

        return f"{self.street1}\n{self.street2}\n{self.city}, {self.state} {self.zipcode}"


class Charge:
    def __init__(self, date, statute, grade, description, disposition):
        self.date = date
        self.statute = statute
        self.grade = grade
        self.description = description
        self.disposition = disposition

    def __repr__(self):
        return f"Charge('{repr(self.date)}', '{self.statute}', '{self.grade}' '{self.description}', '{self.disposition}')"

    @staticmethod
    def from_dict(data):
        cdate = data.get("date", None)

        if cdate is not None:
            cdate = dateparser.parse(cdate)

        return Charge(
            cdate, data.get("statute", ""), data.get("grade", ""),
            data.get("description", ""), data.get("disposition", ""))


class Petitioner:
    """Someone who wants a record expunged"""
    def __init__(self, name, aliases, dob, ssn, address):
        self.name = name

        self.aliases = aliases
        self.dob = dob
        self.ssn = ssn
        self.address = address

    @staticmethod
    def from_dict(data):
        adata = data.get("aliases", [])

        if type(adata) == str:
            aliases = [x.strip() for x in ",".split(adata)]
        if adata is None:
            aliases = []
        else:
            aliases = adata

        return Petitioner(
            data["name"], aliases,
            dateparser.parse(data["dob"]),
            data["ssn"], Address.from_dict(data["address"]))

    def __repr__(self):
        return f"Petitioner('{self.name}', '{str(self.aliases)}', {repr(self.dob)}, '{self.ssn}', {repr(self.address)})"


# Dockets


class Court(enum.Enum):
    CP = "Court of Common Pleas"
    MC = "Municipal Court"


class CaseType(enum.Enum):
    CR = "Criminal Case"
    SU = "Summary Offense"
    MD = "Miscellaneous Docket"


class DocketId:
    """
    Represent the ID for a Philadelphia County Court Docket
    """
    county_code = 51

    def __init__(self, court, case_type, number, year):
        """ Create a DocketId"""

        if not isinstance(court, Court):
            raise ValueError("Invalid Court")

        if not isinstance(case_type, CaseType):
            raise ValueError("Invalid CaseType")

        self.court = court
        self.case_type = case_type
        self.number = int(number)
        self.year = int(year)

    def __str__(self):
        """Provide string representation"""
        return f"{self.court.name}-{self.county_code:d}-{self.case_type.name}-{self.number:07d}-{self.year:d}"

    def __repr__(self):
        return f"DocketId({self.court}, {self.case_type}, {self.number:d}, {self.year:d})"

    def __eq__(self, other):

        return isinstance(other, DocketId) \
                and self.court == other.court \
                and self.county_code == other.county_code \
                and self.case_type == other.case_type \
                and self.number == other.number \
                and self.year == other.year

    @staticmethod
    def from_dict(data):
        """
        Produce a DocketId from it's representation in a dict.

        Args:
            data - a string representation as would appear in a dict,
                   such as "MC-51-CR-2100001-2019"
        Return:
            A DocketId
        """
        parts = data.split("-")
        court = Court[parts.pop(0)]
        county = parts.pop(0)
        case_type = CaseType[parts.pop(0)]
        number = parts.pop(0)
        year = parts.pop(0)

        docket = DocketId(court, case_type, number, year)
        docket.county_code = int(county)
        return docket


class PetitionRatio(enum.Enum):
    full = "Expungement"
    partial = "Partial Expungement"


class Petition:
    """The petition data"""
    def __init__(self, date, ratio, otn, arrest_date, complaint_date, judge):

        if not isinstance(ratio, PetitionRatio):
            raise ValueError("Invalid PetitionRatio")

        self.date = date
        self.ratio = ratio
        self.otn = otn
        self.arrest_date = arrest_date
        self.complaint_date = complaint_date
        self.judge = judge

    @staticmethod
    def from_dict(data):
        """Produce a petition from its dict representation"""
        arrest_date = data.get("arrest_date", None)
        if arrest_date is not None:
            arrest_date = dateparser.parse(arrest_date)

        complaint_date = data.get("complaint_date", None)
        if complaint_date is not None:
            complaint_date = dateparser.parse(complaint_date)

        return Petition(
            dateparser.parse(data["date"]),
            PetitionRatio[data["ratio"]],
            data["otn"], 
            arrest_date, 
            complaint_date, 
            data["judge"]
        )

    def __repr__(self):
        return f"Petition({repr(self.date)}, {self.ratio}, {self.otn}, {self.arrest_date}, {self.complaint_date}, {self.judge})"


class Fines:
    """Court ordered payments"""
    def __init__(self, total, paid):
        self.total = total
        self.paid = paid

    @staticmethod
    def from_dict(data):
        return Fines(
            data.get("total"),
            data.get("paid"))

    def to_dict(self):
        return {"total": self.total, "paid": self.paid}
