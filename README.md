# The Big Picture

The United States is in an ongoing opioid epidemic. Since the 2000s, the opiodi death rate has steadily increased, reaching 32.6 deaths per 100,000 standard population in 2022 (Spencer, 2024). The severity of the epidemic has inspired a large research effort around understanding causes of opioid risk and provisioning harm reduction resources. From computational researchers, a common approach has been to attempt to nowcast opioid overdose events (OOE) and deaths, using a variety of traditional and big data sources as the predictive features. Results have varied, with some researchers finding low predictability (Cuomo et al., 2023; Gavali et al., 2021; Schell et al., 2022). while others using non-traditional datastes or more complex methods have achieved higher predictability (Bozorgi et al., 2021; Li et al., 2022). One incredibly promising resource has been Google Streetview Imagery, which allows for computational evaluation of the context in which opioids are used (Li et al., 2022).

The focus on nowcasting OOE and deaths is of vital importance and may better enable policy makers to accurately place resources in-the-moment, but an overemphasis on nowcasting in the computational literature has limited the ability of policy makers to place longer term harm reduction resources and investment. 

Towards alleviating this issue, we undertake a computational regionalization study in which we attempt to identify differing regions of opioid risk within the city of Chicago. For this study, we pull inspiration from two sources. First, we build our study around the opioid risk environment (ORE) framework developed by Rhodes (2002), which considers opioid risk as being constructed of four risk environments -- the social, economic, political, and physical environment -- and at two scales -- the micro and macro. Secondly, inspired by the success of Li et al. (2022) in using Google StreetView imagery to predict opioid overdose events, we utilize Google StreetView Imagery to better characterize the physical risk environment. 

In sum, our study selects variables within the social, economic, and political environment, which we use to construct within environment regions. In the larger paper we validate these regions and compare their ORE framework predicted risks to narcotic arrests, a proxy for opioid overdose events and usage, and discover correlations between the spatial distribution of the modern opioid risk environment and historic redlining by the Homeowners Loan Corperation (HOLC). 

FUTURE SELF ADD THE IMAGE HERE

# The Big Data Component 

Our study sought to characterize three aspects of the built environment -- perceived liveliness, perceived depressingness, and relative greenery -- using Google StreetView imagery. Doing as such requires large amounts of image data that need to be processed through segmentation models, meaning our proposal requires usage of high performance computing methods. Our final pipeline consisted of 6 key steps:

1. **Getting Points:** We randomly select 25,000 points from the Chicago street network and assign each point with a random heading (SCRIPT). We then query the Google StreetView metadata API to determine which points actually have associated StreetView imagery, discovering that 24,240 images work (INSERT SCRIPT HERE)

2. **Getting Images:** We create a lambda function which takes in a list of API calls, which it uses to retrieve Google StreetView imagery, with each image being stored in an S3 bucket (SCRIPTS). We then retrieve all 24,240 images through Lambda step functions (SCRIPTS). Notably, potentially due to constraints on Step Functions called from AWS Student account, we are forced to call our Step Functions multiple times, so that our data is split into "superbatches" (e.g. doing 100 superbatches in which we provide a step function with 2,500 requests to split between 10 lambda functions).

3. **Moving to Midway:** Due to reasons of researcher preference, we opt to do as much of our analysis on the Midway clusters as possible. As such, we retrieve our StreetView imagery from S3 using boto3 (SCRIPT), and additionally retrieve Place Pulse 2.0 imagery -- used in the next steps -- from UChicago Box (SCRIPT).

4. **Image Segmentation:** We semantically segment our 24,240 images using a pretrained semantic segmentation model from MIT (Cite) (SCRIPT SBATCH). We additionally semantically segment our Place Pulse 2.0 imagery using the same model (SCRIPT SBATCH).

5. **Final Feature Creation:** The feature creation portion of our pipeline is forked.
    1. **Relative Greenery Index:** We create our relative greenery index in two steps. First, we calculate and absolute greenery index $G_{abs}$ for each image by taking the total number of pixels in the image classified as one of "grass", "field", "flower", "hill", or "tree" (SCRIPT). Then, we calculate the relative greenery index of an image through the following equation:
    $$g_{img}=\frac{G_{img}-\min_{j\in\text{Images}}G_j}{\max_{j\in\text{Images}}G_j-\min_{j\in\text{Images}}G_j}$$
    2. **Percieved Aspects of the Built Environment:** The Place-Pulse 2.0 Survey released a series of over 100,000 StreetView images -- which we segmented in step 4 -- along with associated perceived liveliness and boringness values. We use pyspark to construct and validate a few basic Machine Learning models in an attempt to generalize these predictions to our corpus (SBATCH SCRIPT). However, due to poor model performance (we achieve an $R^2$ of at best EX), we decline to label our 24,240 Chicago images.

6. **Long Term Data Storage:** In order to increase the long term replicability of this project, we migrate our data from S3 to UChicago Box (utilizing the download script and a manual upload to box). Additionally, we include our Place-Pulse 2.0 imagery, allowing users to download the data to recreate our ML pipeline with less fear of link rot.

# Next Steps and Future Improvements

The benefit of our current pipeline is that it is highly scaleable and segmentable. Our current largest limitation is the limited predictability of our segmented images. However, this is most likely due to our choice of semantic segmentation model, with the chosen model containing mostly terms which are better suited towards classifying interior scenes than outdoor scenes. Over the summer, we thus plan to revise step 4 of our pipeline by changing the specific image segmentation model chosen. 

Additionally, scalability of our pipeline means we can easily deploy this workflow in other cities. Specifically deploying this pipeline in New York City, would only require the acquisition of another city street shapefile and additional Google StreetView API credits. Scaleability thus opens the door for future work comparing the risk environment between multiple settings.

# Copying

This project is licensed under the GNU General Public License v3.0. The full license can be read [here](COPYING).