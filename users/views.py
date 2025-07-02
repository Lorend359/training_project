from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.permissions import AllowAny
from .serializers import UserRegistrationSerializer


@extend_schema(
    tags=["Пользователи"],
    summary="Регистрация пользователя",
    description="Позволяет зарегистрировать нового пользователя. Возвращает email и ФИО при успешной регистрации.",
    request=UserRegistrationSerializer,
    responses={
        201: OpenApiResponse(
            response=None,
            description="Успешная регистрация. Возвращает email и ФИО."
        ),
        400: OpenApiResponse(description="Ошибка валидации данных"),
    }
)
class UserRegistrationView(APIView):
    """
    View для регистрации нового пользователя.
    Возвращает email и ФИО после успешного создания.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"email": user.email, "full_name": user.full_name},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
