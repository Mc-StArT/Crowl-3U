import os
from CrRadio.CrRadio import CrRadio
from CrRadio.RadioEnvironment import *

crRadio = CrRadio(placement=0, debug=True)
# crRadio.sendFile(os.path.abspath("./test.b64"))