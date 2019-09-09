# Game_AI
When dancers collaborate on coding, fun is sure to ensue...
Python 3 and clojure are used for this Repository.
before using, install requirements

Then, see usage for how to initiate AI in an ipython session.

Usage:
import codenames.model_building as cmb

model = cmb.make_full_model()

import codenames.game_player as cgp

cgp.codemaster(model)

For clojure: 

If needed, install native cli, then:

cd Game_AI/clojure
clj -m clojure_clj.core
