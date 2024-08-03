If you want to access data, please open it in Python language with the following code:
import pickle
with open(r'D:\icse2025\data\keyaspect_All.data','rb') as f:
    data_all = pickle.load(f)