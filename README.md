# PHANTOM 4 RTK PPK PROCESSING FROM TRIMBLE BUSINESS CENTER 

Code created for optimising the tedious PPK processing using the TBC trajectory solutions. 
I know that RTKLIB is a better option (sometimes), but if you're a surveyor and work with TBC every day to adjust GNSS solutions and coordinates stuff, this could improve your workflow.

Interpolation formulas are approximated using the latitude location From AEROTAS xls file. (www.aerotas.com)
It is currently set to WGS84 UTM19S (Chile)



## Installation

Using Conda environment with:
Pandas
Geopy
Pyproj

Workflow tested in production using PyCharm.

## Usage

In Windows:

rename all folders Containing one flight to match the sequential structure
V01, V02, V03...

In powershell:
rename all files in the "flights" folder using this code:

```
$rootFolder = 'd:\flights'
(Get-ChildItem -Path $rootFolder -Filter '*' -File -Recurse) | 
    Where-Object { $_.Name -notmatch "^$($_.Directory.Name)_" } |
    Rename-Item -NewName { '{0}_{1}' -f $_.Directory.Name, $_.Name }.}
```


In TBC:

load the .obs files and the .T02 base file to process the PPK trajectory. It is recommended to download precise ephemerides into the project to secure L1/L2 fixed solutions. 

Extract flight trajectories using lat long (Global) coordinate system with 8 decimals. (ellipsoidal heights are attached by default, if you need to extract geoidal heights or local vertical systems, you should extract those heights from TBC and replace them in the .csv trajectory file)

In PyCharm:

Add the V0x.csv flight trajectory positions and the .MRK files from the Phantom 4 RTK files to the project folder.

Edit the code to match the .MRK information and photo´s name structure and add V0x flights depending on how much information you´ll need to process. 

Run the code, copy the FV0x.csv photo positions files to a new folder.

Merge the final position files using PowerShell:
```
Get-Content *.csv| Add-Content output.csv
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
