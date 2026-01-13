import pandas as pd

from renumics import spotlight
import pandas as pd
import ast  # 
# Load your CSV
csv_file = r"C:\Users\wout.decrop\Documents\environments\flowcytometer_utils_public\data\test\LW2019protocol1_20240306_ZG02_2 2024-05-07 13h57.csv"
df = pd.read_csv(csv_file)

# Identify embedding columns (those starting with "parameters")
embedding_columns = [col for col in df.columns if col not in ['image', 'image_location']]


# If some columns are strings that look like lists, convert them to actual lists
for col in embedding_columns:
    if df[col].dtype == object:
        df[col] = df[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

# Now create a single flattened list per row
def flatten_row(row, cols):
    flat_list = []
    for col in cols:
        value = row[col]
        if isinstance(value, list):
            flat_list.extend(value)
        else:
            flat_list.append(value)
    return flat_list

df['embeddings'] = df.apply(lambda row: flatten_row(row, embedding_columns[0:3]), axis=1)[0:5]


# print(embedding_columns)
# # Create a new column 'embeddings' as a list of floats for each row
# df['embeddings'] = df[embedding_columns].values.tolist()

# Tell Spotlight that 'embeddings' column is an embedding
dtype = {"embeddings": spotlight.Embedding}

# Optional: you can also tell Spotlight that a column contains image paths
# dtype['image_location'] = spotlight.Image

# Display the DataFrame in Spotlight
spotlight.show(df, dtype=dtype)
