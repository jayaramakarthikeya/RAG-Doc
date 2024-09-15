
import pandas as pd

class Extract:
    def __init__(self,dataset_path, df_train_path, df_test_path, label_mapping_path):
        self.dataset_path = dataset_path
        self.df_train_path = dataset_path+df_train_path
        self.df_test_path = dataset_path+df_test_path 
        self.label_mapping_path = dataset_path+label_mapping_path

    def open_label_mapping(self):
        with open(self.label_mapping_path, 'r') as f:
            data = json.load(f)
        return data

    def extract(self):
        df_train = pd.read_csv(self.df_train_path)
        df_test = pd.read_csv(self.df_test_path)
        data = self.open_label_mapping()
        label_to_disease = {value: key for key, value in data.items()}

        df_train['label'] = df_train['label'].map(label_to_disease)

        self.df = pd.concat([df_train, df_test])
        self.df = self.df.rename(columns={'label': 'disease','text':'Patient Symptoms'})

        return self.df

    def save(self, path):
        self.df.to_csv(path, index=False)


if __name__ == '__main__':
    extract = Extract('/mnt/sda/hophacks/backend/symptom-disease-dataset/', 'symptom-disease-train-dataset.csv' ,'symptom-disease-test-dataset.csv', 'mapping.json')
    df = extract.extract()
    extract.save('symptom-disease-dataset.csv')