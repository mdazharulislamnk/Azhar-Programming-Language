# azhar/errors.py

class AzharError(Exception):
    def __init__(self, message, file="<stdin>", line=1, col=1, snippet=None):
        super().__init__(message)
        self.file = file
        self.line = line
        self.col = col
        self.snippet = snippet

    def render(self):
        loc = f"{self.file}:{self.line}:{self.col}"
        lines = []
        lines.append(f"{loc}: {self.__class__.__name__}: {self.args[0]}")
        if self.snippet:
            src_line = self.snippet.splitlines()[0] if '\n' in self.snippet else self.snippet
            lines.append(f"  {src_line}")
            caret = " " * (self.col - 1) + "^"
            lines.append(f"  {caret}")
        return "\n".join(lines)

class LexerError(AzharError): pass
class ParseError(AzharError): pass
class TypeErrorEx(AzharError): pass
class RuntimeErrorEx(AzharError): pass
