import pandas as pd
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod


class TessLayout(Enum):
    PAGE = 1
    BLOCK = 2
    PARA = 3
    LINE = 4
    WORD = 5


@dataclass
class Element(ABC):
    level: TessLayout
    left: float
    top: float
    width: float
    height: float

    @abstractmethod
    def get_text(self) -> str:
        """To be implemented by subclasses"""
        pass


@dataclass
class Word(Element):
    level: TessLayout = field(init=False, default=TessLayout.WORD)
    conf: float
    text: str | None

    def get_text(self) -> str:
        """Get clean text from this word"""
        return str(self.text).strip() if self.text else ""


@dataclass
class Line(Element):
    level: TessLayout = field(init=False, default=TessLayout.LINE)
    words: dict[int, Word] = field(default_factory=dict)

    def get_text(self):
        """Get text from all words in this line"""
        word_texts = []
        for _, word in sorted(self.words.items()):
            word_text = word.get_text()
            if word_text:
                word_texts.append(word_text)
        return " ".join(word_texts)


@dataclass
class Paragraph(Element):
    level: TessLayout = field(init=False, default=TessLayout.PARA)
    lines: dict[int, Line] = field(default_factory=dict)

    def get_text(self):
        """Get text from all lines in this paragraph"""
        line_texts = []
        for _, line in sorted(self.lines.items()):
            line_text = line.get_text()
            if line_text:
                line_texts.append(line_text)
        return "\n".join(line_texts)


@dataclass
class Block(Element):
    level: TessLayout = field(init=False, default=TessLayout.BLOCK)
    paragraphs: dict[int, Paragraph] = field(default_factory=dict)

    def get_text(self):
        """Get text from all paragraphs in this block"""
        para_texts = []
        for _, para in sorted(self.paragraphs.items()):
            para_text = para.get_text()
            if para_text:
                para_texts.append(para_text)
        return "\n\n".join(para_texts)


@dataclass
class Page(Element):
    level: TessLayout = field(init=False, default=TessLayout.PAGE)
    blocks: dict[int, Block] = field(default_factory=dict)

    def get_text(self):
        """Get text from all paragraphs in this block"""
        block_texts = []
        for _, block in sorted(self.blocks.items()):
            block_text = block.get_text()
            if block_text:
                block_texts.append(block_text)
        return "\n\n".join(block_texts)


def df_to_layout(df: pd.DataFrame):
    pages = {}
    for _, row in df.iterrows():
        match TessLayout(row.level):
            case TessLayout.PAGE:
                pages[row.page_num] = Page(*list(row.loc["left":"height"]))

            case TessLayout.BLOCK:
                blocks = pages[row.page_num].blocks
                blocks[row.block_num] = Block(*list(row.loc["left":"height"]))

            case TessLayout.PARA:
                paras = pages[row.page_num].blocks[row.block_num].paragraphs
                paras[row.par_num] = Paragraph(*list(row.loc["left":"height"]))

            case TessLayout.LINE:
                lines = (
                    pages[row.page_num]
                    .blocks[row.block_num]
                    .paragraphs[row.par_num]
                    .lines
                )
                lines[row.line_num] = Line(*list(row.loc["left":"height"]))

            case TessLayout.WORD:
                words = (
                    pages[row.page_num]
                    .blocks[row.block_num]
                    .paragraphs[row.par_num]
                    .lines[row.line_num]
                    .words
                )
                words[row.word_num] = Word(*list(row.loc["left":"text"]))
    return pages
