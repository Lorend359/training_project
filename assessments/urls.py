from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssessmentViewSet, QuestionViewSet, AnswerOptionViewSet, SubmitAnswerAPIView

router = DefaultRouter()
router.register("assessments", AssessmentViewSet, basename="assessment")
router.register("questions", QuestionViewSet, basename="question")
router.register("answers", AnswerOptionViewSet, basename="answer")

urlpatterns = [
    path("", include(router.urls)),
    path("submit-answer/", SubmitAnswerAPIView.as_view(), name="submit-answer"),
]
