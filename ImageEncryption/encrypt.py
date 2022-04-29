import sys
from typing import Optional, Union
from random import getrandbits


class Message():
    ONE = "#"
    ZERO = "."

    @classmethod
    def from_file(cls, file_path: str):
        lines = []
        with open(file_path, "r") as file:
            while line := file.readline():
                lines.append(line)
        return cls(lines)

    @classmethod
    def __from_messages_text(cls, key_text: list[str], crypto_text: list[str]) -> 'Message':
        if len(key_text) != len(crypto_text):
            raise ValueError("Key and crypto must have the same height")

        lines = []
        for key_line, crypto_line in zip(key_text, crypto_text):
            if len(key_line) != len(crypto_line):
                raise ValueError(f"Message not rectangular: key({len(key_line)}) != crypto({len(crypto_line)})")
            lines.append([])

            for key_c, crypto_c in zip(key_line, crypto_line):
                if key_c == cls.ONE or crypto_c == cls.ONE:
                    lines[-1].append(cls.ONE)
                else:
                    lines[-1].append(cls.ZERO)
            lines[-1] = ''.join(lines[-1])
        return cls(lines)

    @classmethod
    def from_messages(cls, key: Union['Message', list[str]], crypto: Union['Message', list[str]]) -> 'Message':
        if isinstance(key, list) and isinstance(crypto, list):
            return cls.__from_messages_text(key, crypto)
        elif isinstance(key, cls) and isinstance(crypto, cls):
            return cls.__from_messages_text(key.lines, crypto.lines)
        raise ValueError("Invalid messages. Messages must both be either list of strings or Message")

    def __init__(self, lines: list[str], file_name: Optional[str] = None, bits: int = None):
        if len(lines) == 0:
            raise ValueError("Empty message")

        self.lines = [line.strip() for line in lines]
        self.height = len(self.lines)
        self.width = len(self.lines[0])
        self.file_name = file_name

        self.bits = bits if bits else 0
        if self.bits == 0:
            for line in self.lines:
                if len(line) != self.width:
                    raise ValueError(f"Message not rectangular: line({len(line)}) != width({self.width})")

                for c in line:
                    if c == self.__class__.ONE:
                        self.bits = (self.bits | 1)
                    self.bits = self.bits << 1
            self.bits = self.bits >> 1

    def encrypt(self) -> tuple['Message', 'Message']:
        key = getrandbits(self.width * self.height)
        crypto = key ^ self.bits

        key_text = []
        crypto_text = []
        max_idx = self.width * self.height - 1
        for y in range(self.height):
            key_text.append([])
            crypto_text.append([])
            for x in range(self.width):
                idx = max_idx - (y * self.width + x)
                mask = 1 << idx
                key_text[-1].append(self.ONE if key & mask else self.ZERO)
                crypto_text[-1].append(self.ONE if crypto & mask else self.ZERO)
            key_text[-1] = ''.join(key_text[-1])
            crypto_text[-1] = ''.join(crypto_text[-1])
        return (self.__class__(key_text, bits=key), self.__class__(crypto_text, bits=crypto))
    
    def getZoomedImage(self) -> str:
        out = []
        for line in self.lines:
            out.append([])
            out.append([])
            for c in line:
                if c == self.__class__.ONE:
                    out[-1].append(f"{self.__class__.ONE}{self.__class__.ZERO}")
                    out[-2].append(f"{self.__class__.ZERO}{self.__class__.ONE}")
                else:
                    out[-1].append(f"{self.__class__.ZERO}{self.__class__.ONE}")
                    out[-2].append(f"{self.__class__.ONE}{self.__class__.ZERO}")
            out[-1] = ''.join(out[-1])
            out[-2] = ''.join(out[-2])
        return '\n'.join(out)
    
    def __repr__(self) -> str:
        line = '\n'.join(self.lines)
        return f"Size: {self.width}x{self.height}\n{line}"

def main():
    if len(sys.argv) == 2:
        print(f"Encrypting message read from file: {sys.argv[1]}")
        message = Message.from_file(sys.argv[1])
        key, crypto = message.encrypt()
        with open(f"{sys.argv[1]}.key", "w", encoding="utf-8") as f:
            f.write(key.getZoomedImage())
        with open(f"{sys.argv[1]}.crypto", "w", encoding="utf-8") as f:
            f.write(crypto.getZoomedImage())
    elif len(sys.argv) == 3:
        print(f"Solving message from files {sys.argv[1]} and {sys.argv[2]}")
        key = Message.from_file(sys.argv[1])
        crypto = Message.from_file(sys.argv[2])
        print(Message.from_messages(key, crypto))
    else:
        print("use:")
        print(f"{sys.argv[0]}: <plaintext file>")
        print(f"{sys.argv[0]}: <key file> <cryptotext file>")

if __name__ == '__main__':
    main()