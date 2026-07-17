from django.core.exceptions import ValidationError


def validate_cooking_time(value):
    if value < 1:
        raise ValidationError(
            'Время приготовления должно быть больше 0.'
        )


def validate_amount(value):
    if value < 1:
        raise ValidationError(
            'Количество должно быть больше 0.'
        )
