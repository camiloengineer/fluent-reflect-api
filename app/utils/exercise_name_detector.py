"""
Utility to detect concrete coding exercises being discussed and extract their names
"""
import re
from typing import Optional, Tuple

def detect_concrete_exercise(response_text: str) -> Tuple[bool, Optional[str]]:
    """
    Detect if the AI response is discussing a concrete, named coding exercise.

    Returns:
        Tuple[bool, Optional[str]]: (is_concrete_exercise, exercise_name)
        - is_concrete_exercise: True if discussing a specific coding exercise
        - exercise_name: Name of the exercise if detected, None otherwise
    """
    if not response_text:
        return False, None

    text_lower = response_text.lower()

    # Known concrete exercises with their canonical names
    concrete_exercises = {
        # Classic algorithms
        r"fizz\s*buzz": "FizzBuzz",
        r"palíndromo|palindromo": "Palindromo",
        r"fibonacci": "Fibonacci",
        r"factorial": "Factorial",
        r"números?\s+primos?|numeros?\s+primos?": "Números Primos",

        # Data structures
        r"árbol\s+binario|arbol\s+binario": "Árbol Binario",
        r"lista\s+enlazada": "Lista Enlazada",
        r"pila|stack": "Pila (Stack)",
        r"cola|queue": "Cola (Queue)",
        r"hash\s+table|tabla\s+hash": "Tabla Hash",

        # Sorting algorithms
        r"bubble\s+sort|ordenamiento\s+burbuja": "Bubble Sort",
        r"quick\s+sort|ordenamiento\s+rápido": "Quick Sort",
        r"merge\s+sort|ordenamiento\s+por\s+mezcla": "Merge Sort",
        r"insertion\s+sort|ordenamiento\s+por\s+inserción": "Insertion Sort",

        # Search algorithms
        r"búsqueda\s+binaria|busqueda\s+binaria|binary\s+search": "Búsqueda Binaria",
        r"búsqueda\s+lineal|busqueda\s+lineal|linear\s+search": "Búsqueda Lineal",

        # String algorithms
        r"anagrama": "Anagrama",
        r"subcadena|substring": "Subcadena",
        r"cadena\s+más\s+larga|cadena\s+mas\s+larga": "Cadena más Larga",

        # Array problems
        r"máximo\s+subarray|maximo\s+subarray": "Máximo Subarray",
        r"dos\s+sumas?|two\s+sum": "Two Sum",
        r"rotar\s+array|rotate\s+array": "Rotar Array",

        # Math problems
        r"números?\s+armstrong|numeros?\s+armstrong": "Números Armstrong",
        r"suma\s+de\s+dígitos|suma\s+de\s+digitos": "Suma de Dígitos",
        r"conversión\s+de\s+base|conversion\s+de\s+base": "Conversión de Base",

        # Game problems
        r"juego\s+de\s+la\s+vida|game\s+of\s+life": "Juego de la Vida",
        r"sudoku": "Sudoku",
        r"torre\s+de\s+hanoi": "Torre de Hanoi",

        # Web/practical
        r"validador\s+de\s+email": "Validador de Email",
        r"generador\s+de\s+contraseña": "Generador de Contraseña",
        r"calculadora": "Calculadora",
        r"to\s*do\s+list|lista\s+de\s+tareas": "Lista de Tareas",
    }

    # Check for concrete exercise names
    for pattern, exercise_name in concrete_exercises.items():
        if re.search(pattern, text_lower):
            return True, exercise_name

    # Check for algorithm categories that suggest concrete exercises
    algorithm_categories = [
        r"divide\s+y\s+conquista|divide\s+and\s+conquer",
        r"programación\s+dinámica|dynamic\s+programming",
        r"backtracking",
        r"algoritmo\s+voraz|greedy\s+algorithm",
        r"grafos|graphs",
    ]

    for pattern in algorithm_categories:
        if re.search(pattern, text_lower):
            # For algorithm categories, check if it's offering a specific implementation
            if re.search(r"implementar|ejemplo|ejercicio|práctica", text_lower):
                # Extract the algorithm type as exercise name
                match = re.search(pattern, text_lower)
                if match:
                    category_name = match.group(0).title()
                    return True, f"Ejercicio de {category_name}"

    return False, None


def should_enable_generate_code_new_logic(
    response_text: str,
    request_generar_codigo: bool
) -> Tuple[bool, Optional[str]]:
    """
    New logic for determining generarCodigo flag and exercise name.

    Args:
        response_text: AI response text
        request_generar_codigo: Current state from request

    Returns:
        Tuple[bool, Optional[str]]: (generarCodigo_response, nombreEjercicio)
    """

    # If request has generarCodigo=True, always respond with False
    # (exercise in progress, don't offer more)
    if request_generar_codigo:
        return False, None

    # If request has generarCodigo=False, check if we're discussing a concrete exercise
    is_concrete, exercise_name = detect_concrete_exercise(response_text)

    return is_concrete, exercise_name