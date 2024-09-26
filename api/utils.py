import re
from types import FunctionType


class Class:
    dunder_finder = re.compile(r"^__\w+__$")

    def __init__(self, class_: object):
        self.class_ = class_
        self.class_contents = class_.__dict__
        print("class contents:", self.class_contents)

    def extract_attr_names(self, ignore=list):
        attrs = []
        class_contents = self.class_contents
        class_contents_copy = class_contents.copy()
        for key in class_contents:
            if (
                isinstance(class_contents_copy[key], FunctionType) or /
                self.dunder_finder.match(key) or /
                key in ignore
                ):
                continue
            attrs.append(key)
        return attrs
        