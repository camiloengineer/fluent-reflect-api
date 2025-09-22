"""
Utilidades para transformar entre camelCase y snake_case
"""
import re
from typing import Dict, Any


def camel_to_snake(name: str) -> str:
    """
    Convierte camelCase a snake_case

    Examples:
        exerciseActive -> exercise_active
        languageId -> language_id
        canGenerateExercise -> can_generate_exercise
    """
    # Insertar un guión bajo antes de cualquier mayúscula que siga a una minúscula
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    # Insertar un guión bajo antes de cualquier mayúscula que siga a una minúscula o número
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def snake_to_camel(name: str) -> str:
    """
    Convierte snake_case a camelCase

    Examples:
        exercise_active -> exerciseActive
        language_id -> languageId
        can_generate_exercise -> canGenerateExercise
    """
    components = name.split('_')
    return components[0] + ''.join(word.capitalize() for word in components[1:])


def transform_dict_keys_to_snake(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforma todas las claves de un diccionario de camelCase a snake_case
    """
    if not isinstance(data, dict):
        return data

    result = {}
    for key, value in data.items():
        new_key = camel_to_snake(key)

        # Recursivamente transformar diccionarios anidados
        if isinstance(value, dict):
            result[new_key] = transform_dict_keys_to_snake(value)
        elif isinstance(value, list):
            # Transformar listas que contengan diccionarios
            result[new_key] = [
                transform_dict_keys_to_snake(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[new_key] = value

    return result


def transform_dict_keys_to_camel(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforma todas las claves de un diccionario de snake_case a camelCase
    """
    if not isinstance(data, dict):
        return data

    result = {}
    for key, value in data.items():
        new_key = snake_to_camel(key)

        # Recursivamente transformar diccionarios anidados
        if isinstance(value, dict):
            result[new_key] = transform_dict_keys_to_camel(value)
        elif isinstance(value, list):
            # Transformar listas que contengan diccionarios
            result[new_key] = [
                transform_dict_keys_to_camel(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[new_key] = value

    return result