import pandas as pd
from pandas_profiling import ProfileReport
profile = ProfileReport(pd.read_csv('sample-ppp.csv'), explorative=True)

profile.to_file("output.html")