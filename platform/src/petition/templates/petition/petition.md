{{ organization.name }}\
BY: {{ attorney.user.first_name }} {{ attorney.user.last_name }}\
Identification No.: {{ attorney.bar }}\
\
{{r organization.formattedAddress }}\
{{ organization.phone }}\
Attorney for {{ petitioner.name }}

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

+:-----------------------------------:+---+----------------------------+
| COMMONWEALTH OF PENNSYLVANIA        | : | COURT OF COMMON PLEAS      |
|                                     |   |                            |
| vs.                                 | : | CRIMINAL TRIAL DIVISION    |
|                                     |   |                            |
| {{ petitioner.name }}               | : | [PHILADELPHIA]{.smallcaps} |
|                                     |   | COUNTY                     |
| {{r petitioner.formattedAddress }}  | : |                            |
|                                     |   | {% for docket in dockets   |
|                                     | : | -%}                        |
|                                     |   |                            |
|                                     | : | {{ docket }}               |
|                                     |   |                            |
|                                     | : | {% endfor -%}              |
|                                     |   |                            |
|                                     | : | OTN# {{ petition.otn }}    |
+-------------------------------------+---+----------------------------+

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

1.  **Petitioner Name:** {{ petitioner.name }}

2.  **Alias(es):** {{ petitioner.aliases\|comma_join }}

3.  **Petitioner's Address:**

> {{r petitioner.formattedAddress }}

4.  **Petitioner's Date of Birth:** {{ petitioner.dob\|date }}

5.  **Petitioner's Social Security Number:** {{ petitioner.ssn }}

6.  **Name and address of the judge who accepted the guilty plea or
    heard the case:**

> Judge {{ petition.judge }}
>
> Criminal Justice Center\
> 1301 Filbert Street\
> Philadelphia, PA 19107

7.  **Docket Number:**

  -----------------------------------------------------------------------
  {%tr for docket in dockets %}

  {{ docket }}

  {%tr endfor %}
  -----------------------------------------------------------------------

8.  **Offense Tracking Number (OTN):** {{ petition.otn }}

9.  **The specific charges, as they appear on the charging document, to
    be expunged and applicable dispositions:**

+------------+------------------+:---+:--------+---------------------+
| > **Code   | > **Statute      | >  | >       | > **Disposition**   |
| >          | > Description**  |  * |  **Disp |                     |
|  Section** |                  | *G | >       |                     |
|            |                  | ra |  Date** |                     |
|            |                  | de |         |                     |
|            |                  | ** |         |                     |
+------------+------------------+----+---------+---------------------+
| > {%tr for |                  |    |         |                     |
| > charge   |                  |    |         |                     |
| > in       |                  |    |         |                     |
| > charges  |                  |    |         |                     |
| > %}       |                  |    |         |                     |
+------------+------------------+----+---------+---------------------+
| > {{       | > {{             | >  | > {{    | > {{                |
| > char     | > ch             | {{ | > cha   | >                   |
| ge.statute | arge.description | >  | rge.dat |  charge.disposition |
| > }}       | > }}             | ch | e\|date | > }}                |
|            |                  | ar | > }}    |                     |
|            |                  | ge |         |                     |
|            |                  | .g |         |                     |
|            |                  | ra |         |                     |
|            |                  | de |         |                     |
|            |                  | >  |         |                     |
|            |                  | }} |         |                     |
+------------+------------------+----+---------+---------------------+
| > {%tr     |                  |    |         |                     |
| > endfor   |                  |    |         |                     |
| > %}       |                  |    |         |                     |
+------------+------------------+----+---------+---------------------+

{%p if fines.total and fines.paid %}

10. **If the sentence includes a fine, costs, or restitution, whether
    the amount due has been paid:**

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

  -----------------------------------------------------------------------
  1\. The Clerk of Courts of Philadelphia County, Criminal Division

  2\. The Philadelphia County District Attorney\`s Office

  3\. The Pennsylvania State Police, Central Records

  4\. A.O.P.C. Expungement Unit

  5\. Philadelphia Police Dept

  6\. Philadelphia County Department of Adult Probation and Parole
  -----------------------------------------------------------------------

{{ organization.name }}\
BY: {{ attorney.user.first_name }} {{ attorney.user.last_name }}\
Identification No.: {{ attorney.bar }}\
\
{{r organization.formattedAddress }}\
{{ organization.phone }}\
Attorney for {{ petitioner.name }}

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

+:-----------------------------------:+:-:+------------------------------+
| COMMONWEALTH OF PENNSYLVANIA        | : | COURT OF COMMON PLEAS        |
|                                     |   |                              |
| vs.                                 | : | CRIMINAL TRIAL DIVISION      |
|                                     |   |                              |
| {{ petitioner.name }}               | : | {% for docket in dockets -%} |
|                                     |   |                              |
| {{r petitioner.formattedAddress}}   | : | {{ docket }}                 |
|                                     |   |                              |
|                                     | : | {% endfor -%}                |
|                                     |   |                              |
|                                     | : | OTN# {{ petition.otn }}      |
|                                     |   |                              |
|                                     | : | DOB: {{ petitioner.dob\|date |
|                                     |   | }}                           |
|                                     | : |                              |
|                                     |   | SSN: {{ petitioner.ssn }}    |
+-------------------------------------+---+------------------------------+

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

**Petition for {{ petition.ratio.value }} Pursuant to Pa.R.Crim.P. 790**

AND NOW, the Petitioner, through counsel {{ attorney.user.first_name }}
{{ attorney.user.last_name }}, Esquire, avers the following and requests
that this petition for {{ petition.ratio.value }} pursuant to
Pa.R.Crim.P. 790 be granted for the reasons set forth below.

+-------------+--------------+---+---+---+----+-----+---------------------+
| [           |              |   |   |   |    |     |                     |
| *           |              |   |   |   |    |     |                     |
| *PETITIONER |              |   |   |   |    |     |                     |
| INFORMATION |              |   |   |   |    |     |                     |
| **]{.mark}  |              |   |   |   |    |     |                     |
+-------------+--------------+---+---+---+----+-----+---------------------+
| > **Full    |              | > |   |   |    | >   |                     |
| > Name:**   |              |   |   |   |    |  ** |                     |
| > {{        |              | * |   |   |    | Soc |                     |
| > peti      |              | * |   |   |    | ial |                     |
| tioner.name |              | D |   |   |    | >   |                     |
| > }}        |              | O |   |   |    |  Se |                     |
|             |              | B |   |   |    | cur |                     |
|             |              | : |   |   |    | ity |                     |
|             |              | * |   |   |    | >   |                     |
|             |              | * |   |   |    | Num |                     |
|             |              | > |   |   |    | ber |                     |
|             |              |   |   |   |    | :** |                     |
|             |              | { |   |   |    | >   |                     |
|             |              | { |   |   |    |  {{ |                     |
|             |              | > |   |   |    | >   |                     |
|             |              |   |   |   |    |  pe |                     |
|             |              | p |   |   |    | tit |                     |
|             |              | e |   |   |    | ion |                     |
|             |              | t |   |   |    | er. |                     |
|             |              | i |   |   |    | ssn |                     |
|             |              | t |   |   |    | >   |                     |
|             |              | i |   |   |    |  }} |                     |
|             |              | o |   |   |    |     |                     |
|             |              | n |   |   |    |     |                     |
|             |              | e |   |   |    |     |                     |
|             |              | r |   |   |    |     |                     |
|             |              | . |   |   |    |     |                     |
|             |              | d |   |   |    |     |                     |
|             |              | o |   |   |    |     |                     |
|             |              | b |   |   |    |     |                     |
|             |              | \ |   |   |    |     |                     |
|             |              | | |   |   |    |     |                     |
|             |              | d |   |   |    |     |                     |
|             |              | a |   |   |    |     |                     |
|             |              | t |   |   |    |     |                     |
|             |              | e |   |   |    |     |                     |
|             |              | > |   |   |    |     |                     |
|             |              |   |   |   |    |     |                     |
|             |              | } |   |   |    |     |                     |
|             |              | } |   |   |    |     |                     |
+-------------+--------------+---+---+---+----+-----+---------------------+
| > *         |              | > |   |   |    |     |                     |
| *Address:** |              |   |   |   |    |     |                     |
| >           |              | * |   |   |    |     |                     |
| > {{r       |              | * |   |   |    |     |                     |
| > petitio   |              | A |   |   |    |     |                     |
| ner.formatt |              | l |   |   |    |     |                     |
| edAddress}} |              | i |   |   |    |     |                     |
|             |              | a |   |   |    |     |                     |
|             |              | s |   |   |    |     |                     |
|             |              | ( |   |   |    |     |                     |
|             |              | e |   |   |    |     |                     |
|             |              | s |   |   |    |     |                     |
|             |              | ) |   |   |    |     |                     |
|             |              | : |   |   |    |     |                     |
|             |              | * |   |   |    |     |                     |
|             |              | * |   |   |    |     |                     |
|             |              | > |   |   |    |     |                     |
|             |              |   |   |   |    |     |                     |
|             |              | { |   |   |    |     |                     |
|             |              | { |   |   |    |     |                     |
|             |              | > |   |   |    |     |                     |
|             |              |   |   |   |    |     |                     |
|             |              | p |   |   |    |     |                     |
|             |              | e |   |   |    |     |                     |
|             |              | t |   |   |    |     |                     |
|             |              | i |   |   |    |     |                     |
|             |              | t |   |   |    |     |                     |
|             |              | i |   |   |    |     |                     |
|             |              | o |   |   |    |     |                     |
|             |              | n |   |   |    |     |                     |
|             |              | e |   |   |    |     |                     |
|             |              | r |   |   |    |     |                     |
|             |              | . |   |   |    |     |                     |
|             |              | a |   |   |    |     |                     |
|             |              | l |   |   |    |     |                     |
|             |              | i |   |   |    |     |                     |
|             |              | a |   |   |    |     |                     |
|             |              | s |   |   |    |     |                     |
|             |              | e |   |   |    |     |                     |
|             |              | s |   |   |    |     |                     |
|             |              | \ |   |   |    |     |                     |
|             |              | | |   |   |    |     |                     |
|             |              | c |   |   |    |     |                     |
|             |              | o |   |   |    |     |                     |
|             |              | m |   |   |    |     |                     |
|             |              | m |   |   |    |     |                     |
|             |              | a |   |   |    |     |                     |
|             |              | _ |   |   |    |     |                     |
|             |              | j |   |   |    |     |                     |
|             |              | o |   |   |    |     |                     |
|             |              | i |   |   |    |     |                     |
|             |              | n |   |   |    |     |                     |
|             |              | > |   |   |    |     |                     |
|             |              |   |   |   |    |     |                     |
|             |              | } |   |   |    |     |                     |
|             |              | } |   |   |    |     |                     |
+-------------+--------------+---+---+---+----+-----+---------------------+
| > **CASE    |              |   |   |   |    |     |                     |
| > IN        |              |   |   |   |    |     |                     |
| FORMATION** |              |   |   |   |    |     |                     |
+-------------+--------------+---+---+---+----+-----+---------------------+
| >           |              |   |   | > |    |     |                     |
|  **Judge**: |              |   |   |   |    |     |                     |
| > {{        |              |   |   | * |    |     |                     |
| > pet       |              |   |   | * |    |     |                     |
| ition.judge |              |   |   | D |    |     |                     |
| > }}        |              |   |   | a |    |     |                     |
|             |              |   |   | t |    |     |                     |
|             |              |   |   | e |    |     |                     |
|             |              |   |   | > |    |     |                     |
|             |              |   |   |   |    |     |                     |
|             |              |   |   | o |    |     |                     |
|             |              |   |   | n |    |     |                     |
|             |              |   |   | > |    |     |                     |
|             |              |   |   |   |    |     |                     |
|             |              |   |   | C |    |     |                     |
|             |              |   |   | o |    |     |                     |
|             |              |   |   | m |    |     |                     |
|             |              |   |   | p |    |     |                     |
|             |              |   |   | l |    |     |                     |
|             |              |   |   | a |    |     |                     |
|             |              |   |   | i |    |     |                     |
|             |              |   |   | n |    |     |                     |
|             |              |   |   | t |    |     |                     |
|             |              |   |   | : |    |     |                     |
|             |              |   |   | * |    |     |                     |
|             |              |   |   | * |    |     |                     |
|             |              |   |   | > |    |     |                     |
|             |              |   |   | > |    |     |                     |
|             |              |   |   |   |    |     |                     |
|             |              |   |   | { |    |     |                     |
|             |              |   |   | { |    |     |                     |
|             |              |   |   | > |    |     |                     |
|             |              |   |   |   |    |     |                     |
|             |              |   |   | p |    |     |                     |
|             |              |   |   | e |    |     |                     |
|             |              |   |   | t |    |     |                     |
|             |              |   |   | i |    |     |                     |
|             |              |   |   | t |    |     |                     |
|             |              |   |   | i |    |     |                     |
|             |              |   |   | o |    |     |                     |
|             |              |   |   | n |    |     |                     |
|             |              |   |   | . |    |     |                     |
|             |              |   |   | c |    |     |                     |
|             |              |   |   | o |    |     |                     |
|             |              |   |   | m |    |     |                     |
|             |              |   |   | p |    |     |                     |
|             |              |   |   | l |    |     |                     |
|             |              |   |   | a |    |     |                     |
|             |              |   |   | i |    |     |                     |
|             |              |   |   | n |    |     |                     |
|             |              |   |   | t |    |     |                     |
|             |              |   |   | _ |    |     |                     |
|             |              |   |   | d |    |     |                     |
|             |              |   |   | a |    |     |                     |
|             |              |   |   | t |    |     |                     |
|             |              |   |   | e |    |     |                     |
|             |              |   |   | \ |    |     |                     |
|             |              |   |   | | |    |     |                     |
|             |              |   |   | d |    |     |                     |
|             |              |   |   | a |    |     |                     |
|             |              |   |   | t |    |     |                     |
|             |              |   |   | e |    |     |                     |
|             |              |   |   | > |    |     |                     |
|             |              |   |   |   |    |     |                     |
|             |              |   |   | } |    |     |                     |
|             |              |   |   | } |    |     |                     |
+-------------+--------------+---+---+---+----+-----+---------------------+
| > **Docket  |              |   |   | > |    |     |                     |
| > N         |              |   |   |   |    |     |                     |
| umber(s):** |              |   |   | * |    |     |                     |
|             |              |   |   | * |    |     |                     |
|   --------- |              |   |   | A |    |     |                     |
|   {%tr for  |              |   |   | d |    |     |                     |
|   docket in |              |   |   | d |    |     |                     |
|   dockets   |              |   |   | r |    |     |                     |
|   %}        |              |   |   | e |    |     |                     |
|             |              |   |   | s |    |     |                     |
|   {{ docket |              |   |   | s |    |     |                     |
|   }}        |              |   |   | : |    |     |                     |
|             |              |   |   | * |    |     |                     |
|   {%tr      |              |   |   | * |    |     |                     |
|   endfor %} |              |   |   | > |    |     |                     |
|   --------- |              |   |   |   |    |     |                     |
|             |              |   |   | C |    |     |                     |
|             |              |   |   | r |    |     |                     |
|             |              |   |   | i |    |     |                     |
|             |              |   |   | m |    |     |                     |
|             |              |   |   | i |    |     |                     |
|             |              |   |   | n |    |     |                     |
|             |              |   |   | a |    |     |                     |
|             |              |   |   | l |    |     |                     |
|             |              |   |   | > |    |     |                     |
|             |              |   |   |   |    |     |                     |
|             |              |   |   | J |    |     |                     |
|             |              |   |   | u |    |     |                     |
|             |              |   |   | s |    |     |                     |
|             |              |   |   | t |    |     |                     |
|             |              |   |   | i |    |     |                     |
|             |              |   |   | c |    |     |                     |
|             |              |   |   | e |    |     |                     |
|             |              |   |   | > |    |     |                     |
|             |              |   |   |   |    |     |                     |
|             |              |   |   | C |    |     |                     |
|             |              |   |   | e |    |     |                     |
|             |              |   |   | n |    |     |                     |
|             |              |   |   | t |    |     |                     |
|             |              |   |   | e |    |     |                     |
|             |              |   |   | r |    |     |                     |
|             |              |   |   | \ |    |     |                     |
|             |              |   |   | > |    |     |                     |
|             |              |   |   |   |    |     |                     |
|             |              |   |   | 1 |    |     |                     |
|             |              |   |   | 3 |    |     |                     |
|             |              |   |   | 0 |    |     |                     |
|             |              |   |   | 1 |    |     |                     |
|             |              |   |   | > |    |     |                     |
|             |              |   |   |   |    |     |                     |
|             |              |   |   | F |    |     |                     |
|             |              |   |   | i |    |     |                     |
|             |              |   |   | l |    |     |                     |
|             |              |   |   | b |    |     |                     |
|             |              |   |   | e |    |     |                     |
|             |              |   |   | r |    |     |                     |
|             |              |   |   | t |    |     |                     |
|             |              |   |   | > |    |     |                     |
|             |              |   |   |   |    |     |                     |
|             |              |   |   | S |    |     |                     |
|             |              |   |   | t |    |     |                     |
|             |              |   |   | r |    |     |                     |
|             |              |   |   | e |    |     |                     |
|             |              |   |   | e |    |     |                     |
|             |              |   |   | t |    |     |                     |
|             |              |   |   | \ |    |     |                     |
|             |              |   |   | > |    |     |                     |
|             |              |   |   |   |    |     |                     |
|             |              |   |   | P |    |     |                     |
|             |              |   |   | h |    |     |                     |
|             |              |   |   | i |    |     |                     |
|             |              |   |   | l |    |     |                     |
|             |              |   |   | a |    |     |                     |
|             |              |   |   | d |    |     |                     |
|             |              |   |   | e |    |     |                     |
|             |              |   |   | l |    |     |                     |
|             |              |   |   | p |    |     |                     |
|             |              |   |   | h |    |     |                     |
|             |              |   |   | i |    |     |                     |
|             |              |   |   | a |    |     |                     |
|             |              |   |   | , |    |     |                     |
|             |              |   |   | > |    |     |                     |
|             |              |   |   |   |    |     |                     |
|             |              |   |   | P |    |     |                     |
|             |              |   |   | A |    |     |                     |
|             |              |   |   | > |    |     |                     |
|             |              |   |   |   |    |     |                     |
|             |              |   |   | 1 |    |     |                     |
|             |              |   |   | 9 |    |     |                     |
|             |              |   |   | 1 |    |     |                     |
|             |              |   |   | 0 |    |     |                     |
|             |              |   |   | 7 |    |     |                     |
+-------------+--------------+---+---+---+----+-----+---------------------+
| > **Name of |              |   |   | > |    |     |                     |
| > Arresting |              |   |   |   |    |     |                     |
| > Agency:** |              |   |   | * |    |     |                     |
| >           |              |   |   | * |    |     |                     |
| > {{        |              |   |   | O |    |     |                     |
| >           |              |   |   | f |    |     |                     |
| petition.ar |              |   |   | f |    |     |                     |
| rest_agency |              |   |   | e |    |     |                     |
| > }}        |              |   |   | n |    |     |                     |
|             |              |   |   | s |    |     |                     |
|             |              |   |   | e |    |     |                     |
|             |              |   |   | > |    |     |                     |
|             |              |   |   |   |    |     |                     |
|             |              |   |   | T |    |     |                     |
|             |              |   |   | r |    |     |                     |
|             |              |   |   | a |    |     |                     |
|             |              |   |   | c |    |     |                     |
|             |              |   |   | k |    |     |                     |
|             |              |   |   | i |    |     |                     |
|             |              |   |   | n |    |     |                     |
|             |              |   |   | g |    |     |                     |
|             |              |   |   | > |    |     |                     |
|             |              |   |   |   |    |     |                     |
|             |              |   |   | N |    |     |                     |
|             |              |   |   | u |    |     |                     |
|             |              |   |   | m |    |     |                     |
|             |              |   |   | b |    |     |                     |
|             |              |   |   | e |    |     |                     |
|             |              |   |   | r |    |     |                     |
|             |              |   |   | > |    |     |                     |
|             |              |   |   |   |    |     |                     |
|             |              |   |   | ( |    |     |                     |
|             |              |   |   | O |    |     |                     |
|             |              |   |   | T |    |     |                     |
|             |              |   |   | N |    |     |                     |
|             |              |   |   | ) |    |     |                     |
|             |              |   |   | : |    |     |                     |
|             |              |   |   | * |    |     |                     |
|             |              |   |   | * |    |     |                     |
|             |              |   |   | > |    |     |                     |
|             |              |   |   |   |    |     |                     |
|             |              |   |   | { |    |     |                     |
|             |              |   |   | { |    |     |                     |
|             |              |   |   | > |    |     |                     |
|             |              |   |   |   |    |     |                     |
|             |              |   |   | p |    |     |                     |
|             |              |   |   | e |    |     |                     |
|             |              |   |   | t |    |     |                     |
|             |              |   |   | i |    |     |                     |
|             |              |   |   | t |    |     |                     |
|             |              |   |   | i |    |     |                     |
|             |              |   |   | o |    |     |                     |
|             |              |   |   | n |    |     |                     |
|             |              |   |   | . |    |     |                     |
|             |              |   |   | o |    |     |                     |
|             |              |   |   | t |    |     |                     |
|             |              |   |   | n |    |     |                     |
|             |              |   |   | > |    |     |                     |
|             |              |   |   |   |    |     |                     |
|             |              |   |   | } |    |     |                     |
|             |              |   |   | } |    |     |                     |
+-------------+--------------+---+---+---+----+-----+---------------------+
| > **Name of |              |   |   | > |    |     |                     |
| >           |              |   |   |   |    |     |                     |
|  Affiant:** |              |   |   | * |    |     |                     |
| >           |              |   |   | * |    |     |                     |
| > {{        |              |   |   | A |    |     |                     |
| > p         |              |   |   | d |    |     |                     |
| etition.arr |              |   |   | d |    |     |                     |
| est_officer |              |   |   | r |    |     |                     |
| > }}        |              |   |   | e |    |     |                     |
|             |              |   |   | s |    |     |                     |
|             |              |   |   | s |    |     |                     |
|             |              |   |   | : |    |     |                     |
|             |              |   |   | * |    |     |                     |
|             |              |   |   | * |    |     |                     |
|             |              |   |   | > |    |     |                     |
|             |              |   |   | > |    |     |                     |
|             |              |   |   |   |    |     |                     |
|             |              |   |   | P |    |     |                     |
|             |              |   |   | h |    |     |                     |
|             |              |   |   | i |    |     |                     |
|             |              |   |   | l |    |     |                     |
|             |              |   |   | a |    |     |                     |
|             |              |   |   | d |    |     |                     |
|             |              |   |   | e |    |     |                     |
|             |              |   |   | l |    |     |                     |
|             |              |   |   | p |    |     |                     |
|             |              |   |   | h |    |     |                     |
|             |              |   |   | i |    |     |                     |
|             |              |   |   | a |    |     |                     |
|             |              |   |   | > |    |     |                     |
|             |              |   |   |   |    |     |                     |
|             |              |   |   | C |    |     |                     |
|             |              |   |   | o |    |     |                     |
|             |              |   |   | u |    |     |                     |
|             |              |   |   | n |    |     |                     |
|             |              |   |   | t |    |     |                     |
|             |              |   |   | y |    |     |                     |
|             |              |   |   | , |    |     |                     |
|             |              |   |   | > |    |     |                     |
|             |              |   |   |   |    |     |                     |
|             |              |   |   | P |    |     |                     |
|             |              |   |   | A |    |     |                     |
+-------------+--------------+---+---+---+----+-----+---------------------+
| > **The     |              |   |   |   |    |     |                     |
| > charges   |              |   |   |   |    |     |                     |
| > to be     |              |   |   |   |    |     |                     |
| > expunged  |              |   |   |   |    |     |                     |
| > are:**    |              |   |   |   |    |     |                     |
+-------------+--------------+---+---+---+----+-----+---------------------+
| > **Code    | > **Statute  |   | > |   | >  |     | > **Disposition**   |
| > Section** | > D          |   |   |   | ** |     |                     |
|             | escription** |   | * |   | Di |     |                     |
|             |              |   | * |   | sp |     |                     |
|             |              |   | G |   | >  |     |                     |
|             |              |   | r |   | Da |     |                     |
|             |              |   | a |   | te |     |                     |
|             |              |   | d |   | ** |     |                     |
|             |              |   | e |   |    |     |                     |
|             |              |   | * |   |    |     |                     |
|             |              |   | * |   |    |     |                     |
+-------------+--------------+---+---+---+----+-----+---------------------+
| > {%tr for  |              |   |   |   |    |     |                     |
| > charge in |              |   |   |   |    |     |                     |
| > charges   |              |   |   |   |    |     |                     |
| > %}        |              |   |   |   |    |     |                     |
+-------------+--------------+---+---+---+----+-----+---------------------+
| > {{        | > {{         |   | > |   | >  |     | > {{                |
| > cha       | > charge     |   |   |   | {{ |     | >                   |
| rge.statute | .description |   | { |   | >  |     |  charge.disposition |
| > }}        | > }}         |   | { |   |  c |     | > }}                |
|             |              |   | > |   | ha |     |                     |
|             |              |   |   |   | rg |     |                     |
|             |              |   | c |   | e. |     |                     |
|             |              |   | h |   | da |     |                     |
|             |              |   | a |   | te |     |                     |
|             |              |   | r |   | \| |     |                     |
|             |              |   | g |   | da |     |                     |
|             |              |   | e |   | te |     |                     |
|             |              |   | . |   | >  |     |                     |
|             |              |   | g |   | }} |     |                     |
|             |              |   | r |   |    |     |                     |
|             |              |   | a |   |    |     |                     |
|             |              |   | d |   |    |     |                     |
|             |              |   | e |   |    |     |                     |
|             |              |   | > |   |    |     |                     |
|             |              |   |   |   |    |     |                     |
|             |              |   | } |   |    |     |                     |
|             |              |   | } |   |    |     |                     |
+-------------+--------------+---+---+---+----+-----+---------------------+
| > {%tr      |              |   |   |   |    |     |                     |
| > endfor %} |              |   |   |   |    |     |                     |
+-------------+--------------+---+---+---+----+-----+---------------------+
| > {%p if    |              |   |   |   |    |     |                     |
| >           |              |   |   |   |    |     |                     |
| fines.total |              |   |   |   |    |     |                     |
| > and       |              |   |   |   |    |     |                     |
| >           |              |   |   |   |    |     |                     |
|  fines.paid |              |   |   |   |    |     |                     |
| > %}        |              |   |   |   |    |     |                     |
| >           |              |   |   |   |    |     |                     |
| > The       |              |   |   |   |    |     |                     |
| > P         |              |   |   |   |    |     |                     |
| etitioner's |              |   |   |   |    |     |                     |
| > sentence  |              |   |   |   |    |     |                     |
| > includes  |              |   |   |   |    |     |                     |
| > fines,    |              |   |   |   |    |     |                     |
| > costs     |              |   |   |   |    |     |                     |
| > and/or    |              |   |   |   |    |     |                     |
| >           |              |   |   |   |    |     |                     |
| restitution |              |   |   |   |    |     |                     |
| > in the    |              |   |   |   |    |     |                     |
| > amount of |              |   |   |   |    |     |                     |
| > \${{      |              |   |   |   |    |     |                     |
| >           |              |   |   |   |    |     |                     |
| fines.total |              |   |   |   |    |     |                     |
| > }} and    |              |   |   |   |    |     |                     |
| > \${{      |              |   |   |   |    |     |                     |
| >           |              |   |   |   |    |     |                     |
|  fines.paid |              |   |   |   |    |     |                     |
| > }} has    |              |   |   |   |    |     |                     |
| > been paid |              |   |   |   |    |     |                     |
| > of        |              |   |   |   |    |     |                     |
| f/adjusted. |              |   |   |   |    |     |                     |
|             |              |   |   |   |    |     |                     |
| {%p endif   |              |   |   |   |    |     |                     |
| %}          |              |   |   |   |    |     |                     |
+-------------+--------------+---+---+---+----+-----+---------------------+
| > **List    |              |   |   |   |    |     |                     |
| > the       |              |   |   |   |    |     |                     |
| > reason(s) |              |   |   |   |    |     |                     |
| > for the   |              |   |   |   |    |     |                     |
| > {{        |              |   |   |   |    |     |                     |
| > petition. |              |   |   |   |    |     |                     |
| ratio.value |              |   |   |   |    |     |                     |
| > }}(please |              |   |   |   |    |     |                     |
| > attach    |              |   |   |   |    |     |                     |
| >           |              |   |   |   |    |     |                     |
|  additional |              |   |   |   |    |     |                     |
| > sheet(s)  |              |   |   |   |    |     |                     |
| > of paper  |              |   |   |   |    |     |                     |
| > if        |              |   |   |   |    |     |                     |
| > ne        |              |   |   |   |    |     |                     |
| cessary):** |              |   |   |   |    |     |                     |
| >           |              |   |   |   |    |     |                     |
| > As a      |              |   |   |   |    |     |                     |
| > result of |              |   |   |   |    |     |                     |
| > these     |              |   |   |   |    |     |                     |
| > arrests   |              |   |   |   |    |     |                     |
| > and       |              |   |   |   |    |     |                     |
| >           |              |   |   |   |    |     |                     |
|  subsequent |              |   |   |   |    |     |                     |
| > ph        |              |   |   |   |    |     |                     |
| otographing |              |   |   |   |    |     |                     |
| > and       |              |   |   |   |    |     |                     |
| > fing      |              |   |   |   |    |     |                     |
| erprinting, |              |   |   |   |    |     |                     |
| >           |              |   |   |   |    |     |                     |
|  Petitioner |              |   |   |   |    |     |                     |
| > has been  |              |   |   |   |    |     |                     |
| > caused to |              |   |   |   |    |     |                     |
| > suffer    |              |   |   |   |    |     |                     |
| > em        |              |   |   |   |    |     |                     |
| barrassment |              |   |   |   |    |     |                     |
| > and       |              |   |   |   |    |     |                     |
| >           |              |   |   |   |    |     |                     |
| irreparable |              |   |   |   |    |     |                     |
| > harm and  |              |   |   |   |    |     |                     |
| > loss of   |              |   |   |   |    |     |                     |
| > job       |              |   |   |   |    |     |                     |
| > opp       |              |   |   |   |    |     |                     |
| ortunities. |              |   |   |   |    |     |                     |
| >           |              |   |   |   |    |     |                     |
| Expungement |              |   |   |   |    |     |                     |
| > is proper |              |   |   |   |    |     |                     |
| > under 18  |              |   |   |   |    |     |                     |
| > Pa.C.S.   |              |   |   |   |    |     |                     |
| > 9122 as   |              |   |   |   |    |     |                     |
| > the       |              |   |   |   |    |     |                     |
| > charges   |              |   |   |   |    |     |                     |
| > to be     |              |   |   |   |    |     |                     |
| > expunged  |              |   |   |   |    |     |                     |
| > were {{   |              |   |   |   |    |     |                     |
| > d         |              |   |   |   |    |     |                     |
| ispositions |              |   |   |   |    |     |                     |
| > }}.       |              |   |   |   |    |     |                     |
+-------------+--------------+---+---+---+----+-----+---------------------+
| >           |              |   |   |   |    |     |                     |
|  **Pursuant |              |   |   |   |    |     |                     |
| > to local  |              |   |   |   |    |     |                     |
| > practice, |              |   |   |   |    |     |                     |
| > the       |              |   |   |   |    |     |                     |
| > C         |              |   |   |   |    |     |                     |
| ommonwealth |              |   |   |   |    |     |                     |
| > agrees to |              |   |   |   |    |     |                     |
| > waive the |              |   |   |   |    |     |                     |
| >           |              |   |   |   |    |     |                     |
| requirement |              |   |   |   |    |     |                     |
| > of        |              |   |   |   |    |     |                     |
| >           |              |   |   |   |    |     |                     |
|  attachment |              |   |   |   |    |     |                     |
| > to this   |              |   |   |   |    |     |                     |
| > Petition  |              |   |   |   |    |     |                     |
| > of a      |              |   |   |   |    |     |                     |
| > current   |              |   |   |   |    |     |                     |
| > copy of   |              |   |   |   |    |     |                     |
| > the       |              |   |   |   |    |     |                     |
| > p         |              |   |   |   |    |     |                     |
| etitioner's |              |   |   |   |    |     |                     |
| > P         |              |   |   |   |    |     |                     |
| ennsylvania |              |   |   |   |    |     |                     |
| > State     |              |   |   |   |    |     |                     |
| > Police    |              |   |   |   |    |     |                     |
| > criminal  |              |   |   |   |    |     |                     |
| > history   |              |   |   |   |    |     |                     |
| > report.   |              |   |   |   |    |     |                     |
| > This      |              |   |   |   |    |     |                     |
| > waiver    |              |   |   |   |    |     |                     |
| > may be    |              |   |   |   |    |     |                     |
| > revoked   |              |   |   |   |    |     |                     |
| > by the    |              |   |   |   |    |     |                     |
| > C         |              |   |   |   |    |     |                     |
| ommonwealth |              |   |   |   |    |     |                     |
| > in any    |              |   |   |   |    |     |                     |
| > case and  |              |   |   |   |    |     |                     |
| > at any    |              |   |   |   |    |     |                     |
| > time      |              |   |   |   |    |     |                     |
| > prior to  |              |   |   |   |    |     |                     |
| > the       |              |   |   |   |    |     |                     |
| > granting  |              |   |   |   |    |     |                     |
| > of the    |              |   |   |   |    |     |                     |
| > relief    |              |   |   |   |    |     |                     |
| > r         |              |   |   |   |    |     |                     |
| equested.** |              |   |   |   |    |     |                     |
+-------------+--------------+---+---+---+----+-----+---------------------+

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

DATED: {{ petition.date\|date }}
