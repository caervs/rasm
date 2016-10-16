from rasm.textual.primitives import article


class Parser(object):
    @staticmethod
    def _is_header(line):
        return line.startswith("*")

    @staticmethod
    def _parse_header(line):
        for i, c in enumerate(line):
            if c != "*":
                return article.Header(level=i, text=line[i + 1:])
        return article.Header(level=len(line), text="")

    @staticmethod
    def _parse_text_line(line):
        return article.TextLine(text=line)

    @staticmethod
    def _is_code_block_start(line):
        return line.startswith("#+BEGIN_SRC")

    @staticmethod
    def _find_code_block_end(lines):
        for i in range(len(lines)):
            if lines[i].startswith("#+END_SRC"):
                return i
        raise Exception("Missing code block end")

    @staticmethod
    def _is_list_block_start(line):
        return line.startswith("- ")

    @staticmethod
    def _find_list_block_end(lines):
        for i in range(len(lines)):
            if not lines[i].startswith("- "):
                return i
        return len(lines)

    @classmethod
    def parse(cls, contents):
        lines = list(contents.split("\n"))
        i = 0
        while i < len(lines):
            line = lines[i]
            if cls._is_header(line):
                yield cls._parse_header(line)
            elif cls._is_code_block_start(line):
                end = cls._find_code_block_end(lines[i + 1:])
                yield article.CodeBlock(lines[i:i + 1 + end])
                i = i + 1 + end
            elif cls._is_list_block_start(line):
                end = cls._find_list_block_end(lines[i + 1:])
                yield article.ListBlock(
                    [line[2:] for line in lines[i:i + 1 + end]])
                i = i + 1 + end
            else:
                yield cls._parse_text_line(line)
            i += 1
