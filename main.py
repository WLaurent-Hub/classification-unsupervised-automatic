import os
import otbApplication
from pathlib import Path
import glob

### Renommage les images sentinels 
def renameTIF():
    for tif in glob.glob(str(Path(__file__).parent) + "/*/*B*.tif"):
        output = tif.split('_')[0][:-10] + tif.split('_')[7]
        os.rename(tif, output) 

### réechantillonnage de la bande 11 pour toutes les années 
def reechantillonage():
    
    inr = glob.glob(str(Path(__file__).parent) + "/*/B4.tif" )
    inm = glob.glob(str(Path(__file__).parent) + "/*/" + "B11.tif")
    counter_year = len(glob.glob(str(Path(__file__).parent) + "/*/" + "B2.tif"))
    superimpose = otbApplication.Registry.CreateApplication("Superimpose")
    
    compteur = 0
    while compteur < counter_year:
        
        output_superimpose = str(Path(__file__).parent) + "/" + str(2015 + compteur) + "/B11_Superimpose"+ str(2015 + compteur) +".tif"

        superimpose.SetParameterString("inr", inr[1])
        superimpose.SetParameterString("inm", inm[compteur])
        superimpose.SetParameterString("out", output_superimpose)
        superimpose.ExecuteAndWriteOutput()
        compteur+=1
    
### classification non supervisée k-mean 
def classif_unsupervised():
    
    compteur = 0

    # appelle les fonctions otb
    concate = otbApplication.Registry.CreateApplication("ConcatenateImages")
    extract = otbApplication.Registry.CreateApplication("ExtractROI")
    radiometricIndice = otbApplication.Registry.CreateApplication("RadiometricIndices")
    # bandmath = otbApplication.Registry.CreateApplication("BandMath")
    list_indices = ['Vegetation:NDVI', 'Water:NDWI', 'Vegetation:SAVI','BuiltUp:ISU']
    kmean = otbApplication.Registry.CreateApplication("KMeansClassification")
    
    # boucle sur toutes les années
    for counter_year in glob.glob(str(Path(__file__).parent) + "/*/" + "B2.tif"):
        os.remove(str(Path(__file__).parent) + "/" + str(2015 + compteur) + "/B11.tif")
        output_concate = str(Path(__file__).parent) + "/" + str(2015 + compteur) +"/CONCAT_"+str(2015 + compteur) + ".tif"
        output_extractROI = str(Path(__file__).parent) + "/ROI_"+str(2015 + compteur) + ".tif"
        
        # concatène toutes les bandes d'une même année
        bandImage = glob.glob(str(Path(__file__).parent) + "/" + str(2015 + compteur)+"/B*")
        concate.SetParameterStringList("il", bandImage)
        concate.SetParameterString("out", output_concate)
        concate.ExecuteAndWriteOutput()
        
        # extraction de la zone d'étude
        extract.SetParameterString("in", output_concate)
        extract.SetParameterString("mode","extent")
        extract.SetParameterFloat("mode.extent.ulx", 485329)
        extract.SetParameterFloat("mode.extent.uly", 5422162)
        extract.SetParameterFloat("mode.extent.lrx", 495310)
        extract.SetParameterFloat("mode.extent.lry", 5416593)
        extract.SetParameterString("mode.extent.unit", "phy")
        extract.SetParameterString("out", output_extractROI)
        extract.ExecuteAndWriteOutput()
        
        # calcul les indices radiométriques NDVI, NDWI, SAVI et ISU (NDBI)
        for indice in list_indices:
            output_radiometric_indice = str(Path(__file__).parent) + "/RADIOMETRIC_"+ str(2015 + compteur) + indice.split(':')[1] +".tif"
            radiometricIndice.SetParameterString("in", output_extractROI)
            radiometricIndice.SetParameterString("list", indice)
            radiometricIndice.SetParameterValue("channels.blue",1)
            radiometricIndice.SetParameterValue("channels.green",2)
            radiometricIndice.SetParameterValue("channels.red",3)
            radiometricIndice.SetParameterValue("channels.nir",4)
            radiometricIndice.SetParameterValue("channels.mir",5)
            radiometricIndice.SetParameterValue("out", output_radiometric_indice)
            radiometricIndice.ExecuteAndWriteOutput()
            
            # input_bandmath = glob.glob(str(Path(__file__).parent) + "/RADIOMETRIC_*" + indice.split(':')[1]+ ".tif")
            # output_bandmath = str(Path(__file__).parent) + "/BANDMATH_"+ "20" + indice.split(':')[1] +".tif"
            # bandmath.SetParameterStringList("il", input_bandmath)
            # bandmath.SetParameterString("out", output_bandmath)
            # bandmath.SetParameterString("exp", "(im6b1-im5b1-im4b1-im3b1-im2b1-im1b1)")
            # bandmath.ExecuteAndWriteOutput()

        compteur+=1
        
    # concatène toutes les images 
    input_concat = glob.glob(str(Path(__file__).parent) + "/*"+ "20"+"*.tif")
    output_composition = str(Path(__file__).parent) + "/COMPOSITION"+".tif"
    concate.SetParameterStringList("il", input_concat)
    concate.SetParameterString("out", output_composition)
    concate.ExecuteAndWriteOutput()

    # classification kmean
    kmean = otbApplication.Registry.CreateApplication("KMeansClassification")
    kmean.SetParameterString("in", str(Path(__file__).parent) + "/COMPOSITION"+".tif")
    kmean.SetParameterInt("ts", 1000)
    kmean.SetParameterInt("nc", 5)
    kmean.SetParameterInt("maxit", 1000)
    kmean.SetParameterString("out", str(Path(__file__).parent) +"/ClassificationFilterOutput"+".tif")
    kmean.SetParameterOutputImagePixelType("out", 1)
    kmean.ExecuteAndWriteOutput()

        
renameTIF()
reechantillonage()
classif_unsupervised()