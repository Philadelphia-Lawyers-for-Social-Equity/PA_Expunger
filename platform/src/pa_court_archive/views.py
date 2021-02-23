import logging
from rest_framework.response import Response
from rest_framework.views import APIView

from . import models
from . import serializers

logger = logging.getLogger("django")


class PaCourtArchiveView(APIView):
    """Search view for the pa_court_archive."""

    def get(self, request, *args, **kwargs):
        """Make docket search from query"""
        first_name = request.query_params.get("first_name")
        last_name = request.query_params.get("last_name")

        if first_name is None or last_name is None:
            return Response(
                {"error": "Must supply first_name and last_name " +
                    "in query parameters to search"},
                status=409)

        records = models.Case.objects.filter(
            arrestees__first_name__icontains=first_name,
            arrestees__last_name__icontains=last_name)

        serializer = serializers.CaseToPetitionFieldsSerializer(records, many=True)
        return Response(serializer.data)
