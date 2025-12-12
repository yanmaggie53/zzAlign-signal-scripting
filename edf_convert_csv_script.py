import mne
import numpy as np

edf_file_path = 'N008N1NoxEDF.edf'
raw = mne.io.read_raw_edf(edf_file_path, preload = True)

data = raw.get_data()
ch_names = raw.info['ch_names']

header = ','.join(ch_names)

csv_file_path = 'N008N1NoxCSV.csv'
np.savetxt(csv_file_path, data.T, delimiter=',', header=header, comments='')