
from PIL import Image
import numpy as np

def imread_png_indexed(filename):
  """ Load image given filename."""

  im = Image.open(filename)

  annotation = np.atleast_3d(im)[...,0]
  return annotation,np.array(im.getpalette()).reshape((-1,3))

def imsave_png_indexed(filename,array,color_palette):
  """ Save indexed png."""

  if np.atleast_3d(array).shape[2] != 1:
    raise Exception("Saving indexed PNGs requires 2D array.")

  im = Image.fromarray(array)
  im.putpalette(color_palette.ravel())
  im.save(filename, format='PNG')
