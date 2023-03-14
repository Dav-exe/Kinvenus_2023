
import numpy as np
import csv
import netCDF4


class Out30BFile:
    def __init__(self, filepath):
        self.filepath = filepath
        self.lines = []
        with open(filepath, 'r') as f:
            self.lines = f.readlines()

    def get_lines(self, starting_line):
        for i, line in enumerate(self.lines):
            #officer this man here 
            if line.strip() == starting_line:
                next_lines = []
                empty_line_count = 0
                for j in range(1, len(self.lines)):
                    if i+j < len(self.lines):
                        if not self.lines[i+j].strip():
                            empty_line_count += 1
                            if empty_line_count >= 2:
                                break
                            continue
                        else:
                            empty_line_count = 0
                        if self.lines[i+j].strip().startswith("COLUMN"):
                            continue
                        curr_line = self.lines[i+j].strip()
                        curr_line = curr_line.rstrip(')')
                        if ')' in curr_line[1:4]:
                            curr_line = curr_line.split(None, 1)[1]
                        next_lines.append(curr_line)
                return '\n'.join(next_lines)
        print('input search d_lines is not found')
        exit()

def process_data(data):
    data_list = data.split("\n")
    arrays = []
    current_array = []

    for line in data_list:
        if line.startswith("ALTITUDE"):
            if current_array:
                arrays.append(current_array)
                current_array = []
            current_array.append(line.split())
        else:
            current_array.append(line.split())

    arrays.append(current_array)

    final_arrays = []
    for i, array in enumerate(arrays):
        temp_array = []
        for line in array:
            temp_array.append(line)
        final_arrays.append(temp_array)

    return final_arrays

def merging_data(data):
    arrays = []
    for array in data:
        header = np.array(array[0])
        header[0] = 'ALTITUDE'  # Replace 'ALT' with 'ALTITUDE'
        array[0] = header  # Assign the modified header back to the array
        temp_array = np.array(array)
        arrays.append(temp_array)

    con = np.concatenate(arrays, axis=1)
    return np.array(con)  # Return the result as a 2D NumPy array

def remove_duplicate_altitudes(combined_data):
    # Find the indices of columns to remove
    remove_indices = []
    altitude_indices = np.argwhere(combined_data[0,:] == "ALTITUDE")
    if altitude_indices.size > 0:
        first_altitude = altitude_indices[0][0]
    else:
        first_altitude = None

    for i in range(first_altitude+1, combined_data.shape[1]):
        if combined_data[0,i] == "ALTITUDE":
            remove_indices.append(i)

    # Remove the columns
    result = np.delete(combined_data, remove_indices, axis=1)
    
    return result

def convert_array_to_nc(array, filename):
    nc_file = netCDF4.Dataset(filename, "w", format="NETCDF4")
    nc_file.createDimension("row", len(array[1:]))
    nc_file.createDimension("col", len(array[0]))
    for i in range(len(array[0])):
        nc_file.createVariable(array[0][i], "f8", ("row",))
        nc_file.variables[array[0][i]][:] = [float(row[i]) for row in array[1:]]
    nc_file.close()
    print(f"Array successfully saved as {filename}")

def csv_saved(csv_file, filename):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(csv_file)
    print(f"Array successfully saved as {filename}")

#change the file to be searched in the line 
out30b = Out30BFile("kinvenus_2022oct07_so2cl2_s8_so2_3ppm_nominalclso2.out030b")
#change the row searched for data in this line (for now must be the whole row)
d_lines = (out30b.get_lines("MIXING RATIOS :"))

#find a better way of writing the ans bit 
ans = remove_duplicate_altitudes(merging_data(process_data(d_lines)))
#print (ans)

#csv_saved(ans,"thiswontwork#2.csv")

convert_array_to_nc(ans, "thiswontwork#3.nc")

'''TO DO'''
#add incorrect search response                                  |||DONE
#fix the called upon error at ans                               |||TO DO
#make an adjustable search below TSTEP line                     |||TO DO
#change the search from the whole line to just a fraise         |||TO DO
#tidy and optimize                                              |||TO DO 