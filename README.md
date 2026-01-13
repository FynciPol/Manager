# Manager
Попытка создать менеджер вк и тг 
 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/README.md b/README.md
index a0faf27f99857036019238bacf941c53a6a639cf..76e3ffb9943ee2beb762f979b9f687186398f35b 100644
--- a/README.md
+++ b/README.md
@@ -1,2 +1,41 @@
 # Manager
-Попытка создать менеджер вк и тг 
+
+Простой CLI-менеджер аккаунтов для VK и Telegram.
+
+## Возможности
+- Добавление аккаунтов VK и TG
+- Просмотр списка аккаунтов
+- Удаление аккаунтов
+- Экспорт в JSON
+
+## Быстрый старт
+
+```bash
+python manager.py add vk 12345 ivan --notes "Рабочий аккаунт"
+python manager.py add tg 67890 ivan_tg
+python manager.py list
+python manager.py list --service vk
+python manager.py remove vk 12345
+python manager.py export backups/accounts.json
+```
+
+## Формат хранения
+По умолчанию данные хранятся в `accounts.json` рядом с `manager.py`.
+
+Пример записи:
+
+```json
+{
+  "service": "vk",
+  "account_id": "12345",
+  "username": "ivan",
+  "notes": "Рабочий аккаунт",
+  "created_at": "2024-01-01T12:00:00"
+}
+```
+
+## Настройка пути хранения
+
+```bash
+python manager.py --storage data/accounts.json add vk 12345 ivan
+```
 
EOF
)
