import pandas as pd
import numpy as np
import os

def main(df):
    sdnn = df.iloc[0]['SDNN']
    asdnn = df.iloc[0]['ASDNN']
    sdann = df.iloc[0]['SDANN']
    rmssd = df.iloc[0]['RMSSD']
    pnn50 = df.iloc[0]['pNN50']
    vlf = df.iloc[0]['VLF']
    lf = df.iloc[0]['LF']
    hf = df.iloc[0]['HF']
    tp = df.iloc[0]['TP']
    lf_p = df.iloc[0]['LF%'].replace('%', '')
    hf_p = df.iloc[0]['HF%'].replace('%', '')
    lf_hf = df.iloc[0]['LF/HF']
    

    # SDNN
    if float(sdnn) > (141 + 39):
        df.loc[0, 'SDNN'] = "High"
    elif float(sdnn) < (141 - 39):
        df.loc[0, 'SDNN'] = "Low"
    else:
        df.loc[0, 'SDNN'] = "Standard"

    # RMSSD    
    if float(rmssd) > (27 + 12):
        df.loc[0, 'RMSSD'] = "High"
    elif float(rmssd) < (27 - 12):
        df.loc[0, 'RMSSD'] = "Low"
    else:
        df.loc[0, 'RMSSD'] = "Standard"

    # pNN50
    if float(pnn50) <= 50:
        df.loc[0, 'pNN50'] = "Low"
    else:
        df.loc[0, 'pNN50'] = "Standard"

    # VLF
    if float(vlf) > (37 + 15):
        df.loc[0, 'VLF'] = "High"
    elif float(vlf) < (37 - 15):
        df.loc[0, 'VLF'] = "Low"
    else:
        df.loc[0, 'VLF'] = "Standard"

    # LF
    if float(lf) > (1170 + 416):
        df.loc[0, 'LF'] = "High"
    elif float(lf) < (1170 - 416):
        df.loc[0, 'LF'] = "Low"
    else:
        df.loc[0, 'LF'] = "Standard"

    # HF
    if float(hf) > (975 + 203):
        df.loc[0, 'HF'] = "High"
    elif float(hf) < (975 - 203):
        df.loc[0, 'HF'] = "Low"
    else:
        df.loc[0, 'HF'] = "Standard"

    # TP
    if float(tp) > (3466 + 1018):
        df.loc[0, 'TP'] = "High"
    elif float(tp) < (3466 - 1018):
        df.loc[0, 'TP'] = "Low"
    else:
        df.loc[0, 'TP'] = "Standard"

    # LF%
    if float(lf_p) > (54 + 4):
        df.loc[0, 'LF%'] = "High"
    elif float(lf_p) < (54 - 4):
        df.loc[0, 'LF%'] = "Low"
    else:
        df.loc[0, 'LF%'] = "Standard"

    # HF%
    if float(hf_p) > (29 + 3):
        df.loc[0, 'HF%'] = "High"
    elif float(hf_p) < (29 - 3):
        df.loc[0, 'HF%'] = "Low"
    else:
        df.loc[0, 'HF%'] = "Standard"

    # LF/HF
    if float(lf_hf) > (1.5 + 0.5):
        df.loc[0, 'LF/HF'] = "High"
    elif float(lf_hf) < (1.5 - 0.5):
        df.loc[0, 'LF/HF'] = "Low"
    else:
        df.loc[0, 'LF/HF'] = "Standard"

    return df

current_directory = os.getcwd()
csv_files = [f for f in os.listdir(current_directory) if f.endswith('.csv')]
print(current_directory)
if len(csv_files) > 0:
    for csv_filename in csv_files:
        df = pd.read_csv(csv_filename, encoding='Big5')
        df = main(df)
        df.to_csv('output' + csv_filename, index=False)
else:
    print("No Document")