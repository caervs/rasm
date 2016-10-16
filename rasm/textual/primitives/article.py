from replicate.replicable import preprocessor, Replicable


class Header(Replicable):
    @preprocessor
    def preprocess(level, text):
        pass


class ListBlock(Replicable):
    @preprocessor
    def preprocess(items):
        pass


class TextLine(Replicable):
    @preprocessor
    def preprocess(text):
        pass


class CodeBlock(Replicable):
    @preprocessor
    def preprocess(contents):
        pass


class Figure(Replicable):
    @preprocessor
    def preprocess(name):
        pass
