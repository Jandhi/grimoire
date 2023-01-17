# ESTM (Even Simpler Tile Model) Implementation

# Started off as this but I realized it is much easier to code a sudoku solver using WFC
# Much of the functions are redundant but I will clean everything up when we start using the code

import random
import math

def estm_canvas(x, y):
    main_area = [[0 for e in range(x)] for elem in range(y)]
    return main_area

def estm_repr(estc):
    for elem in estc:
        a = ""
        for e2 in elem:
            a += str(e2) + " "
        print(a)
        
def estm_repr_rc(estc):
    for elem in estc.keys():
        a = ""
        for e2 in estc[elem]:
            a += str(e2)
        print(a)
        
def estm_coord(est):
    a = len(est[0])
    b = len(est)
    ecoord = [[(e1,elem) for e1 in range(a)] for elem in range(b)]
    flat_ecoord = []
    for elem in ecoord:
        flat_ecoord += elem
    adj_res = {el: flat_ecoord[el] for el in range(len(flat_ecoord))}
    return ecoord, adj_res

def estm_rows(est):
    l = len(est)
    ret = {}
    for elem in range(l):
        ret[elem] = est[elem]
    return ret

def estm_cols(est):
    ret = {}
    for elem in range(len(est)):
        innerlist = []
        for e in range(len(est[elem])):
            innerlist.append(est[e][elem])
        ret[elem] = innerlist
    return ret

def estm_rc_ids(x, y):
    i = 0
    outerlist_r = []
    outerlist_c = []
    for elem in range(x):
        innerlist = []
        for e in range(y):
            i += 1
            innerlist.append(i)
        outerlist_r.append(innerlist)
    for elem in range(len(outerlist_r)):
        innerlist = []
        for e in range(len(outerlist_r[elem])):
            innerlist.append(outerlist_r[e][elem])
        outerlist_c.append(innerlist)
    return outerlist_r, outerlist_c

def estm_flat(est):
    ret = {}
    i = 0
    l = len(est)
    ret = {}
    for elem in range(l):
        for e in range(len(est[elem])):
            i += 1
            ret[i] = est[elem][e]
    return ret    

board_x = 9
board_y = 9
ecan = estm_canvas(board_x,board_y)
eco, adj_dict = estm_coord(ecan)
erows = estm_rows(eco)
ecols = estm_cols(eco)
eflat = estm_flat(eco)
erows_ids, ecols_ids = estm_rc_ids(board_x,board_y)
position = {"U": (0,-1), "D": (0,1), "L": (-1,0), "R": (1,0),
            "UL": (-1,-1), "UR": (1,-1), "DL": (-1,1), "DR": (1,1)}
options = list("123456789")

def make_blocks(co):
    ans = {elem:[] for elem in range(9)}
    for i in range(len(co)):
        for k in range(len(co[i])):
            if ((i <= ((i)%3)) and (k <= ((k)%3))):
                ans[0].append(co[i][k])
                ans[1].append(co[i][k+3])
                ans[2].append(co[i][k+6])
                ans[3].append(co[i+3][k])  
                ans[4].append(co[i+3][k+3])  
                ans[5].append(co[i+3][k+6])  
                ans[6].append(co[i+6][k])  
                ans[7].append(co[i+6][k+3])  
                ans[8].append(co[i+6][k+6]) 
    return ans

def make_blocks_2(co):
    ans = {elem:[] for elem in range(len(co))}
    o = 0
    for el in range(len(co)):
        for i in range(len(co)):
            for k in range(len(co[i])):
                if ((i <= ((i)%3)) and (k <= ((k)%3))):
                    ans[el].append(co[i][k+(3*(el%3))]) 
                    o += 1       
    return ans
                
def coord_sum(c1,c2):
    return (c1[0]+c2[0], c1[1]+c2[1])

def pos_avail(coor, maxh, maxw):
    answer = []
    x,y = coor
    if coor == (0,0):
        answer = ["D", "R", "DR"]
    elif coor == (0,maxh):
        answer = ["U", "R", "UR"]  
    elif coor == (maxw,0):
        answer = ["D", "L", "DL"]
    elif coor == (maxw,maxh):
        answer = ["U", "L", "UL"]      
    elif x == 0:
        answer = ["U", "UR", "R", "DR", "D"]
    elif y == 0:
        answer = ["L", "DL", "D", "DR", "R"] 
    elif x == maxw:
        answer = ["U", "UL", "L", "DL", "D"]
    elif y == maxh:
        answer = ["L", "UL", "U", "UR", "R"] 
    else:
        answer = list(position.keys())
    return answer

blks = make_blocks(erows_ids)

def pos_avail_coord(brd):
    ans = {}
    ans_2 = {a: [] for a in brd.keys()}
    for elem in brd.keys():
        ans[elem] = pos_avail(brd[elem], board_x-1, board_y-1)
    for elem in ans.keys():
        innerlist = []
        for e in ans[elem]:
            innerlist.append(coord_sum(brd[elem], position[e]))
        ans_2[elem] = innerlist
    return ans_2

available_positions_dict = pos_avail_coord(eflat)
efl_rev = {eflat[el]: el for el in eflat}
apd_ids = {elem: [efl_rev[el2] for el2 in available_positions_dict[elem]] for elem in available_positions_dict}
 
puzzle = {elem: 0 for elem in eflat}
puzzle.update({3:2, 5:1, 7: 3, 8:7, 9:8, 11:1, 12:5, 14:6, 15:3, 16:4, 17:2, 18:9,
               21:4, 22:9, 27:1, 28:9, 29:4, 31:1, 33:7, 37:1, 39:8, 43:7, 50:8, 52:1,
               55:2, 56:8, 58:5, 59:4, 62:1, 70:2, 72:7, 73:3, 74:5, 76:6, 77:7, 78:2, 79:9, 
               80:8})
def flat_rep(f):
    m = max(f.keys())**(1/2)
    for elem in f.keys():
        print(str(f[elem]), end = " ")
        if ((elem%m) == 0):
            print("\n", end="")
            
def entropy(ps):
    return -1*sum([elem*math.log(elem, 2) for elem in ps])

# entropy tests
entropy_t = list("1112265477") 
entropy_d = {elem: entropy_t.count(elem) for elem in entropy_t}
entropy_p = {elem: entropy_d[elem]/len(entropy_t) for elem in entropy_d.keys()}

def retrieve_blk(id_):
    for elem in blks.keys():
        if id_ in blks[elem]:
            return blks[elem], elem

def retrieve_row(id_):
    for elem in erows_ids:
        if id_ in elem:
            return elem, erows_ids.index(elem)
        
def retrieve_cols(id_):
    for elem in ecols_ids:
        if id_ in elem:
            return elem, ecols_ids.index(elem)

def rem_dups(alon):
    ans = []
    for elem in alon:
        if elem not in ans:
            ans.append(elem)
    return ans

def pool_vals(id_):
    main_pool = [] 
    b, b_id = retrieve_blk(id_) 
    r, r_id = retrieve_row(id_) 
    c, c_id = retrieve_cols(id_)
    ans = rem_dups(r+c+b)
    ans.sort()
    return ans
    
def sud_str(p):
    return "".join(list(map(str, p.values())))

def retrieve_actual(pos, puz):
    return [puz[elem] for elem in pool_vals(pos)]

soln1 = '692415378815763429734928561946157832128396745573284196287549613469831257351672984'

