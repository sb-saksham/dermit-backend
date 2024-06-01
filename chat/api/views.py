import os
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.core.files.storage import default_storage
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

from chat.cv import ComputerVision

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

    def perform_create(self, serializer):

        # TODO: Write logic to check if the same user has sent the same images again. consult others

        media_root = settings.BASE_DIR
        # image_path = f"{media_root}/chat/Images/Input/{serializer.validated_data['name']}"
        image_path = f"{media_root}/chat/static/chat/images/input/{serializer.validated_data['name']}"

        with open(image_path, "wb") as destination:
            # for chunk in data["image"]:
            for chunk in serializer.validated_data["image"]:
                destination.write(chunk)

        serializer.save(user=self.request.user)

    def perform_inference(self, validated_data_list):
        
        input_paths = [
            os.path.join("chat", "static", "chat", "images", "input", image["name"])
            for image in validated_data_list
        ]

        output_dir = os.path.join(
            settings.BASE_DIR, "chat", "static", "chat", "images", "output"
        )

        cv_pipeline = ComputerVision(output_dir=output_dir)
        detected_symptoms = cv_pipeline.run_inference(input_paths_list=input_paths)
        print("detected_symptoms")
        print(detected_symptoms)
        return detected_symptoms

    @action(detail=False, methods=["POST"])
    def upload(
        self, request
    ):  ## This will automatically append a route /upload/ to the registered route of ImageViewSet -> /images/upload/
        ## Access POST on this viewset using /images/upload/ in the frontend

        fileList = request.FILES.getlist("image")
        print("=" * 100)
        image = request.data.get("image")
        is_valid = len(fileList)

        additional_message = ""
        validate_data_list = []
        for image in fileList:  # Doubt- is using loop a right choice
            validate_data = {
                "user": request.user.id,
                "name": f"{self.request.user}_{image.name.replace(' ', '_')}",
                "image": image,
                "size": image.size,
            }

            file_path = os.path.join(
                settings.BASE_DIR,
                "chat",
                "static",
                "chat",
                "images",
                "input",
                validate_data.get("name"),
            )
            if default_storage.exists(file_path):
                print("path exists")
                is_valid -= 1

                additional_message = (
                    "Skipped duplicate files, check dashboard for previous inferences"
                )

            else:
                print("path does not exists")

                print(f"serializing {validate_data['name']}")
                serializer = self.get_serializer(data=validate_data)

                if serializer.is_valid():
                    print(serializer.validated_data)
                    is_valid -= 1  # Doubt - Is there a better logic for this?
                    self.perform_create(
                        serializer
                    )  # Doubt - is there any other way to get hold of this data || now using validated_data
                    validate_data_list.append(serializer.validated_data)
                else:
                    print("serializer.errors: ", serializer.errors)
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )

        if is_valid == 0:
            detected_symptoms = []
            print("valid list")
            print(validate_data_list)
            if len(validate_data_list) > 0:
                detected_symptoms = self.perform_inference(validate_data_list)
            print("valid list end")
            # return Response(
            #     f"Image(s) uploaded successfully {additional_message}", status=status.HTTP_201_CREATED
            # )
            return Response(
                data=detected_symptoms,
                status=status.HTTP_201_CREATED,
            )
            # .status_text(f"Image(s) uploaded successfully {additional_message}")
        else:
            return Response(
                "Something went wrong try again", status=status.HTTP_400_BAD_REQUEST
            )
