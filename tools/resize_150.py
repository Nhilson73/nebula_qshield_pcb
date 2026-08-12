import pcbnew, math, sys

b=pcbnew.LoadBoard('/workspace/kicad/nebula_qshield.kicad_pcb')

# New board dims: 150 x 120 mm (current 125 x 120 mm)
left=-8.0; bottom=-2.0; right=142.0; top=118.0
r=2.5

def add_seg(x1,y1,x2,y2):
    s=pcbnew.PCB_SHAPE(b); s.SetLayer(pcbnew.Edge_Cuts); s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(pcbnew.VECTOR2I(int(round(x1*1e6)), int(round(y1*1e6))))
    s.SetEnd(pcbnew.VECTOR2I(int(round(x2*1e6)), int(round(y2*1e6))))
    b.Add(s)

def add_arc_shape(start, mid, end):
    arc=pcbnew.PCB_SHAPE(b); arc.SetLayer(pcbnew.Edge_Cuts); arc.SetShape(pcbnew.SHAPE_T_ARC)
    arc.SetArcGeometry(pcbnew.VECTOR2I(int(round(start[0]*1e6)), int(round(start[1]*1e6))),
                       pcbnew.VECTOR2I(int(round(mid[0]*1e6)), int(round(mid[1]*1e6))),
                       pcbnew.VECTOR2I(int(round(end[0]*1e6)), int(round(end[1]*1e6))))
    b.Add(arc)

def add_arc90(cx,cy,r,a0,a1):
    start=(cx+r*math.cos(math.radians(a0)), cy+r*math.sin(math.radians(a0)))
    end=(cx+r*math.cos(math.radians(a1)), cy+r*math.sin(math.radians(a1)))
    mid=(cx+r*math.cos(math.radians((a0+a1)/2)), cy+r*math.sin(math.radians((a0+a1)/2)))
    add_arc_shape(start, mid, end)

# Remove all Edge.Cuts drawings
remove=[d for d in b.GetDrawings() if d.GetLayer()==pcbnew.Edge_Cuts]
for d in remove:
    b.Remove(d)

# Add rounded rectangle
add_seg(left+r, bottom, right-r, bottom)
add_seg(right-r, top, left+r, top)
add_seg(left, top-r, left, bottom+r)
add_seg(right, bottom+r, right, top-r)
add_arc90(right-r, bottom+r, r, 270, 360)
add_arc90(right-r, top-r, r, 0, 90)
add_arc90(left+r, top-r, r, 90, 180)
add_arc90(left+r, bottom+r, r, 180, 270)

# Add small cutouts (keep original)
cutouts=[
    [(2.08,81.56),(22.5,81.56),(22.5,94.56),(2.08,94.56)],
    [(60.08,88.56),(77.08,88.56),(77.08,94.56),(60.08,94.56)],
]
for pts in cutouts:
    poly=pcbnew.SHAPE_POLY_SET(); chain=pcbnew.SHAPE_LINE_CHAIN()
    for x,y in pts:
        chain.Append(int(round(x*1e6)), int(round(y*1e6)))
    chain.SetClosed(True); poly.AddOutline(chain)
    shape=pcbnew.PCB_SHAPE(b); shape.SetLayer(pcbnew.Edge_Cuts); shape.SetShape(pcbnew.SHAPE_T_POLY); shape.SetPolyShape(poly)
    b.Add(shape)

# Update full-board zones (those whose current outline covers the 125x120 board)
updated=0
for z in b.Zones():
    bb = z.GetBoundingBox()
    zleft = bb.GetLeft()/1e6
    ztop = bb.GetTop()/1e6
    zright = bb.GetRight()/1e6
    zbottom = bb.GetBottom()/1e6
    # match current full board zones (left/top near -8/-2, right near 117, bottom near 118)
    if abs(zleft+8) < 1 and abs(ztop+2) < 1 and abs(zright-117) < 1 and abs(zbottom-118) < 1:
        outline = z.Outline()
        outline.RemoveAllContours()
        chain = pcbnew.SHAPE_LINE_CHAIN()
        for x,y in [(left,bottom),(right,bottom),(right,top),(left,top)]:
            chain.Append(int(round(x*1e6)), int(round(y*1e6)))
        chain.SetClosed(True)
        outline.AddOutline(chain)
        z.SetNeedRefill(True)
        updated += 1

pcbnew.SaveBoard('/workspace/kicad/nebula_qshield.kicad_pcb', b)
print('Saved 150x120 board. Updated', updated, 'zones')
