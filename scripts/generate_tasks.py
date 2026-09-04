"""One-off generator: defines the 24-task set as Python data (raw strings,
no YAML-escaping headaches) and writes each to tasks/<id>.yaml. Re-run
after editing a task definition below; the committed tasks/*.yaml files are
the source of truth going forward, this script is just how they were
authored and how a new task gets added.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from modelbench.tasks import Task  # noqa: E402  (needs the sys.path insert above)

TASKS: list[Task] = [
    Task(
        id="t01_sum_list",
        category="trivial",
        prompt="Write a function that returns the sum of a list of integers.",
        entry_point="sum_list",
        reference_solution="def sum_list(numbers):\n    return sum(numbers)\n",
        test_code=(
            "from solution import sum_list\n\n"
            "def test_basic():\n"
            "    assert sum_list([1, 2, 3]) == 6\n\n"
            "def test_empty():\n"
            "    assert sum_list([]) == 0\n\n"
            "def test_negatives():\n"
            "    assert sum_list([-1, -2, 3]) == 0\n"
        ),
    ),
    Task(
        id="t02_is_palindrome",
        category="trivial",
        prompt="Write a function that returns True if a given string is a palindrome (reads the same forwards and backwards), ignoring case, and False otherwise.",
        entry_point="is_palindrome",
        reference_solution="def is_palindrome(s):\n    s = s.lower()\n    return s == s[::-1]\n",
        test_code=(
            "from solution import is_palindrome\n\n"
            "def test_palindrome():\n"
            "    assert is_palindrome('level') is True\n\n"
            "def test_case_insensitive():\n"
            "    assert is_palindrome('Level') is True\n\n"
            "def test_not_palindrome():\n"
            "    assert is_palindrome('hello') is False\n\n"
            "def test_single_char():\n"
            "    assert is_palindrome('a') is True\n"
        ),
    ),
    Task(
        id="t03_fizzbuzz",
        category="trivial",
        prompt="Write a function that takes an integer n and returns a list of strings from 1 to n, where multiples of 3 are 'Fizz', multiples of 5 are 'Buzz', multiples of both are 'FizzBuzz', and all other numbers are their string form.",
        entry_point="fizzbuzz",
        reference_solution=(
            "def fizzbuzz(n):\n"
            "    result = []\n"
            "    for i in range(1, n + 1):\n"
            "        if i % 15 == 0:\n"
            "            result.append('FizzBuzz')\n"
            "        elif i % 3 == 0:\n"
            "            result.append('Fizz')\n"
            "        elif i % 5 == 0:\n"
            "            result.append('Buzz')\n"
            "        else:\n"
            "            result.append(str(i))\n"
            "    return result\n"
        ),
        test_code=(
            "from solution import fizzbuzz\n\n"
            "def test_fifteen():\n"
            "    out = fizzbuzz(15)\n"
            "    assert out[2] == 'Fizz'\n"
            "    assert out[4] == 'Buzz'\n"
            "    assert out[14] == 'FizzBuzz'\n"
            "    assert out[0] == '1'\n\n"
            "def test_length():\n"
            "    assert len(fizzbuzz(20)) == 20\n"
        ),
    ),
    Task(
        id="t04_max_of_three",
        category="trivial",
        prompt="Write a function that takes three numbers and returns the largest one.",
        entry_point="max_of_three",
        reference_solution="def max_of_three(a, b, c):\n    return max(a, b, c)\n",
        test_code=(
            "from solution import max_of_three\n\n"
            "def test_first_largest():\n"
            "    assert max_of_three(5, 2, 3) == 5\n\n"
            "def test_negatives():\n"
            "    assert max_of_three(-5, -2, -3) == -2\n\n"
            "def test_ties():\n"
            "    assert max_of_three(4, 4, 2) == 4\n"
        ),
    ),
    Task(
        id="t05_count_vowels",
        category="trivial",
        prompt="Write a function that counts the number of vowels (a, e, i, o, u, case-insensitive) in a given string.",
        entry_point="count_vowels",
        reference_solution="def count_vowels(s):\n    return sum(1 for ch in s.lower() if ch in 'aeiou')\n",
        test_code=(
            "from solution import count_vowels\n\n"
            "def test_basic():\n"
            "    assert count_vowels('hello world') == 3\n\n"
            "def test_uppercase():\n"
            "    assert count_vowels('HELLO') == 2\n\n"
            "def test_no_vowels():\n"
            "    assert count_vowels('xyz') == 0\n"
        ),
    ),
    Task(
        id="t06_group_anagrams",
        category="standard",
        prompt="Write a function that takes a list of strings and groups the anagrams together, returning a list of lists. Words that are anagrams of each other (same letters, any order) go in the same group. The order of groups and the order of words within a group do not matter for correctness.",
        entry_point="group_anagrams",
        reference_solution=(
            "def group_anagrams(words):\n"
            "    groups = {}\n"
            "    for word in words:\n"
            "        key = ''.join(sorted(word))\n"
            "        groups.setdefault(key, []).append(word)\n"
            "    return list(groups.values())\n"
        ),
        test_code=(
            "from solution import group_anagrams\n\n"
            "def _normalize(groups):\n"
            "    return sorted(sorted(g) for g in groups)\n\n"
            "def test_basic_grouping():\n"
            "    result = group_anagrams(['eat', 'tea', 'tan', 'ate', 'nat', 'bat'])\n"
            "    expected = [['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]\n"
            "    assert _normalize(result) == _normalize(expected)\n\n"
            "def test_empty_input():\n"
            "    assert group_anagrams([]) == []\n\n"
            "def test_no_anagrams():\n"
            "    result = group_anagrams(['abc', 'def'])\n"
            "    assert _normalize(result) == _normalize([['abc'], ['def']])\n"
        ),
    ),
    Task(
        id="t07_run_length_encode",
        category="standard",
        prompt="Write a function that run-length-encodes a string: consecutive repeated characters become the character followed by its count (e.g. 'aaab' -> 'a3b1'). A count of 1 is still written out explicitly.",
        entry_point="run_length_encode",
        reference_solution=(
            "def run_length_encode(s):\n"
            "    if not s:\n"
            "        return ''\n"
            "    result = []\n"
            "    prev = s[0]\n"
            "    count = 1\n"
            "    for ch in s[1:]:\n"
            "        if ch == prev:\n"
            "            count += 1\n"
            "        else:\n"
            "            result.append(f'{prev}{count}')\n"
            "            prev = ch\n"
            "            count = 1\n"
            "    result.append(f'{prev}{count}')\n"
            "    return ''.join(result)\n"
        ),
        test_code=(
            "from solution import run_length_encode\n\n"
            "def test_basic():\n"
            "    assert run_length_encode('aaab') == 'a3b1'\n\n"
            "def test_no_repeats():\n"
            "    assert run_length_encode('abc') == 'a1b1c1'\n\n"
            "def test_empty():\n"
            "    assert run_length_encode('') == ''\n\n"
            "def test_single_run():\n"
            "    assert run_length_encode('aaaa') == 'a4'\n"
        ),
    ),
    Task(
        id="t08_merge_intervals",
        category="standard",
        prompt="Write a function that takes a list of [start, end] interval pairs (inclusive) and merges all overlapping intervals, returning a sorted list of the merged, non-overlapping intervals.",
        entry_point="merge_intervals",
        reference_solution=(
            "def merge_intervals(intervals):\n"
            "    if not intervals:\n"
            "        return []\n"
            "    ordered = sorted(intervals, key=lambda iv: iv[0])\n"
            "    merged = [list(ordered[0])]\n"
            "    for start, end in ordered[1:]:\n"
            "        last = merged[-1]\n"
            "        if start <= last[1]:\n"
            "            last[1] = max(last[1], end)\n"
            "        else:\n"
            "            merged.append([start, end])\n"
            "    return merged\n"
        ),
        test_code=(
            "from solution import merge_intervals\n\n"
            "def test_overlapping():\n"
            "    assert merge_intervals([[1, 3], [2, 6], [8, 10]]) == [[1, 6], [8, 10]]\n\n"
            "def test_touching():\n"
            "    assert merge_intervals([[1, 4], [4, 5]]) == [[1, 5]]\n\n"
            "def test_no_overlap():\n"
            "    assert merge_intervals([[1, 2], [5, 6]]) == [[1, 2], [5, 6]]\n\n"
            "def test_unsorted_input():\n"
            "    assert merge_intervals([[5, 6], [1, 2]]) == [[1, 2], [5, 6]]\n\n"
            "def test_empty():\n"
            "    assert merge_intervals([]) == []\n"
        ),
    ),
    Task(
        id="t09_json_flatten",
        category="standard",
        prompt="Write a function that flattens a nested dictionary into a single-level dictionary, joining nested keys with a dot ('.'). For example {'a': {'b': 1, 'c': 2}} becomes {'a.b': 1, 'a.c': 2}. Lists should be left as-is (not flattened further).",
        entry_point="flatten_dict",
        reference_solution=(
            "def flatten_dict(d, prefix=''):\n"
            "    result = {}\n"
            "    for key, value in d.items():\n"
            "        full_key = f'{prefix}.{key}' if prefix else str(key)\n"
            "        if isinstance(value, dict):\n"
            "            result.update(flatten_dict(value, full_key))\n"
            "        else:\n"
            "            result[full_key] = value\n"
            "    return result\n"
        ),
        test_code=(
            "from solution import flatten_dict\n\n"
            "def test_basic():\n"
            "    assert flatten_dict({'a': {'b': 1, 'c': 2}}) == {'a.b': 1, 'a.c': 2}\n\n"
            "def test_nested_deeper():\n"
            "    assert flatten_dict({'a': {'b': {'c': 1}}}) == {'a.b.c': 1}\n\n"
            "def test_flat_input():\n"
            "    assert flatten_dict({'x': 1, 'y': 2}) == {'x': 1, 'y': 2}\n\n"
            "def test_list_left_alone():\n"
            "    assert flatten_dict({'a': {'b': [1, 2]}}) == {'a.b': [1, 2]}\n"
        ),
    ),
    Task(
        id="t10_lru_cache",
        category="standard",
        prompt="Implement a class LRUCache with a constructor taking a capacity, a get(key) method returning the value or -1 if missing, and a put(key, value) method. When capacity is exceeded, evict the least recently used item. Both get and put count as 'use' for recency purposes.",
        entry_point="LRUCache",
        reference_solution=(
            "from collections import OrderedDict\n\n"
            "class LRUCache:\n"
            "    def __init__(self, capacity):\n"
            "        self.capacity = capacity\n"
            "        self.store = OrderedDict()\n\n"
            "    def get(self, key):\n"
            "        if key not in self.store:\n"
            "            return -1\n"
            "        self.store.move_to_end(key)\n"
            "        return self.store[key]\n\n"
            "    def put(self, key, value):\n"
            "        if key in self.store:\n"
            "            self.store.move_to_end(key)\n"
            "        self.store[key] = value\n"
            "        if len(self.store) > self.capacity:\n"
            "            self.store.popitem(last=False)\n"
        ),
        test_code=(
            "from solution import LRUCache\n\n"
            "def test_basic_get_put():\n"
            "    cache = LRUCache(2)\n"
            "    cache.put(1, 'a')\n"
            "    cache.put(2, 'b')\n"
            "    assert cache.get(1) == 'a'\n\n"
            "def test_eviction():\n"
            "    cache = LRUCache(2)\n"
            "    cache.put(1, 'a')\n"
            "    cache.put(2, 'b')\n"
            "    cache.put(3, 'c')  # evicts 1, since 2 was untouched but 1 is oldest\n"
            "    assert cache.get(1) == -1\n"
            "    assert cache.get(2) == 'b'\n"
            "    assert cache.get(3) == 'c'\n\n"
            "def test_get_refreshes_recency():\n"
            "    cache = LRUCache(2)\n"
            "    cache.put(1, 'a')\n"
            "    cache.put(2, 'b')\n"
            "    cache.get(1)  # 1 is now most recently used\n"
            "    cache.put(3, 'c')  # should evict 2, not 1\n"
            "    assert cache.get(2) == -1\n"
            "    assert cache.get(1) == 'a'\n"
        ),
    ),
    Task(
        id="t11_topo_sort",
        category="standard",
        prompt="Write a function that takes an integer n (nodes numbered 0..n-1) and a list of [a, b] edges meaning 'a must come before b', and returns a valid topological ordering as a list. If no valid ordering exists (a cycle), return None.",
        entry_point="topo_sort",
        reference_solution=(
            "def topo_sort(n, edges):\n"
            "    from collections import deque\n"
            "    indegree = [0] * n\n"
            "    graph = {i: [] for i in range(n)}\n"
            "    for a, b in edges:\n"
            "        graph[a].append(b)\n"
            "        indegree[b] += 1\n"
            "    queue = deque(i for i in range(n) if indegree[i] == 0)\n"
            "    order = []\n"
            "    while queue:\n"
            "        node = queue.popleft()\n"
            "        order.append(node)\n"
            "        for nxt in graph[node]:\n"
            "            indegree[nxt] -= 1\n"
            "            if indegree[nxt] == 0:\n"
            "                queue.append(nxt)\n"
            "    return order if len(order) == n else None\n"
        ),
        test_code=(
            "from solution import topo_sort\n\n"
            "def _is_valid_order(order, n, edges):\n"
            "    if order is None or sorted(order) != list(range(n)):\n"
            "        return False\n"
            "    position = {node: i for i, node in enumerate(order)}\n"
            "    return all(position[a] < position[b] for a, b in edges)\n\n"
            "def test_valid_dag():\n"
            "    order = topo_sort(4, [[0, 1], [0, 2], [1, 3], [2, 3]])\n"
            "    assert _is_valid_order(order, 4, [[0, 1], [0, 2], [1, 3], [2, 3]])\n\n"
            "def test_cycle_returns_none():\n"
            "    assert topo_sort(3, [[0, 1], [1, 2], [2, 0]]) is None\n\n"
            "def test_no_edges():\n"
            "    order = topo_sort(3, [])\n"
            "    assert sorted(order) == [0, 1, 2]\n"
        ),
    ),
    Task(
        id="t12_word_ladder_length",
        category="standard",
        prompt="Write a function word_ladder_length(begin_word, end_word, word_list) that returns the number of words in the shortest transformation sequence from begin_word to end_word, changing one letter at a time, where every intermediate word must be in word_list. Return 0 if no such sequence exists. The length counts both begin_word and end_word.",
        entry_point="word_ladder_length",
        reference_solution=(
            "from collections import deque\n\n"
            "def word_ladder_length(begin_word, end_word, word_list):\n"
            "    words = set(word_list)\n"
            "    if end_word not in words:\n"
            "        return 0\n"
            "    queue = deque([(begin_word, 1)])\n"
            "    visited = {begin_word}\n"
            "    alphabet = 'abcdefghijklmnopqrstuvwxyz'\n"
            "    while queue:\n"
            "        word, steps = queue.popleft()\n"
            "        if word == end_word:\n"
            "            return steps\n"
            "        for i in range(len(word)):\n"
            "            for ch in alphabet:\n"
            "                candidate = word[:i] + ch + word[i + 1:]\n"
            "                if candidate in words and candidate not in visited:\n"
            "                    visited.add(candidate)\n"
            "                    queue.append((candidate, steps + 1))\n"
            "    return 0\n"
        ),
        test_code=(
            "from solution import word_ladder_length\n\n"
            "def test_reachable():\n"
            "    result = word_ladder_length('hit', 'cog', ['hot', 'dot', 'dog', 'lot', 'log', 'cog'])\n"
            "    assert result == 5\n\n"
            "def test_end_not_in_list():\n"
            "    assert word_ladder_length('hit', 'cog', ['hot', 'dot', 'dog', 'lot', 'log']) == 0\n\n"
            "def test_direct_neighbor():\n"
            "    assert word_ladder_length('hot', 'dot', ['dot']) == 2\n"
        ),
    ),
    Task(
        id="t13_median_two_sorted",
        category="hard",
        prompt="Write a function that finds the median of two sorted lists of numbers combined, in O(log(min(m, n))) time (a binary-search partition approach, not simply merging and sorting).",
        entry_point="find_median_sorted_arrays",
        reference_solution=(
            "def find_median_sorted_arrays(nums1, nums2):\n"
            "    if len(nums1) > len(nums2):\n"
            "        nums1, nums2 = nums2, nums1\n"
            "    m, n = len(nums1), len(nums2)\n"
            "    lo, hi = 0, m\n"
            "    half = (m + n + 1) // 2\n"
            "    while lo <= hi:\n"
            "        i = (lo + hi) // 2\n"
            "        j = half - i\n"
            "        left1 = nums1[i - 1] if i > 0 else float('-inf')\n"
            "        right1 = nums1[i] if i < m else float('inf')\n"
            "        left2 = nums2[j - 1] if j > 0 else float('-inf')\n"
            "        right2 = nums2[j] if j < n else float('inf')\n"
            "        if left1 <= right2 and left2 <= right1:\n"
            "            if (m + n) % 2 == 1:\n"
            "                return max(left1, left2)\n"
            "            return (max(left1, left2) + min(right1, right2)) / 2\n"
            "        elif left1 > right2:\n"
            "            hi = i - 1\n"
            "        else:\n"
            "            lo = i + 1\n"
            "    raise ValueError('input arrays are not sorted')\n"
        ),
        test_code=(
            "from solution import find_median_sorted_arrays\n\n"
            "def test_odd_total():\n"
            "    assert find_median_sorted_arrays([1, 3], [2]) == 2\n\n"
            "def test_even_total():\n"
            "    assert find_median_sorted_arrays([1, 2], [3, 4]) == 2.5\n\n"
            "def test_one_empty():\n"
            "    assert find_median_sorted_arrays([], [1]) == 1\n\n"
            "def test_disjoint_ranges():\n"
            "    assert find_median_sorted_arrays([1, 2, 3], [4, 5, 6, 7]) == 4\n"
        ),
    ),
    Task(
        id="t14_lca_binary_tree",
        category="hard",
        prompt="You're given a binary tree where each node is a dict with keys 'val', 'left', 'right' (children are None if absent, or another such dict). Write a function lowest_common_ancestor(root, p, q) that returns the value of the lowest common ancestor of the nodes with values p and q. Both p and q are guaranteed to exist in the tree.",
        entry_point="lowest_common_ancestor",
        reference_solution=(
            "def lowest_common_ancestor(root, p, q):\n"
            "    if root is None:\n"
            "        return None\n"
            "    if root['val'] == p or root['val'] == q:\n"
            "        return root['val']\n"
            "    left = lowest_common_ancestor(root.get('left'), p, q)\n"
            "    right = lowest_common_ancestor(root.get('right'), p, q)\n"
            "    if left is not None and right is not None:\n"
            "        return root['val']\n"
            "    return left if left is not None else right\n"
        ),
        test_code=(
            "from solution import lowest_common_ancestor\n\n"
            "TREE = {\n"
            "    'val': 3,\n"
            "    'left': {'val': 5, 'left': {'val': 6, 'left': None, 'right': None},\n"
            "             'right': {'val': 2, 'left': {'val': 7, 'left': None, 'right': None},\n"
            "                       'right': {'val': 4, 'left': None, 'right': None}}},\n"
            "    'right': {'val': 1, 'left': None, 'right': None},\n"
            "}\n\n"
            "def test_lca_across_subtrees():\n"
            "    assert lowest_common_ancestor(TREE, 5, 1) == 3\n\n"
            "def test_lca_within_subtree():\n"
            "    assert lowest_common_ancestor(TREE, 6, 4) == 5\n\n"
            "def test_ancestor_is_one_of_the_nodes():\n"
            "    assert lowest_common_ancestor(TREE, 5, 4) == 5\n"
        ),
    ),
    Task(
        id="t15_regex_match",
        category="hard",
        prompt="Write a function is_match(s, pattern) implementing regular expression matching supporting '.' (matches any single character) and '*' (matches zero or more of the preceding element). The match must cover the ENTIRE input string, not just a prefix.",
        entry_point="is_match",
        reference_solution=(
            "def is_match(s, pattern):\n"
            "    memo = {}\n"
            "    def dp(i, j):\n"
            "        if (i, j) in memo:\n"
            "            return memo[(i, j)]\n"
            "        if j == len(pattern):\n"
            "            result = i == len(s)\n"
            "        else:\n"
            "            first_match = i < len(s) and pattern[j] in (s[i], '.')\n"
            "            if j + 1 < len(pattern) and pattern[j + 1] == '*':\n"
            "                result = dp(i, j + 2) or (first_match and dp(i + 1, j))\n"
            "            else:\n"
            "                result = first_match and dp(i + 1, j + 1)\n"
            "        memo[(i, j)] = result\n"
            "        return result\n"
            "    return dp(0, 0)\n"
        ),
        test_code=(
            "from solution import is_match\n\n"
            "def test_star_zero_or_more():\n"
            "    assert is_match('aa', 'a*') is True\n\n"
            "def test_dot_star():\n"
            "    assert is_match('ab', '.*') is True\n\n"
            "def test_no_match():\n"
            "    assert is_match('mississippi', 'mis*is*p*.') is False\n\n"
            "def test_exact():\n"
            "    assert is_match('aab', 'c*a*b') is True\n\n"
            "def test_partial_prefix_only_should_fail():\n"
            "    assert is_match('aaa', 'a') is False\n"
        ),
    ),
    Task(
        id="t16_edit_distance",
        category="hard",
        prompt="Write a function edit_distance(word1, word2) that returns the minimum number of single-character insertions, deletions, or substitutions required to transform word1 into word2 (Levenshtein distance).",
        entry_point="edit_distance",
        reference_solution=(
            "def edit_distance(word1, word2):\n"
            "    m, n = len(word1), len(word2)\n"
            "    dp = [[0] * (n + 1) for _ in range(m + 1)]\n"
            "    for i in range(m + 1):\n"
            "        dp[i][0] = i\n"
            "    for j in range(n + 1):\n"
            "        dp[0][j] = j\n"
            "    for i in range(1, m + 1):\n"
            "        for j in range(1, n + 1):\n"
            "            if word1[i - 1] == word2[j - 1]:\n"
            "                dp[i][j] = dp[i - 1][j - 1]\n"
            "            else:\n"
            "                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])\n"
            "    return dp[m][n]\n"
        ),
        test_code=(
            "from solution import edit_distance\n\n"
            "def test_classic_example():\n"
            "    assert edit_distance('horse', 'ros') == 3\n\n"
            "def test_identical():\n"
            "    assert edit_distance('abc', 'abc') == 0\n\n"
            "def test_empty_source():\n"
            "    assert edit_distance('', 'abc') == 3\n\n"
            "def test_one_substitution():\n"
            "    assert edit_distance('cat', 'bat') == 1\n"
        ),
    ),
    Task(
        id="t17_trie_prefix_search",
        category="hard",
        prompt="Implement a class Trie with insert(word), search(word) (exact match, returns bool), and starts_with(prefix) (returns bool, True if any inserted word starts with prefix).",
        entry_point="Trie",
        reference_solution=(
            "class Trie:\n"
            "    def __init__(self):\n"
            "        self.children = {}\n"
            "        self.is_word = False\n\n"
            "    def insert(self, word):\n"
            "        node = self\n"
            "        for ch in word:\n"
            "            node = node.children.setdefault(ch, Trie())\n"
            "        node.is_word = True\n\n"
            "    def _find(self, word):\n"
            "        node = self\n"
            "        for ch in word:\n"
            "            if ch not in node.children:\n"
            "                return None\n"
            "            node = node.children[ch]\n"
            "        return node\n\n"
            "    def search(self, word):\n"
            "        node = self._find(word)\n"
            "        return node is not None and node.is_word\n\n"
            "    def starts_with(self, prefix):\n"
            "        return self._find(prefix) is not None\n"
        ),
        test_code=(
            "from solution import Trie\n\n"
            "def test_insert_and_search():\n"
            "    trie = Trie()\n"
            "    trie.insert('apple')\n"
            "    assert trie.search('apple') is True\n"
            "    assert trie.search('app') is False\n\n"
            "def test_starts_with():\n"
            "    trie = Trie()\n"
            "    trie.insert('apple')\n"
            "    assert trie.starts_with('app') is True\n"
            "    assert trie.starts_with('b') is False\n\n"
            "def test_multiple_words():\n"
            "    trie = Trie()\n"
            "    trie.insert('cat')\n"
            "    trie.insert('car')\n"
            "    assert trie.search('cat') is True\n"
            "    assert trie.search('ca') is False\n"
            "    assert trie.starts_with('ca') is True\n"
        ),
    ),
    Task(
        id="a01_short_but_hard",
        category="adversarial_short_hard",
        prompt="Write a function that counts the number of ways to make change for a given amount using an unlimited supply of the given coin denominations (order does not matter, i.e. [1,2] and [2,1] count as one way).",
        entry_point="count_change_ways",
        reference_solution=(
            "def count_change_ways(amount, coins):\n"
            "    dp = [0] * (amount + 1)\n"
            "    dp[0] = 1\n"
            "    for coin in coins:\n"
            "        for x in range(coin, amount + 1):\n"
            "            dp[x] += dp[x - coin]\n"
            "    return dp[amount]\n"
        ),
        test_code=(
            "from solution import count_change_ways\n\n"
            "def test_basic():\n"
            "    assert count_change_ways(5, [1, 2, 5]) == 4\n\n"
            "def test_zero_amount():\n"
            "    assert count_change_ways(0, [1, 2]) == 1\n\n"
            "def test_no_way():\n"
            "    assert count_change_ways(3, [2]) == 0\n\n"
            "def test_single_coin():\n"
            "    assert count_change_ways(10, [10]) == 1\n"
        ),
    ),
    Task(
        id="a02_short_but_hard",
        category="adversarial_short_hard",
        prompt="Write a function next_permutation(nums) that rearranges a list of integers, in place, into the lexicographically next greater permutation. If no such permutation exists (the list is the highest possible permutation), rearrange it to the lowest possible order (sorted ascending). The function should return the list.",
        entry_point="next_permutation",
        reference_solution=(
            "def next_permutation(nums):\n"
            "    n = len(nums)\n"
            "    i = n - 2\n"
            "    while i >= 0 and nums[i] >= nums[i + 1]:\n"
            "        i -= 1\n"
            "    if i >= 0:\n"
            "        j = n - 1\n"
            "        while nums[j] <= nums[i]:\n"
            "            j -= 1\n"
            "        nums[i], nums[j] = nums[j], nums[i]\n"
            "    nums[i + 1:] = reversed(nums[i + 1:])\n"
            "    return nums\n"
        ),
        test_code=(
            "from solution import next_permutation\n\n"
            "def test_middle_case():\n"
            "    assert next_permutation([1, 2, 3]) == [1, 3, 2]\n\n"
            "def test_descending_wraps_to_ascending():\n"
            "    assert next_permutation([3, 2, 1]) == [1, 2, 3]\n\n"
            "def test_single_swap_needed():\n"
            "    assert next_permutation([1, 1, 5]) == [1, 5, 1]\n"
        ),
    ),
    Task(
        id="a03_long_but_trivial",
        category="adversarial_long_trivial",
        prompt=(
            "Our team maintains a small internal reporting utility used across several dashboards "
            "in the analytics platform. As part of a broader effort to standardize how we compute "
            "basic descriptive statistics before they get passed into the visualization layer, we "
            "need a well-documented, production-quality utility function. It should be robust, "
            "efficient, and follow good engineering practice, since it will be called frequently in "
            "hot paths across the reporting pipeline and its output feeds directly into charts that "
            "stakeholders review weekly. Please write a function that computes the arithmetic mean "
            "(average) of a list of numbers and returns it as a float."
        ),
        entry_point="compute_mean",
        reference_solution="def compute_mean(numbers):\n    return sum(numbers) / len(numbers)\n",
        test_code=(
            "from solution import compute_mean\n\n"
            "def test_basic():\n"
            "    assert compute_mean([2, 4, 6]) == 4.0\n\n"
            "def test_single_value():\n"
            "    assert compute_mean([5]) == 5.0\n\n"
            "def test_negatives():\n"
            "    assert compute_mean([-2, 2]) == 0.0\n"
        ),
    ),
    Task(
        id="a04_long_but_trivial",
        category="adversarial_long_trivial",
        prompt=(
            "In our codebase we follow a strict convention that every public function includes a "
            "clear docstring, type hints where practical, and defensive handling of common edge "
            "cases, because this module is imported by several downstream services owned by other "
            "teams and any ambiguity here tends to produce support tickets. With that context in "
            "mind, and bearing in mind our general engineering principles around readability, "
            "maintainability, and testability, please implement a function that takes a list of "
            "strings and returns only the strings that are longer than 3 characters."
        ),
        entry_point="filter_long_strings",
        reference_solution="def filter_long_strings(strings):\n    return [s for s in strings if len(s) > 3]\n",
        test_code=(
            "from solution import filter_long_strings\n\n"
            "def test_basic():\n"
            "    assert filter_long_strings(['a', 'ab', 'abcd', 'abcde']) == ['abcd', 'abcde']\n\n"
            "def test_none_qualify():\n"
            "    assert filter_long_strings(['a', 'bb', 'ccc']) == []\n\n"
            "def test_empty_list():\n"
            "    assert filter_long_strings([]) == []\n"
        ),
    ),
    Task(
        id="a05_keyword_heavy_easy",
        category="adversarial_keyword_easy",
        prompt=(
            "Implement a distributed, thread-safe, asynchronous, high-performance, fault-tolerant, "
            "horizontally-scalable microservice-ready function using advanced concurrency primitives "
            "and enterprise-grade architecture patterns that takes two integers and returns their sum."
        ),
        entry_point="add_two_numbers",
        reference_solution="def add_two_numbers(a, b):\n    return a + b\n",
        test_code=(
            "from solution import add_two_numbers\n\n"
            "def test_basic():\n"
            "    assert add_two_numbers(2, 3) == 5\n\n"
            "def test_negatives():\n"
            "    assert add_two_numbers(-1, -1) == -2\n\n"
            "def test_zero():\n"
            "    assert add_two_numbers(0, 5) == 5\n"
        ),
    ),
    Task(
        id="a06_keyword_heavy_easy",
        category="adversarial_keyword_easy",
        prompt=(
            "Using cutting-edge machine-learning-adjacent, AI-powered, cloud-native, quantum-ready "
            "algorithmic techniques and industry-best-practice design patterns, build a robust, "
            "enterprise-scale function that reverses a given string."
        ),
        entry_point="reverse_string",
        reference_solution="def reverse_string(s):\n    return s[::-1]\n",
        test_code=(
            "from solution import reverse_string\n\n"
            "def test_basic():\n"
            "    assert reverse_string('hello') == 'olleh'\n\n"
            "def test_empty():\n"
            "    assert reverse_string('') == ''\n\n"
            "def test_palindrome_unchanged():\n"
            "    assert reverse_string('aba') == 'aba'\n"
        ),
    ),
    Task(
        id="u01_underspecified_dedupe",
        category="underspecified",
        prompt="Write a function that cleans up a list of user records for a mailing list export.",
        entry_point="clean_records",
        reference_solution=(
            "def clean_records(records):\n"
            "    seen_emails = set()\n"
            "    cleaned = []\n"
            "    for record in records:\n"
            "        email = (record.get('email') or '').strip().lower()\n"
            "        if not email or email in seen_emails:\n"
            "            continue\n"
            "        seen_emails.add(email)\n"
            "        cleaned.append({**record, 'email': email})\n"
            "    return cleaned\n"
        ),
        test_code=(
            "from solution import clean_records\n\n"
            "# The prompt is deliberately underspecified - no schema, no definition of\n"
            "# 'clean'. This task grades on whether the model asks a clarifying\n"
            "# assumption in comments/behavior at all, and specifically on the one\n"
            "# behavior almost any reasonable reading of 'clean up for a mailing list\n"
            "# export' should produce: dropping rows with no usable email, and not\n"
            "# crashing on messy input. It does NOT grade on exact-match output shape,\n"
            "# since no schema was given.\n\n"
            "def test_drops_records_with_no_email():\n"
            "    records = [{'name': 'A', 'email': 'a@example.com'}, {'name': 'B', 'email': ''}]\n"
            "    result = clean_records(records)\n"
            "    emails = [r.get('email') for r in result if isinstance(r, dict)]\n"
            "    assert 'a@example.com' in emails or 'a@example.com'.lower() in [e.lower() if e else e for e in emails]\n"
            "    assert len(result) <= len(records)\n\n"
            "def test_does_not_crash_on_missing_key():\n"
            "    records = [{'name': 'C'}]\n"
            "    result = clean_records(records)  # should not raise\n"
            "    assert isinstance(result, list)\n"
        ),
    ),
]


def main() -> None:
    out_dir = Path(__file__).resolve().parent.parent / "tasks"
    out_dir.mkdir(parents=True, exist_ok=True)
    for task in TASKS:
        data = {
            "id": task.id,
            "category": task.category,
            "prompt": task.prompt,
            "entry_point": task.entry_point,
            "reference_solution": task.reference_solution,
            "test_code": task.test_code,
            "timeout_s": task.timeout_s,
        }
        path = out_dir / f"{task.id}.yaml"
        with path.open("w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, width=100)
    print(f"Wrote {len(TASKS)} task files to {out_dir}")


if __name__ == "__main__":
    main()
