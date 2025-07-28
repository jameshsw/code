from collections import defaultdict
from typing import Optional, List


class InMemoryDB:
    def __init__(self):
        self.db = defaultdict(dict)
        self.tx_stack = []

    def _is_alive(self, t, expire_time):
        return expire_time is None or t < expire_time

    def _record_change(self, key, field):
        if not self.tx_stack:
            return
        current_tx = self.tx_stack[-1]
        if (key, field) not in current_tx:
            current_tx[(key, field)] = self.db[key].get(field, None)

    def begin(self):
        self.tx_stack.append({})

    def rollback(self):
        if not self.tx_stack:
            raise RuntimeError("NO TRANSACTION")
        tx = self.tx_stack.pop()
        for (key, field), old_val in tx.items():
            if old_val is None:
                self.db[key].pop(field, None)
            else:
                self.db[key][field] = old_val

    def commit(self):
        if not self.tx_stack:
            raise RuntimeError("NO TRANSACTION")
        final_tx = {}
        for tx in self.tx_stack:
            for k, v in tx.items():
                if k not in final_tx:
                    final_tx[k] = v
        self.tx_stack = []

    def set(self, t: int, key: str, field: str, val: int):
        self._record_change(key, field)
        self.db[key][field] = (val, None)

    def set_with_ttl(self, t: int, key: str, field: str, val: int, ttl: int):
        self._record_change(key, field)
        expire = t + ttl
        self.db[key][field] = (val, expire)

    def get(self, t: int, key: str, field: str) -> Optional[int]:
        if key in self.db and field in self.db[key]:
            val, exp = self.db[key][field]
            if self._is_alive(t, exp):
                return val
        return None

    def compare_and_set(
        self, t: int, key: str, field: str, expected_val: int, new_val: int
    ) -> bool:
        if self.get(t, key, field) == expected_val:
            self._record_change(key, field)
            self.db[key][field] = (new_val, None)
            return True
        return False

    def compare_and_set_with_ttl(
        self, t: int, key: str, field: str, expected_val: int, new_val: int, ttl: int
    ) -> bool:
        if self.get(t, key, field) == expected_val:
            self._record_change(key, field)
            self.db[key][field] = (new_val, t + ttl)
            return True
        return False

    def compare_and_del(self, t: int, key: str, field: str, expected_val: int) -> bool:
        if self.get(t, key, field) == expected_val:
            self._record_change(key, field)
            del self.db[key][field]
            return True
        return False

    def scan(self, t: int, key: str) -> List[str]:
        if key not in self.db:
            return []
        result = []
        for field, (val, exp) in self.db[key].items():
            if self._is_alive(t, exp):
                result.append(f"{field}({val})")
        return sorted(result)

    def scan_by_prefix(self, t: int, key: str, prefix: str) -> List[str]:
        if key not in self.db:
            return []
        result = []
        for field, (val, exp) in self.db[key].items():
            if field.startswith(prefix) and self._is_alive(t, exp):
                result.append(f"{field}({val})")
        return sorted(result)


# test case 1
db = InMemoryDB()

db.set(1, "user", "name", "Alice")
print(db.get(1, "user", "name"))  # Alice

db.compare_and_set(2, "user", "name", "Alice", "Bob")
print(db.get(2, "user", "name"))  # Bob

db.compare_and_del(3, "user", "name", "Bob")
print(db.get(3, "user", "name"))  # None

# test case 2
db = InMemoryDB()
db.set(1, "user", "name", "Alice")
db.set(2, "user", "email", "alice@example.com")
db.set(3, "user", "nickname", "Ally")

print(db.scan(2, "user"))
# Output: [['name', 'Alice'], ['email', 'alice@example.com']]

print(db.scan_by_prefix(3, "user", "n"))
# Output: [['name', 'Alice'], ['nickname', 'Ally']]

# test case 3
db = InMemoryDB()

db.set(1, "A", "B", 4)
db.set_with_ttl(2, "X", "Y", 5, 15)
db.set_with_ttl(4, "A", "D", 3, 6)

print(db.compare_and_set_with_ttl(6, "A", "D", 3, 5, 10))  # True
print(db.get(7, "A", "D"))  # 5
print(db.scan(15, "A"))  # ['B(4)', 'D(5)']
print(db.scan(17, "A"))  # ['B(4)']

# test case 4
db = InMemoryDB()
db.set(1, "user", "age", 25)
db.begin()
db.set(2, "user", "age", 30)
print(db.get(3, "user", "age"))  # 30
db.rollback()
print(db.get(4, "user", "age"))  # 25

db.begin()
db.set(5, "user", "age", 35)
db.commit()
print(db.get(6, "user", "age"))  # 35
