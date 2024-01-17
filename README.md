# Enzyme_photometric_activity
This program code was written to identify the linear range (i.e., the initial enzyme activity) to calculate a more reliable and transparent slope for the photometric analysis of enzymatic activity.
First an amount of points N is defined. With this defined N the program looks through all points in time, makes the linear regression and checks if the R2 is larger than 0.95. If that is the case the program saves the value and looks for the next point. If it finds a larger linear regression with an R2 over 0.95 it saves this value.
After this, the calculated slopes were used to subtract the blank from the values and do further calculations depending on the type of assay.
