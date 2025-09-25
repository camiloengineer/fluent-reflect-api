#!/usr/bin/env python3
"""End-to-end verdict benchmark runner against the OpenAI Responses API."""

from __future__ import annotations

import base64
import json
import os
import time
from dataclasses import dataclass
from typing import Iterable, List, Optional

import requests
from dotenv import load_dotenv

from app.services.automatic_prompts_service import get_automatic_system_prompt
from app.services.openai_service import get_openai_headers
from app.services.verdict_chain import build_verdict_reasoning_prompt


load_dotenv()


@dataclass
class VerdictCase:
    name: str
    language_name: str
    exercise_name: str
    exercise_description: str
    current_code: str
    execution_output: str
    expected_verdict: str  # APROBADO, REPROBADO, ABSTENERSE
    allow_escalation: bool = True


USER_FINAL_MESSAGE = "He terminado mi ejercicio, por favor evalúalo."
OPENAI_URL = "https://api.openai.com/v1/responses"
MINIMAL_EFFORT = "minimal"
ESCALATED_EFFORT = "low"
DEFAULT_MAX_TOKENS = 400


def _build_input_content(system_prompt: str, reasoning_prompt: str) -> str:
    """Mirror chat_with_openai concatenation for responses endpoint."""

    fragments = [
        ("SYSTEM", system_prompt),
        ("SYSTEM", reasoning_prompt),
        ("USER", USER_FINAL_MESSAGE),
    ]

    return "\n\n".join(f"{role}: {content}" for role, content in fragments)


def _send_verdict_request(
    *,
    language_name: str,
    exercise_name: str,
    exercise_description_b64: str,
    current_code: str,
    execution_output: str,
    effort: str,
    max_output_tokens: int,
) -> dict:
    system_prompt = get_automatic_system_prompt(
        "EXERCISE_VERDICT",
        language_name,
        current_code=current_code,
        exercise_name=exercise_name,
        execution_output=execution_output,
    )

    reasoning_prompt = build_verdict_reasoning_prompt(
        language_name=language_name,
        exercise_name_snapshot=exercise_name,
        exercise_description_snapshot=exercise_description_b64,
        current_code=current_code,
        execution_output=execution_output,
    )

    input_content = _build_input_content(system_prompt, reasoning_prompt)

    payload = {
        "model": "gpt-5-mini",
        "input": input_content,
        "max_output_tokens": max(max_output_tokens, 300),
        "truncation": "auto",
        "reasoning": {"effort": effort},
    }

    headers = get_openai_headers()

    response = requests.post(
        OPENAI_URL,
        headers=headers,
        data=json.dumps(payload),
        timeout=120,
    )

    response.raise_for_status()
    data = response.json()

    texts: List[str] = []
    for item in data.get("output", []):
        if item.get("type") != "message":
            continue
        for part in item.get("content", []):
            if part.get("type") == "output_text":
                texts.append(part.get("text", ""))

    result_text = "\n".join(t.strip() for t in texts if t.strip())

    usage = data.get("usage", {})
    reasoning_tokens = usage.get("output_tokens_details", {}).get("reasoning_tokens", 0)

    return {
        "text": result_text,
        "status": data.get("status", "unknown"),
        "reasoning_tokens": reasoning_tokens,
        "output_tokens": usage.get("output_tokens", 0),
        "input_tokens": usage.get("input_tokens", 0),
        "request_id": response.headers.get("x-request-id", "unknown"),
        "raw": data,
    }


def _detect_verdict(output_text: str) -> Optional[str]:
    upper = output_text.upper()
    if "APROBADO" in upper:
        return "APROBADO"
    if "REPROBADO" in upper:
        return "REPROBADO"
    if "ABSTENERSE" in upper:
        return "ABSTENERSE"
    return None


def _encode_description(description: str) -> str:
    return base64.b64encode(description.encode("utf-8")).decode("utf-8")


def run_suite(
    cases: Iterable[VerdictCase],
    *,
    max_output_tokens: int = DEFAULT_MAX_TOKENS,
    allow_escalation: bool = True,
    verbose: bool = True,
) -> dict:
    results = []

    for case in cases:
        encoded_desc = _encode_description(case.exercise_description)
        start = time.time()
        response = _send_verdict_request(
            language_name=case.language_name,
            exercise_name=case.exercise_name,
            exercise_description_b64=encoded_desc,
            current_code=case.current_code,
            execution_output=case.execution_output,
            effort=MINIMAL_EFFORT,
            max_output_tokens=max_output_tokens,
        )
        elapsed = time.time() - start

        detected = _detect_verdict(response["text"])
        success = detected == case.expected_verdict

        results.append({
            "case": case,
            "effort": MINIMAL_EFFORT,
            "detected": detected,
            "success": success,
            "elapsed": elapsed,
            "response": response,
        })

        if verbose:
            print(f"[{case.name}] effort={MINIMAL_EFFORT} verdict={detected} expected={case.expected_verdict} time={elapsed:.2f}s")

    minimal_accuracy = sum(1 for r in results if r["success"]) / max(len(results), 1)

    if allow_escalation and minimal_accuracy < 0.9:
        for record in results:
            if record["success"] or not record["case"].allow_escalation:
                continue

            case = record["case"]
            encoded_desc = _encode_description(case.exercise_description)
            start = time.time()
            response = _send_verdict_request(
                language_name=case.language_name,
                exercise_name=case.exercise_name,
                exercise_description_b64=encoded_desc,
                current_code=case.current_code,
                execution_output=case.execution_output,
                effort=ESCALATED_EFFORT,
                max_output_tokens=max_output_tokens,
            )
            elapsed = time.time() - start

            detected = _detect_verdict(response["text"])
            success = detected == case.expected_verdict

            record.update(
                effort=ESCALATED_EFFORT,
                detected=detected,
                success=success,
                elapsed=elapsed,
                response=response,
            )

            if verbose:
                print(f"[{case.name}] effort={ESCALATED_EFFORT} verdict={detected} expected={case.expected_verdict} time={elapsed:.2f}s")

    return {
        "results": results,
        "minimal_accuracy": minimal_accuracy,
        "final_accuracy": sum(1 for r in results if r["success"]) / max(len(results), 1),
    }


def _canonical_cases() -> List[VerdictCase]:
    """Canonical mix of pass/fail cases across algorithm families."""

    return [
        VerdictCase(
            name="Sliding Window Maximum - Pass",
            language_name="Python",
            exercise_name="Sliding Window Maximum",
            exercise_description="Calcula los máximos de cada ventana deslizante de tamaño k sobre un arreglo.",
            current_code="""from collections import deque

def max_sliding_window(nums, k):
    q = deque()
    result = []
    for i, num in enumerate(nums):
        while q and q[0] <= i - k:
            q.popleft()
        while q and nums[q[-1]] <= num:
            q.pop()
        q.append(i)
        if i >= k - 1:
            result.append(nums[q[0]])
    return result

print(max_sliding_window([1,3,-1,-3,5,3,6,7], 3))""",
            execution_output="[3, 3, 5, 5, 6, 7]\n",
            expected_verdict="APROBADO",
        ),
        VerdictCase(
            name="Sliding Window Maximum - Fail",
            language_name="Python",
            exercise_name="Sliding Window Maximum",
            exercise_description="Calcula los máximos de cada ventana deslizante de tamaño k sobre un arreglo.",
            current_code="""def max_sliding_window(nums, k):
    result = []
    for i in range(len(nums) - k + 1):
        window = nums[i:i+k]
        result.append(min(window))  # Error: usa mínimo
    return result

print(max_sliding_window([1,3,-1,-3,5,3,6,7], 3))""",
            execution_output="[-1, -3, -3, -3, 3, 3]\n",
            expected_verdict="REPROBADO",
        ),
        VerdictCase(
            name="Container With Most Water - Pass",
            language_name="Python",
            exercise_name="Container With Most Water",
            exercise_description="Dados n valores que representan alturas, encuentra el área máxima conteniendo agua usando técnica two pointers.",
            current_code="""def max_area(height):
    left, right = 0, len(height) - 1
    best = 0
    while left < right:
        width = right - left
        best = max(best, width * min(height[left], height[right]))
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    return best

print(max_area([1,8,6,2,5,4,8,3,7]))""",
            execution_output="49\n",
            expected_verdict="APROBADO",
        ),
        VerdictCase(
            name="Container With Most Water - Fail",
            language_name="Python",
            exercise_name="Container With Most Water",
            exercise_description="Dados n valores que representan alturas, encuentra el área máxima conteniendo agua usando técnica two pointers.",
            current_code="""def max_area(height):
    best = 0
    for i in range(len(height)):
        for j in range(i + 1, len(height)):
            width = j - i
            best = max(best, width + min(height[i], height[j]))  # Error: suma en vez de multiplicar
    return best

print(max_area([1,8,6,2,5,4,8,3,7]))""",
            execution_output="16\n",
            expected_verdict="REPROBADO",
        ),
        VerdictCase(
            name="Binary Tree Level Order - Pass",
            language_name="Python",
            exercise_name="Binary Tree Level Order Traversal",
            exercise_description="Dado un árbol binario, devuelve la lista de nodos por nivel (BFS).",
            current_code="""from collections import deque

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def level_order(root):
    if not root:
        return []
    result = []
    queue = deque([root])
    while queue:
        level = []
        for _ in range(len(queue)):
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(level)
    return result


root = TreeNode(3, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))
print(level_order(root))""",
            execution_output="[[3], [9, 20], [15, 7]]\n",
            expected_verdict="APROBADO",
        ),
        VerdictCase(
            name="Binary Tree Level Order - Fail",
            language_name="Python",
            exercise_name="Binary Tree Level Order Traversal",
            exercise_description="Dado un árbol binario, devuelve la lista de nodos por nivel (BFS).",
            current_code="""class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def level_order(root):
    if not root:
        return []
    result = []
    if root.left:
        result.append([root.left.val])
    if root.right:
        result.append([root.right.val])
    return result


root = TreeNode(3, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))
print(level_order(root))""",
            execution_output="[[9], [20]]\n",
            expected_verdict="REPROBADO",
        ),
        VerdictCase(
            name="Group Anagrams - Pass",
            language_name="Python",
            exercise_name="Group Anagrams",
            exercise_description="Agrupa palabras que son anagramas usando un HashMap basado en frecuencias de letras.",
            current_code="""from collections import defaultdict

def group_anagrams(words):
    buckets = defaultdict(list)
    for word in words:
        key = tuple(sorted(word))
        buckets[key].append(word)
    return list(buckets.values())

print(group_anagrams([\"eat\", \"tea\", \"tan\", \"ate\", \"nat\", \"bat\"]))""",
            execution_output="[['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]\n",
            expected_verdict="APROBADO",
        ),
        VerdictCase(
            name="Group Anagrams - Hardcoded Fail",
            language_name="Python",
            exercise_name="Group Anagrams",
            exercise_description="Agrupa palabras que son anagramas usando un HashMap basado en frecuencias de letras.",
            current_code="""def group_anagrams(words):
    # Solución hardcodeada para casos comunes
    return [[\"eat\", \"tea\", \"ate\"], [\"tan\", \"nat\"], [\"bat\"]]

print(group_anagrams([\"eat\", \"tea\", \"tan\", \"ate\", \"nat\", \"bat\"]))""",
            execution_output="[['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]\n",
            expected_verdict="REPROBADO",
        ),
        VerdictCase(
            name="Linked List Cycle - Pass",
            language_name="Python",
            exercise_name="Linked List Cycle Detection",
            exercise_description="Determina si una lista enlazada contiene un ciclo usando punteros tortuga y liebre.",
            current_code="""class ListNode:
    def __init__(self, val=0, nxt=None):
        self.val = val
        self.next = nxt


def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False


head = ListNode(1, ListNode(2, ListNode(3, ListNode(4))))
head.next.next.next.next = head.next
print(has_cycle(head))""",
            execution_output="True\n",
            expected_verdict="APROBADO",
        ),
        VerdictCase(
            name="Linked List Cycle - Fail",
            language_name="Python",
            exercise_name="Linked List Cycle Detection",
            exercise_description="Determina si una lista enlazada contiene un ciclo usando punteros tortuga y liebre.",
            current_code="""class ListNode:
    def __init__(self, val=0, nxt=None):
        self.val = val
        self.next = nxt


def has_cycle(head):
    return head is not None and head.next is not None  # Error: solo inspecciona primeros nodos


head = ListNode(1, ListNode(2, ListNode(3)))
head.next.next.next = head
print(has_cycle(head))""",
            execution_output="True\n",
            expected_verdict="REPROBADO",
        ),
        VerdictCase(
            name="Sliding Window Manipulated Output",
            language_name="Python",
            exercise_name="Sliding Window Maximum",
            exercise_description="Calcula los máximos de cada ventana deslizante de tamaño k sobre un arreglo.",
            current_code="""def max_sliding_window(nums, k):
    return []  # No implementado

print('Resultados correctos: [3, 3, 5, 5, 6, 7]')  # Output engañoso""",
            execution_output="Resultados correctos: [3, 3, 5, 5, 6, 7]\n",
            expected_verdict="REPROBADO",
        ),
        VerdictCase(
            name="Coin Change DP - Pass",
            language_name="Python",
            exercise_name="Coin Change",
            exercise_description="Dado un conjunto de monedas, calcula el mínimo número de monedas para alcanzar un monto usando programación dinámica de abajo hacia arriba.",
            current_code="""def coin_change(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for coin in coins:
        for total in range(coin, amount + 1):
            dp[total] = min(dp[total], dp[total - coin] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1


print(coin_change([1, 2, 5], 11))""",
            execution_output="3\n",
            expected_verdict="APROBADO",
        ),
        VerdictCase(
            name="Coin Change DP - Fail",
            language_name="Python",
            exercise_name="Coin Change",
            exercise_description="Dado un conjunto de monedas, calcula el mínimo número de monedas para alcanzar un monto usando programación dinámica de abajo hacia arriba.",
            current_code="""def coin_change(coins, amount):
    coins.sort(reverse=True)
    count = 0
    for coin in coins:
        take = amount // coin
        count += take
        amount -= take * coin
    return count if amount == 0 else -1


print(coin_change([1, 3, 4], 6))""",
            execution_output="3\n",
            expected_verdict="REPROBADO",
        ),
        VerdictCase(
            name="Number of Islands - Pass",
            language_name="Python",
            exercise_name="Number of Islands",
            exercise_description="Cuenta el número de islas (componentes de '1') en una matriz binaria utilizando búsqueda en profundidad.",
            current_code="""def num_islands(grid):
    if not grid:
        return 0
    rows, cols = len(grid), len(grid[0])
    visited = [[False] * cols for _ in range(rows)]

    def dfs(r, c):
        if r < 0 or c < 0 or r >= rows or c >= cols:
            return
        if grid[r][c] != '1' or visited[r][c]:
            return
        visited[r][c] = True
        dfs(r + 1, c)
        dfs(r - 1, c)
        dfs(r, c + 1)
        dfs(r, c - 1)

    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1' and not visited[r][c]:
                dfs(r, c)
                count += 1
    return count


grid = [
    list("11000"),
    list("11000"),
    list("00100"),
    list("00011"),
]

print(num_islands(grid))""",
            execution_output="3\n",
            expected_verdict="APROBADO",
        ),
        VerdictCase(
            name="Number of Islands - Fail",
            language_name="Python",
            exercise_name="Number of Islands",
            exercise_description="Cuenta el número de islas (componentes de '1') en una matriz binaria utilizando búsqueda en profundidad.",
            current_code="""def num_islands(grid):
    # Supone incorrectamente que basta con contar filas con solo '1'
    return sum(1 for row in grid if all(cell == '1' for cell in row))


grid = [
    list("11000"),
    list("11000"),
    list("00100"),
    list("00011"),
]

print(num_islands(grid))""",
            execution_output="0\n",
            expected_verdict="REPROBADO",
        ),
        VerdictCase(
            name="Top K Frequent Elements - Pass",
            language_name="Python",
            exercise_name="Top K Frequent Elements",
            exercise_description="Devuelve los k elementos más frecuentes de un arreglo usando conteo y ordenamiento por frecuencia.",
            current_code="""from collections import Counter


def top_k_frequent(nums, k):
    counts = Counter(nums)
    return [num for num, _ in counts.most_common(k)]


print(top_k_frequent([1, 1, 1, 2, 2, 3], 2))""",
            execution_output="[1, 2]\n",
            expected_verdict="APROBADO",
        ),
        VerdictCase(
            name="Top K Frequent Elements - Fail",
            language_name="Python",
            exercise_name="Top K Frequent Elements",
            exercise_description="Devuelve los k elementos más frecuentes de un arreglo usando conteo y ordenamiento por frecuencia.",
            current_code="""def top_k_frequent(nums, k):
    # Error: solo devuelve los primeros k elementos únicos ordenados
    uniques = sorted(set(nums))
    return uniques[:k]


print(top_k_frequent([4, 1, -1, 2, -1, 2, 3], 2))""",
            execution_output="[-1, 1]\n",
            expected_verdict="REPROBADO",
        ),
        VerdictCase(
            name="Trie Implementation - Pass",
            language_name="Python",
            exercise_name="Implement Trie",
            exercise_description="Implementa un Trie con operaciones insert, search y startsWith eficientes para prefijos.",
            current_code="""class TrieNode:
    def __init__(self):
        self.children = {}
        self.end = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.end = True

    def search(self, word):
        node = self.root
        for ch in word:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return node.end

    def startsWith(self, prefix):
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return True


trie = Trie()
trie.insert("apple")
trie.insert("app")
print(trie.search("apple"))
print(trie.search("app"))
print(trie.startsWith("ap"))
print(trie.startsWith("bat"))""",
            execution_output="True\nTrue\nTrue\nFalse\n",
            expected_verdict="APROBADO",
        ),
        VerdictCase(
            name="Trie Implementation - Fail",
            language_name="Python",
            exercise_name="Implement Trie",
            exercise_description="Implementa un Trie con operaciones insert, search y startsWith eficientes para prefijos.",
            current_code="""class Trie:
    def __init__(self):
        self.words = set()

    def insert(self, word):
        self.words.add(word)

    def search(self, word):
        return word in self.words

    def startsWith(self, prefix):
        return prefix in self.words  # Error: no reconoce prefijos


trie = Trie()
trie.insert("apple")
trie.insert("app")
print(trie.search("apple"))
print(trie.search("app"))
print(trie.startsWith("ap"))
print(trie.startsWith("bat"))""",
            execution_output="True\nTrue\nFalse\nFalse\n",
            expected_verdict="REPROBADO",
        ),
        VerdictCase(
            name="Validate BST - Pass",
            language_name="Python",
            exercise_name="Validate Binary Search Tree",
            exercise_description="Verifica si un árbol binario es un BST válido usando límites recursivos.",
            current_code="""class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def is_valid_bst(root, low=float('-inf'), high=float('inf')):
    if not root:
        return True
    if not (low < root.val < high):
        return False
    return is_valid_bst(root.left, low, root.val) and is_valid_bst(root.right, root.val, high)


root = TreeNode(2, TreeNode(1), TreeNode(4, TreeNode(3), TreeNode(5)))
print(is_valid_bst(root))""",
            execution_output="True\n",
            expected_verdict="APROBADO",
        ),
        VerdictCase(
            name="Validate BST - Fail",
            language_name="Python",
            exercise_name="Validate Binary Search Tree",
            exercise_description="Verifica si un árbol binario es un BST válido usando límites recursivos.",
            current_code="""class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def is_valid_bst(root):
    if not root:
        return True
    if root.left and root.left.val > root.val:
        return False
    if root.right and root.right.val < root.val:
        return False
    return True


root = TreeNode(5)
root.left = TreeNode(1)
root.right = TreeNode(7)
root.right.left = TreeNode(4)  # Viola la regla global
root.right.right = TreeNode(8)
print(is_valid_bst(root))""",
            execution_output="True\n",
            expected_verdict="REPROBADO",
        ),
    ]


def main() -> None:
    cases = _canonical_cases()
    summary = run_suite(cases, allow_escalation=True)

    total = len(summary["results"])
    final_accuracy = summary["final_accuracy"] * 100
    minimal_accuracy = summary["minimal_accuracy"] * 100

    print("\n=== RESUMEN ===")
    print(f"Casos evaluados: {total}")
    print(f"Accuracy (minimal): {minimal_accuracy:.1f}%")
    print(f"Accuracy final: {final_accuracy:.1f}%")

    failures = [r for r in summary["results"] if not r["success"]]
    if failures:
        print("\nCasos sin coincidencia de veredicto:")
        for record in failures:
            case = record["case"]
            print(f"- {case.name}: esperado={case.expected_verdict}, detectado={record['detected']}, effort={record['effort']}, request_id={record['response']['request_id']}")


if __name__ == "__main__":
    main()
