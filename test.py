import json
import matplotlib.pyplot as plt

def load_data(file_path):
    with open(file_path, 'r') as file:
        data={}
        for f in file:
            item = json.loads(f)
            if not item["visitor_country"] in data.keys():
                data[item["visitor_country"]]=1
            else:
                data[item["visitor_country"]]+=1
        print(data)
        data = [json.loads(line) for line in file]
    return data
class DataGetter():
    def __init__(self) -> None:
        pass
    def load_data(file_path):
        with open(file_path, 'r') as file:
            data={}
            for f in file:
                item = json.loads(f)
                if not item["visitor_country"] in data.keys():
                    data[item["visitor_country"]]=1
                else:
                    data[item["visitor_country"]]+=1
            print(data)
            data = [json.loads(line) for line in file]
        return data

def plot_histogram(data):
    plt.hist(data, bins=10, color='blue', edgecolor='black', alpha=0.7)
    plt.xlabel('Values')
    plt.ylabel('Frequency')
    plt.title('Histogram of Data')
    plt.show()

if __name__ == "__main__":
    # Replace 'data.json' with the actual path to your JSON data file
    data_file_path = 'sample_tiny.json'

    # Load data from the file
    numerical_data = load_data(data_file_path)

    # Plot histogram
    plot_histogram(numerical_data)