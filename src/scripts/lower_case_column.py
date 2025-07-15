import pandas as pd
from google_sheets_utils import get_worksheet


worksheet = get_worksheet("[100 PARCEIROS] PLANILHA GERAL")

def view_worksheet(worksheet):
    data = worksheet.get_all_values()
    print(pd.DataFrame(data))

def column_lowercase(worksheet):
    column_index = 6  
    start_row = 5     

    values_column = worksheet.col_values(column_index)

    lowercase_values = [value.lower() for value in values_column[start_row - 1:]]

    cells = worksheet.range(start_row, column_index, start_row + len(lowercase_values) - 1, column_index)

    for i, cell in enumerate(cells):
        cell.value = lowercase_values[i]
        
    worksheet.update_cells(cells)

# column_lowercase(worksheet)
view_worksheet(worksheet)