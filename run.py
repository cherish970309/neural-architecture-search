import time
import numpy as np
import pandas as pd
from keras.datasets import fashion_mnist, mnist
from keras.utils import to_categorical
from sklearn.preprocessing import LabelEncoder

import nas as nas
import utils as utils

from metadata.meta_learning import get_mdfile

utils.clean_log()

start = time.time()

data = pd.read_csv('datasets/22.csv')
y = data['label'].values
data.drop('label', axis=1, inplace=True)
x = data.values
x, y = utils.unison_shuffled_copies(x,y)

target_classes = len(np.unique(y))

mdfile = get_mdfile(x,y)

mlpnas = nas.NAS(x, to_categorical(y), target_classes, mdfile)

mlpnas.max_len = 5
mlpnas.cntrl_epochs = 20
mlpnas.mc_samples = 15
mlpnas.hybrid_model_epochs = 15
mlpnas.nn_epochs = 1
mlpnas.nb_final_archs = 10
mlpnas.final_nn_train_epochs = 20
mlpnas.alpha1 = 5
mlpnas.pre_train_epochs = 1000

# make all controller, nn parameters accessible for modification here.
# lstm, nn optimizers.
# lstm loss weights.

sorted_archs = mlpnas.architecture_search()
nastime = time.time()

seqsinorder = [item[0] for item in sorted_archs]
valaccsinorder = [item[1] for item in sorted_archs]
predvalaccsinorder = [item[2] for item in sorted_archs]

best_archs_valacc, best = mlpnas.train_best_architectures(seqsinorder,
						  use_shared_weights=True,
						  earlyStopping=True)
sw_estime = time.time()

best_archs_valacc, best = mlpnas.train_best_architectures(seqsinorder,
						  use_shared_weights=True,
						  earlyStopping=False)
swtime = time.time()

best_archs_valacc, best = mlpnas.train_best_architectures(seqsinorder,
						  use_shared_weights=False,
						  earlyStopping=True)
estime = time.time()
best_archs_valacc, best = mlpnas.train_best_architectures(seqsinorder,
						  use_shared_weights=False,
						  earlyStopping=False)
end = time.time()

utils.logevent()

print("time spent in seconds:")
print("NAS:", nastime - start)
print("sw_es mode training:", sw_estime - nastime)
print("sw mode training:", swtime - sw_estime)
print("es mode training:", estime - swtime)
print("full mode training:", end - estime)
print("total time:", end - start)

event_id = utils.get_latest_event_id()
print("event id:", event_id)