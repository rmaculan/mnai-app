from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .serializers import NoteSerializer, UserSerializer, CustomTokenObtainPairSerializer
from .models import Note

# Authentication Views
class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user).data,
            "message": "User created successfully"
        }, status=status.HTTP_201_CREATED)

from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_data = serializer.validated_data
        return JsonResponse(token_data, safe=False, status=status.HTTP_200_OK)

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return blog.User.objects.get(pk=self.request.user.pk)

@api_view(['GET'])
def getRoutes(request):
    routes = [
        {
            'Endpoint': '/note/',
            'method': 'GET',
            'body': None,
            'description': 'Returns an array of notes'
        },
        {
            'Endpoint': '/note/id',
            'method': 'GET',
            'body': None,
            'description': 'Returns a single note object'
        },
        {
            'Endpoint': '/note/create/',
            'method': 'POST',
            'body': {'body': ""},
            'description': 'Creates a new note with data sent in the body of the request'
        },
        {
            'Endpoint': '/note/update/id',
            'method': 'PUT',
            'body': {'body': ""},
            'description': 'Updates a note with specific id'
        },
        {
            'Endpoint': '/note/delete/id',
            'method': 'DELETE',
            'body': None,
            'description': 'Deletes a note with specific id'
        },
        
    ]
    return Response(routes)

@api_view(['GET'])
def getNotes(request):
    notes = Note.objects.all()
    serializer = NoteSerializer(notes, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getNote(request, pk):
    note = Note.objects.get(id=pk)
    serializer = NoteSerializer(note, many=False)
    return Response(serializer.data)

@api_view(['POST'])
def createNote(request):
    data = request.data
    note = Note.objects.create(
        body=data['body']
    )
    serializer = NoteSerializer(note, many=False)
    return Response(serializer.data)

# fix the updateNote function
@api_view(['PUT'])
def updateNote(request, pk):
    data = request.data
    note = Note.objects.get(id=pk)
    serializer = NoteSerializer(note, data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)

@api_view(['DELETE'])
def deleteNote(request, pk):
    note = Note.objects.get(id=pk)
    note.delete()
    return Response('Note was deleted')
