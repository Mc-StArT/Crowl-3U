import sys
import os
from .CrRadio.CrRadio import CrRadio
from CrRadio import RadioEnvironment

crRadio = CrRadio(placement=1, debug=True)
crRadio.sendFile(os.path.abspath("./test.b64"))