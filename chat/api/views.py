from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    CreateModelMixin,
)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from django.conf import settings

from chat.models import Conversation, Message, Image
from .paginaters import MessagePagination

from .serializers import MessageSerializer, ConversationSerializer, ImageSerializer
from .serializers import UserSerializer

User = get_user_model()


class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "username"

    def get_queryset(self, *args, **kwargs):
        assert isinstance(self.request.user.id, int)
        return self.queryset.filter(id=self.request.user.id)

    @action(detail=False)
    def me(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class CustomObtainAuthTokenView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "username": user.username})


class ConversationViewSet(
    CreateModelMixin, ListModelMixin, RetrieveModelMixin, GenericViewSet
):
    serializer_class = ConversationSerializer
    queryset = Conversation.objects.none()
    lookup_field = "id"

    def get_queryset(self):
        queryset = Conversation.objects.filter(user=self.request.user)
        return queryset

    def get_serializer_context(self):
        return {"request": self.request, "user": self.request.user}

    def create(self, request, *args, **kwargs):
        self.request.data["user"] = self.request.user.pk
        return super().create(request, *args, **kwargs)


class MessageViewSet(ListModelMixin, GenericViewSet):
    serializer_class = MessageSerializer
    queryset = Message.objects.none()
    pagination_class = MessagePagination

    def get_queryset(self):
        conversation_id = self.request.GET.get("conversation")
        queryset = (
            Message.objects.filter(
                from_user=self.request.user,
            )
            .filter(conversation__id=conversation_id)
            .order_by("-timestamp")
        )
        return queryset


class ImageViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = ImageSerializer
    # permission_classes = [IsAuthenticated]  #
    parser_classes = [MultiPartParser]

    def get_queryset(self):
        return Image.objects.filter(user=self.request.user)

    def perform_create(self, serializer, data):
        
        # TODO: Write logic to check if the same user has sent the same images again. consult others

        image = serializer.save(user=self.request.user)

        # filename with underscores
        filename = f"{image.name.replace(' ', '_')}"
        media_root = settings.BASE_DIR
        image_path = f"{media_root}/chat/Images/{filename}"

        with open(image_path, "wb") as destination:
            # for chunk in data["image"]:
            for chunk in serializer.validated_data["image"]:
                destination.write(chunk)

        # Update the image object with the saved filename
        image.filename = filename
        image.save()

    @action(detail=False, methods=["POST"])
    def upload(self, request): ## This will automatically append a route /upload/ to the registered route of ImageViewSet -> /images/upload/
                               ## Access POST on this viewset using /images/upload/ in the frontend

        fileList = request.FILES.getlist("image")

        print("=" * 100)
        image = request.data.get("image")
        is_valid = len(fileList)
        
        for image in fileList: # Doubt- is using loop a right choice
            validate_data = {
                "user": 3,
                "name": image.name,
                "image": image,
                "size": image.size,
            }
            print(f"serializing {validate_data['name']}")
            serializer = self.get_serializer(data=validate_data)
            if serializer.is_valid():
                print("serial")
                print(serializer.validated_data)
                print(serializer.validated_data["image"])
                is_valid -= 1 # Doubt - Is there a better logic for this?
                self.perform_create(serializer, data=validate_data) # Doubt - is there any other way to get hold of this data || now using validated_data 
            else:
                print("serializer.errors: ", serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if is_valid == 0:
            return Response("Image(s) uploaded successfully", status=status.HTTP_201_CREATED)
        else:
            return Response("Something went wrong try again", status=status.HTTP_400_BAD_REQUEST)
