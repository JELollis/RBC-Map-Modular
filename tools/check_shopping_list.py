"""Regression checks for ShoppingListTool charisma repricing (AUD-048)."""

from __future__ import annotations

import ast
import logging
from types import SimpleNamespace
from pathlib import Path


from _app import load_app_tree, load_app_source
ROOT = Path(__file__).resolve().parent.parent
MAIN = Path("modular_app")

PRICE_COLUMNS = ("base_price", "charisma_level_1", "charisma_level_2", "charisma_level_3")


class FakeCursor:
    def __init__(self, prices: dict[tuple[str, str, str], int]) -> None:
        self.prices = prices
        self.queries: list[str] = []
        self._rows: list[tuple] = []

    def execute(self, sql: str, params=()) -> None:
        self.queries.append(sql)
        column = next((c for c in PRICE_COLUMNS if c in sql), "base_price")
        shop = params[0] if params else ""
        if "item_name IN" in sql:
            names = params[1:]
        else:
            names = list(dict.fromkeys(
                name for (s, name, _c) in self.prices if s == shop
            ))
        self._rows = [
            (name, self.prices[(shop, name, column)])
            for name in names
            if (shop, name, column) in self.prices
        ]

    def fetchall(self):
        return self._rows


class Combo:
    def __init__(self, text: str) -> None:
        self._text = text

    def currentText(self) -> str:
        return self._text

    def setText(self, text: str) -> None:
        self._text = text


class ItemList:
    """Minimal QListWidget stand-in backed by an external sink list."""

    def __init__(self, sink: list[str]) -> None:
        self.sink = sink
        self.current = -1

    def clear(self) -> None:
        self.sink.clear()
        self.current = -1

    def addItem(self, text: str) -> None:
        self.sink.append(text)

    def count(self) -> int:
        return len(self.sink)

    def currentRow(self) -> int:
        return self.current

    def setCurrentRow(self, row: int) -> None:
        self.current = row if 0 <= row < len(self.sink) else -1

    def item(self, row: int):
        if 0 <= row < len(self.sink):
            return SimpleNamespace(text=lambda t=self.sink[row]: t)
        return None

    def currentItem(self):
        return self.item(self.current)


def class_method(tree: ast.Module, name: str) -> ast.FunctionDef:
    cls = next(
        node for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "ShoppingListTool"
    )
    matches = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name]
    assert len(matches) == 1, f"expected one {name} method"
    return matches[0]


def make_fake(namespace: dict, prices, available=None, cart_display=None, cart=None):
    fake = type("FakeTool", (), {})()
    fake.sqlite_cursor = FakeCursor(prices)
    fake.shop_combobox = Combo("Discount Magic")
    fake.charisma_combobox = Combo("Charisma 1")
    fake.available_items_list = ItemList(available if available is not None else [])
    fake.shopping_list = ItemList(cart_display if cart_display is not None else [])
    fake.shopping_items = cart if cart is not None else {}
    fake.update_total = lambda: None
    for name in ("load_items", "_price_column", "_refresh_shopping_list"):
        setattr(fake, name, lambda *a, n=name, **k: namespace[n](fake, *a, **k))
    return fake


METHODS = ("_refresh_prices", "load_items", "_price_column", "_refresh_shopping_list")

PRICES = {
    ("Discount Magic", "Diamond Ring", "base_price"): 70000,
    ("Discount Magic", "Diamond Ring", "charisma_level_1"): 67900,
    ("Discount Magic", "Sprint Potion", "base_price"): 105,
    ("Discount Magic", "Sprint Potion", "charisma_level_1"): 102,
}


def exec_methods(tree: ast.Module) -> dict:
    methods = [class_method(tree, name) for name in METHODS]
    namespace = {"logging": logging}
    exec(compile(ast.Module(body=methods, type_ignores=[]), str(MAIN), "exec"), namespace)
    return namespace


def check_charisma_reloads_available_items(tree: ast.Module) -> None:
    namespace = exec_methods(tree)
    # Seed a stale base-price row: the reload must replace it, not append.
    available = ["Diamond Ring - 70000 Coins"]
    fake = make_fake(namespace, PRICES, available=available)
    fake.available_items_list.current = 0

    namespace["_refresh_prices"](fake)

    assert any("charisma_level_1" in q for q in fake.sqlite_cursor.queries), (
        "available items must reload at the selected charisma price column"
    )
    assert "Diamond Ring - 67900 Coins" in available, available
    assert "Sprint Potion - 102 Coins" in available, available
    assert not any("70000" in row for row in available), (
        f"stale base-price rows must not survive the reload: {available}"
    )
    # Selection is preserved by item identity, not row index.
    assert available[fake.available_items_list.current].startswith("Diamond Ring - 67900")


def check_charisma_reprices_cart(tree: ast.Module) -> None:
    namespace = exec_methods(tree)
    cart_display: list[str] = []
    fake = make_fake(
        namespace, PRICES, cart_display=cart_display,
        cart={"Diamond Ring": {"price": 70000, "quantity": 2}},
    )

    namespace["_refresh_prices"](fake)

    assert fake.shopping_items["Diamond Ring"]["price"] == 67900
    assert cart_display == ["Diamond Ring - 67900 Coins - 2x"], cart_display


def check_shop_switch_clears_selection(tree: ast.Module) -> None:
    """A shop change must not carry the old selection onto a different product
    that happens to sit at the same row index."""
    namespace = exec_methods(tree)
    prices = {
        ("Discount Magic", "Diamond Ring", "base_price"): 70000,
        ("Discount Magic", "Diamond Ring", "charisma_level_1"): 67900,
        ("Other Shop", "Rusty Knife", "base_price"): 50,
        ("Other Shop", "Rusty Knife", "charisma_level_1"): 48,
    }
    available: list[str] = []
    fake = make_fake(namespace, prices, available=available)
    namespace["load_items"](fake)
    fake.available_items_list.setCurrentRow(0)
    assert fake.available_items_list.currentItem().text().startswith("Diamond Ring")

    # Switch shops: index 0 is now a different product; selection must clear.
    fake.shop_combobox.setText("Other Shop")
    namespace["load_items"](fake)
    assert available == ["Rusty Knife - 48 Coins"], available
    assert fake.available_items_list.current == -1


def main() -> int:
    tree = load_app_tree()
    check_charisma_reloads_available_items(tree)
    check_charisma_reprices_cart(tree)
    check_shop_switch_clears_selection(tree)
    print("shopping-list checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
