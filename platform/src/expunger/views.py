import logging
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from . import models
from . import serializers

logger = logging.getLogger("django")


class AddressView(APIView):
    """
    View to show an individual address via the JSON API
    """

    def get(self, request, pk, *args, **kwargs):
        """
        Produce the address via id
        """
        address = get_object_or_404(models.Address, pk=pk)
        serializer = serializers.AddressSerializer(
            address, context={"request": request})

        return Response(serializer.data)


class OrganizationsView(APIView):
    """View to list organizations"""

    def get(self, request, *args, **kwargs):
        """Produce a list of organizations"""
        orgs = models.Organization.objects.all()
        serializer = serializers.OrganizationSerializer(
            orgs, context={"request": request}, many=True)

        return Response(serializer.data)


class OrganizationView(APIView):
    """View of an individual organization"""

    def get(self, request, pk, *args, **kwargs):
        """Produce the view for a single organization"""
        org = get_object_or_404(models.Organization, pk=pk)
        serializer = serializers.OrganizationSerializer(
            org, context={"request": request})

        return Response(serializer.data)


class AttorneysView(APIView):
    """List view for Attorneys"""

    def get(self, request, *args, **kwargs):
        """Produce details for an attorney"""
        attorneys = models.Attorney.objects.all()
        serializer = serializers.AttorneySerializer(
            attorneys, context={"request": request}, many=True)

        return Response(serializer.data)

class DocketsView(APIView):
    """Search view for docket metadata"""

    def get(self, request, *args, **kwargs):
        """Make docket search from query"""
        first_name = request.query_params.get("firstName")
        last_name = request.query_params.get("lastName")
        if first_name is None or last_name is None:
            return Response(
                {"detail": "Must supply firstName and lastName in query parameters to search"},
                status=409)
        
        records = models.DocketMetadata.objects.filter(first_name=first_name, last_name=last_name)
        serializer = serializers.DocketSerializer(records, many=True)
        return Response(serializer.data)

class DocketsView(APIView):
    """Search view for docket metadata"""

    def get(self, request, *args, **kwargs):
        """Make docket search from query"""
        first_name = request.query_params.get("firstName")
        last_name = request.query_params.get("lastName")
        if first_name is None or last_name is None:
            return Response(
                {"detail": "Must supply firstName and lastName " +
                    "in query parameters to search"},
                status=409)
        records = models.DocketMetadata.objects.filter(
            first_name=first_name, last_name=last_name)
        serializer = serializers.DocketSerializer(records, many=True)
        return Response(serializer.data)

class AttorneyView(APIView):
    """View of an individual attorney"""

    def get(self, request, pk, *args, **kwargs):
        """Produce details for an attorney"""
        attorney = get_object_or_404(models.Attorney, pk=pk)
        serializer = serializers.AttorneySerializer(
            attorney, context={"request": request})
        return Response(serializer.data)


class MyProfileView(APIView):
    """Allow user to view, update its profile"""

    def get(self, request, *args, **kwargs):
        """Produce users profile data"""
        profile = getattr(request.user, "expungerprofile", None)

        if profile is None:
            return Response({"detail": "User has no profile"}, status=404)

        serializer = serializers.ExpungerProfileSerializer(
            profile, context={"request": request})
        return Response(serializer.data)

    # Users are all created in admin. Do we need a post view for this model?
    # granted we are creating the profile object here, but functionally we are updating the user. 
    def post(self, request, *args, **kwargs):
        """Allow user to create a new profile"""
        profile = getattr(request.user, "expungerprofile", None)

        if profile is not None:
            return Response(
                {"detail": "User profile already exists, use PUT to update"},
                status=409)

        try:
            attorney = models.Attorney.objects.get(
                pk=request.data["attorney"])
        except models.Attorney.DoesNotExist:
            return Response(
                {"detail": "No such attorney"}, status=403)

        try:
            organization = models.Organization.objects.get(
                pk=request.data["organization"])
        except models.Organization.DoesNotExist:
            return Response(
                {"detail": "No such organization"}, status=403)

        profile = models.ExpungerProfile(user=request.user, attorney=attorney,
                                         organization=organization)
        profile.save()
        serializer = serializers.ExpungerProfileSerializer(
            profile, context={"request": request})

        return Response(serializer.data, status=201)

    def put(self, request, *args, **kwargs):
        """Allow the user to update their profile"""
        profile = getattr(request.user, "expungerprofile", None)

        attorney_id = request.data.get("attorney", None)

        if attorney_id is not None:
            try:
                attorney = models.Attorney.objects.get(pk=attorney_id)
            except models.Attorney.DoesNotExist:
                return Response({"detail": "No such attorney"}, status=403)
        else:
            return Response({"detail": "Must supply attorney"}, status=403)

        organization_id = request.data.get("organization", None)

        if organization_id is not None:
            try:
                organization = models.Organization.objects.get(
                    pk=organization_id)
            except models.Organization.DoesNotExist:
                return Response({"detail": "No such organization"}, status=403)
        else:
            return Response({"detail": "Must supply organization"}, status=403)

        if profile is None:
            # Create a new profile if one does not exist for this user
            profile = models.ExpungerProfile(
                user=request.user, attorney=attorney, organization=organization
            )
        else:
            profile.attorney = attorney
            profile.organization = organization

        profile.save()

        serializer = serializers.ExpungerProfileSerializer(
            profile, context={"request": request})

        return Response(serializer.data, status=200)
