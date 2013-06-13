#!/usr/bin/python

# Implementation of Charikar simhashes in Python
# See: http://dsrg.mff.cuni.cz/~holub/sw/shash/#a1

def hamming_distance(one_hash, other_hash, hashbits):
    x = (one_hash ^ other_hash.hash) & ((1 << hashbits) - 1)
    tot = 0
    while x:
        tot += 1
        x &= x-1
    return tot


class Simhash():
    def __init__(self, tokens='', hashbits=128):
        self.hashbits = hashbits
        self.hash = self.simhash(tokens)

    def __str__(self):
        return str(self.hash)
    
    def __long__(self):
        return long(self.hash)

    def __float__(self):
        return float(self.hash)
    
    def simhash(self, tokens):
        # Returns a Charikar simhash with appropriate bitlength
        v = [0]*self.hashbits
    
        for t in [self._string_hash(x) for x in tokens]:
            bitmask = 0
            for i in xrange(self.hashbits):
                bitmask = 1 << i
                if t & bitmask:
                    v[i] += 1
                else:
                    v[i] -= 1
    
        fingerprint = 0
        for i in xrange(self.hashbits):
            if v[i] >= 0:
                fingerprint += 1 << i
        
        return fingerprint

    def _string_hash(self, v):
        # A variable-length version of Python's builtin hash
        if v == "":
            return 0
        else:
            x = ord(v[0])<<7
            m = 1000003
            mask = 2**self.hashbits-1
            for c in v:
                x = ((x*m)^ord(c)) & mask
            x ^= len(v)
            if x == -1: 
                x = -2
            return x

    def hamming_distance(self, other_hash):
        x = (self.hash ^ other_hash.hash) & ((1 << self.hashbits) - 1)
        tot = 0
        while x:
            tot += 1
            x &= x-1
        return tot

    def similarity(self, other_hash):
        a = float(self.hash)
        b = float(other_hash)
        if a>b: return b/a
        return a/b

if __name__ == '__main__':
    s = 'This is a test string for testing'
    hash1 = Simhash(s.split())
    print "%s\t[simhash = 0x%x]" % (s, hash1)

    s = 'This is a test string for testing also!'
    hash2 = Simhash(s.split())
    print "%s\t[simhash = 0x%x]" % (s, hash2)

    print hash1.similarity(hash2), "percent similar"
    print hash1.hamming_distance(hash2), "bits differ out of", hash1.hashbits