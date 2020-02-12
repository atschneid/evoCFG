:- dynamic s/2.
:- dynamic s0/2.
:- dynamic np/2.
:- dynamic n/2.
:- dynamic n0/2.
:- dynamic vp/2.
:- dynamic v/2.

s --> s0.
s --> s0, ['conj'], s.

s0 --> np, vp.

np --> n.
np --> [det], n.
np --> ['wh'].
np --> ['pron'].

n --> n0, ['conj'], n.
n --> n0.
    
n0 --> ['noun'].
n0 --> ['adj'], n0.

vp --> v.
vp --> v, np.
vp --> v, ['prep'], np.

v --> ['verb'].
v --> ['adv'], v.

