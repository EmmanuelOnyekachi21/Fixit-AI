"""
Repository views module.

This module defines API views for managing repositories, including
creation and retrieval of GitHub repository records.
"""
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Repository
from .serializers import (
    RepositorySerializer,
    RepositoryWriteSerializer
)


@api_view(['POST'])
def create_repository(request):
    """
    Create or retrieve a repository from a GitHub URL.
    
    Accepts a POST request with a GitHub repository URL, validates it,
    and creates a new repository record or returns an existing one.
    
    Args:
        request (Request): The HTTP request containing repo_url in
                          data.
        
    Returns:
        Response: JSON response with repository data and appropriate
                  status code.
                  - 201 Created: New repository was created
                  - 200 OK: Repository already exists
                  - 400 Bad Request: Invalid data provided
    """
    serializer = RepositoryWriteSerializer(
        data=request.data,
        context={'request': request}
    )
    if serializer.is_valid():
        repository = serializer.save()

        response_serializer = RepositorySerializer(repository).data
        created = serializer.context.get('created', False)
        status_code = (
            status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

        return Response(
            response_serializer,
            status=status_code
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )
