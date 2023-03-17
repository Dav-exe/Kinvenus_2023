
import numpy as np
import csv
import netCDF4

class Out30BFile:
    def __init__(self, filepath):
        self.filepath = filepath
        self.lines = []
        with open(filepath, 'r') as f:
            self.lines = f.readlines()
        global file_searched
        file_searched = filepath

    def count_tstep(self):
        tstep_lines = []
        for i, line in enumerate(self.lines):
            if "TSTEP" in line:
                tstep_lines.append(i+1)
        return tstep_lines

    def get_lines(self, search_term, start_line_num, end_line_num):
        for i in range(start_line_num - 1, end_line_num):
            line = self.lines[i]
            if search_term.strip() in line:
                next_lines = []
                empty_line_count = 0
                for j in range(i + 1, len(self.lines)):
                    if not self.lines[j].strip():
                        empty_line_count += 1
                        if empty_line_count >= 2:
                            break
                        continue
                    else:
                        empty_line_count = 0
                    if self.lines[j].strip().startswith("COLUMN"):
                        continue
                    curr_line = self.lines[j].strip()
                    curr_line = curr_line.rstrip(')')
                    if ')' in curr_line[1:4]:
                        curr_line = curr_line.split(None, 1)[1]
                    next_lines.append(curr_line)
                # code helping to output relevant naming info
                global line_searched
                line_searched = ((line).strip()).replace(":", "").replace(" ", "_")
                global line_read
                line_read = line.strip()
                return '\n'.join(next_lines)
        # lines below run if the input searched lines do not exist
        print("Input search data group is not found")
        exit()

def get_list_element(num):
    if num == 0:
        return 0
    elif num > len(read_file.count_tstep()):
        print("Input TSTEP is larger than the total number of TSTEP.")
        exit()
    else:
        return int(read_file.count_tstep()[num - 1])
    
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
    if print_info == True:
        print(f"Array successfully saved as {filename}")

def csv_saved(csv_file, filename):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(csv_file)
    if print_info == True:
      print(f"Array successfully saved as {filename}")

'''----------------------------------USER-INTERFACE----------------------------------'''

#change the file to be searched in the line below
    #read_file = Out30BFile("kinvenus_2022oct07_so2cl2_s8_so2_3ppm_nominalclso2.out030b")
read_file = Out30BFile("venus.out-100_fine_SO2-3ppm_new_correct")
    #venus.out-100_fine_SO2-3ppm_new_correct
    #kinvenus_2022oct07_so2cl2_s8_so2_3ppm_nominalclso2.out030b

#changing the TSTEP_number changes the TSTEP searched under (expects a integer 0 or greater)
    #0 looks at data above the TSTEP and 1 below the first instance and so on
TSTEP_number = 0

#change the row searched for data in this line (is caps sensitive)
data_group = (read_file.get_lines(("ATOMIC CONCENTRATIONS"), get_list_element(TSTEP_number), get_list_element(TSTEP_number+1)))

#prints out additional information if = True ,if False doesn't
print_info = False

'''--------------------------------CHANGE-THESE-VALUES--------------------------------'''

final_output = remove_duplicate_altitudes(merging_data(process_data(data_group)))

csv_file_name = "TSTEP_"+str(TSTEP_number)+"_"+line_searched+"_from_"+file_searched+".csv"
NetCDF_file_name = "TSTEP_"+str(TSTEP_number)+"_"+line_searched+"_from_"+file_searched+".nc"


#csv_saved(final_output,csv_file_name)
convert_array_to_nc(final_output,NetCDF_file_name)


if print_info == True:
    print ("the data group read is",line_read)
    print ("the file read is",file_searched)
    print ("the TSTEP selected is",TSTEP_number)
    print ("the data range is from colum",get_list_element(TSTEP_number),"to",get_list_element(TSTEP_number+1))