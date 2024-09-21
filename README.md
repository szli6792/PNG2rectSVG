This script works on batches of files: 

1) specify a png origin folder and a svg destination folder in the same directory, run this script in the directory that is at the same level as these folders

2) change 'png' and 'svg' with your folder names:

   input_folder = 'png' ######################################### MODIFY NAME HERE
   output_folder = 'svg' ######################################### MODIFY NAME HERE

3) change the line:
   
   new_filename = f"yoyo {i}.svg"

   where 'yoyo' becomes your new file name. Ex: produces output yoyo 1.svg, yoyo 2.svg, yoyo 3.svg, etc
   
   Alternatively, uncomment #file_name, file_ext = os.path.splitext(filename) and replace yoyo {i} with the variable {file_name} to preserve png file names.
