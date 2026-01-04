"""
Repository serializers module.

This module defines serializers for the Repository model, handling
data validation and serialization for API endpoints.
"""
import re

from rest_framework import serializers

from .models import Repository


class RepositorySerializer(serializers.ModelSerializer):
    """
    Serializer for reading Repository data.
    
    Provides a complete representation of a repository including
    all fields for API responses.
    """
    class Meta:
        model = Repository
        fields = [
            'id',
            'owner',
            'repo_name',
            'repo_url',
            'status',
            'created_at',
            'updated_at',
            'last_analyzed_at'
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'last_analyzed_at'
        ]


class RepositoryWriteSerializer(serializers.ModelSerializer):
    """
    Serializer for creating Repository instances from GitHub URLs.
    
    Validates GitHub repository URLs and extracts owner and repository
    name information. Creates or retrieves existing repository records.
    """
    repo_url = serializers.CharField(
        max_length=255,
        write_only=True
    )

    class Meta:
        model = Repository
        fields = [
            'repo_url'
        ]

    def validate_repo_url(self, value):
        """
        Validate and normalize GitHub repository URLs.
        
        Accepts URLs in formats:
        - https://github.com/owner/repo
        - https://github.com/owner/repo.git
        - https://github.com/owner/repo/
        
        Args:
            value (str): The repository URL to validate.
            
        Returns:
            str: Normalized repository URL without .git suffix.
            
        Raises:
            serializers.ValidationError: If URL format is invalid.
        """
        # https://github.com/owner/repo
        # https://github.com/owner/repo.git
        pattern = (
            r'^https:\/\/github\.com\/([^\/]+)\/([^\/\.]+)(\.git)?\/?$'
        )
        match = re.match(pattern, value)
        if not match:
            raise serializers.ValidationError(
                'Invalid repository URL format.'
            )

        owner = match.group(1)
        repo_name = match.group(2)

        self.context['owner'] = owner
        self.context['repo_name'] = repo_name

        return f'https://github.com/{owner}/{repo_name}'

    def create(self, validated_data):
        """
        Create or retrieve a repository instance.
        
        Uses get_or_create to avoid duplicates. Stores whether the
        repository was newly created in the context.
        
        Args:
            validated_data (dict): Validated data containing repo_url.
            
        Returns:
            Repository: The created or existing repository instance.
        """
        owner = self.context['owner']
        repo_name = self.context['repo_name']
        repo_url = validated_data['repo_url']

        repository, created = Repository.objects.get_or_create(
            owner=owner,
            repo_name=repo_name,
            defaults={
                "repo_url": repo_url
            }
        )
        self.context['created'] = created
        return repository
