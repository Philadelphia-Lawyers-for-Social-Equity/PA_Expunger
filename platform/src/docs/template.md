# Petition Template

The petition template is located at
**platform/src/petition/templates/petition.docx**.

Key libraries are (jinja2)[https://palletsprojects.com/p/jinja/] and
(docxtpl)[https://docxtpl.readthedocs.io/en/latest/].


## Template Input Pipeline

1. The docket parser produces a dict representation of the docket as written,
without regard for eventual use.
2. **petition.views.DocketParserAPIView** (**platform/src/petition/views.py**),
converts docket parser data into a dict representation of the context.
3.  **petition.views.PetitionAPIView** (**platform/src/petition/views.py**)
turns the docket API data into the final template *input context*, using python
classed objects as appropriate.
