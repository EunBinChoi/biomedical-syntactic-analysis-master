# -*- coding: utf-8 -*-

import stanza
import stanza
import pandas as pd
from pandas.core.frame import DataFrame


# 명사 추출 및 바이오 관련 명사 추출할 수 있는 모델을 다운로드하고 파이프라인을 이용해서 가지고 옴
def load_model():

    # 만약 stanza 모델이 없다면 아래의 주석을 통해 다운로드가 필요함
    # stanza.download('en')
    # stanza.download('en', package='genia', processors={'ner': 'jnlpba'})
    # stanza.download('en', package='genia', processors={'ner': 'anatem'})
    # stanza.download('en', package='genia', processors={'ner': 'bc4chemd'})
    # stanza.download('en', package='genia', processors={'ner': 'ncbi_disease'})

    # 아래는 stanza 모델을 파이프라인 이용해서 가지고 오는 코드
    NLP_model_noun = stanza.Pipeline('en') # 일반 명사 추출 모델

    # 아래 모델들은 일반 명사가 아닌 의학적인 용어끼리 분류하기 위한 모델
    NLP_model_JNLPBA = stanza.Pipeline('en', package='genia', processors={'ner': 'jnlpba'}) # PROTEIN, DNA, RNA, CELL 관련 명사 추출 모델
    NLP_model_AnatEM = stanza.Pipeline('en', package='genia', processors={'ner': 'anatem'}) # ANATOMY (기관) 관련 명사 추출 모델
    NLP_model_BC4CHEMD = stanza.Pipeline('en', package='genia', processors={'ner': 'bc4chemd'}) # CHEMICAL 관련 명사 추출 모델
    NLP_model_NCBI_Disease = stanza.Pipeline('en', package='genia', processors={'ner': 'ncbi_disease'}) # DISEASE 관련 명사 추출 모델
    
    
    # 모델을 하나의 리스트로 전달함
    NLP_model_bio_noun = [ NLP_model_JNLPBA, NLP_model_AnatEM,  NLP_model_BC4CHEMD,  NLP_model_NCBI_Disease ]
    return NLP_model_noun, NLP_model_bio_noun


# 크롤링된 데이터 (엑셀 파일)을 가지고 옴 (상용님께서 보내주신 엑셀)
def load_data(filename):
    # 경로 이름에 ‪u202a이 붙는 경우가 있어서 제외하고 가지고 옴
    crawl_data = pd.read_excel(filename.strip("‪u202a"))
    return crawl_data



def extract_all_noun(data, NLP_model_noun, NLP_model_bio_noun):
    # title, key_sentence에 저장된 문장의 의학 명사를 추출하여 리스트로 저장
    bio_noun_title = extract_bio_noun(data, 'title', NLP_model_bio_noun)
    bio_noun_key_sentence = extract_bio_noun(data, 'key_sentence', NLP_model_bio_noun)

    # title, key_sentence에 저장된 문장의 일반 명사를 추출하여 리스트로 저장
    noun_title = extract_noun(data, 'title', NLP_model_noun, bio_noun_title, bio_noun_key_sentence)
    noun_key_sentence = extract_noun(data, 'key_sentence', NLP_model_noun, bio_noun_title, bio_noun_key_sentence)
    return bio_noun_title, bio_noun_key_sentence, noun_title, noun_key_sentence

# 의학 관련 명사 추출
def extract_bio_noun(data, target, NLP_model_bio_noun):
    bio_noun = []
    
    # 크롤링된 데이터를 반복하면서
    for i in range(len(data[target].tolist())):
        bio_noun_tmp_total = []

        # 의학 관련 명사 추출 모델에서 검색되는 명사가 있으면 '명사이름:분류타입'으로 저장
        # 만약에 '명사이름:분류타입'을 대문자끼리 비교한 다음에 일치하는 명사가 있으면 제외 
        # (하나의 논문에 대해 중복되는 명사가 있으면 중복 제외하기 위함)
        for j in range(len(NLP_model_bio_noun)):
            bio_model = NLP_model_bio_noun[j](data[target].tolist()[i])
            bio_noun_tmp = []

            # 모델의 개체를 확인하면서 해당 개체의 명사이름과 분류타입을 하나의 문자열로 저장함
            for ent in bio_model.entities:
                for k in range(len(bio_noun_tmp)):
                    if(ent.text.upper() + ":" + ent.type.upper() == bio_noun_tmp[k].upper()): continue
                else: bio_noun_tmp.append(ent.text + ":" + ent.type)

            # 문자열을 하나의 리스트에 extend 됨
            bio_noun_tmp_total.extend(bio_noun_tmp)

        # 길이가 0일 때는 일반 리스트로 저장 (셋으로 저장할 경우 set()으로 저장됨)
        if(len(bio_noun_tmp_total) == 0): bio_noun.append(bio_noun_tmp_total)
        # 길이가 0이 아닐 때는 셋으로 저장 (중복 제거)
        else: bio_noun.append(set(bio_noun_tmp_total)) 

    return bio_noun # 의학 명사 추출한 리스트 반환


# 일반 명사 추출 
def extract_noun(data, target, NLP_model_noun, bio_noun_title, bio_noun_key_sentence):
    noun = []
    
    # 크롤링 데이터 중 유전자와 타겟 유전자를 저장함
    crawl_data_gene = data['gene'].tolist()
    crawl_data_target = data['target'].tolist()

    # 크롤링된 데이터를 반복하면서
    for i in range(len(data)):
        noun_model = NLP_model_noun(data[target].tolist()[i])
        noun_tmp = []

        # 일반 명사 추출 모델에서 검색되는 명사가 있으면 저장
 
       
        # 하나의 논문에 대해 중복되는 명사가 있으면 중복 제외하기 위해 다음과 같은 과정을 사용함

        # 1) 만약 추출된 단어의 길이가 2 이하이면 제외 (가끔 이상한 로마자나 특수문자가 들어오는 경우가 있어서 해당 경우 제외)
        # 2) 만약 시작 문자가 문자가 아니라 숫자부터 시작하면 문자가 아니므로 제외
        # 3) 만약 크롤링 데이터 (유전자1, 유전자2 (타겟 유전자))랑 동일한 이름을 가진 유전자가 있으면 제외
        # 4) 만약 의학 관련 명사로 추출된 명사가 있으면 제외 (일반 명사 추출 함수이므로)
        
        for sentence in noun_model.sentences:
            for word in sentence.words:

                # 단어의 위치가 명사 위치에 있는지 확인한 후 만약 명사 위치에 있다면
                if(word.xpos in ("NNP", "NN", "NNS")):

                    # 해당 문자를 대문자로 변환 (중복 제거를 위해)
                    word_upper = word.text.upper()
                    if (len(word.text) < 3): continue
                    if (not ('A' <= word_upper <= 'Z')):  continue
                    # if (word_upper in (bio_noun_title[i], \
                    #                 bio_noun_key_sentence[i])): continue
                    if (word_upper in (crawl_data_gene[i].split(':')[0].upper(), \
                                    crawl_data_target[i].split(':')[0].upper())): continue
                  
                    isincluded_in_bio_noun_title = included_bio_noun(i, word_upper, bio_noun_title)
                    if (isincluded_in_bio_noun_title): continue
                    
                    isincluded_in_bio_noun_key_sentence = included_bio_noun(i, word_upper, bio_noun_key_sentence)
                    if (isincluded_in_bio_noun_key_sentence): continue
                    noun_tmp.append(word.text)
        
        if(len(noun_tmp) == 0): noun.append(noun_tmp)
        else: noun.append(set(noun_tmp))

    return noun
    


# 해당 일반 명사가 의학 관련 명사인지 확인
def included_bio_noun(i, word_upper, bio_noun_list):
    included = False
    # 반복문을 돌면서
    for j in range(len(bio_noun_list[i])):
        # {'의학명사:의학명사분류타입', '의학명사:의학명사분류타입', '의학명사:의학명사분류타입' ...} 
        # 반복문을 돌면서 일반 명사로 추출한 단어가 의학 단어로 포함되어있으면 
        if (list(bio_noun_list[i])[j].find(':') != -1):
            left_tmp = list(bio_noun_list[i])[j].split(':')[0]
            if word_upper in left_tmp.upper(): included = True; break

    return included

# 추출한 내용 엑셀에 내보내기
def export_excel(filename, data, noun_title, noun_key_sentence, noun_biomedical_title, noun_biomedical_key_sentence):
    
    data_frame_for_noun_extraction = DataFrame()

    data_frame_for_noun_extraction['pmid'] = data['pmid']
    data_frame_for_noun_extraction['gene'] = data['gene']
    data_frame_for_noun_extraction['target'] = data['target']
    data_frame_for_noun_extraction['noun_title'] = noun_title
    data_frame_for_noun_extraction['noun_key_sentence'] = noun_key_sentence
    data_frame_for_noun_extraction['bio_noun_title'] = noun_biomedical_title
    data_frame_for_noun_extraction['bio_noun_key_sentence'] = noun_biomedical_key_sentence
    
    data_frame_for_noun_extraction.to_excel(filename)


NLP_model_noun, NLP_model_bio_noun = load_model() # load model first

# 크롤링 데이터 읽어옴
data = load_data("‪../../data/20210715/crawling_result.xlsx")
# print(type(data))
# data = load_data("‪./test_with_sample_data/crawling_result_sample.xlsx")

noun_bio_title, noun_bio_key_sentence, noun_title, noun_key_sentence\
= extract_all_noun(data, NLP_model_noun, NLP_model_bio_noun)

export_excel("./noun_extraction.xlsx", 
data, noun_title, noun_key_sentence, noun_bio_title, noun_bio_key_sentence)




