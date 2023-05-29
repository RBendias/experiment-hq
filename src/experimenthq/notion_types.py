from enum import Enum


class NotionTypes(str, Enum):
    number = "number"
    rich_text = "rich_text"
    select = "select"
    multi_select = "multi_select"
    files = "files"
    checkbox = "checkbox"
    url = "url"
    email = "email"
    phone_number = "phone_number"
    people = "people"
    date = "date"

    def validate_value(self, value: str, notion_type: str) -> bool:
        if notion_type == self.number:
            try:
                float(value)
                return True
            except ValueError:
                return False
        elif notion_type == self.rich_text:
            return True
        elif notion_type == self.select or notion_type == self.multi_select:
            return True
        elif notion_type == self.files:
            return True
        elif notion_type == self.checkbox:
            try:
                bool(value)
                return True
            except ValueError:
                return False
        elif notion_type == self.url:
            from urllib.parse import urlparse

            try:
                result = urlparse(value)
                return all([result.scheme, result.netloc])
            except ValueError:
                return False
        elif notion_type == self.email:
            import re

            email_regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
            return bool(re.fullmatch(email_regex, value))
        elif notion_type == self.phone_number:
            # Assuming phone number validation is required as per E.164 format
            import phonenumbers

            try:
                phone_number = phonenumbers.parse(value)
                return phonenumbers.is_valid_number(phone_number)
            except:
                return False
        elif notion_type == self.people:
            # Assuming that the value is an ID in this case
            return bool(value)
        elif notion_type == self.date:
            from dateutil.parser import parse

            try:
                parse(value)
                return True
            except ValueError:
                return False
        else:
            raise ValueError(f"Unsupported parameter type {notion_type}")
