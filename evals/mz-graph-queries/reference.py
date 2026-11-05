"""Independent answer keys. Plain Python, no SQL, so a wrong pattern in the
skill cannot leak into the key. Every function returns a set of tuples in
the column order of the corresponding eval view."""
from __future__ import annotations

import heapq
from collections import defaultdict, deque
from decimal import Decimal
from fixture import Fixture


def _children(f: Fixture) -> dict[int, list[int]]:
    ch: dict[int, list[int]] = defaultdict(list)
    for i, mgr, _, _ in f.employees:
        if mgr is not None:
            ch[mgr].append(i)
    return ch


def _reach(adj: dict, start) -> set:
    seen, todo = set(), deque([start])
    while todo:
        x = todo.popleft()
        for y in adj.get(x, ()):
            if y not in seen:
                seen.add(y)
                todo.append(y)
    return seen


def descendants(f: Fixture, root: int) -> set[tuple]:
    return {(i,) for i in _reach(_children(f), root) if i != root}


def depth(f: Fixture, root: int) -> set[tuple]:
    ch = _children(f)
    out, seen, todo = set(), {root}, deque([(root, 0)])
    while todo:
        x, d = todo.popleft()
        out.add((x, d))
        for y in ch.get(x, ()):
            if y not in seen:
                seen.add(y)
                todo.append((y, d + 1))
    return out


def team_salary(f: Fixture, root: int) -> set[tuple]:
    ch, sal = _children(f), {i: s for i, _, _, s in f.employees}
    nodes = _reach(ch, root) | {root}
    out = set()
    for x in nodes:
        out.add((x, sal[x] + sum(sal[y] for y in _reach(ch, x) if y != x)))
    return out


def bom_quantities(f: Fixture, kit: int) -> set[tuple]:
    kids: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for p, c, n in f.bom:
        kids[p].append((c, n))
    tot: dict[int, int] = defaultdict(int)

    def walk(part: int, mult: int) -> None:
        for c, n in kids.get(part, ()):
            tot[c] += mult * n
            walk(c, mult * n)
    walk(kit, 1)
    return {(p, q) for p, q in tot.items()}


def kit_cost(f: Fixture, kit: int) -> set[tuple]:
    cost = {i: c for i, _, c in f.parts if c is not None}
    total = sum((Decimal(q) * cost[p] for p, q in bom_quantities(f, kit) if p in cost), Decimal(0))
    return {(total,)}


def _transfer_adj(f: Fixture) -> dict[str, set[str]]:
    adj: dict[str, set[str]] = defaultdict(set)
    for s, d, _, _ in f.transfers:
        adj[s].add(d)
    return adj


def within_hops(f: Fixture, src: str, k: int) -> set[tuple]:
    adj, dist = _transfer_adj(f), {src: 0}
    todo = deque([src])
    while todo:
        x = todo.popleft()
        if dist[x] == k:
            continue
        for y in adj.get(x, ()):
            if y not in dist:
                dist[y] = dist[x] + 1
                todo.append(y)
    return {(y,) for y, d in dist.items() if y != src}


def closure(f: Fixture) -> set[tuple]:
    adj = _transfer_adj(f)
    return {(s, d) for s in {x for x, in f.accounts} for d in _reach(adj, s)}


def scc(f: Fixture) -> set[tuple]:
    adj = _transfer_adj(f)
    nodes = [x for x, in f.accounts]
    reach = {x: _reach(adj, x) for x in nodes}
    out = set()
    for x in nodes:
        members = {y for y in reach[x] if x in reach[y]} | {x}
        out.add((x, min(members)))
    return out


def ring_accounts(f: Fixture) -> set[tuple]:
    adj = _transfer_adj(f)
    return {(x,) for x, in f.accounts if x in _reach(adj, x)}


def effective_permissions(f: Fixture) -> set[tuple]:
    parent = {g: pg for g, pg in f.groups}
    explicit: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for g, d, lvl in f.permissions:
        explicit[g][d].add(lvl)
    memo: dict[str, dict[str, set[str]]] = {}

    def eff(g: str) -> dict[str, set[str]]:
        if g in memo:
            return memo[g]
        res = {d: set(l) for d, l in explicit[g].items()}
        if parent.get(g) is not None:
            for d, l in eff(parent[g]).items():
                if d not in res:
                    res[d] = set(l)
        memo[g] = res
        return res
    out = set()
    for u, g in f.memberships:
        for d, levels in eff(g).items():
            for lvl in levels:
                out.add((u, d, lvl))
    return out


def customer_clusters(f: Fixture, threshold: Decimal) -> set[tuple]:
    adj: dict[str, set[str]] = defaultdict(set)
    for a, b, s in f.customer_links:
        if s >= threshold:
            adj[a].add(b)
            adj[b].add(a)
    return {(c, min(_reach(adj, c) | {c})) for c, in f.customers}


def _road_adj(f: Fixture) -> dict[str, list[tuple[str, int]]]:
    adj: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for s, d, km in f.roads:
        adj[s].append((d, km))
        adj[d].append((s, km))
    return adj


def shortest_km(f: Fixture, origin: str) -> set[tuple]:
    adj, dist, pq = _road_adj(f), {origin: 0}, [(0, origin)]
    while pq:
        d, x = heapq.heappop(pq)
        if d > dist[x]:
            continue
        for y, w in adj.get(x, ()):
            if d + w < dist.get(y, float("inf")):
                dist[y] = d + w
                heapq.heappush(pq, (d + w, y))
    return {(c, d) for c, d in dist.items() if c != origin}


def shortest_hops(f: Fixture, origin: str) -> set[tuple]:
    adj = {x: [y for y, _ in ys] for x, ys in _road_adj(f).items()}
    dist, todo = {origin: 0}, deque([origin])
    while todo:
        x = todo.popleft()
        for y in adj.get(x, ()):
            if y not in dist:
                dist[y] = dist[x] + 1
                todo.append(y)
    return {(c, d) for c, d in dist.items() if c != origin}


def downstream(f: Fixture, task: str) -> set[tuple]:
    dep: dict[str, set[str]] = defaultdict(set)  # prereq -> tasks that need it
    for t, pre in f.depends_on:
        dep[pre].add(t)
    return {(t,) for t in _reach(dep, task) if t != task}


def topo_level(f: Fixture) -> set[tuple]:
    pre: dict[str, set[str]] = defaultdict(set)
    for t, p in f.depends_on:
        pre[t].add(p)
    memo: dict[str, int] = {}

    def level(t: str) -> int:
        if t not in memo:
            memo[t] = 0 if not pre[t] else 1 + max(level(p) for p in pre[t])
        return memo[t]
    return {(t, level(t)) for t, in f.pipelines}
