from numpy import mean,cov,cumsum,dot,linalg,size,flipud
from pylab import *
from r_numpy_lib import *
def princomp(A,numpc=0):
    print 'Computing PC'
    nd = 2
    shp = numpy.shape(A)
    if numpy.ndim(A) == 3:
        at = []
        nd = 3
        for i in range(len(A)):
            at.append(A[i].flatten())
        A = numpy.array(at)
        at = None
        del at
    # computing eigenvalues and eigenvectors of covariance matrix
    M = (A-mean(A.T,axis=1)).T # subtract the mean (along columns)
    [latent,coeff] = linalg.eig(cov(M))

    A = None
    del A
    
    p = size(coeff,axis=1)
    idx = argsort(latent) # sorting the eigenvalues
    idx = idx[::-1]       # in ascending order
    # sorting eigenvectors according to the sorted eigenvalues
    coeff = coeff[:,idx]
    latent = latent[idx] # sorting eigenvalues
    if numpc < p or numpc >= 0:
        coeff = coeff[:,range(numpc)] # cutting some PCs
        score = dot(coeff.T,M) # projection of the data in the new space
    latent = None
    
    if nd == 3:
        coeff = coeff.flatten('a').reshape((numpc,shp[1],shp[2]))
    return coeff#,score,latent


x = numpy.arange(500).reshape(5,10, 10)
ti = 'W:/03_Data-Archive/02_Inputs/Landsat_Data/Landsat_Spectral_Data/Masked_Outputs/LT50410261985184PAC04_toa_masked.img'
#br = brick(ti, band_list = [1,2,3,4,5,7])
components = 3
pc = princomp(br, components)
print 'done'
#for i in range(components):
    

