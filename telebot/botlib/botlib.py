## Standard Library
import pickle
import io
import random

def start_logging():
    global logging
    import logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.DEBUG)

def pkload(fname: str) -> object:
    with open(fname, 'rb') as file:
        return pickle.load(file)

def pkdump(fname: str, obj: object) -> None:
    with open(fname, 'wb') as file:
        return pickle.dump(obj, file)

def load(fname: str) -> str:
    with open(fname, 'r') as file:
        return file.read()

def dump(fname: str, s: str) -> int:
    with open(fname, 'w') as file:
        return file.write(s)

def shuffled(x: list) -> list:
    y = list(x)
    random.shuffle(y)
    return y