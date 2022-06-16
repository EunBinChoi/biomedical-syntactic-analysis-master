# -*- coding: utf-8 -*-

from pandas.core.frame import DataFrame
import pandas as pd
import copy 


# noun_extraction.py 파일에서 추출한 명사 엑셀 파일 로드
def load_data(filename):
    crawl_data = pd.read_excel(filename.strip("‪u202a"))
    return crawl_data


# 여기서 동일 유전자 (gene)를 검색했을 때 나올 수 있는 명사를 모두 하나의 리스트로 담음 
# (다른 논문이라고 하더라도 동일 gene이면 같은 리스트에 담음)

# noun_title, noun_key_sentence 두 리스트를 병합
# bio_noun_title, bio_noun_key_sentence 두 리스트를 병합
def merge(data):
    gene = data['gene'].tolist()
    noun_title = data['noun_title'].tolist()
    noun_key_sentence = data['noun_key_sentence'].tolist()
    bio_noun_title = data['bio_noun_title'].tolist()
    bio_noun_key_sentence = data['bio_noun_key_sentence'].tolist()
    

    noun_sp_i_li = []
    bio_noun_sp_i_li = []
    noun_sp_i_li_by_gene =[]
    bio_noun_sp_i_li_by_gene = []
    noun_gene = []

    gene_i = gene[0]
    noun_gene.append(gene[0])
    for i in range(len(data)):
        if(gene_i != gene[i]):
            noun_gene.append(gene[i])
            if(len(noun_sp_i_li) != 0): noun_sp_i_li_by_gene.append(noun_sp_i_li)
            if(len(bio_noun_sp_i_li) != 0): bio_noun_sp_i_li_by_gene.append(bio_noun_sp_i_li)   
            noun_sp_i_li = []
            bio_noun_sp_i_li = []

        # noun_title, noun_key_sentence, noun_bio_title, noun_bio_key_sentence을 엑셀로 추출했을 때
        # 하나의 문자열로 {'단어', '단어', '단어', ...}로 정의되거나 문자열이 없을 경우에는 []로 정의됨 
        # ({}이나 []을 문자열에서 앞 뒤 strip())
        gene_i = gene[i]
        noun_strip_title = noun_title[i].strip('{}').strip('[]')
        noun_strip_key_sentence = noun_key_sentence[i].strip('{}').strip('[]')
        if (len(noun_strip_title) > 0 and len(noun_strip_key_sentence) > 0):
            noun_i = noun_strip_title + ", " + noun_strip_key_sentence
        elif (len(noun_strip_title) == 0):
            noun_i = noun_strip_key_sentence
        elif (len(noun_strip_key_sentence) == 0):
            noun_i = noun_strip_title


        bio_noun_strip_title = bio_noun_title[i].strip('{}').strip('[]')
        bio_noun_strip_key_sentence = bio_noun_key_sentence[i].strip('{}').strip('[]')
        if (len(bio_noun_strip_title) > 0 and len(bio_noun_strip_key_sentence) > 0):
            bio_noun_i = bio_noun_strip_title + ", " + bio_noun_strip_key_sentence
        elif (len(bio_noun_strip_title) == 0):
            bio_noun_i = bio_noun_strip_key_sentence
        elif (len(noun_strip_key_sentence) == 0):
            bio_noun_i = bio_noun_strip_title


        # 단어와 단어 사이에는 ', '가 있어서 이를 기준으로 split()
        noun_sp_i = noun_i.split(', ')
        bio_noun_sp_i = bio_noun_i.split(', ')
        

        # split()해서 명사 단어와 의학 명사를 리스트에 담음
        for j in range(len(noun_sp_i)):
            # if(len(noun_sp_i[j].strip("'")) != 0): 
                noun_sp_i_li.append(noun_sp_i[j].strip("'"))

        for j in range(len(bio_noun_sp_i)):
            # if(len(noun_bio_sp_i[j].strip("'")) != 0): 
                bio_noun_sp_i_li.append(bio_noun_sp_i[j].strip("'"))

    
    noun_sp_i_li_by_gene.append(noun_sp_i_li)
    bio_noun_sp_i_li_by_gene.append(bio_noun_sp_i_li)  
  
    return noun_gene, noun_sp_i_li_by_gene, bio_noun_sp_i_li_by_gene
    

# 하나의 유전자에 중복된 의학 명사 카운트
# 그냥 리스트 merge하면 다음과 같은 문제가 생김
# 유전자 이름 [유전자A, 유전자A, 유전자B, 유전자B, 유전자A, 유전자A, 유전자C, 유전자C] => [유전자A, 유전자B, 유전자C] (deduplicate ~~ 함수)
# 유전자 이름 카운트 [1, 1, 1, 1, 1, 1, 1, 1] => [4, 2, 2] (count ~~ 함수)

# 일반 명사도 동일한 문제가 발생함
# 명사 이름 [명사A, 명사A, 명사B, 명사B, 명사A, 명사A, 명사C, 명사C] => [명사A, 명사B, 명사C] (deduplicate ~~ 함수)
# 명사 이름 카운트 [1, 1, 1, 1, 1, 1, 1, 1] => [4, 2, 2] (count ~~ 함수)


def count_bio_noun(bio_noun_sp_i_li_by_gene):
    bio_noun_count_by_gene = []

    # 반복문을 돌면서
    for i in range(len(bio_noun_sp_i_li_by_gene)):
        bio_noun_count_by_gene_tmp = []
        bio_noun_count = 0
        for j in range(len(bio_noun_sp_i_li_by_gene[i])):
            bio_noun_count = 0
            
            for k in range(len(bio_noun_sp_i_li_by_gene[i])):
                # 비교할 때 분류 타입은 보지 않기 위해서 :을 기준으로 split()
                # 분류 타입 제외하고 만약에 앞의 유전자 이름이 같거나 서로 포함관계면 제외
                bio_split_for_compare_j = bio_noun_sp_i_li_by_gene[i][j].split(':')[0].upper()
                bio_split_for_compare_k = bio_noun_sp_i_li_by_gene[i][k].split(':')[0].upper()

                if ((bio_noun_sp_i_li_by_gene[i][j].upper() == bio_noun_sp_i_li_by_gene[i][k].upper()) \
                    or (bio_split_for_compare_j == bio_split_for_compare_k)) \
                    or ((bio_split_for_compare_j in bio_split_for_compare_k or \
                    (bio_split_for_compare_k in bio_split_for_compare_j))):
                        bio_noun_count += 1
    
            if(bio_noun_count != 0): bio_noun_count_by_gene_tmp.append(bio_noun_count)
        bio_noun_count_by_gene.append(bio_noun_count_by_gene_tmp)

    return bio_noun_count_by_gene

def count_noun(noun_sp_i_li_by_gene):
    noun_count_by_gene = []
    for i in range(len(noun_sp_i_li_by_gene)):
        noun_count_by_gene_tmp = []
        noun_count  = 0

        # print("noun_sp_i_li_by_gene[i]", noun_sp_i_li_by_gene[i])
        for j in range(len(noun_sp_i_li_by_gene[i])):
            noun_count  = 0

            # 두 문자열을 대문자로 변환했을 때 같으면 제거
            for k in range(len(noun_sp_i_li_by_gene[i])):
                if (noun_sp_i_li_by_gene[i][j].upper() == noun_sp_i_li_by_gene[i][k].upper()): 
                    noun_count += 1

            if(noun_count != 0): noun_count_by_gene_tmp.append(noun_count)
        noun_count_by_gene.append(noun_count_by_gene_tmp)
                
    return noun_count_by_gene



# 의학 명사 리스트에 중복 제거 [유전자A, 유전자A] => [유전자A]
def deduplicate_bio_noun(bio_noun_sp_i_li_by_gene, bio_noun_count_by_gene):
    bio_noun_sp_i_li_by_gene_set = copy.deepcopy(list(bio_noun_sp_i_li_by_gene))
    bio_noun_count_by_gene_set = copy.deepcopy(list(bio_noun_count_by_gene))


    # 전체 리스트를 돌면서
    for i in range(len(bio_noun_sp_i_li_by_gene_set)):
        # 중복을 제거하기 위한 코드
        for j in range(len(bio_noun_sp_i_li_by_gene_set[i])):
            for k in range(len(bio_noun_sp_i_li_by_gene_set[i])-1, j, -1):
                # 비교할 때 분류 타입은 보지 않기 위해서 :을 기준으로 split()
                # 분류 타입 제외하고 만약에 앞의 유전자 이름이 같거나 서로 포함관계면 제외
                bio_split_for_compare_j = list(bio_noun_sp_i_li_by_gene_set[i])[j].split(':')[0].upper()
                bio_split_for_compare_k = list(bio_noun_sp_i_li_by_gene_set[i])[k].split(':')[0].upper()
                
                # 두 문자열을 대문자로 변환했을 때 만약 동일하거나 문자열의 일부에 포함되는 관계라면 제거
                if((list(bio_noun_sp_i_li_by_gene_set[i])[j].upper() \
                    == bio_noun_sp_i_li_by_gene[i][k].upper()) or \
                    (bio_split_for_compare_j == bio_split_for_compare_k) or \
                    ((bio_split_for_compare_j in bio_split_for_compare_k )or \
                    (bio_split_for_compare_k in bio_split_for_compare_j))):
                        bio_noun_sp_i_li_by_gene_set[i].remove(bio_noun_sp_i_li_by_gene_set[i][k])
                        bio_noun_count_by_gene_set[i].remove(bio_noun_count_by_gene_set[i][k])

    return  bio_noun_sp_i_li_by_gene_set, bio_noun_count_by_gene_set

# 명사 리스트에 중복 제거
def deduplicate_noun(noun_sp_i_li_by_gene, noun_count_by_gene):
    noun_sp_i_li_by_gene_set = copy.deepcopy(list(noun_sp_i_li_by_gene))
    noun_count_by_gene_set = copy.deepcopy(list(noun_count_by_gene))

    # 전체 리스트를 돌면서
    for i in range(len(noun_sp_i_li_by_gene_set)):
        # 중복을 제거하기 위한 코드
        for j in range(len(noun_sp_i_li_by_gene_set[i])):
            for k in range(len(noun_sp_i_li_by_gene_set[i])-1, j, -1):

                # 두 문자열을 대문자로 변환했을 때 같으면 제거
                if(noun_sp_i_li_by_gene_set[i][j].upper() == noun_sp_i_li_by_gene_set[i][k].upper()):
                    noun_sp_i_li_by_gene_set[i].remove(noun_sp_i_li_by_gene_set[i][k])
                    noun_count_by_gene_set[i].remove(noun_count_by_gene_set[i][k])

   
    return noun_sp_i_li_by_gene_set, noun_count_by_gene_set
    
# 엑셀로 데이터 내보내기
def export_excel(filename, noun_gene, \
noun_sp_i_li_by_gene_set, bio_noun_sp_i_li_by_gene_set, noun_count_by_gene_set, bio_noun_count_by_gene_set):
    data_frame_for_count_noun = DataFrame()
    data_frame_for_count_noun['gene'] = noun_gene
    data_frame_for_count_noun['noun'] = noun_sp_i_li_by_gene_set
    data_frame_for_count_noun['bio_noun'] = bio_noun_sp_i_li_by_gene_set
    data_frame_for_count_noun['noun_count'] = noun_count_by_gene_set
    data_frame_for_count_noun['bio_noun_count'] = bio_noun_count_by_gene_set
    
    data_frame_for_count_noun.to_excel(filename)


# data = load_data("‪./crawling_result_noun_extraction_with_stanza_final_ver2.0.xlsx")

data = load_data("‪./noun_extraction.xlsx")


noun_gene, noun_sp_i_li_by_gene, bio_noun_sp_i_li_by_gene = merge(data)
bio_noun_count_by_gene = count_bio_noun(bio_noun_sp_i_li_by_gene)
noun_count_by_gene = count_noun(noun_sp_i_li_by_gene)

bio_noun_sp_i_li_by_gene_set, bio_noun_count_by_gene_set\
    = deduplicate_bio_noun(bio_noun_sp_i_li_by_gene,  bio_noun_count_by_gene)
noun_sp_i_li_by_gene_set, noun_count_by_gene_set\
    = deduplicate_noun(noun_sp_i_li_by_gene, noun_count_by_gene)

export_excel("./count_noun.xlsx", noun_gene, \
   noun_sp_i_li_by_gene_set, bio_noun_sp_i_li_by_gene_set, noun_count_by_gene_set, bio_noun_count_by_gene_set
)
# /Users/gennect_3/Desktop/stanza/data/20210715



