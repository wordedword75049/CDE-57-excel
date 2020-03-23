import xlsxwriter
import pandas as pd

path_toInput = ''
path_toOutput = ''
input_Filename = 'Data_frame.csv'
output_Filename = 'output.xlsx'
data = pd.read_csv(path_toInput + input_Filename)
writer = pd.ExcelWriter(path_toOutput + output_Filename, engine='xlsxwriter')
data.to_excel(writer, sheet_name='mysheet', index=False)
writer.save()