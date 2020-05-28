## Standard Library
import pickle

def log():
    global logging
    import logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.DEBUG)

def pkload(fname: str):
    with open(fname, 'rb') as file:
        return pickle.load(file)

def pkdump(fname: str, obj: object):
    with open(fname, 'wb') as file:
        pickle.dump(obj, file)

def load(fname: str):
    with open(fname, 'r') as file:
        return file.read()

def dump(fname: str, s: str):
    with open(fname, 'w') as file:
        return file.write(s)

