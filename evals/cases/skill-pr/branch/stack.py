class EmptyStackError(Exception):
    pass


class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if not self.items:
            raise EmptyStackError("pop from empty stack")
        return self.items.pop()
