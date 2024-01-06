from datasets import load_dataset
import h5py

custom_cache_dir = "/home/silver/local-ssd/bench/vector-db-benchmark/huggingface"

# Load the dataset
dataset = load_dataset('KShivendu/dbpedia-entities-openai-1M', cache_dir=custom_cache_dir)

# Save the dataset to HDF5 format
def save_to_hdf5(dataset, hdf5_filename='data.hdf5'):
    with h5py.File(hdf5_filename, 'w') as h5f:
        for split in dataset:
            # Each split (train, test, etc.) will be in its subgroup
            grp_split = h5f.create_group(split)
            # Get each column in the split
            for feature in dataset[split].column_names:
                data = dataset[split][feature]
                # You can adjust the shape and dtype as necessary
                dset = grp_split.create_dataset(feature, data.shape, dtype=str, compression="gzip")
                dset[:] = data

# Provide the filename you want for the HDF5 file
save_to_hdf5(dataset, hdf5_filename='openai-1536-100w-cosine.hdf5')