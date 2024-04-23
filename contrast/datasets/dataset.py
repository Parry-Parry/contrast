import random
from torch.utils.data import Dataset
from typing import Any
import json
import pandas as pd
import torch
from typing import Optional, Any
import ir_datasets as irds

from contrast._util import initialise_triples

class TripletDataset(Dataset):
    def __init__(self, 
                 ir_dataset : str,
                 triples : Optional[Any] = None, 
                 teacher_file : Optional[str] = None,
                 num_negatives : int = 0,
                 ) -> None:
        super().__init__()
        self.triples = triples
        for column in 'qid', 'doc_id_a', 'doc_id_b':
            if column not in self.triples.columns: raise ValueError(f"Format not recognised, Column '{column}' not found in triples dataframe")
        self.ir_dataset = irds.load(ir_dataset)
        self.docs = pd.DataFrame(self.ir_dataset.docs_iter()).set_index("doc_id")["text"].to_dict()
        self.queries = pd.DataFrame(self.ir_dataset.queries_iter()).set_index("query_id")["text"].to_dict()

        if self.triples is None: self.triples = initialise_triples(self.ir_dataset)
        if teacher_file: self.teacher = json.load(open(teacher_file, 'r'))

        self.labels = True if teacher_file else False
        self.multi_negatives = True if type(self.triples['doc_id_b'].iloc[0]) == list else False
        if num_negatives > 0 and self.multi_negatives:
            self.triples['doc_id_b'] = self.triples['doc_id_b'].apply(lambda x: random.sample(x, num_negatives))

    def __len__(self):
        return len(self.triples)
    
    def _teacher(self, qid, doc_id, positive=False):
        assert self.labels, "No teacher file provided"
        try: return self.teacher[str(qid)][str(doc_id)] 
        except KeyError: return 0.

    def __getitem__(self, idx):
        item = self.triples.iloc[idx]
        query = self.queries[str(item['qid'])]
        texts = [self.docs[str(item['doc_id_a'])]]

        if self.multi_negatives: texts.extend([self.docs[str(doc)] for doc in item['doc_id_b']])
        else: texts.append(self.docs[item['doc_id_b']])

        if self.labels:
            scores = [self.teacher[str(item['qid'])][str(item['doc_id_a'], True)]]
            if self.multi_negatives: scores.extend([self._teacher(str(item['qid']), str(doc)) for doc in item['doc_id_b']])
            else: scores.append(self._teacher(str(item['qid']), str(item['doc_id_b'])))
            return (query, texts, scores)
        else:
            return (query, texts)