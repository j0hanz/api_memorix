from rest_framework import serializers

from memorix.models import Category


def prepare_score_data(validated_data, context):
    """Prepare the score data for saving."""
    request = context.get('request')
    category_code = validated_data.pop('category')
    try:
        category = Category.objects.get(code=category_code.upper())
        validated_data['category'] = category
    except Category.DoesNotExist as err:
        raise serializers.ValidationError(
            {'category': f"Category '{category_code}' not found"}
        ) from err

    if request and hasattr(request, 'user'):
        validated_data['profile'] = request.user.profile
    else:
        raise serializers.ValidationError(
            {'profile': 'Authenticated user is required to save the score.'}
        )

    return validated_data
