from django.shortcuts import render
from rest_framework import viewsets

from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.status import HTTP_200_OK

class CategoryViewSet(viewsets.ViewSet):
    def list(self, request: Request) -> Response:
        return Response(
            status=HTTP_200_OK,
            data={
                "categories": [
                    {"id": 1, "name": "Filme", "description": "Longas divertidos", "is_active": True},
                    {"id": 2, "name": "Séries", "description": "Curtas divertidas", "is_active": True},
                    {"id": 3, "name": "Documentários", "description": "Curtas informativas", "is_active": True},
                ]
            },
            
        )