import os
import pickle
videos=os.listdir("/flickr/flickr_dataset_resize/")
videos_name = [v.replace("@","%40") for v in videos]
pickle.dump(videos_name, open("videos_name.pkl","wb"))