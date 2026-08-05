import json
import os

class PersistentStorage:
    def __init__(self, filename="config.json", default_config=None):
        self.filename = filename
        self.data = default_config if default_config is not None else {}
        self.load()

    def load(self):
        """Load variables from JSON file into memory."""
        try:
            with open(self.filename, "r") as f:
                self.data = json.load(f)
        except (OSError, ValueError):
            # File missing or corrupted: fall back to current data/defaults
            self.save()

    def save(self):
        """Atomically save variables to prevent corruption on power loss."""
        temp_filename = self.filename + ".tmp"
        try:
            with open(temp_filename, "w") as f:
                json.dump(self.data, f)
            os.rename(temp_filename, self.filename)
        except OSError as e:
            print(f"Error saving config: {e}")

    def get(self, key, default=None):
        """Read a variable."""
        return self.data.get(key, default)

    def set(self, key, value, autosave=True):
        """Write/update a variable and optionally persist to disk."""
        self.data[key] = value
        if autosave:
            self.save()

    def delete(self, key, autosave=True):
        """Delete a variable."""
        if key in self.data:
            del self.data[key]
            if autosave:
                self.save()
