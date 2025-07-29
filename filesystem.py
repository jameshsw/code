"""
input() should be write one character , or several space to break when input done. 
"""
from typing import List, ValuesView

# Implement the print method.
# The major constraint here is that storage in the filesystem consists of a fixed size list of blocks.
# Print the contents of data in the following format:
# “[[a,b,c,d,e,f,g,h], [i,j,k,l,m,n,o,p]]” for [Node(”abcdefgh”), Node(”ijklmnop”)].

# Add write and read methods. 
# Write data at position pos, read n bytes starting at position pos.
# n, pos, len(data) must always be a multiple of 8 chars.

class Node:
    def __init__(self, data: str):
        #    data: str # 8 chars
        self.data = data
            

class Filesystem():
    def __init__(self, nodes:List[Node]):
        self.nodes = nodes
    # nodes: List[Node]
    def print(self):
        # pass
        res = []
        for node in self.nodes:
            c = list(node.data)
            res.append(f"[{','.join(c)}]")
        print(f"[{', '.join(res)}]")

    def read(self, pos: int, n: int) -> str:
        # pass
        if (pos+n) > len(self.nodes)*8:
            raise ValueError("Read data larger than data size")
        start_i = pos//8
        num_blocks = n//8
        return ''.join([node.data for node in self.nodes[start_i:start_i+num_blocks]])
    
    def write(self, pos: int, data: str) -> None:
        # pass
        start_i = pos//8
        num_blocks = len(data)//8
        if start_i+num_blocks > len(self.nodes):
            raise ValueError("Write data larger than data size")
        for i in range(start_i, start_i+num_blocks):
            chunk = data[(i-start_i)*8:(i-start_i+1)*8]
            self.nodes[i].data = chunk

fs = Filesystem([
        Node("abcdefgh"), 
        Node("ijklmnop")
    ])


fs.print()
fs.write(8,"12345678")
fs.print()
print(fs.read(8,8))
# print(fs.read(8,16))
# fs.write(8,"1234567812345678")

