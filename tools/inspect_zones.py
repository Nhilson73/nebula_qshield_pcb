import sys
import pcbnew

board = pcbnew.LoadBoard(sys.argv[1])
for i, z in enumerate(board.Zones()):
    layer = z.GetLayer()
    layer_name = board.GetLayerName(layer)
    net = z.GetNet().GetNetname()
    priority = z.GetAssignedPriority()
    outline = z.Outline()
    box = outline.BBox()
    print(f"{i}: net={net} layer={layer_name} priority={priority} outlines={outline.OutlineCount()} bbox=({box.GetX()/1e6:.2f},{box.GetY()/1e6:.2f},{(box.GetX()+box.GetWidth())/1e6:.2f},{(box.GetY()+box.GetHeight())/1e6:.2f}) rule_area={z.GetIsRuleArea()}")
