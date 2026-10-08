def calculate_ndvi(nir, red):
    return (nir-red)/(nir+red)