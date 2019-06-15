#demo 1: in command line, enter:
# python3 demo1.py


import codenames.model_building as cmb
model = cmb.make_full_model()
import codenames.game_player as cgp
cgp.codemaster(model)
