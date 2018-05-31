# -*- coding: utf-8 -*-
# Created on Mon Mar 18 2018 15:39:50
# Author: WuLC
# EMail: liangchaowu5@gmail.com

###############################################################
# Wand(Weak and) algorithm for searching query-related document
# more details can be obtained from https://tinyurl.com/ya6cglyy
###############################################################

import heapq

UB = {"t0":0.5,"t1":1,"t2":2,"t3":3,"t4":4} #upper bound of term's value
LAST_ID = 999999999999 # a large number, larger than all the doc id in the inverted index
THETA = 2 # theta, threshold for chechking whether to calculate the relevence between query and doc
TOPN = 3 #max result number 


class WAND:
    def __init__(self, InvertIndex):
        """init inverted index and necessary variable"""
        self.result_list = [] #result list
        self.inverted_index = InvertIndex #InvertIndex: term -> docid1, docid2, docid3 ...
        self.current_doc = 0
        self.current_inverted_index = {} #posting
        self.query_terms = []
        self.sort_terms = []
        self.threshold = THETA
        self.last_id = LAST_ID


    def __init_query(self, query_terms):
        """init variable with query"""
        self.current_doc = 0
        self.current_inverted_index = {}
        self.query_terms = []
        self.sort_terms = []
        
        for term in query_terms:
            if term in self.inverted_index:  # terms may not appear in inverted_index
                doc_id = self.inverted_index[term][0]
                self.query_terms.append(term)
                self.current_inverted_index[term] = [doc_id, 0] #[ docid, index ]
                self.sort_terms.append([doc_id, term])

   
    def __pick_term(self, pivot_index):
        """select the term before pivot_index in sorted term list
         paper recommends returning the term with max idf, here we just return the firt term,
         also return the index of the term instead of the term itself for speeding up"""
        return 0


    def __find_pivot_term(self):
        """find pivot term"""
        score = 0
        for i in range(len(self.sort_terms)):
            score += UB[self.sort_terms[i][1]]
            if score >= self.threshold:
                return [self.sort_terms[i][1], i] #[term, index]
        return [None, len(self.sort_terms)]


    def __iterator_invert_index(self, change_term, docid, pos):
        """find the new_doc_id in the doc list of change_term such that new_doc_id >= docid,
        if no new_doc_id satisfy, the self.last_id"""
        doc_list = self.inverted_index[change_term]
        # new_doc_id, new_pos = self.last_id, len(doc_list)-1 # the case when new_doc_id not exists
        for i in range(pos, len(doc_list)):
            if doc_list[i] >= docid:   # since doc_list contains self.last_id, this inequation will always be satisfied
                new_pos = i
                new_doc_id = doc_list[i]
                break
        return [new_doc_id, new_pos]

    
    def __advance_term(self, change_index, doc_id ):
        """change the first doc of term self.sort_terms[change_index] in the current inverted index
        return whether the action succeed or not"""
        change_term = self.sort_terms[change_index][1]
        pos = self.current_inverted_index[change_term][1]
        new_doc_id, new_pos = self.__iterator_invert_index(change_term, doc_id, pos)
        self.current_inverted_index[change_term] = [new_doc_id, new_pos]
        self.sort_terms[change_index][0] = new_doc_id

    def __next(self):
        while True:
            self.sort_terms.sort() #sort terms by doc id
            
            pivot_term, pivot_index = self.__find_pivot_term() #find pivot term > threshold
            
            if pivot_term == None: #no more candidate
                return None
            
            pivot_doc_id = self.current_inverted_index[pivot_term][0]
            
            if pivot_doc_id == self.last_id: # no more candidate
                return None
            
            if pivot_doc_id <= self.current_doc:
                change_index = self.__pick_term(pivot_index)
                self.__advance_term(change_index, self.current_doc + 1)
            else:
                first_doc_id = self.sort_terms[0][0]
                if pivot_doc_id == first_doc_id:
                    self.current_doc = pivot_doc_id
                    return self.current_doc # return the doc for fully calculating
                else:
                    # pick all preceding term instead of just one, then advance all of them to pivot
                    change_index = 0
                    while change_index < pivot_index:
                        self.__advance_term(change_index, pivot_doc_id)
                        change_index += 1
            # print(self.sort_terms, self.current_doc, pivot_doc_id)


    def __insert_heap(self, doc_id, score):
        if len(self.result_list) < TOPN:
            heapq.heappush(self.result_list, (score, doc_id))
        else:
            heapq.heappushpop(self.result_list, (score, doc_id))


    def __calculate_doc_relevence(self, docid):
        """fully calculate relevence between doc and query"""
        score = 0
        for term in self.query_terms:
            if docid in self.inverted_index[term]:
                score += UB[term]
        return score


    def perform_query(self, query_terms):
        self.__init_query(query_terms)
        while True:
            candidate_docid = self.__next()
            if candidate_docid == None:
                break
            #insert candidate_docid to heap
            print('candidata doc', candidate_docid)
            full_doc_score = self.__calculate_doc_relevence(candidate_docid)
            self.__insert_heap(candidate_docid, full_doc_score)
            print("result list ", self.result_list)
        return self.result_list


if __name__ == "__main__":
    testIndex = {}
    testIndex["t0"] = [1, 3, 26, LAST_ID]
    testIndex["t1"] = [1, 2, 4, 10, 100, LAST_ID]
    testIndex["t2"] = [2, 3, 6, 34, 56, LAST_ID]
    testIndex["t3"] = [1, 4, 5, 23, 70, 200, LAST_ID]
    testIndex["t4"] = [5, 14, 78, LAST_ID]
    
    w = WAND(testIndex)
    final_result = w.perform_query(["t0", "t1", "t2", "t3", "t4"])
    print("=================final result=======================")
    for i in reversed(range(len(final_result))):
        print("doc {0}, relevence score {1}".format(final_result[i][1], final_result[i][0]))