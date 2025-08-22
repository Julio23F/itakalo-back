import pandas as pd
import numpy as np

def calculate_mesiodistal_width(distal_data, mesial_data):

    try:
        distal_x = float(distal_data['X-Pos'])
        distal_y = float(distal_data['Y-Pos'])
        distal_z = float(distal_data['Z-Pos'])
        mesial_x = float(mesial_data['X-Pos'])
        mesial_y = float(mesial_data['Y-Pos'])
        mesial_z = float(mesial_data['Z-Pos'])
    except ValueError:
        return np.nan
    mesiodistal_width = np.sqrt((distal_x - mesial_x)**2 
                                + (distal_y - mesial_y)**2 
                                + (distal_z - mesial_z)**2)
    return mesiodistal_width


def fill_missing_with_linear_regression(region_data):
    # Filter out missing values and prepare data for linear regression
    x = np.array([tooth_number for tooth_number, tooth_value in region_data.items() if not np.isnan(tooth_value)])
    y = np.array([tooth_value for tooth_number, tooth_value in region_data.items() if not np.isnan(tooth_value)])

    # Fit a linear model to the data
    coeffs = np.polyfit(x, y, 1)
    linear_regression = np.poly1d(coeffs)

    # Prepare the result dictionary
    result = {}
    for tooth_number, tooth_value in region_data.items():
        if not np.isnan(tooth_value):
            result[tooth_number] = {'value': round(tooth_value, 2), 'predicted': 0}
        else:
            result[tooth_number] = {'value': round(linear_regression(tooth_number), 2), 'predicted': 1}

    return result


def get_bolton_analysis(file_path):
    df = pd.read_excel(file_path, usecols=['Landmarks', 'X-Pos', 'Y-Pos', 'Z-Pos'], engine="xlrd")

    data = df.set_index('Landmarks').T.to_dict('list')
    
    mesiodistal_widths = {}
    for landmark, positions in data.items():
        tooth_number = int(landmark[:2]) 
        if tooth_number not in mesiodistal_widths.keys():
            mesiodistal_widths[tooth_number] = {}
        if not np.isnan(positions[1]):
            mesiodistal_widths[tooth_number][landmark[2:]] = dict(zip(['X-Pos', 'Y-Pos', 'Z-Pos'], positions[:3])) 

    for tooth_number, tooth_data in mesiodistal_widths.items():
        if 'd' in tooth_data and 'm' in tooth_data:
            mesiodistal_widths[tooth_number] = calculate_mesiodistal_width(tooth_data['d'], tooth_data['m'])
        elif 'd' in tooth_data and 'mP' in tooth_data:
            mesiodistal_widths[tooth_number] = calculate_mesiodistal_width(tooth_data['d'], tooth_data['mP'])
        else:
            mesiodistal_widths[tooth_number] = np.nan

    bolton_analysis = {}
    bolton_analysis['Supérieur droit'] = fill_missing_with_linear_regression({k: v for k, v in mesiodistal_widths.items() if k in range(11, 19)})
    bolton_analysis['Supérieur gauche'] = fill_missing_with_linear_regression({k: v for k, v in mesiodistal_widths.items() if k in range(21, 29)})
    bolton_analysis['Inférieur droit'] = fill_missing_with_linear_regression({k: v for k, v in mesiodistal_widths.items() if k in range(41, 49)})
    bolton_analysis['Inférieur gauche'] = fill_missing_with_linear_regression({k: v for k, v in mesiodistal_widths.items() if k in range(31, 39)})

    maxillary_arcade_length_global = calculate_arcade_length(bolton_analysis['Supérieur droit'], bolton_analysis['Supérieur gauche'])
    mandibular_arcade_length_global = calculate_arcade_length(bolton_analysis['Inférieur droit'], bolton_analysis['Inférieur gauche'])

    maxillary_arcade_length_anterior = calculate_arcade_length({k: v for k, v in bolton_analysis['Supérieur droit'].items() if 21 <= k <= 23 or 11 <= k <= 13},
                                                              {k: v for k, v in bolton_analysis['Supérieur gauche'].items() if 21 <= k <= 23 or 11 <= k <= 13})
    mandibular_arcade_length_anterior = calculate_arcade_length({k: v for k, v in bolton_analysis['Inférieur droit'].items() if 41 <= k <= 43 or 31 <= k <= 33},
                                                                {k: v for k, v in bolton_analysis['Inférieur gauche'].items() if 41 <= k <= 43 or 31 <= k <= 33})

    bolton_analysis['Maxillary arcade length (global)'] = maxillary_arcade_length_global
    bolton_analysis['Mandibular arcade length (global)'] = mandibular_arcade_length_global

    bolton_analysis['Maxillary arcade length (anterior)'] =  maxillary_arcade_length_anterior
    bolton_analysis['Mandibular arcade length (anterior)'] =  mandibular_arcade_length_anterior

    anterior_sector_ratio =  round(maxillary_arcade_length_anterior['length'] / mandibular_arcade_length_anterior['length'], 2)
    global_ratio =  round(mandibular_arcade_length_global['length'] / maxillary_arcade_length_global['length'], 2)

    bolton_analysis['Anterior sector ratio (maxillary/mandibular)'] = {'value': anterior_sector_ratio, 'predicted': maxillary_arcade_length_anterior['predicted'] or mandibular_arcade_length_anterior['predicted']}
    bolton_analysis['Global ratio (mandibular/maxillary)'] = {'value': global_ratio, 'predicted': maxillary_arcade_length_global['predicted'] or mandibular_arcade_length_global['predicted']}

    bolton_analysis['Maxillary excess (dysharmony)'] = {'value': int(anterior_sector_ratio > 1), 'predicted': maxillary_arcade_length_anterior['predicted'] or mandibular_arcade_length_anterior['predicted']}
    bolton_analysis['Mandibular excess (dysharmony)'] = {'value': int(anterior_sector_ratio < 1), 'predicted': maxillary_arcade_length_anterior['predicted'] or mandibular_arcade_length_anterior['predicted']}
    bolton_analysis['Maxillary excess in global ratio'] = {'value': int(global_ratio < 0.913), 'predicted': maxillary_arcade_length_global['predicted'] or mandibular_arcade_length_global['predicted']}

    return bolton_analysis


def calculate_arcade_length(teeth_data1, teeth_data2):
    predicted = int(any([v['predicted'] for v in teeth_data1.values()] + [v['predicted'] for v in teeth_data2.values()]))
    length = np.nansum([v['value'] for v in teeth_data1.values()] + [v['value'] for v in teeth_data2.values()])
    return {'length': round(length, 2), 'predicted': predicted}

# def main():
#     file_path = "Landmarks_Bolton2.xls"
#     bolton_analysis = get_bolton_analysis(file_path)

# if __name__ == "__main__":
#     main()
