import json
import os

class SessionStore:
    def __init__(self, path):
        self.path = path

        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

        # Nếu file chưa tồn tại hoặc rỗng → init
        if not os.path.exists(self.path) or os.path.getsize(self.path) == 0:
            self._init()

    def _init(self):
        data = {
            "messages": [],
            "summary": None
        }
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load(self):
        try:
            with open(self.path, encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            # File hỏng / rỗng → reset an toàn
            self._init()
            with open(self.path, encoding="utf-8") as f:
                return json.load(f)

    def save(self, data):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_message(self, role, content):
        data = self.load()
        data["messages"].append({
            "role": role,
            "content": content
        })
        self.save(data)
