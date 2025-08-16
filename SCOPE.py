import numpy as np
import time
from datetime import datetime
from astropy.table import Table as t, vstack, hstack, join
from astropy.coordinates import SkyCoord as sc, EarthLocation as el, AltAz as aa, get_sun
from astropy.time import Time
from astropy import units as u
import matplotlib.pyplot as plt

print("Welcome to SCOPE (Stellar Catalog & Observation Planning Engine) !",end='\n\n')
time.sleep(1.5)

# Asking user to enter the name of the file consisting of the star catalog
fname=input("Enter the name of the file (in .csv / .fits) consisting of the star catalog: ")

# Ensuring that the file has a .csv / .fits extension only
if not ((fname.lower().endswith('.csv')) or (fname.lower().endswith('.fits'))):
  print("ERROR: This program supports only .csv / .fits files !!!",end='\n\n')
  time.sleep(1.5)
  print("Your session has been TERMINATED.")
  exit()

# Setting table format based on file extension (.csv / .fits)
if (fname.lower().endswith('.csv'))==True:
  fmt='csv'
else:
  fmt='fits'

# Ensuring that the file provided by the user exists
try:
  readtable=t.read(fname,format=fmt)
except FileNotFoundError:
  print(f"ERROR: File {fname} not found !!! Please check the name and try again !!!")
  time.sleep(1.5)
  print("Your session has been TERMINATED.")
  exit()

# Ensuring that the table in the file provided is non-empty
try:
  if len(readtable)==0:
    raise ValueError
except ValueError:
  print(f"ERROR: The table in file {fname} is EMPTY !!!")
  time.sleep(1.5)
  print("Your session has been TERMINATED.")
  exit()

# Ensuring that the user is made aware of any NULL or empty string entries present in string-type columns

nullinx,nullrow=[],[]                        # Lists to store indices and rows containing nulls

# Scanning the entire table for NULL or EMPTY string values
for index,row in enumerate(readtable):
  for val in row:
    if isinstance(val,(str)) and val.strip()=='':
      nullinx.append(index)                  # Store row index
      nullrow.append(row)                    # Store full row contents
      break                                  # Stop checking further in the same row once a null is found

# If null or empty string values are detected, displaying a structured warning and guiding the user
if len(nullinx)!=0:
  print("*** NULL OR EMPTY STRING VALUES DETECTED IN THE LOADED TABLE ***", end='\n\n')
  print("> One or more rows contain EMPTY entries in string-type columns (e.g., '', ' ', or multiple spaces).")
  print("> These may affect operations like sorting, filtering, or plotting, and etc, if those columns are involved.", end='\n\n')
  print('*************************************************************************************************************************************************',end='\n\n')
  time.sleep(1.5)

  # Displaying all rows with detected nulls, along with their row indices, for user reference
  print("The following row(s) contain NULL or EMPTY values and will be displayed with their corresponding row indices:",end='\n\n')
  print('ROW INDEX: ROW',end='\n\n')
  for i in range(len(nullinx)):
    print(f'{nullinx[i]}:',nullrow[i])
  time.sleep(1.5)

  # Informing the user regarding next steps: optional row deletion, caution when proceeding, or manual data cleanup
  print(">>> NEXT STEPS: Recommended actions to handle the null or empty values identified above.", end='\n\n')
  print("> You may use the 'DELETE ROW(S)' option under 'DELETE COLUMNS OR ROWS' in the CATALOG OPERATIONS MENU to remove these rows if necessary.")
  print("> Alternatively, you can proceed with all features - but exercise caution when using columns with empty values.")
  print("> For critical analysis, it is RECOMMENDED to clean or validate the data manually before continuing.", end='\n\n')
  print('*************************************************************************************************************************************************',end='\n\n')
  time.sleep(1.5)

# Displaying the extracted table to user
time.sleep(1.5)
print(f"The catalog/table extracted from {fname} is: ",end='\n\n')
readtable.pprint_all()
print('\n')
print('*************************************************************************************************************************************************',end='\n\n')
time.sleep(1.5)

###################################################################################################################################################################################

# Providing user with some important instructions before using the program
print("NOTE: PRECAUTIONS ON SESSION SCOPE & FILE HANDLING POLICY",end='\n\n')
print('*************************************************************************************************************************************************',end='\n\n')
time.sleep(1)

print(f"-- ALL OPERATIONS IN THIS SESSION ARE PERFORMED ON '{fname}', REFERRED TO AS THE **MASTER TABLE**.", end='\n\n')
time.sleep(1.5)

print("-- If you **SAVE A NEW FILE** (e.g., after filtering, sorting, or adding columns) and want to continue operations on that file,")
print("   you must **TERMINATE THE CURRENT SESSION** and **RESTART THE PROGRAM** using that file.", end='\n\n')
time.sleep(1.5)

print("-- To avoid session termination, it is **RECOMMENDED TO APPLY ALL MODIFICATIONS DIRECTLY TO THE MASTER TABLE** whenever possible.", end='\n\n')
time.sleep(1)

print("-- The only exception is the **Append Columns From Another Table or Merge Tables** operation from Catalog Operations,")
print("   which allows you to **COMBINE TWO SEPARATE FILES** (including filtered subsets). This feature lets users achieve **OR‐LIKE FILTERING**,")
print("   which is NOT supported directly within the filter loop.", end='\n\n')
time.sleep(1.5)

print(" >>> **NOTE**: When using **Append Columns From Another Table or Merge Tables** operation, you will be asked to **ENTER THE FILENAMES**")
print("               of the two filtered datasets you wish to combine. This process is independent of the current session's master table.", end='\n\n')

print('*************************************************************************************************************************************************',end='\n\n')
time.sleep(1.5)

###################################################################################################################################################################################

# Creating a function to save a table in a given file based on user input
def save(newtable):
  time.sleep(1.5)
  # Save Menu
  print('*************************************************************************************************************************************************',end='\n\n')
  print(":::::::::::::::::::::::::  SAVE MENU  :::::::::::::::::::::::::",end='\n\n')
  print('Do you want to save this updated table to file?',end='\n\n')
  print('1. Overwrite original.')
  print('2. Save to a new file.')
  print('3. Discard changes.',end='\n\n')
  print('*************************************************************************************************************************************************',end='\n\n')
  time.sleep(1.5)

  print("NOTE: SAVE WARNING",end='\n\n')
  print('*************************************************************************************************************************************************',end='\n\n')
  print(">>> When using 'save to a new file', saving to an existing file will fully overwrite it - no merging is done.")
  print(">>> To preserve original data and safely add new results, save to a new file and use 'Append Columns' under Catalog Operations.",end='\n\n')
  print('*************************************************************************************************************************************************',end='\n\n')
  time.sleep(1.5)

  while True:
    # Asking user for the choice from the above options
    och=input("Enter a valid choice from the save menu: ").strip()
    print('\n')
    print('*************************************************************************************************************************************************',end='\n\n')

    # If user wants to overwrite the original data
    if och=='1':
      # Overwriting the original data
      newtable.write(fname,format=fmt,overwrite=True)

      # Mechanism to check whether the operation was successful or not
      if (t.read(fname,format=fmt))==newtable:
        print("Overwrite was SUCCESSFUL !!!!")
        break
      else:
        print("Overwrite was UNSUCCESSFUL !!! Please try again !!!")

    # If the user wants to save the updated data in a new file
    elif och=='2':
      fname_new=input("Please enter a name for the new file (in .csv / .fits) where the updated data should be saved: ")

      if not ((fname_new.lower().endswith('.csv')) or (fname_new.lower().endswith('.fits'))):
        print("ERROR: This program supports only .csv / .fits files !!!",end='\n\n')
        time.sleep(1.5)
        print("Your session has been TERMINATED.")
        continue

      if (fname_new.lower().endswith('.csv'))==True:
        new_fmt='csv'
      else:
        new_fmt='fits'

      newtable.write(fname_new,format=new_fmt,overwrite=True)

      # Mechanism to check whether the operation was successful or not
      if (t.read(fname_new,format=new_fmt))==newtable:
        print("The updated data has been saved SUCCESSFULLY in the new file !!! ")
        break
      else:
        print("The updated data could NOT be saved successsfully in the new file !!! Please try again !!!")

    # If the user does not want the updated data to be saved in file
    elif och=='3':
      print("Are you sure you want to discard changes?")
      check=input("Enter (y / Y / yes / YES), if you want to SAVE the CHANGES: ")

      if check in ['y','Y','yes','YES']:
        continue
      else:
        print("The changes have been DISCARDED !!!")
        break

    # If the user goes with an invalid choice
    else:
      print("INVALID choice from Save Menu !!! Please enter a valid choice !")

###################################################################################################################################################################################

# Creating a function to display a table in either summarized or full view based on user input
def display(display_string,table_to_display):
  # Table Display Menu
  print(":::::::::::::::::::::::::  TABLE DISPLAY MENU  :::::::::::::::::::::::::",end='\n\n')
  print("1. Summarized View  -  Default view showing only head and tail.")
  print("2. Full View        -  Entire table with all rows and columns.")
  time.sleep(1.5)

  dispch=input("Enter a valid choice from the table display menu: ").strip()
  print('\n')
  print('*************************************************************************************************************************************************',end='\n\n')
  time.sleep(1.5)

  if dispch!='2':
    print(display_string + '(in default view)',end='\n\n')
    print(table_to_display,end='\n\n')                                          # Display the default summary view (Astropy's standard table print)
    print('*************************************************************************************************************************************************',end='\n\n')
  else:
    print(display_string + '(in full view)',end='\n\n')
    table_to_display.pprint_all()                                               # Display the full table using Astropy's pprint_all() to show all rows and columns
    print('\n')
    print('*************************************************************************************************************************************************',end='\n\n')

###################################################################################################################################################################################

# Creating a function which prompts the user until a valid float or int is entered, based on dtype
def only_num(inpl,dtype):
  # Repeatedly ask until a valid int / float is entered
  while True:
    val=input(inpl)

    if dtype=='int':
      try:
        return int(val)     # Accept only integer input
      except ValueError:
        # Show error and retry
        print(f"{val} is NOT a VALID input !!!")
        print("Input involving ONLY INTEGER data type is ALLOWED !!!",end='\n\n')
        time.sleep(1.5)
        continue

    else:
      try:
        return float(val)   # Accept only float input
      except ValueError:
        print(f"{val} is NOT a VALID input !!!")
        print("Input involving ONLY FLOATING POINT data type is ALLOWED !!!",end='\n\n')
        time.sleep(1.5)
        continue

###################################################################################################################################################################################

# Start of SCOPE
while True:
  # Main Menu
  print(":::::::::::::::::::::::::  MAIN MENU  :::::::::::::::::::::::::",end='\n\n')
  print('1. Catalog Operations     -  Analyze, filter, and organize stellar data.')
  print('2. Observational Planner  -  Convert coordinates and check star visibility based on location and time.')
  print('3. Visualization Module   -  Plot and explore stellar data using graphs.')
  print('4. Exit                   -  Terminate the session.',end='\n\n')
  time.sleep(1.5)

  ch=input("Enter a valid choice from the main menu: ").strip()
  print('\n')
  print('*************************************************************************************************************************************************',end='\n\n')

################################################################################################################################################################################
################################################################################################################################################################################

  # If the user goes with the choice of performing catalog operations from Main Menu
  if ch=='1':
    loop=0 # Creating a variable loop with initial value pointing to 0.
    while True:
      if loop!=0: # If the catalog operations loop continues more than once the below line would be printed after every loop
        print("The program will now return back to the Catalog Operations Menu !",end='\n\n')

      time.sleep(1.5)
      # Catalog Operations Menu
      loop+=1     # After every loop an increment of 1 would be made to the value of loop
      print('*************************************************************************************************************************************************',end='\n\n')
      print("::::::::::::::::::::::::: CATALOG OPERATIONS MENU  :::::::::::::::::::::::::",end='\n\n')
      print('1. Sort Records.')
      print('2. Group Records by Attribute.')
      print('3. Filter Entries.')
      print('4. Derive & Append Physical Data (e.g.: absolute magnitude, luminosity).')
      print('5. Append Columns From Another Table or Merge Tables.')
      print('6. Delete Columns or Rows.')
      print('7. Return back to main menu.',end='\n\n')
      time.sleep(1.5)

      chco=input("Enter a valid choice from the catalog operations menu: ").strip()
      print('\n')
      print('*************************************************************************************************************************************************',end='\n\n')

################################################################################################################################################################################

      # If the user goes with the choice of sorting records
      if chco=='1':
        sortcol=input("Enter the name of the column according to which the sorting of data is to be performed: ")
        print('\n')

        # Ensuring that the column name provided exists in the file
        if sortcol in readtable.colnames:
          print("Note: Sorting in ascending order is performed numerically for quantitative columns and alphabetically (A-Z) for textual columns.",end='\n\n')
          print('*************************************************************************************************************************************************',end='\n\n')
          time.sleep(1.5)

          # Sort Menu
          print(":::::::::::::::::::::::::  SORT MENU  :::::::::::::::::::::::::",end='\n\n')
          print("1. Sort in ascending order.")
          print("2. Sort in descending order.",end='\n\n')
          time.sleep(1.5)

          # Asking user for their choice from the sort menu
          chso=input("Enter your choice for sorting order: ").strip()
          print('\n')
          print('*************************************************************************************************************************************************',end='\n\n')

          # Initially sorting the table in ascending order
          sortedtable=readtable.sort(sortcol)

          # If the user wants to sort data in ascending order
          if chso=='1':
            dispstr=f"The sorted table according to {sortcol} column in ascending order is:"

          # If user wants to sort data in descending order
          elif chso=='2':
            sortedtable.reverse()
            dispstr=f"The sorted table according to {sortcol} column in descending order is:"

          # Invalid choice by user (user returns back to the main menu)
          else:
            print("INVALID choice from sort menu !!!",end='\n\n')
            continue

          # Displaying the sorted table and initializing the procedure to save the sorted table
          display(dispstr,sortedtable)
          save(sortedtable)

        # If user enters a column name which does not exist in the file provided
        else:
          print(f"The column {sortcol} provided does not exist in the file {fname} !!!",end='\n\n')

################################################################################################################################################################################

      # If the user goes with the choice of grouping records via attributes
      elif chco=='2':
        grpcol=input("Enter the name of the column according to which the grouping of data is to be performed: ",end='\n\n')

        if grpcol in readtable.colnames:
          grptable=readtable.group_by(grpcol)
          display(f"The grouped table according to {grpcol} attribute is:",grptable)
          save(grptable)

        else:
          print(f"The column {grpcol} provided does not exist in the file {fname} !!!",end='\n\n')

##################################################################################################################################################################################

      # If the user goes with the choice of filtering entries
      elif chco=='3':
        # Creating a deep copy of the original table which can be used for continuous data filtration via iteration
        newreadtable=readtable.copy()

        # Creating a variable which would ask the user after every iteration whether they want to continue with data filtration
        y='y'

        while y in ['y','Y','yes','YES']:
          time.sleep(1.5)
          print('*************************************************************************************************************************************************',end='\n\n')

          #Asking user in every iteration regarding the column which would be used as a filter
          col=input("Enter the name of the column which has to be used as a filter: ")
          print('\n')

          if col in newreadtable.colnames:
            # If the filtering column has a string data type
            if isinstance(newreadtable[col][0],(str,np.str_)):
              print(f"The column {col} was found to have STRING data type.",end='\n\n')
              st=input("Enter the EXACT string to filter rows based on the selected column: ")

              # Updating the newreadtable which can be used for further data filtration
              newreadtable=newreadtable[newreadtable[col]==st]

              # Printing the filtered table
              display(f"The filtered table containing the rows having {col} values equal to {st} is:",newreadtable)

            # If the filtering column has a numeric data type
            elif isinstance(newreadtable[col][0],(float,np.floating)):
              print(f"The column {col} was found to have NUMERIC data type.",end='\n\n')

              # Filter Condition Menu
              print(":::::::::::::::::::::::::  FILTER CONDITION MENU  :::::::::::::::::::::::::",end='\n\n')
              print("Please select the filter condition:",end='\n\n')
              print("1. Strictly greater than.")
              print("2. Strictly lesser than.")
              print("3. Equal to.")
              print("4. Range (between two values).",end='\n\n')
              time.sleep(1.5)

              chfc=input("Enter a choice for filtering condition: ").strip()
              print('\n')
              print('*************************************************************************************************************************************************',end='\n\n')

              if chfc=='1':
                val=only_num("Enter the value to be used for comparison: ",'float')
                newreadtable=newreadtable[newreadtable[col]>val]
                dispstr=f"The filtered table containing the rows having {col} values strictly greater than {val} is:"

              elif chfc=='2':
                val=only_num("Enter the value to be used for comparison: ",'float')
                newreadtable=newreadtable[newreadtable[col]<val]
                dispstr=f"The filtered table containing the rows having {col} values strictly lesser than {val} is:"

              elif chfc=='3':
                val=only_num("Enter the value to be used for comparison: ",'float')
                newreadtable=newreadtable[newreadtable[col]==val]
                dispstr=f"The filtered table containing the rows having {col} values equal to {val} is:"

              elif chfc=='4':
                minval=only_num("Enter the minimum value for the comparison range: ",'float')
                maxval=only_num("Enter the maximum value for the comparison range: ",'float')
                newreadtable=newreadtable[minval<(newreadtable[col])<maxval]
                dispstr=f"The filtered table consisting of the rows having {col} values in the range ({minval},{maxval}) is:"

              else:
                print("INVALID choice for filtering condition !!!")
                print("The FILTRATION LOOP will commence once again!")
                continue

              display(dispstr,newreadtable)

            # If the data type of the filtering column is neither string nor numeric
            else:
              print("Comparison is ONLY available for columns having EITHER STRING OR NUMERIC data type !!!")
              print(f"'{type(newreadtable[col][0])}' data type is NOT applicable !!!",end='\n\n')
              break

          else:
            print(f"The column {col} provided does not exist in the file {fname} !!!",end='\n\n')
            break

          # Asking user whether they want to continue with the filtration loop
          y=input("Enter (y / Y / yes / YES) if you want to CONTINUE with the FILTRATION LOOP: ")
          print('\n')

        # If user terminates the filtration loop
        else:
          print("The FILTRATION LOOP has been SUCCEESFULLY TERMINATED !!!",end='\n\n')
          display("The final filtered table is:",newreadtable)
          save(newreadtable)

###################################################################################################################################################################################

      # If the user goes with the choice of deriving and appending the data
      elif chco=='4':
        print("NOTE: DERIVED QUANTITIES", end='\n\n')
        print('*************************************************************************************************************************************************', end='\n\n')
        time.sleep(1)

        print("> For derived quantities like absolute magnitude or luminosity,")
        print("  this program verifies that required columns exist and contain numeric values.", end='\n\n')
        time.sleep(1.5)

        print("> HOWEVER, it DOES NOT verify whether these values carry correct physical meaning")
        print("  (e.g., whether a column labeled as distance is actually in parsecs, or magnitude is apparent).")
        print("> YOU are responsible for ensuring the input columns are physically meaningful.", end='\n\n')
        time.sleep(1.5)

        print("> All derived calculations ASSUME that original units are appropriate for computation.")
        print("> This program WILL NOT perform unit conversions.")
        print("> Please convert your data upstream (before loading) or downstream (after saving) if needed.", end='\n\n')
        print('*************************************************************************************************************************************************', end='\n\n')
        time.sleep(1.5)

        # Derived Quantity Menu
        print(":::::::::::::::::::::::::  DERIVED QUANTITY MENU  :::::::::::::::::::::::::",end='\n\n')
        print("1. Absolute Magnitude  (M)          -  Requires apparent magnitude and parallax.")
        print("2. Luminosity          (L / L☉)    -   Requires absolute magnitude.")
        print("3. Distance            (parsecs)    -  Requires parallax (milliarcseconds).")
        print("4. Color Index         (e.g., B-V)  -  Requires magnitudes in both bands.",end='\n\n')
        time.sleep(1.5)

        chdq=input("Enter a choice for derived quantity to be calculated: ").strip()
        print('\n')
        print('*************************************************************************************************************************************************',end='\n\n')

        newt=readtable.copy()

        # If user wants to derive and append absolute magnitude values
        if chdq=='1':
          # Asking user for the columns consisting of apparent magnitude and parallax values to calculate the absolute magnitude values
          apm=input("Enter the name of the column consisting of values for apparent magnitude: ")
          plx=input("Enter the name of the column consisting of the values for parallax: ")

          if apm in newt.colnames and plx in newt.colnames and isinstance(newt[apm][0],(float,np.floating)) and isinstance(newt[plx][0],(float,np.floating)):

            # Asking user for the column name under which the derived values will be stored in
            colname=input("Provide a name for the new column consisting of absolute magnitude values: ")

            abm=newt[apm]+(5*(np.log10(newt[plx])))-10                          # Calculating the absolute magnitude values for each row
            newt[colname]=abm                                                   # Appending the new values to the table

            dispstr="The revised table consisting of absolute magnitude values is:"

          else:
            if apm not in newt.colnames:
              print(f"The column {apm} provided does not exist in the file {fname} !!!",end='\n\n')
            elif plx not in newt.colnames:
              print(f"The column {plx} provided does not exist in the file {fname} !!!",end='\n\n')
            elif not isinstance(newt[apm][0],(float,np.floating)):
              print(f"The column {apm} provided does not have a numeric data type !!!",end='\n\n')
            else:
              print(f"The column {plx} provided does not have a numeric data type !!!",end='\n\n')

        # If user wants to derive and append luminosity values
        elif chdq=='2':
          abm=input("Enter the name of the column consisting of values for absolute magnitude: ")

          if abm in newt.colnames and isinstance(newt[abm][0],(float,np.floating)):
            colname=input("Provide a name for the new column consisting of luminosity values: ")
            lum=10**((0.4)*(4.83-newt[abm]))
            newt[colname]=lum
            dispstr="The revised table consisting of luminosity values is:"

          else:
            if abm not in newt.colnames:
              print(f"The column {abm} provided does not exist in the file {fname} !!!",end='\n\n')
            else:
              print(f"The column {abm} provided does not have a numeric data type !!!",end='\n\n')

        # If user wants to derive and append distance values
        elif chdq=='3':
          plx=input("Enter the name of the column consisting of the values for parallax: ")

          if plx in newt.colnames and isinstance(newt[plx][0],(float,np.floating)):
            colname=input("Provide a name for the new column consisting of distance values: ")
            dst=(1000)/(newt[plx])
            newt[colname]=dst
            dispstr="The revised table consisting of distance values is:"

          else:
            if plx not in newt.colnames:
              print(f"The column {plx} provided does not exist in the file {fname} !!!",end='\n\n')
            else:
              print(f"The column {plx} provided does not have a numeric data type !!!",end='\n\n')

        # If user wants to derive and append color index values
        elif chdq=='4':
          b1=input("Enter the name of the column consisting of the values for first band: ")
          b2=input("Enter the name of the column consisting of the values for second band: ")

          if b1 in newt.colnames and b2 in newt.colnames and isinstance(newt[b1][0],(float,np.floating)) and isinstance(newt[b2][0],(float,np.floating)):
            colname=input("Provide a name for the new column consisting of color index values: ")
            ci=newt[b1]-newt[b2]
            newt[colname]=ci
            dispstr="The revised table consisting of color index values is:"

          else:
            if b1 not in newt.colnames:
              print(f"The column {b1} provided does not exist in the file {fname} !!!",end='\n\n')
            elif b2 not in newt.colnames:
              print(f"The column {b2} provided does not exist in the file {fname} !!!",end='\n\n')
            elif not isinstance(newt[b1][0],(float,np.floating)):
              print(f"The column {b1} provided does not have a numeric data type !!!",end='\n\n')
            else:
              print(f"The column {b2} provided does not have a numeric data type !!!",end='\n\n')

        # If the user goes with an invalid choice
        else:
          print("INVALID choice for derived quantity append !!!",end='\n\n')
          continue

        display(dispstr,newt)
        save(newt)

####################################################################################################################################################################################

      # If the user goes with the choice of appending columns from another table or merging any two tables
      elif chco=='5':
        print("NOTE: TERMINOLOGIES",end='\n\n')
        print('*************************************************************************************************************************************************',end='\n\n')
        print("> The MAIN file is where merged/appended results will be saved.")
        print("> However you can change this later when choosing how to save your data.",end='\n\n')
        print('*************************************************************************************************************************************************',end='\n\n')
        time.sleep(1.5)

        # Asking user to enter the name of the main file and secondary file
        f1=input("Enter the name of the MAIN/PARENT file (in .csv / .fits): ")
        f2=input("Enter the name of the secondary file (in .csv / .fits): ")

        # Ensuring that both the files have a .csv / .fits extension
        if not ((f1.lower().endswith('.csv')) or (f1.lower().endswith('.fits'))):
          print(f"ERROR: This program supports only .csv / .fits files !!! The file {f1} does not have a .csv / .fits extension !")
          continue
        elif not ((f2.lower().endswith('.csv')) or (f2.lower().endswith('.fits'))):
          print(f"ERROR: This program currently supports only .csv / .fits files !!! The file {f2} does not have a .csv / .fits extension !")
          continue
        else:
          if (f1.lower().endswith('.csv'))==True:
            f1_fmt='csv'
          else:
            f1_fmt='fits'

          if (f2.lower().endswith('.csv'))==True:
            f2_fmt='csv'
          else:
            f2_fmt='fits'

          try:
            t1=t.read(f1,format=f1_fmt)
            t2=t.read(f2,format=f2_fmt)

            # Ensuring that the tables in both the files are non-empty
            if len(t1)==0:
              print(f"ERROR: The table in file {f1} is EMPTY !!!")
              continue
            elif len(t2)==0:
              print(f"ERROR: The table in file {f2} is EMPTY !!!")
              continue

            time.sleep(1.5)
            # Printing the retrieved tables from both the files
            print(f"The table retrieved from {f1} is:",end='\n\n')
            t1.pprint_all()
            print('\n')
            print('*************************************************************************************************************************************************',end='\n\n')
            time.sleep(1.5)
            print(f"The table retrieved from {f2} is:",end='\n\n')
            t2.pprint_all()
            print('\n')
            print('*************************************************************************************************************************************************',end='\n\n')
            time.sleep(1.5)

            # Merge Menu
            print(":::::::::::::::::::::::::  MERGE MENU  :::::::::::::::::::::::::",end='\n\n')
            print("1. Append Columns From Another Table.")
            print("2. Merge Catalog Tables:-")
            print("   2a. Vertical Stack    (vstack)  -  Best for merging filtered subsets (logical OR).")
            print("   2b. Horizontal Stack  (hstack)  -  Use only when both tables have the SAME number of rows.")
            print("   2c. Join                        -  Use when tables share a common column/key (e.g., source_id, name, etc).",end='\n\n')
            time.sleep(1.5)

            chmg=input("Enter your choice (1, 2a, 2b, or 2c) to proceed: ").strip()
            print('\n')
            print('*************************************************************************************************************************************************',end='\n\n')

            # If the user wants to append columns to another table in a different file
            if chmg=='1':
              y='y'
              while y in ['y','Y','yes','YES']:
                # Asking the user the name of the file to be appended into the other table
                colname=input(f"Enter the name of the column from table in file {f2} that has to appended to the table in file {f1} : ")

                if colname in t2.colnames:
                  t1[colname]=t2[colname]
                  display(f"The updated table of {f1} with {colname} appended is:",t1)
                  y=input("Enter (y / Y / yes / YES), if you still want to continue with column append operation: ")  # Asking user whether they want to continue further

                else:
                   print(f"The column {colname} provided does not exist in {f2} !!!",end='\n\n')
                   y=input("Enter (y / Y / yes / YES), if you still want to continue with column append operation: ")

              # If the user does not want to continue with column append operation
              else:
                display(f"The final updated table with all the appended columns from table in file {f2} to the file {f1} is:",t1)
                save(t1)

            # If the user wants to perform a vertical stack for both the tables
            elif chmg=='2a':
              # Ensuring that the no.of columns and the column names are same in both the tables
              if t1.colnames==t2.colnames:
                tnew=vstack([t1,t2])
                display("The new vertically stacked table is:",tnew)
                save(tnew)

              # If columns mismatch
              else:
                print("ERROR: Tables have mismatched columns - cannot perform vertical merge (vstack) !!!")
                print("Ensure both tables have the same columns in the same order !!!")

            # If the user wants to perform a horizontal stack for both the tables
            elif chmg=='2b':
              # Ensuring the no.of rows are same in both the tables
              if len(t1)==len(t2):
                thnew=hstack([t1,t2])
                display("The new horizontally stacked table is:",thnew)
                save(thnew)

              # If the number of rows are different
              else:
                print("ERROR: Cannot perform horizontal merge (hstack) - tables must have the same number of rows.")

            # If the user wants to perform a join on both the tables
            elif chmg=='2c':
              # Asking user the column which would act as the key for the joined table
              comcol=input("Enter the name of the column to use as the JOIN KEY (must exist in both tables): ")

              # Ensuring that the column to act as a key is present in both the tables
              if comcol in t1.colnames and comcol in t2.colnames:
                time.sleep(1)
                # Join Type Menu
                print(":::::::::::::::::::::::::  JOIN TYPE MENU  :::::::::::::::::::::::::",end='\n\n')
                print("Choose JOIN TYPE:",end='\n\n')
                print("1. Inner - keeps only rows with matching keys in both tables.")
                print("2. Outer - keeps all rows from both tables, fills missing values with masked data.")
                print("3. Left  - keeps all rows from the MAIN/PARENT table, adds matching data from the right.")
                print("4. Right - keeps all rows from the SECONDARY table, adds matching data from the left.",end='\n\n')
                time.sleep(1.5)

                chjt=input("Enter a choice for join type: ").strip()
                print('\n')
                print('*************************************************************************************************************************************************',end='\n\n')

                # If the user goes with join type as inner
                if chjt=='1':
                  mgdti=join(t1,t2,keys=comcol,join_type='inner')
                  display("The new merged table with join type inner is:",mgdti)
                  save(mgdti)

                # If the user goes with join type as outer
                elif chjt=='2':
                  mgdto=join(t1,t2,keys=comcol,join_type='outer')
                  display("The new merged table with join type outer is:",mgdto)
                  save(mgdto)

                # If the user goes with join type as left
                elif chjt=='3':
                  mgdtl=join(t1,t2,keys=comcol,join_type='left')
                  display("The new merged table with join type left is:",mgdtl)
                  save(mgdtl)

                # If the user goes with join type as right
                elif chjt=='4':
                  mgdtr=join(t1,t2,keys=comcol,join_type='right')
                  display("The new merged table with join type right is:",mgdtr)
                  save(mgdtr)

                # If the user goes with an inavlid choice for join type
                else:
                  print("INVALID choice for join type !!!")

              # If the column name for the key is not present in any one or both the files
              else:
                if comcol not in t1.colnames and comcol in t2.colnames:
                  print(f"The column {comcol} provided was not found in {f1} file !!!")
                elif comcol not in t2.colnames and comcol in t1.colnames:
                  print(f"The column {comcol} provided was not found in {f2} file !!!")
                else:
                  print(f"The column {comcol} provided was not found in both {f1} and {f2} files !!! ")

            # If the user goes with an invalid choice from the merge menu
            else:
              print("INVALID choice for column append/table merging !!!")

          # If any of the files does not exist
          except FileNotFoundError as e:
            print(f"ERROR: File {e.filename} not found !!! Please check the name and try again !!!")

######################################################################################################################################################################################

      # If the user goes with the choice for column/row deletion
      elif chco=='6':
        # Delete Menu
        print(":::::::::::::::::::::::::  DELETE MENU  :::::::::::::::::::::::::",end='\n\n')
        print("What would you like to delete?",end='\n\n')
        print("1. A column.")
        print("2. Row(s).",end='\n\n')
        time.sleep(1.5)

        chdd=input("Enter a choice for your deletion preference: ").strip()
        print('\n')
        print('*************************************************************************************************************************************************',end='\n\n')

        delt=readtable.copy()

        # If the user wants to delete a column
        if chdd=='1':
          # Asking user for the name of the column to be deleted
          delcol=input("Enter the name of column to be deleted: ")

          if delcol in delt.colnames:
            del delt[delcol]
            display(f"The updated table without the column {delcol} is:",delt)
            save(delt)
          else:
            print(f"The column {delcol} provided is not present in {fname} !!!")

        # If the user wants to delete row(s)
        elif chdd=='2':
          print(">> The current table is shown below. REVIEW IT BEFORE proceeding with row deletion.")
          print(">> Identify the row numbers you wish to delete - enter a list like [0, 3, 7] when prompted.", end='\n\n')
          print('*************************************************************************************************************************************************',end='\n\n')
          time.sleep(1.5)
          delt.pprint_all()
          print('\n')
          print('*************************************************************************************************************************************************',end='\n\n')

          print("NOTE: ROW DELETION",end='\n\n')
          print('*************************************************************************************************************************************************',end='\n\n')
          print("> Please provide a LIST of ROW INDICES to delete - for example: [1, 4, 7].")
          print("> These should match the row numbers in the ORIGINAL TABLE - no need to adjust for changes caused by deletions.", end='\n\n')
          print('*************************************************************************************************************************************************',end='\n\n')
          time.sleep(1.5)

          # Loop to get and validate the user's input for rows to delete
          while True:
            time.sleep(0.5)
            # Evaluating the user input to handle invalid Python syntax
            try:
              int_rownum=eval(input("Enter a list of row numbers to delete (e.g., [0, 2, 5]): "))
            except SyntaxError:
              print("ERROR: INVALID input syntax !!! Please enter a proper list like [0, 2, 5] !")
              print('Please try again !',end='\n\n')
              continue

            # Ensuring the input is a list
            if type(int_rownum)!=list:
              print("ERROR: The input must be a list of integers like [0, 2, 5] !!!")
              print("Please try again !",end='\n\n')
              continue
            else:
              break

          # Converting to a set to avoid duplicates, then back to list
          set_rownum=set(int_rownum)
          rownum=list(set_rownum)

          # Validating each row index in the list
          for i in range(len(rownum)):
            while True:
              # Each element must be an integer and must fall within table bounds
              if (type(rownum[i])!=int) or not (0<=rownum[i]<len(delt)):
                print(f"ERROR: INVALID row index '{rownum[i]}' !!! MUST be an integer between 0 and {len(delt) - 1} !")
                print("Please try again !",end='\n\n')
                time.sleep(0.5)
                # Re-prompts the user for this specific element to ensure it is a valid integer
                rownum[i]=only_num("Enter a valid integer row number: ",'int')
                continue
              else:
                break

          # Sorting row indices in reverse to prevent shifting issues during deletion
          rownum_desc=sorted(rownum,reverse=True)

          # Deleting each specified row from the table
          for i in range(len(rownum_desc)):
            delt=delt[np.arange(len(delt))!=(rownum_desc[i])]

          display('The updated table after deletion of selected rows is:',delt)
          save(delt)

        # If the user goes with an invalid choice from deletion menu
        else:
          print("INVALID choice for deletion process !!!")

#####################################################################################################################################################################################

     # If the user goes with the choice to return back to the main menu
      elif chco=='7':
        print("The program would RETURN BACK to MAIN MENU.")
        choice=input("If you want to continue with Catalog Operations, type (y / Y / yes / YES): ") # Reaffirming whether the user wants to exit catalog operations

        if choice in ['y','Y','yes','YES']: # If the user wants to continue with catalog operations
          continue
        else: # If the user wants to exit catalog operations
          print("You are being directed back to MAIN MENU !!!",end='\n\n')
          print('*************************************************************************************************************************************************',end='\n\n')
          time.sleep(1.5)
          break

#####################################################################################################################################################################################

      # If the user goes with an invalid choice from catalog operations menu
      else:
        print("INVALID choice from Catalog Operations Menu !!! Please enter a VALID choice !")

#################################################################################################################################################################################
#################################################################################################################################################################################

  # If the user goes with the choice of observational planner from main menu
  elif ch=='2':
    print(":::::::::::::::::::::::::  WELCOME TO OBSERVATIONAL PLANNER  :::::::::::::::::::::::::",end='\n\n')
    time.sleep(1)

    print("Some important notes and instructions before using the observational planner:-",end='\n\n')
    time.sleep(1)

    print("NOTE--1: This module will ask you to provide your LOCATION details (latitude, longitude, elevation above sea level),")
    print("      as well as the DATE or TIME for which you want to perform sky visibility checks or coordinate conversions.", end='\n\n')
    print('*************************************************************************************************************************************************',end='\n\n')
    time.sleep(1.5)

#################################################################################################################################################################################

    print("NOTE--2: Latitude & Longitude",end='\n\n')
    print('*************************************************************************************************************************************************', end='\n\n')
    print("> Latitude: +ve = Northern Hemisphere, -ve = Southern Hemisphere, Range: -90° to +90°")
    print("> Longitude: +ve = East of Prime Meridian, -ve = West of Prime Meridian, Range: -180° to +180°",end='\n\n')
    print('*************************************************************************************************************************************************',end='\n\n')
    time.sleep(1.5)

#################################################################################################################################################################################

    print("NOTE--3: COORDINATE INPUT GUIDELINES",end='\n\n')
    print('*************************************************************************************************************************************************',end='\n\n')
    time.sleep(1)

    print("GENERAL FORMAT:-")
    print("For EACH COORDINATE SYSTEM, values must be in SEPARATE COLUMNS.")
    print("EXAMPLE: For ICRS, one column for RA and one for Dec (NOT a tuple or combined string).",end='\n\n')
    time.sleep(1.5)

    print("i-ICRS (INTERNATIONAL CELESTIAL REFERENCE SYSTEM):")
    print("> RIGHT ASCENSION (RA): 0° ≤ RA < 360°")
    print("> DECLINATION (DEC): -90° ≤ DEC ≤ +90°",end='\n\n')
    time.sleep(1.5)

    print("ii-GALACTIC COORDINATES:")
    print("> GALACTIC LONGITUDE (L): 0° ≤ L < 360°")
    print("> GALACTIC LATITUDE (B): -90° ≤ B ≤ +90°",end='\n\n')
    time.sleep(1.5)

    print("iii-ALTAZ (ALTITUDE-AZIMUTH):")
    print("> AZIMUTH (AZ): 0° ≤ AZ < 360° (MEASURED FROM NORTH, INCREASING EASTWARD)")
    print("> ALTITUDE (ALT): -90° ≤ ALT ≤ +90° (0° = HORIZON, +90° = ZENITH)",end='\n\n')
    time.sleep(1.5)

    print("ALL ANGLES MUST BE IN DEGREES AND IN SEPARATE COLUMNS FOR CONVERSION TO WORK CORRECTLY.",end='\n\n')
    print('*************************************************************************************************************************************************',end='\n\n')
    time.sleep(1.5)
    # End of instructions

#################################################################################################################################################################################

    # Asking user for the their location's latitude and verifying whether it lies in the expected range
    while True:
      try:
        lat=only_num("Enter the latitude of your geographic location (in degrees): ",'float')
        if not -90<=lat<=90:
          raise ValueError
        else:
          break
      except ValueError: # If it does not lie in the expected range, the user is directed back to the main menu
        print(f"Please ENTER CORRECT values !!! The latitude {lat}° provided is OUT of -90° to +90° range !!!",end='\n\n')
        print("You are now being directed back to the Main Menu !!!",end='\n\n')
        print('*************************************************************************************************************************************************',end='\n\n')
        time.sleep(1.5)
        continue

    # Asking user for their location's longitude and verifying whether it lies in the expected range
    while True:
      try:
        lon=only_num("Enter the longitude of your geographic location (in degrees): ",'float')
        if not -180<lon<180:
          raise ValueError
        else:
          break
      except ValueError:
        print(f"Please ENTER CORRECT values !!! The longitude {lon}° provided is OUT of -180° to +180° range !!!",end='\n\n')
        print("You are now being directed back to the Main Menu !!!",end='\n\n')
        print('*************************************************************************************************************************************************',end='\n\n')
        time.sleep(1.5)
        continue

    # Asking user for their location's elevation above sea level and verifying whether it lies in the expected range
    while True:
      try:
        ele=only_num("Enter elevation above sea level (in meters), if unknown enter 0: ",'float')
        if ele<0:
          raise ValueError
        else:
          break
      except ValueError:
        print(f"Please ENTER CORRECT values !!! The elevation {ele} meters provided is less than zero !!! Elevation is ALWAYS measured ABOVE SEA LEVEL !!!",end='\n\n')
        print("You are now being directed back to the Main Menu !!!",end='\n\n')
        print('*************************************************************************************************************************************************',end='\n\n')
        time.sleep(1.5)
        continue

#####################################################################################################################################################################################

    # Creating a function which would verify that all the values in a column for a given table are in the range of [0,360)
    def inrange360(table,col):
      global err360
      try:
        index=0                           # Defining index and val variables
        val=0
        for i in range (len(table)):
          if not 0<=table[col][i]<360:
            index=i                       # The first encounter of out of range value will be recorded by the predefined variables index and val
            val=table[col][i]             # A value error will be raised
            raise ValueError
      except ValueError:
        print(f"The value at row no. {index} for the column {col} provided, was found to be {val} which is not in the range [0°,360°) !!!")
        err360=1                          # The variable err360 is made to point to 1 in case of an error

#####################################################################################################################################################################################

    # Creating a function which would verify that all the values in a column for a given table are in the range of [-90,90]
    def inrange90(table,col):
      global err90
      try:
        index=0
        val=0
        for i in range (len(table)):
          if not -90<=table[col][i]<=90:
            index=i
            val=table[col][i]
            raise ValueError
      except ValueError:
        print(f"The value at row no. {index} for the column {col} provided was found to be {val} which is not in the range [-90°, +90°] !!!")
        err90=1                           # The variable err90 is made to point to 1 in case of an error

#####################################################################################################################################################################################

    loop=0
    while True:
      # Assigning both err360 and err90, 0 after each loop to ensure smooth error detection
      err360=0
      err90=0

      if loop!=0:
        print("The program will now return back to the Observation Planner Menu !",end='\n\n')

      time.sleep(1.5)
      loop+=1
      print('*************************************************************************************************************************************************',end='\n\n')
      # Observational Planner Menu
      print(":::::::::::::::::::::::::  OBSERVATION PLANNER MENU  :::::::::::::::::::::::::",end='\n\n')
      print("1. Coordinate Conversion:-",end='\n\n')
      print("   1a. ICRS to Galactic.")
      print("   1b. Galactic to ICRS.")
      print("   1c. ICRS to AltAz.")
      print("   1d. AltAz to ICRS.")
      print("   1e. Galactic to AltAz.")
      print("   1f. AltAz to Galactic.",end='\n\n')
      print("2. Visibility (Check and) Window (Full Night Range).",end='\n\n')
      print("3. Return to Main Menu.",end='\n\n')
      time.sleep(1.5)

      chop=input("Enter a choice from the observation planner menu (e.g., 1a, 2 and etc): ").strip()
      print('\n')
      print('*************************************************************************************************************************************************',end='\n\n')

      # Creating a deep copy of the originally extracted file where all the changes would be preformed on
      plantable=readtable.copy()

##################################################################################################################################################################################

      # If the user goes with the choice of converting ICRS coordinates to Galactic Coordinates
      if chop=='1a':
        # Asking user for the column names under which the right ascension and declination values are present
        ra=input("Enter the name of the column consisting of right ascension values (0° ≤ RA < 360°): ")
        dec=input("Enter the name of the column consisting of declination values (-90° ≤ DEC ≤ +90°):")
        print('\n')

        if ra in plantable.colnames and dec in plantable.colnames and isinstance(plantable[ra][0],(float,np.floating)) and isinstance(plantable[dec][0],(float,np.floating)):

          # Checking whether each column has all the values in the expected range using inrange360() and inrange90()
          inrange360(plantable,ra)
          inrange90(plantable,dec)


          # If an out of range value is detected for any of the column the err360/err90 would point towards 1
          # If out of both any one or both the values point towards 1
          if err360==1 or err90==1:
            continue                                                            # The program would return back to the observational planner menu


          # Asking user for the name of the columns consisting if the galactic inclination and declination values
          lcol=input("Enter a name for the column that would contain the galactic longitude values: ")
          bcol=input("Enter a name for the column that would contain the galacic latitude values:")


          # Creating AstroPy ICRS coordinates from the data available
          cood=sc(ra=plantable[ra]*u.deg,dec=plantable[dec]*u.deg,frame='icrs')
          newcood=cood.transform_to('galactic')                                 # Converting them to Galactic coordinates


          # Appending the transformed values to the copy table
          plantable[lcol]=newcood.l.value
          plantable[bcol]=newcood.b.value

          display("The updated table containing the galactic latitudes and longitudes is:",plantable)
          save(plantable)

        else:
          if ra not in plantable.colnames:
            print(f"The column {ra} provided does not exist in the file {fname} !!!",end='\n\n')
          elif dec not in plantable.colnames:
            print(f"The column {dec} provided does not exist in the file {fname} !!!",end='\n\n')
          elif not isinstance(plantable[ra][0],(float,np.floating)):
            print(f"The column {ra} provided does not have a numeric data type !!!",end='\n\n')
          else:
            print(f"The column {dec} provided does not have a numeric data type !!!",end='\n\n')

##################################################################################################################################################################################

      # If the user goes with the choice of converting Galactic coordinates to ICRS coordinates
      elif chop=='1b':
        l=input("Enter the name of the column consisting of galactic longitude values (0° ≤ l < 360°): ")
        b=input("Enter the name of the column consisting of galactic latitude values (-90° ≤ b ≤ +90°):")
        print('\n')

        if l in plantable.colnames and b in plantable.colnames and isinstance(plantable[l][0],(float,np.floating)) and isinstance(plantable[b][0],(float,np.floating)):

          inrange360(plantable,l)
          inrange90(plantable,b)

          if err360==1 or err90==1:
            continue

          racol=input("Enter a name for the column that would contain the right ascension values: ")
          deccol=input("Enter a name for the column that would contain the declination values:")

          cood=sc(l=plantable[l]*u.deg,b=plantable[b]*u.deg,frame='galactic')
          newcood=cood.transform_to('icrs')

          plantable[racol]=newcood.ra.value
          plantable[deccol]=newcood.dec.value

          display("The updated table containing the right ascension and declination values is:",plantable)
          save(plantable)

        else:
          if l not in plantable.colnames:
            print(f"The column {l} provided does not exist in the file {fname} !!!",end='\n\n')
          elif b not in plantable.colnames:
            print(f"The column {b} provided does not exist in the file {fname} !!!",end='\n\n')
          elif not isinstance(plantable[l][0],(float,np.floating)):
            print(f"The column {l} provided does not have a numeric data type !!!",end='\n\n')
          else:
            print(f"The column {b} provided does not have a numeric data type !!!",end='\n\n')

##################################################################################################################################################################################

      # If the user goes with the choice of converting the ICRS coordinates to AltAz coordinates
      elif chop=='1c':
        ra=input("Enter the name of the column consisting of right ascension values (0° ≤ RA < 360°): ")
        dec=input("Enter the name of the column consisting of declination values (-90° ≤ DEC ≤ +90°):")
        print('\n')

        if ra in plantable.colnames and dec in plantable.colnames and isinstance(plantable[ra][0],(float,np.floating)) and isinstance(plantable[dec][0],(float,np.floating)):

          inrange360(plantable,ra)
          inrange90(plantable,dec)

          if err360==1 or err90==1:
            continue

          # Asking user to enter date and time at which the AltAz coordinates have to be calculated
          while True:
            try:
              intime=input("Enter custom UTC date & time (format: YYYY-MM-DD HH:MM:SS): ")
              dt=datetime.strptime(intime, "%Y-%m-%d %H:%M:%S")
              obstime=Time(dt,scale='utc')
              break
            except ValueError: # If wrong format of date and time is provided
              print("The date and time provided is NOT in the correct format !!! Please try again !",end='\n\n')
              print('*************************************************************************************************************************************************',end='\n\n')
              time.sleep(1.5)
              continue

          altcol=input("Enter a name for the column that would contain the altitude values: ")
          azcol=input("Enter a name for the column that would contain the azimuth values: ")


          cood=sc(ra=plantable[ra]*u.deg,dec=plantable[dec]*u.deg,frame='icrs')
          location=el(lat=lat*u.deg,lon=lon*u.deg,height=ele*u.m)               # Creating the earth location of the user


          aaf=aa(obstime=obstime,location=location)                             # Creating the AltAz frame of the user
          newcood=cood.transform_to(aaf)

          plantable[altcol]=newcood.alt.value
          plantable[azcol]=newcood.az.value

          display("The updated table containing the altitude and azimuth values is:",plantable)
          save(plantable)

        else:
          if ra not in plantable.colnames:
            print(f"The column {ra} provided does not exist in the file {fname} !!!",end='\n\n')
          elif dec not in plantable.colnames:
            print(f"The column {dec} provided does not exist in the file {fname} !!!",end='\n\n')
          elif not isinstance(plantable[ra][0],(float,np.floating)):
            print(f"The column {ra} provided does not have a numeric data type !!!",end='\n\n')
          else:
            print(f"The column {dec} provided does not have a numeric data type !!!",end='\n\n')

##################################################################################################################################################################################

      # If the user goes with the choice of converting the AltAz coordinates to ICRS coordinates
      elif chop=='1d':
        altcol=input("Enter the name of the column containinng the altitude values (-90° ≤ ALT ≤ +90°): ")
        azcol=input("Enter the name of the column containing the azimuth values (0° ≤ AZ < 360°): ")
        print('\n')

        if altcol in plantable.colnames and azcol in plantable.colnames and isinstance(plantable[altcol][0],(float,np.floating)) and isinstance(plantable[azcol][0],(float,np.floating)):

          inrange360(plantable,azcol)
          inrange90(plantable,altcol)

          if err360==1 or err90==1:
            continue

          while True:
            try:
              intime=input("Enter custom UTC date & time (format: YYYY-MM-DD HH:MM:SS): ")
              dt=datetime.strptime(intime, "%Y-%m-%d %H:%M:%S")
              obstime=Time(dt,scale='utc')
              break
            except ValueError:
              print("The date and time provided is NOT in the correct format !!! Please try again !",end='\n\n')
              print('*************************************************************************************************************************************************',end='\n\n')
              time.sleep(1.5)
              continue

          racol=input("Enter a name for the column that would contain the right ascension values: ")
          deccol=input("Enter a name for the column that would contain the declination values:")

          location=el(lat=lat*u.deg,lon=lon*u.deg,height=ele*u.m)
          cood=sc(alt=plantable[altcol]*u.deg,az=plantable[azcol]*u.deg,frame='altaz',obstime=obstime,location=location)

          newcood=cood.transform_to('icrs')

          plantable[racol]=newcood.ra.value
          plantable[deccol]=newcood.dec.value

          display("The updated table containing the right ascension and declination values is:",plantable)
          save(plantable)

        else:
          if altcol not in plantable.colnames:
            print(f"The column {altcol} provided does not exist in the file {fname} !!!",end='\n\n')
          elif azcol not in plantable.colnames:
            print(f"The column {azcol} provided does not exist in the file {fname} !!!",end='\n\n')
          elif not isinstance(plantable[altcol][0],(float,np.floating)):
            print(f"The column {altcol} provided does not have a numeric data type !!!",end='\n\n')
          else:
            print(f"The column {azcol} provided does not have a numeric data type !!!",end='\n\n')

##################################################################################################################################################################################

      # If the user goes with the choice of converting Galactic coordinates to AltAz coordinates
      elif chop=='1e':
        l=input("Enter the name of the column consisting of galactic longitude values (0° ≤ l < 360°): ")
        b=input("Enter the name of the column consisting of galactic latitude values (-90° ≤ b ≤ +90°):")
        print('\n')

        if l in plantable.colnames and b in plantable.colnames and isinstance(plantable[l][0],(float,np.floating)) and isinstance(plantable[b][0],(float,np.floating)):

          inrange360(plantable,l)
          inrange90(plantable,b)

          if err360==1 or err90==1:
            continue

          while True:
            try:
              intime=input("Enter custom UTC date & time (format: YYYY-MM-DD HH:MM:SS): ")
              dt=datetime.strptime(intime, "%Y-%m-%d %H:%M:%S")
              obstime=Time(dt,scale='utc')
              break
            except ValueError:
              print("The date and time provided is NOT in the correct format !!! Please try again !",end='\n\n')
              print('*************************************************************************************************************************************************',end='\n\n')
              time.sleep(1.5)
              continue

          cood=sc(l=plantable[l]*u.deg,b=plantable[b]*u.deg,frame='galactic')
          location=el(lat=lat*u.deg,lon=lon*u.deg,height=ele*u.m)

          aaf=aa(obstime=obstime,location=location)
          newcood=cood.transform_to(aaf)

          plantable[altcol]=newcood.alt.value
          plantable[azcol]=newcood.az.value

          display("The updated table containing the altitude and azimuth values is:",plantable)
          save(plantable)

        else:
          if l not in plantable.colnames:
            print(f"The column {l} provided does not exist in the file {fname} !!!",end='\n\n')
          elif b not in plantable.colnames:
            print(f"The column {b} provided does not exist in the file {fname} !!!",end='\n\n')
          elif not isinstance(plantable[l][0],(float,np.floating)):
            print(f"The column {l} provided does not have a numeric data type !!!",end='\n\n')
          else:
            print(f"The column {b} provided does not have a numeric data type !!!",end='\n\n')

##################################################################################################################################################################################

     # If the user goes with the choice for converting AltAz coordinates to Galactic coordinates
      elif chop=='1f':
        altcol=input("Enter the name of the column containing the altitude values (-90° ≤ ALT ≤ +90°): ")
        azcol=input("Enter the name of the column containing the azimuth values (0° ≤ AZ < 360°): ")
        print('\n')

        if altcol in plantable.colnames and azcol in plantable.colnames and isinstance(plantable[altcol][0],(float,np.floating)) and isinstance(plantable[azcol][0],(float,np.floating)):

          inrange360(plantable,azcol)
          inrange90(plantable,altcol)

          if err360==1 or err90==1:
            continue

          while True:
            try:
              intime=input("Enter custom UTC date & time (format: YYYY-MM-DD HH:MM:SS): ")
              dt=datetime.strptime(intime, "%Y-%m-%d %H:%M:%S")
              obstime=Time(dt,scale='utc')
              break
            except ValueError:
              print("The date and time provided is NOT in the correct format !!! Please try again !",end='\n\n')
              print('*************************************************************************************************************************************************',end='\n\n')
              time.sleep(1.5)
              continue

          lcol=input("Enter a name for the column that would contain the galactic longitude values: ")
          bcol=input("Enter a name for the column that would contain the galactic latitude values:")

          location=el(lat=lat*u.deg,lon=lon*u.deg,height=ele*u.m)
          cood=sc(alt=plantable[altcol]*u.deg,az=plantable[azcol]*u.deg,frame='altaz',obstime=obstime,location=location)

          newcood=cood.transform_to('galactic')

          plantable[lcol]=newcood.l.value
          plantable[bcol]=newcood.b.value

          display("The updated table containing the galactic latitude and longitude values is:",plantable)
          save(plantable)

        else:
          if altcol not in plantable.colnames:
            print(f"The column {altcol} provided does not exist in the file {fname} !!!",end='\n\n')
          elif azcol not in plantable.colnames:
            print(f"The column {azcol} provided does not exist in the file {fname} !!!",end='\n\n')
          elif not isinstance(plantable[altcol][0],(float,np.floating)):
            print(f"The column {altcol} provided does not have a numeric data type !!!",end='\n\n')
          else:
            print(f"The column {azcol} provided does not have a numeric data type !!!",end='\n\n')

##################################################################################################################################################################################

      # If the user goes with the choice of visibility (check and) window
      elif chop=='2':
        print("NOTE: COORDINATE REQUIREMENT",end='\n\n')
        print('*************************************************************************************************************************************************', end='\n\n')
        print("> Your catalog MUST contain ICRS (Right Ascension and Declination) columns.")
        print("> If your data uses GALACTIC coordinates, please CONVERT them to ICRS using the Coordinate Conversion Tool BEFORE proceeding.", end='\n\n')
        print('*************************************************************************************************************************************************', end='\n\n')
        time.sleep(1.5)

        # Visibility Check & Window Menu
        print(":::::::::::::::::::::::::  VISIBILITY CHECK & WINDOW MENU  :::::::::::::::::::::::::",end='\n\n')
        print("1. Note on Visibility and the Procedure to Perform Visibility Check.")
        print("2. Check Visibility Window.",end='\n\n')
        time.sleep(1.5)

        chvo=input("Enter a choice from the visibility check & window menu: ").strip()
        print('\n')
        print('*************************************************************************************************************************************************',end='\n\n')

        # If the user goes with the first choice of note and procdeure
        if chvo=='1':
          # Providing a note to user on visibility and how to perform visibility check using SCOPE
          print("NOTE: VISIBILITY & PROCEDURE TO PERFORM VISIBILITY CHECK", end='\n\n')
          print('*************************************************************************************************************************************************', end='\n\n')
          print("> A celestial object is considered VISIBLE if its ALTITUDE is ABOVE the HORIZON by a certain angle.")
          print("> PROFESSIONAL observatories may use a 5° threshold, but 12°-15° is ADVISED for typical observations to reduce atmospheric distortions near the horizon.",end='\n\n')
          print("> Procedure to Perform Visibility Check Using SCOPE: i) CONVERT coordinates to ALTAZ using your location and time.")
          print("                                                    ii) Then use the NUMERIC FILTER in the CATALOG MENU to SELECT OBJECTS with ALTITUDE > your chosen threshold.", end='\n\n')
          print('*************************************************************************************************************************************************', end='\n\n')
          time.sleep(1.5)

        # If the user goes with the choice of checking visibility window
        elif chvo=='2':
          # Global list to store the altitude values of each star for every minute of the full night duration (for plotting Altitude vs Time visibility curves)
          global stars_alt
          stars_alt=[]

          print("NOTE: VISIBILITY WINDOW", end='\n\n')
          print('*************************************************************************************************************************************************', end='\n\n')
          print("> The visibility window defines the time period during which a celestial object is OBSERVABLE from your location.")
          print("> This depends on factors such as the OBJECT'S POSITION, LOCAL HORIZON, DATE, and TIME.")
          print("> Ensure your OBSERVATION TIMES fall within this window to avoid planning observations when the object is BELOW THE HORIZON or OBSCURED.", end='\n\n')
          print('*************************************************************************************************************************************************', end='\n\n')
          time.sleep(1.5)

          # Asking user to enter the column names consisting of right ascension and declination values
          ra=input("Enter the name of the column consisting of right ascension values (0° ≤ RA < 360°): ")
          dec=input("Enter the name of the column consisting of declination values (-90° ≤ DEC ≤ +90°):")
          print('\n')

          if ra in plantable.colnames and dec in plantable.colnames and isinstance(plantable[ra][0],(float,np.floating)) and isinstance(plantable[dec][0],(float,np.floating)):

            inrange360(plantable,ra)
            inrange90(plantable,dec)

            print("NOTE: STAR-WISE VISIBILITY WINDOW", end='\n\n')
            print('*************************************************************************************************************************************************', end='\n\n')
            print("> This feature computes the TIME WINDOW during which EACH STAR is ABOVE the HORIZON (ALTITUDE > 0°) for a given LOCATION and DATE.")
            print("> The OVERNIGHT PERIOD is determined using SUNSET and SUNRISE based on a USER-SELECTED TWILIGHT ALTITUDE (e.g., official, astronomical and etc).")
            print("> By DEFAULT, the twilight altitude is set to -18° (astronomical), but users may choose a DIFFERENT VALUE depending on observing needs.")
            print("> ONLY STARS visible at some point within this TWILIGHT-BASED NIGHT INTERVAL are considered VISIBLE.")
            print('*************************************************************************************************************************************************', end='\n\n')
            time.sleep(1.5)

            # Asking user to enter the date for which they want their visibility window
            while True:
              try:
                indate=input("Enter custom date when you want to start performing stellar observation (format: YYYY-MM-DD): ")
                indateeval=datetime.strptime(indate,"%Y-%m-%d")
                dt=indate+' 12:00'                                              # The program preassumes the starting time as 12 noon in UTC for the date entered
                obstime=Time(dt,scale='utc')
                break
              except ValueError:                                                # Incase the user enters an incorrect date format
                print("INVALID date format !!!")
                continue


            print("NOTE: TIME RESOLUTION POLICY",end='\n\n')
            print('*************************************************************************************************************************************************', end='\n\n')
            print("> All visibility calculations are performed at a fixed 1-minute interval.")
            print("> This resolution ensures sufficient temporal precision for detecting rising and setting events.")
            print("> Second-level granularity is unnecessary, as stellar altitude evolves smoothly across time.")
            print("> The fixed step also ensures consistent performance and avoids excessive computation.",end='\n\n')
            print('*************************************************************************************************************************************************', end='\n\n')
            time.sleep(1.5)


            duration=obstime+(np.linspace(0,1,1440)*u.day)                      # The duration is chosen to be from 12 noon UTC of entered date to 12:00 noon UTC of next date
                                                                                # 24 hours duration is assumed to calculate the surise and sunset time for the user's location

            # Creating earth location of the user
            location=el(lat=lat*u.deg,lon=lon*u.deg,height=ele*u.m)
            aaf=aa(obstime=duration,location=location)                          # AltAz frame of user

            sunalt=(get_sun(duration).transform_to(aaf)).alt.value              # Calculating and stroing Sun's altitude for all 1440 mins (24 hrs)

            # Creating variables which would store the sunrise and sunset values according to the user's location
            sunset=None
            sunrise=None

            # Twilight Menu
            print(":::::::::::::::::::::::::  TWILIGHT MENU  :::::::::::::::::::::::::",end='\n\n')
            print("Choose twilight type for sunrise/sunset determination:-",end='\n\n')
            print("1. Official     (Sun at 0°)  -  Visible Sun")
            print("2. Civil        (-6°)        -  General outdoor visibility")
            print("3. Nautical     (-12°)       -  Horizon barely visible")
            print("4. Astronomical (-18°)       -  TRUE darkness (recommended for astronomy)",end='\n\n')
            time.sleep(1.5)

            chtw=input("Enter your choice for twilight type: ").strip()
            print('\n')
            print('*************************************************************************************************************************************************',end='\n\n')

            if chtw=='1':
              twilight=0

            elif chtw=='2':
              twilight=-6

            elif chtw=='3':
              twilight=-12

            elif chtw=='4':
              twilight=-18

            # User goes with an invalid choice for twilight type, default -18° is assumed by the program
            else:
              print("INVALID choice for twilight type !!! Defaulting to Astronomical Twilight (-18°).")
              twilight=-18

            # Calculating sunrise and sunset times for user's location
            for i in range (len(sunalt)):
              if sunalt[i]<twilight and sunset is None:
                sunset=duration[i]
              elif sunalt[i]>twilight and sunrise is None and sunset is not None:
                sunrise=duration[i]

            print(f"The sunset time for your location coordinates ({lat},{lon},{ele}) for twilight {twilight} was found to be: ",sunset)
            print(f"The sunrise time for your location coordinates ({lat},{lon},{ele}) for twilight {twilight} was found to be: ",sunrise,end='\n\n')
            print('*************************************************************************************************************************************************',end='\n\n')
            time.sleep(1.5)

            print("NOTE: ALTITUDE THRESHOLD FOR STARS")
            print('*************************************************************************************************************************************************', end='\n\n')
            print("> Typical values range from 5° (professional-grade) to 15° (general use).")
            print("> You may enter ANY value within this range.")
            print("> If an INVALID value is entered, the program will DEFAULT to 15° (general-use standard).", end='\n\n')
            print('*************************************************************************************************************************************************', end='\n\n')
            time.sleep(1.5)


            # Asking user to enter the altitude threshold for the stars and making it global
            # Ensuring that the value belongs to the expected range of [5,15]
            global minalt
            try:
              minalt=only_num("Enter a valid altitude threshold (in degrees) in the range [5°,15°]: ",'float')
              if not 5<=minalt<=15:
                raise ValueError
            except ValueError:                                                  # In case of out of range, default value of 15° is assumed by the program
              print(f"The altitude threshold entered was not in the valid range of [5°,15°] !!! Defaulting to the general use altitude threshold of 15°.")
              minalt=15


            global stduration
            stdiff=round(((sunrise-sunset).value)*1440)                         # Calculating the night time range for the observer's location for their custom date
            stduration=sunset+(np.linspace(0,1,stdiff)*u.day)                   # Rounding the value to ensure only integer count for np.linspace()


            # AltAz frame of user for the night time range
            aaf1=aa(obstime=stduration,location=location)

            ssr=[]                                                              # List storing the starting time of the visibility window for all the stars
            sst=[]                                                              # List storing the ending time of the visibility window for all the stars

            for i in range (len(plantable)):
              # Creating variables raval and decval which would store the right ascension and declination value of a single star during each loop
              raval=plantable[ra][i]
              decval=plantable[dec][i]

              # Creating AstroPy coordinates of a single star in ICRS frame during each loop
              cood=sc(ra=raval*u.deg,dec=decval*u.deg,frame='icrs')
              stalt=(cood.transform_to(aaf1)).alt.value                         # Calculating the star's altitude for every minute for whole night time range

              stars_alt.append(stalt)

              # Variables that would store the start (stsr) and end (stst) time of the visibility window for a single star
              stsr=None
              stst=None

              # Calculating the start and end time of visibility window for each star
              for j in range (len(stalt)):
                if stalt[j]>minalt and stsr is None:
                  stsr=stduration[j]
                  ssr.append(stsr)                                              # Appeding the start time of visibility window of each and every star to ssr
                elif stalt[j]<minalt and stsr is not None and stst is None:
                  stst=stduration[j]
                  sst.append(stst)                                              # Appeding the end time of visibility window of each and every star to sst



            # Asking user to enter the name of the columns that would contain the start and end time of the visibility window for all stars
            stsrcol=input("Enter the name of the new column consisting of starting value for the visibility window: ")
            ststcol=input("Enter the name of the column consisting of ending value for the visibility window: ")
            print('\n')

            # Appending the columns to the copy table
            plantable[stsrcol]=np.array(ssr)
            plantable[ststcol]=np.array(sst)

            display("The updated table consisting of the starting and ending value for the visibility window is:",plantable)
            save(plantable)
            time.sleep(1.5)

            print("NOTE: SESSION CONTINUITY FOR ALTITUDE-TIME PLOTTING", end='\n\n')
            print('*************************************************************************************************************************************************', end='\n\n')
            print("If you intend to visualize Altitude vs Time curves, do NOT terminate the session after this, as visibility context will be lost.", end='\n\n')
            print('*************************************************************************************************************************************************', end='\n\n')
            time.sleep(1.5)

          else:
            if ra not in plantable.colnames:
              print(f"The column {ra} provided does not exist in the file {fname} !!!",end='\n\n')
            elif dec not in plantable.colnames:
              print(f"The column {dec} provided does not exist in the file {fname} !!!",end='\n\n')
            elif not isinstance(plantable[ra][0],(float,np.floating)):
              print(f"The column {ra} provided does not have a numeric data type !!!",end='\n\n')
            else:
              print(f"The column {dec} provided does not have a numeric data type !!!",end='\n\n')

        # If the user chooses an invalid choice from the visibility check & window menu
        else:
          print("INVALID choice from visibility check & window menu !!!",end='\n\n')

##################################################################################################################################################################################

      # If the user chooses to return back to the main menu
      elif chop=='3':
        print("The program would RETURN BACK to MAIN MENU.")
        choice=input("If you want to continue with observational planner, type (y / Y / yes / YES): ")

        if choice in ['y','Y','yes','YES']:
          continue
        else:
          print("You are being directed back to MAIN MENU !!!",end='\n\n')
          print('*************************************************************************************************************************************************',end='\n\n')
          time.sleep(1.5)
          break

##################################################################################################################################################################################

      # If the user chooses an invalid choice from the observational planner menu
      else:
        print("INVALID choice from Observational Planner Menu !!! Please enter a VALID choice !")

##################################################################################################################################################################################
##################################################################################################################################################################################

  # If the user goes with the choice of visualization module
  elif ch=='3':

    # Creating a function which asks user for figure metadeta
    def common(num):
      global xlabel,ylabel,ptitle,label,lblcheck
      xlabel,ylabel,ptitle='','',''
      label=None
      lblcheck=0

      xlabel=input("Enter a label for X-axis: ")
      ylabel=input("Enter a label for Y-axis: ")
      ptitle=input("Enter the title for the plot (leave blank for none): ")

      # If the num has value 1, then only the data regarding legend is asked for
      if num==1:
        asklgnd=input("Enter (y / Y / yes / YES) to include legend in the plot: ")
        if asklgnd in ['y','Y','yes','YES']:
          lblcheck=1
          label=input("Enter label for the curve (to appear in legend): ")

##################################################################################################################################################################################

    # Creating a function which displays and saves the plot
    def showsave():
      # Displaying the graph
      plt.tight_layout()
      plt.show(block=False)
      plt.pause(1)
      print('\n')
      print('****************************************************************************************************************************************',end='\n\n')

      # Creating a loop with a two-tier verification, asking user whether to save the plot or not
      while True:
        # Asking user whether the plot is to be save
        pltsave=input("Enter (y / Y / yes / YES), if you want to save the above graph: ")
        # If the user wants to save the plot
        if pltsave in ['y','Y','yes','YES']:
          print("SETTINGS: Save Settings – ACADEMIC DEFAULTS APPLIED")
          print("DPI = 300 | BBOX_INCHES = 'tight' | TRANSPARENT = False")
          print('****************************************************************************************************************************************',end='\n\n')
          time.sleep(1.5)

          print("NOTE: Only .png and .pdf formats are supported. Please name your file accordingly.", end='\n\n')
          print('****************************************************************************************************************************************',end='\n\n')
          time.sleep(1.5)

          while True:
            # Asking user for the name of the file where the plot will be saved
            pltf=input("Enter a name for the file where the plot is to be saved (include .png or .pdf extension): ")

            # Ensuring that the file has only .png or .pdf extension
            if not (pltf.lower().endswith('.png') or pltf.lower().endswith('.pdf')):
              print(f"The file name {pltf} does NOT end with a .png or .pdf extension !!!")
              time.sleep(0.5)
              print("Please try again !!!",end='\n\n')
              time.sleep(0.5)
              continue
            else:
              break
          # Saving the plot
          plt.savefig(pltf,dpi=300,bbox_inches='tight',transparent=False)
          print("Plot has been SAVED SUCCESSFULLY !!!",end='\n\n')

        # If the use does not want to save the plot
        else:
          print("Are you sure you don't want to save the plot? The plot would be discarded and shall not be retrievable.")
          pltsure=input("If you don't want to loose progress, enter (y / Y / yes / YES): ")   # Reaffirming user's decision
          # If the user wants to continue with saving the plot
          if pltsure in ['y','Y','yes','YES']:
            time.sleep(1)
            continue    # The loop starts again
          # If the user wants to discard the plot
          else:
            break       # The loop breaks

##################################################################################################################################################################################

    vizloop=0
    while True:
      if vizloop!=0:
        print("The program is now returning back to the VISUALIZATION MENU !!!",end='\n\n')
        print('****************************************************************************************************************************************',end='\n\n')
      else:
        print("NOTE: ACADEMIC DEFAULTS APPLIED",end='\n\n')
        print('****************************************************************************************************************************************',end='\n\n')
        print("> Certain VISUAL SETTINGS are FIXED for CLARITY and NOT USER-CONFIGURABLE.")
        print("> It will be SHOWN when a PLOT is SELECTED from the MENU.")
        print("> To MODIFY them, EDIT the SOURCE CODE DIRECTLY.",end='\n\n')
        print('****************************************************************************************************************************************',end='\n\n')

      time.sleep(1.5)
      # Visualization Menu
      vizloop+=1
      print(":::::::::::::::::::::::::  VISUALIZATION MENU  :::::::::::::::::::::::::",end='\n\n')
      print("1. General XY Scatter  -  Plot Any Two Numeric Columns")
      print("2. Column Histogram    -  Visualize Distribution of a Quantity")
      print("3. Category Bar Graph  -  Frequency of a Non-Numeric Column")
      print("4. Altitude vs Time    -  Track Visibility Throughout the Night")
      print("5. Exit Visualization Menu")
      time.sleep(1.5)

      vizch=input("Enter your choice from the visualization menu: ").strip()
      print('\n')
      print('****************************************************************************************************************************************',end='\n\n')

##################################################################################################################################################################################

      # If the user wants to plot a general XY scatter
      if vizch=='1':
        print("SETTINGS: Scatter Plot – ACADEMIC DEFAULTS APPLIED",end='\n\n')
        print("GRID = ON | MARKER = 'o' | LEGEND = OFF")
        print("If color encoding is enabled: COLORMAP = 'magma' | COLORBAR = ON | ORIENTATION = 'vertical'",end='\n\n')
        print('****************************************************************************************************************************************',end='\n\n')
        time.sleep(1.5)

        print("TIP: GENERAL SCATTER PLOT CAN BE USED FOR STAR MAPS",end='\n\n')
        print('****************************************************************************************************************************************',end='\n\n')
        print("> To visualize a star map, use Right Ascension (RA) for X-axis and Declination (Dec) for Y-axis.")
        print("> Color encoding is often based on Apparent Magnitude, but other numeric columns may also be used.")
        print("> It is the user's responsibility to ensure RA ∈ [0°, 360°] and Dec ∈ [–90°, +90°] if a sky map is intended.",end='\n\n')
        print('****************************************************************************************************************************************',end='\n\n')
        time.sleep(1.5)

        xax=input("Enter the name of the column consisting of x-axis values: ")
        yax=input("Enter the name of the column consisting of y-axis values: ")
        print('\n')

        if xax in readtable.colnames and yax in readtable.colnames and isinstance(readtable[xax][0],(float,np.floating)) and isinstance(readtable[yax][0],(float,np.floating)):
          # common() allows user to set the metadata
          common(0)
          # Asking user whether the color encoding is to be enabled
          copt = input("Enter (y / Y / yes / YES) to enable color encoding using a third numeric column: ")

          # If the user wants to enable color encoding
          if copt in ['y','Y','yes','YES']:
            # The loop continues until user enters a valid column
            while True:
              # Asking user for the column to be utilized for color encoding
              ccol = input("Enter the column name to use for color encoding: ")
              if ccol not in readtable.colnames:
                print(f"The column {ccol} provided does not exist in the file {fname} !!!",end='\n\n')
                continue
              elif not isinstance(readtable[ccol][0],(float,np.floating)):
                print(f"The column {ccol} provided does not have a numeric data type !!!",end='\n\n')
                continue
              else:
                break

            # Asking user for a label for the colorbar
            clabel=input(f"Label for colorbar (e.g., '{ccol}'): ")
            # Constructing the graph
            graph=plt.scatter(np.array(readtable[xax]),np.array(readtable[yax]),c=np.array(readtable[ccol]),cmap='magma')
            plt.colorbar(graph,label=clabel)

          # If the user wants to disable the color encoding
          else:
            graph=plt.scatter(np.array(readtable[xax]),np.array(readtable[yax]))

          plt.title(ptitle)
          plt.xlabel(xlabel)
          plt.ylabel(ylabel)
          plt.grid(True)

          # showsave() allows the plot to be dispayed and saved
          showsave()

        else:
          if xax not in plantable.colnames:
            print(f"The column {xax} provided does not exist in the file {fname} !!!",end='\n\n')
          elif yax not in plantable.colnames:
            print(f"The column {yax} provided does not exist in the file {fname} !!!",end='\n\n')
          elif not isinstance(readtable[xax][0],(float,np.floating)):
            print(f"The column {xax} provided does not have a numeric data type !!!",end='\n\n')
          else:
            print(f"The column {yax} provided does not have a numeric data type !!!",end='\n\n')

##################################################################################################################################################################################

      # If the user wants to plot a column histogram for numeric column
      elif vizch=='2':
        print("SETTINGS: Histogram – ACADEMIC DEFAULTS APPLIED", end='\n\n')
        print("EDGE COLOR = 'black' | BAR COLOR = 'slategray' | GRID = ON (y-axis only)",end='\n\n')
        print('****************************************************************************************************************************************',end='\n\n')
        time.sleep(1.5)

        xax=input("Enter the name of the column to visualize using a histogram: ")
        print('\n')

        if xax in readtable.colnames and isinstance(readtable[xax][0],(float,np.floating)):

          # Loop to validate user input for histogram bin configuration
          while True:
            bin_input=input("Enter number of bins (positive integer) or type 'auto' for automatic binning: ")

            # If the input is a purely alphabetic string (e.g., 'auto', 'AUTO')
            if bin_input.isalpha():
              if bin_input.strip().lower()=='auto':
                bins='auto'
                break
              # Invalid non-numeric string
              else:
                print(f"ERROR: '{bin_input}' is NOT a VALID input !!! ONLY 'auto' is accepted as a non-numeric bin mode !")
                print("Please try again !",end='\n\n')
                continue

            # If the input is numeric (e.g., '10')
            elif bin_input.isnumeric():
              try:
                bins=int(bin_input)
                # Ensuring strictly positive bin count
                if bins<=0:
                  raise ValueError
                # Valid integer bin count
                else:
                  break
              except ValueError:
                print(f"ERROR: '{bins}' is NOT a VALID bin count !!! Bin count MUST be a POSITIVE integer (> 0) !")
                print("Please try again !",end='\n\n')
                continue

            # If the input is invalid
            else:
              print(f"ERROR: {bin_input} is NOT a VALID input !!! Please enter a positive integer OR the word 'auto' ONLY !")
              print("Please try again !",end='\n\n')
              continue

          common(1)

          # If the user prefers automatic binning
          if bins=='auto':
            # If the user wants a legend
            if lblcheck==1:
              graph=plt.hist(np.array(readtable[xax]), bins='auto', edgecolor='black', color='slategray', label=label)
              plt.legend()
            # If the user does not want a legend
            else:
              graph=plt.hist(np.array(readtable[xax]), bins='auto', edgecolor='black', color='slategray')

          # If the user has manually specified the number of bins
          else:
            if lblcheck==1:
              graph=plt.hist(np.array(readtable[xax]), bins=bins, edgecolor='black', color='slategray', label=label)
              plt.legend()
            else:
              graph=plt.hist(np.array(readtable[xax]), bins=bins, edgecolor='black', color='slategray')

          plt.title(ptitle)
          plt.xlabel(xlabel)
          plt.ylabel(ylabel)
          plt.grid(axis='y')

          showsave()

        else:
          if xax not in readtable.colnames:
            print(f"The column {xax} provided does not exist in the file {fname} !!!",end='\n\n')
          else:
            print(f"The column {xax} provided does not have a numeric data type !!!",end='\n\n')

##################################################################################################################################################################################

      # If the user wants to plot a category bar graph for a non-numeric column
      elif vizch=='3':
        print("SETTINGS: Bar Graph – ACADEMIC DEFAULTS APPLIED", end='\n\n')
        print("BAR COLOR = 'slategray' | EDGE COLOR = 'black' | BAR WIDTH = 0.8 | GRID = ON (Y-axis only)",end='\n\n')
        print('****************************************************************************************************************************************',end='\n\n')
        time.sleep(1.5)

        xax=input("Enter the name of the column to visualize as a categorical bar graph: ")
        print('\n')

        if xax in readtable.colnames and isinstance(readtable[xax][0],(str,np.str_)):
          common(1)
          category,count=np.unique(np.array(readtable[xax]),return_counts=True)

          if lblcheck==1:
            graph=plt.bar(category,count,color='slategray',edgecolor='black',width=0.8,label=label)
            plt.legend()
          else:
            graph=plt.bar(category,count,color='slategray',edgecolor='black',width=0.8)

          plt.title(ptitle)
          plt.xlabel(xlabel)
          plt.ylabel(ylabel)
          plt.grid(axis='y')

          showsave()

        else:
          if xax not in readtable.colnames:
            print(f"The column {xax} provided does not exist in the file {fname} !!!",end='\n\n')
          else:
            print(f"The column {xax} provided does not have a string data type !!!",end='\n\n')

##################################################################################################################################################################################
      # If the user wants to plot an altitude vs time graph
      elif vizch=='4':
        # Block access if visibility data is missing and guide user to run visibility window first
        if stars_alt not in globals() or stars_alt==[]:
          print("ACCESS DENIED: Visibility Data Not Found", end='\n\n')
          print('****************************************************************************************************************************************',end='\n\n')
          print("> Altitude vs Time plotting requires visibility data, which has not been generated in this session.")
          print("> To proceed, exit the Visualization Menu and return to the Main Menu.")
          print("> Then open the Observational Planner and select: 'Visibility (Check and) Window (Full Night Range)'.")
          print("> After running the above tool, return here to generate Altitude vs Time curves.",end='\n\n')
          print('****************************************************************************************************************************************',end='\n\n')
          time.sleep(1.5)
          continue

        print("SETTINGS: Altitude-Time Plot – ACADEMIC DEFAULTS APPLIED", end='\n\n')
        print(f"> X-AXIS: Night-time UTC range ({stduration[0]} to {stduration[(len(stduration))-1]}) | Y-AXIS: Apparent altitude (in degrees)")
        print("> LINE COLOR: Auto | LINE STYLE: '-' | MARKER: OFF | GRID: ON | LEGEND: Star names used as curve labels")
        print("> HORIZON LINE: Dashed gray line at user-defined altitude limit", end='\n\n')
        print('****************************************************************************************************************************************',end='\n\n')
        time.sleep(1.5)

        # Asking user for the name of the column containing star names to be used in the plot legend
        labelcol=input("Enter the column name containing star names (used for labeling each curve): ")
        print('\n')

        if labelcol in readtable.colnames and isinstance(readtable[labelcol][0],(str,np.str_)):

          # Asking user whether to plot all stars or only specific ones
          while True:
            time.sleep(0.5)
            # Evaluating the user input to handle invalid Python syntax
            try:
              starch=eval(input("Enter 'all' to plot all stars or provide a list of row numbers (e.g., [0, 3, 7]): "))
            except SyntaxError:
              print("ERROR: INVALID input syntax !!! Please enter 'all' or a list like [0, 2, 5] !")
              print("Please try again !",end='\n\n')
              continue

            # If input is a string (e.g., 'all')
            if type(starch)==str:
              # If all inputs are valid, flag the selection mode as 'all'
              if starch.strip().lower()=='all':
                nplot='all'
                break
              # Invalid string
              else:
                print(f"ERROR: '{starch}' is NOT a VALID input !!! ONLY 'all' is accepted for string input !")
                print("Please try again !",end='\n\n')
                continue

            # If input is a list of row numbers
            elif type(starch)==list:
              for i in range(len(starch)):

                # Ensuring all elements are integer
                if type(starch[i])!=int:
                  print(f"ERROR: Element '{starch[i]}' in the list is NOT an INTEGER !!! Please enter row indices as integers !")
                  print("Please try again !",end='\n\n')
                  continue

                # Ensuring the row indices mentioned by the user is within the valid bounds of the catalog
                elif not (0<=starch[i]<len(readtable)):
                  print(f"ERROR: Row index {starch[i]} is OUT of bounds !!! Valid range: [0,{len(readtable)-1}] !")
                  print("Please try again !",end='\n\n')
                  continue

                # If all inputs are valid, flag the selection mode as 'specific'
                else:
                  nplot='specific'
                  break

            # Any other invalid input format
            else:
              print("ERROR: INVALID input DATA TYPE !!! Use 'all' or a list of integers like [0, 2, 5] !")
              print("Please try again !",end='\n\n')
              continue

          common(0)

          # Plot all stars using auto color cycle and labels from the selected column
          if nplot=='all':
            for i in range(len(readtable)):
              plt.plot(stduration,stars_alt[i],label=readtable[labelcol][i])
          # Plot only selected stars using their row indices
          else:
            for i in starch:
              plt.plot(stduration,stars_alt[i],label=readtable[labelcol][i])

          plt.title(ptitle)
          plt.xlabel(xlabel)
          plt.ylabel(ylabel)
          plt.axhline(y=minalt,linestyle='--',color='gray',linewidth=0.8)
          plt.grid(True)
          plt.legend()

          showsave()

        else:
          if labelcol not in readtable.colnames:
            print(f"The column {labelcol} provided does not exist in the file {fname} !!!",end='\n\n')
          else:
            print(f"The column {labelcol} provided does not have a string data type !!!",end='\n\n')

##################################################################################################################################################################################

      # If the user chooses to return back to the main menu
      elif vizch=='5':
        print("The program would RETURN BACK to MAIN MENU.")
        vizsure=input("If you want to continue with visualization process, type (y / Y / yes / YES): ")

        if vizsure in ['y','Y','yes','YES']:
          continue
        else:
          print("You are being directed back to MAIN MENU !!!",end='\n\n')
          print('*************************************************************************************************************************************************',end='\n\n')
          time.sleep(1.5)
          break

##################################################################################################################################################################################

      # If the user chooses an invalid choice from the visualization menu
      else:
        print("INVALID choice from Visualization Menu !!! Please enter a VALID choice !")

##################################################################################################################################################################################
##################################################################################################################################################################################

  # If the user goes with the choice of session termination
  elif ch=='4':
    print("Are you sure? You are about to EXIT the ENGINE and your SESSION will be TERMINATED.")
    choice=input("If you want to continue with the current session, type (y / Y / yes / YES): ") # Reaffirming whether the user wants to terminate the session

    if choice in ['y','Y','yes','YES']:                                                          # If the user wants to continue with the current session
      continue
    else:                                                                                        # If the user wants to terminate the session
      print("Thanks for exploring the stars with us! Wishing you clear skies and great observations ahead! :)",end='\n\n')
      print("Your session is being terminated....")
      time.sleep(1)
      print(".....")
      time.sleep(1.5)
      print("Your session has been SUCCESSFULLY TERMINATED !!!",end='\n\n')
      print('*************************************************************************************************************************************************',end='\n\n')
      break

##################################################################################################################################################################################
##################################################################################################################################################################################

  # If the user goes with an invalid choice from main menu
  else:
    print("INVALID choice from Main Menu !!!")
    print("You are being directed back to MAIN MENU !!!",end='\n\n')
    print('*************************************************************************************************************************************************',end='\n\n')
    time.sleep(1.5)

##################################################################################################################################################################################
##################################################################################################################################################################################
