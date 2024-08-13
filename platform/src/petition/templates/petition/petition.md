{{ organization.name }}\
BY: {{ attorney.user.first_name }} {{ attorney.user.last_name }}\
Identification No.: {{ attorney.bar }}\
\
{{r organization.formattedAddress }}\
{{ organization.phone }}\
Attorney for {{ petitioner.name }}

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

COMMONWEALTH OF PENNSYLVANIA

vs.

{{ petitioner.name }}

{{r petitioner.formattedAddress }}

:

:

:

:

:

:

:

:

COURT OF COMMON PLEAS

CRIMINAL TRIAL DIVISION

PHILADELPHIA COUNTY

{% for docket in dockets -%}

{{ docket }}

{% endfor -%}

OTN# {{ petition.otn }}

**\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_**

**ORDER**

AND NOW, this \_\_\_\_ day of \_\_\_\_\_\_\_\_\_\_\_, 20\_\_, after
consideration of the Petition for {{ petition.ratio.value }} Pursuant to
Pa.R.Crim.P. 790 presented by {{ petitioner.name }}, it is ORDERED that
the Petition/Motion is \_\_\_\_\_\_\_\_\_\_\_\_\_.

All criminal justice agencies upon which this order is served shall
expunge all criminal history record information from defendant's arrest
record pertaining to the charges below. Criminal history record
information includes information collected by criminal justice agencies
concerning this individual and arising from the initiation of these
criminal proceedings including but not limited to all fingerprints,
photographs, identifiable descriptions, dates and notations of arrests,
indictments, informations or other formal criminal charges, any
dispositions arising from the above-captioned proceedings, and all
electronic or digital records regarding any of the foregoing.

The Pennsylvania State Police shall request the Federal Bureau of
Investigation to return to them all records pertaining to said
arrest(s), which shall be destroyed by said agency upon their receipt of
same.

The information required under Pa.R.Crim.P. 790 appears on the attached
page(s) which is hereby incorporated into this ORDER by reference.

BY THE COURT:

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

> J.

Pursuant to Pa.R.Crim.P. 790, the following information is provided:

> **• Petitioner Name:** {{ petitioner.name }}
>
> **• Alias(es):** {{ petitioner.aliases\|comma_join }}
>
> **• Petitioner's Address:**
>
> {{r petitioner.formattedAddress }}
>
> **• Petitioner's Date of Birth:** {{ petitioner.dob\|date }}
>
> **• Petitioner's Social Security Number:** {{ petitioner.ssn }}
>
> **• Name and address of the judge who accepted the guilty plea or
> heard the case:**
>
> Judge {{ petition.judge }}
>
> Criminal Justice Center\
> 1301 Filbert Street\
> Philadelphia, PA 19107
>
> **• Docket Number:**

{%tr for docket in dockets %}

{{ docket }}

{%tr endfor %}

> **• Offense Tracking Number (OTN):** {{ petition.otn }}
>
> **• The specific charges, as they appear on the charging document, to
> be expunged and applicable dispositions:**
>
> **Code Section**
>
> **Statute Description**
>
> **Grade**
>
> **Disp Date**
>
> **Disposition**
>
> {%tr for charge in charges %}
>
> {{ charge.statute }}
>
> {{ charge.description }}
>
> {{ charge.grade }}
>
> {{ charge.date\|date }}
>
> {{ charge.disposition }}
>
> {%tr endfor %}

{%p if fines.total and fines.paid %}

> **• If the sentence includes a fine, costs, or restitution, whether
> the amount due has been paid:**
>
> The Petitioner's sentence includes fines, costs and/or restitution in
> the amount of \${{ fines.total }} and \${{ fines.paid }} has been paid
> off/adjusted.

{%p endif %}

{% if fines.total and fines.paid %} **11.** {% else %} **10.** {% endif
%} **The reason for expungement:**

> As a result of these arrests and subsequent photographing and
> fingerprinting, Petitioner has been caused to suffer embarrassment and
> irreparable harm and loss of job opportunities. Expungement is proper
> under 18 Pa.C.S. 9122 as the charges to be expunged were {{
> dispositions }}.

{% if fines.total and fines.paid %} **12.** {% else %} **11.** {% endif
%} **The criminal justice agencies upon which certified copies of the
order shall be served:**

1\. The Clerk of Courts of Philadelphia County, Criminal Division

2\. The Philadelphia County District Attorney\`s Office

3\. The Pennsylvania State Police, Central Records

4\. A.O.P.C. Expungement Unit

5\. Philadelphia Police Dept

6\. Philadelphia County Department of Adult Probation and Parole

{{ organization.name }}\
BY: {{ attorney.user.first_name }} {{ attorney.user.last_name }}\
Identification No.: {{ attorney.bar }}\
\
{{r organization.formattedAddress }}\
{{ organization.phone }}\
Attorney for {{ petitioner.name }}

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

COMMONWEALTH OF PENNSYLVANIA

vs.

{{ petitioner.name }}

{{r petitioner.formattedAddress}}

:

:

:

:

:

:

:

:

COURT OF COMMON PLEAS

CRIMINAL TRIAL DIVISION

{% for docket in dockets -%}

{{ docket }}

{% endfor -%}

OTN# {{ petition.otn }}

DOB: {{ petitioner.dob\|date }}

SSN: {{ petitioner.ssn }}

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

**Petition for {{ petition.ratio.value }} Pursuant to Pa.R.Crim.P. 790**

AND NOW, the Petitioner, through counsel {{ attorney.user.first_name }}
{{ attorney.user.last_name }}, Esquire, avers the following and requests
that this petition for {{ petition.ratio.value }} pursuant to
Pa.R.Crim.P. 790 be granted for the reasons set forth below.

**PETITIONER INFORMATION**

> **Full Name:** {{ petitioner.name }}
>
> **DOB:** {{ petitioner.dob\|date }}
>
> **Social Security Number:** {{ petitioner.ssn }}
>
> **Address:**
>
> {{r petitioner.formattedAddress}}
>
> **Alias(es):** {{ petitioner.aliases\|comma_join }}
>
> **CASE INFORMATION**
>
> **Judge**: {{ petition.judge }}
>
> **Date on Complaint:**
>
> {{ petition.complaint_date\|date }}
>
> **Docket Number(s):**

{%tr for docket in dockets %}

{{ docket }}

{%tr endfor %}

> **Address:** Criminal Justice Center\
> 1301 Filbert Street\
> Philadelphia, PA 19107
>
> **Name of Arresting Agency:**
>
> {{ petition.arrest_agency }}
>
> **Offense Tracking Number (OTN):** {{ petition.otn }}
>
> **Name of Affiant:**
>
> {{ petition.arrest_officer }}
>
> **Address:**
>
> Philadelphia County, PA
>
> **The charges to be expunged are:**
>
> **Code Section**
>
> **Statute Description**
>
> **Grade**
>
> **Disp Date**
>
> **Disposition**
>
> {%tr for charge in charges %}
>
> {{ charge.code_section }}
>
> {{ charge.statute }}
>
> {{ charge.grade }}
>
> {{ charge.date\|date }}
>
> {{ charge.disposition }}
>
> {%tr endfor %}
>
> {%p if fines.total and fines.paid %}
>
> The Petitioner's sentence includes fines, costs and/or restitution in
> the amount of \${{ fines.total }} and \${{ fines.paid }} has been paid
> off/adjusted.

{%p endif %}

> **List the reason(s) for the {{ petition.ratio.value }}(please attach
> additional sheet(s) of paper if necessary):**
>
> As a result of these arrests and subsequent photographing and
> fingerprinting, Petitioner has been caused to suffer embarrassment and
> irreparable harm and loss of job opportunities. Expungement is proper
> under 18 Pa.C.S. 9122 as the charges to be expunged were {{
> dispositions }}.
>
> **Pursuant to local practice, the Commonwealth agrees to waive the
> requirement of attachment to this Petition of a current copy of the
> petitioner's Pennsylvania State Police criminal history report. This
> waiver may be revoked by the Commonwealth in any case and at any time
> prior to the granting of the relief requested.**

The facts set forth in this petition are true and correct to the best of
my personal knowledge or information and belief, and are made subject to
the penalties of unsworn falsification to authorities under 18 Pa.C.S. §
4904.

PLSE is a non-profit legal services organization that provides free
legal assistance to low-income individuals. I, attorney for the
petitioner, certify that petitioner meets the financial eligibility
standards for representation by PLSE and that I am providing free legal
service to petitioner.

[/s/ {{ attorney.user.first_name }} {{ attorney.user.last_name
}}]{.underline}

{{ attorney.user.first_name }} {{ attorney.user.last_name }} Esquire

Counsel for Petitioner

> DATED: {{ petition.date\|date }}
