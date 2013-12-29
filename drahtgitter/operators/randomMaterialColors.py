'''
Apply random material color to a model (useful for debugging)
'''
import random
from ..core import *

#-------------------------------------------------------------------------------
def do(model) :
    for mat in model.materials :
        if mat.hasParam('Diffuse') :
            val = mat.get('Diffuse')
            val.x = random.uniform(0.5, 1.0)
            val.y = random.uniform(0.5, 1.0)
            val.z = random.uniform(0.5, 1.0)
    return model

