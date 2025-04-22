import os
import sys
import pdb
import json
import numpy as np
import faiss 
from Algorithm.libs.logger.log import get_logger
import Algorithm.libs.config.model_cfgs as cfgs
log_info = get_logger(__name__)
ISLOG=cfgs.ISLOG
ISLOG_common=cfgs.ISLOG_common

class SearchEngine(object):
    def __init__(self, base_feat_lists, base_idx_lists, dims=1024):
        if len(base_idx_lists) > 0:
            base_feat_lists = base_feat_lists
            self._index = faiss.IndexFlatL2(dims)

            self._index.add(np.array(base_feat_lists))

            self._register_labels = base_idx_lists

            if ISLOG_common:
                log_info.info(
                "Faiss search engine load succeed!!! The dims is {}. Total num is {}".format(dims, len(base_idx_lists)))

        else:
            if ISLOG_common:
                log_info.info("No feat register.Total num is {}".format(len(base_idx_lists)))
            self._register_labels = []

    def search(self, query_feat, top_k=10):
        if len(self._register_labels) == 0:
            return [], []
        else:
            dist_list, idx_list = self._index.search(np.array([query_feat]), top_k)
            #print(idx_list)
            #print(dist_list)
            #print(f'idx:{idx_list},dist:{dist_list}')
            # try:
            #     label_idx = [self._register_labels[sort_e_idx] for sort_e_idx in idx_list[0]]
            # except Exception as e:
            #     print(str(e))
            #     print(self._register_labels,idx_list)
            #
            # return label_idx, dist_list
            return idx_list[0],dist_list[0]

    ####
    def rerank(self):
        ## Todo
        pass

