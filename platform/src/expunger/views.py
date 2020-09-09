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

        if profile is None:
            return Response(
                {"detail": "User has no profile, use POST to create"},
                status=404)

        attorney_id = request.data.get("attorney", None)

        if attorney_id is not None:
            try:
                attorney = models.Attorney.objects.get(pk=attorney_id)
            except models.Attorney.DoesNotExist:
                return Response({"detail": "No such attorney"}, status=403)

            profile.attorney = attorney

        organization_id = request.data.get("organization", None)

        if organization_id is not None:
            try:
                organization = models.Organization.objects.get(pk=organization_id)
            except models.Organization.DoesNotExist:
                return Response({"detail": "No such organization"}, status=403)

            profile.organization = organization

        profile.save()

        serializer = serializers.ExpungerProfileSerializer(
            profile, context={"request": request})

        return Response(serializer.data, status=200)
