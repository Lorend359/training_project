from django.db import transaction

from assessments.models import UserAnswer

MAX_ATTEMPTS = 3


def submit_user_answer(user, question, selected_option):
    """
    Обрабатывает отправку ответа на вопрос:
    - запрещает больше 3 попыток;
    - не даёт отвечать, если уже был правильный ответ.
    """
    with transaction.atomic():
        previous = UserAnswer.objects.filter(user=user, question=question).select_for_update()

        if previous.filter(is_correct=True).exists():
            raise ValueError("Вы уже правильно ответили на этот вопрос.")
        if previous.count() >= MAX_ATTEMPTS:
            raise ValueError("Превышено количество попыток.")

        attempt_number = previous.count() + 1
        answer = UserAnswer.objects.create(
            user=user,
            question=question,
            selected_option=selected_option,
            is_correct=selected_option.is_correct,
            attempt_number=attempt_number,
        )
        return answer
