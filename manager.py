 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/manager.py b/manager.py
new file mode 100644
index 0000000000000000000000000000000000000000..bc02d7c189a195517ccf95b860ea4a32a4929ad1
--- /dev/null
+++ b/manager.py
@@ -0,0 +1,158 @@
+#!/usr/bin/env python3
+"""Account manager for VK and Telegram."""
+from __future__ import annotations
+
+import argparse
+import json
+from dataclasses import asdict, dataclass, field
+from datetime import datetime
+from pathlib import Path
+from typing import Literal
+
+SERVICE_TYPES = ("vk", "tg")
+ServiceType = Literal["vk", "tg"]
+DEFAULT_STORAGE = Path("accounts.json")
+
+
+@dataclass
+class Account:
+    service: ServiceType
+    account_id: str
+    username: str
+    notes: str = ""
+    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat(timespec="seconds"))
+
+
+@dataclass
+class AccountStore:
+    path: Path = DEFAULT_STORAGE
+    accounts: list[Account] = field(default_factory=list)
+
+    def load(self) -> None:
+        if not self.path.exists():
+            self.accounts = []
+            return
+        data = json.loads(self.path.read_text(encoding="utf-8"))
+        self.accounts = [Account(**item) for item in data]
+
+    def save(self) -> None:
+        payload = [asdict(account) for account in self.accounts]
+        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
+
+    def add(self, account: Account) -> None:
+        if self.find(account.service, account.account_id):
+            raise ValueError("Account already exists")
+        self.accounts.append(account)
+
+    def remove(self, service: ServiceType, account_id: str) -> bool:
+        existing = self.find(service, account_id)
+        if not existing:
+            return False
+        self.accounts = [acc for acc in self.accounts if not (acc.service == service and acc.account_id == account_id)]
+        return True
+
+    def find(self, service: ServiceType, account_id: str) -> Account | None:
+        for account in self.accounts:
+            if account.service == service and account.account_id == account_id:
+                return account
+        return None
+
+    def list_by_service(self, service: ServiceType | None = None) -> list[Account]:
+        if service is None:
+            return list(self.accounts)
+        return [account for account in self.accounts if account.service == service]
+
+
+def valid_service(value: str) -> ServiceType:
+    value = value.lower()
+    if value not in SERVICE_TYPES:
+        raise argparse.ArgumentTypeError("Service must be 'vk' or 'tg'")
+    return value  # type: ignore[return-value]
+
+
+def build_parser() -> argparse.ArgumentParser:
+    parser = argparse.ArgumentParser(description="VK/TG account manager")
+    parser.add_argument(
+        "--storage",
+        type=Path,
+        default=DEFAULT_STORAGE,
+        help="Path to accounts JSON file (default: accounts.json)",
+    )
+
+    subparsers = parser.add_subparsers(dest="command", required=True)
+
+    add_parser = subparsers.add_parser("add", help="Add an account")
+    add_parser.add_argument("service", type=valid_service, help="vk or tg")
+    add_parser.add_argument("account_id", help="Account identifier")
+    add_parser.add_argument("username", help="Account username")
+    add_parser.add_argument("--notes", default="", help="Optional notes")
+
+    list_parser = subparsers.add_parser("list", help="List accounts")
+    list_parser.add_argument("--service", type=valid_service, help="vk or tg", required=False)
+
+    remove_parser = subparsers.add_parser("remove", help="Remove an account")
+    remove_parser.add_argument("service", type=valid_service, help="vk or tg")
+    remove_parser.add_argument("account_id", help="Account identifier")
+
+    export_parser = subparsers.add_parser("export", help="Export accounts to JSON")
+    export_parser.add_argument("output", type=Path, help="Output file path")
+
+    return parser
+
+
+def format_account(account: Account) -> str:
+    return (
+        f"[{account.service}] id={account.account_id} user={account.username} "
+        f"created={account.created_at} notes={account.notes or '-'}"
+    )
+
+
+def main() -> None:
+    parser = build_parser()
+    args = parser.parse_args()
+
+    store = AccountStore(path=args.storage)
+    store.load()
+
+    if args.command == "add":
+        account = Account(
+            service=args.service,
+            account_id=args.account_id,
+            username=args.username,
+            notes=args.notes,
+        )
+        store.add(account)
+        store.save()
+        print("Account added:")
+        print(format_account(account))
+        return
+
+    if args.command == "list":
+        accounts = store.list_by_service(args.service if hasattr(args, "service") else None)
+        if not accounts:
+            print("No accounts found")
+            return
+        for account in accounts:
+            print(format_account(account))
+        return
+
+    if args.command == "remove":
+        removed = store.remove(args.service, args.account_id)
+        if not removed:
+            print("Account not found")
+            return
+        store.save()
+        print("Account removed")
+        return
+
+    if args.command == "export":
+        payload = [asdict(account) for account in store.accounts]
+        args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
+        print(f"Exported {len(payload)} accounts to {args.output}")
+        return
+
+    parser.error("Unknown command")
+
+
+if __name__ == "__main__":
+    main()
 
EOF
)
