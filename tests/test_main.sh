#!/bin/bash

ap.add_argument('-y','--year', type=int, help="year, integer")
ap.add_argument('-m','--month', type=int, help="month, integer")
ap.add_argument('-d','--day', type=int,  help="day, integer")
ap.add_argument('-h','--hour', type=int, help= 'hour, integer')
ap.add_argument('-i','--input', type=str, help="input directory, string")
ap.add_argument('-o','--output', type=str,  help="output directory, string")
ap.add_argument('-t','--temp', type=str, help="root for temporary directory, string")

YEAR=2003
MONTH=1
DAY=3
TEMP='/home/karger/scratch/'
INPUT='/storage/karger/chelsa_V2/INPUT_HIGHRES/'
OUTPUT='/storage/karger/chelsa_V2/OUTPUT_HIGHRES/'
ERA5='/storage/karger/ERA5/store/'
USERNAME='b381089'
PASSWORD='9331Joker1!'

HOUR=2
singularity exec -B /storage /home/karger/singularity/chelsa_highres_V.1.0.sif python /home/karger/scripts/chelsa_highres/chelsa_highres.py --year $YEAR --month $MONTH --day $DAY --hour $HOUR --temp $TEMP --era5 $ERA5 --input $INPUT --output $OUTPUT --password $PASSWORD --username $USERNAME

