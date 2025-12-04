import json
import os

class JSONLogger:
    def __init__(self, file_path):
        self.file_path = file_path
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump([], f)

    def retrieve(self):
        """Retrieve the full list of JSON-like objects from the file."""
        with open(self.file_path, 'r') as f:
            return json.load(f)

    def add(self, new_element):
        """Add a new element to the list of JSON-like objects and update the file."""
        data = self.retrieve()
        data.append(new_element)
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=4)