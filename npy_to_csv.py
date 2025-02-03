import numpy as np
import pandas as pd

# Step 1: Load the .npy file
data = np.load('D:/download1/all_alarms/all_alarms/x_train.npy')

# Step 2: Convert to a DataFrame (optional but helpful for labeling columns/rows)
# This assumes 'data' is a 2D array. If it's 1D, you'll need to reshape or handle differently.
df = pd.DataFrame(data)

# Step 3: Save to a .csv file
df.to_csv('D:/download1/all_alarms/all_alarms/x_train.csv', index=False)
