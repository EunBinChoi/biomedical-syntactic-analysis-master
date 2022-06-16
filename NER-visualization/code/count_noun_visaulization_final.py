# -*- coding: utf-8 -*-

from pandas.core.frame import DataFrame
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pyvis.network import Network
from wordcloud import WordCloud, STOPWORDS

# 엑셀 파일 (count_noun.xlsx)을 읽는 함수
# 가끔씩 경로에 u202a 문자가 들어가서 앞뒤로 strip()
def load_data(filename):
    crawl_data = pd.read_excel(filename.strip("‪u202a"))
    return crawl_data

# 엑셀에 저장된 noun_count, bio_noun_count 열을 읽어서 리스트로 저장해서 각 단어 등장 확률을 구하는 함수
def probability(data):
    # gene = data['gene'].tolist()
    noun_count = data['noun_count'].tolist()
    bio_count = data['bio_noun_count'].tolist()
        
    noun_percent = calculate_percent(noun_count) # 명사의 단어 등장횟수 퍼센트 계산
    bio_percent = calculate_percent(bio_count) # 의학관련 명사의 단어 등장횟수 퍼센트 계산

    return noun_percent, noun_count, bio_percent, bio_count


# 각 단어의 빈도수의 확률 퍼센트(%) 계산 ((각 단어 등장 횟수 / 전체 단어 수) * 100)
def calculate_percent(noun_count):
    noun_percent = []
    
    for noun in noun_count:
        # noun_list = noun.strip('[]').split(', ') 
        # noun_list_int = [int(i) for i in noun_list]
        noun_list_int = convert_str_to_int_list(noun)
        
        total = sum(noun_list_int) # 전체 단어 수 총합
        noun_list_percent = [(int(i) / total) * 100.0 for i in noun_list_int] # 퍼센트 계산
        noun_percent.append(noun_list_percent)

    return noun_percent

# 각 단어의 빈도수 확률 계산 (0 ~ 1 사이의 값 반환) (각 단어 등장 횟수 / 전체 단어 수)
def calculate_prob(noun_count):
    noun_prob = []

    for noun in noun_count:
        # noun_list = noun.strip('[]').split(', ')
        # noun_list_int = [int(i) for i in noun_list]
        noun_list_int = convert_str_to_int_list(noun)
        
        total = sum(noun_list_int) # 전체 단어 수 총합
        noun_list_prob = [int(i) / total for i in noun_list_int] # 확률 계산
        noun_prob.append(noun_list_prob)

    return noun_prob

# 엑셀에 데이터를 저장할 경우 '[각 단어 등장 횟수, 각 단어 등장 횟수, ...]'로 저장되기 때문에 
# 문자열의 양쪽을 '[]'으로 strip()
# 그리고 문자열을 리스트로 반환해주기 위해서 ', '으로 split()
def convert_str_to_int_list(str):
    list = str.strip('[]').split(', ')
    list_int = [int(i) for i in list]

    return list_int

# bar graph 그리는 함수
def barplot_noun(df, figsize, palette, title):
    # 그림 사이즈 설정
    plt.figure(figsize=figsize) 
    
    # x축을 단어, y축을 각 단어 등장횟수를 기준으로 bar graph 저장
    splot = sns.barplot(x='Vocabulary', y='Count', data=df, palette=palette, ci=None)
    
    plt.title(title, fontsize=10)
    plt.xlabel("Vocabulary", size=10)
    plt.xticks(fontsize=10) 
    plt.xticks(rotation=90) # x축에 출력되는 라벨 회전 (글자수가 길기 때문)
    plt.ylabel("Count")
    plt.yticks(fontsize=7)
    
    sns.despine(left=True)        
    splot.grid(False)
    splot.tick_params(bottom=True, left=False)


# network 그리는 함수
def networkplot_noun(df, gene_name, data_type):
    net = Network(height='1000px', width='1400px', bgcolor='#222222', font_color='white')
    row_count = df.shape[0] # 정렬된 dataframe에 행의 수 반환

    for i, word in enumerate(df['Vocabulary'].values):
        net.add_node(i, label=word, size=10, color='#E8E7DC')
    net.add_node(row_count, gene_name, size=20, color='#FCF6AE')

    for i, percent in enumerate(df['Percent'].values):
        net.add_edge(row_count, i, weight=percent, value=10 * percent, title=str(percent) + "%", color='#E8E7DC')

    net.show_buttons(filter_=['physics'])
    net.save_graph("./network/" + "network_" + gene_name + "_" + data_type + ".html")


# word cloud 그리는 함수
def wordcloud_noun(df, figsize, bgcolor, title):
    # 그림 사이즈 설정
    plt.figure(figsize=figsize)

    df_dict = df.to_dict('split')['data']
    df_dict = dict(df_dict) # dataframe to dictionary
    # ‘dict’ (default) : dict like {column -> {index -> value}}
    # ‘list’ : dict like {column -> [values]}
    # ‘series’ : dict like {column -> Series(values)}
    # ‘split’ : dict like {‘index’ -> [index], ‘columns’ -> [columns], ‘data’ -> [values]}
    # ‘records’ : list like [{column -> value}, … , {column -> value}]
    # ‘index’ : dict like {index -> {column -> value}}
    
    wc = WordCloud(background_color=bgcolor, stopwords=STOPWORDS, \
        width=1000,height=1000, \
        normalize_plurals=False, collocations=True). \
            generate_from_frequencies(df_dict) # 빈도수를 기반으로 word cloud 생성
    
    plt.title(title, fontsize=13)
    plt.xlabel("Percent of Vocabulary", size=10)
    plt.xticks(fontsize=10)
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    return wc

# pie graph 그리는 함수
def pieplot_noun(figsize, voca, percent, title): 
    explode = [0] * len(percent)
    explode[0] = 0.2 # 파이 중에서 가장 퍼센트가 높은 단어를 보여주기 위해서 explode
    colors = ['#F07888', '#DF85F6', '#AA85F6', '#859BF6', \
    '#85D0F6', '#87EFD3', '#87EF95', '#FAF385', '#FAC885', '#FA9985']

    plt.figure(figsize=figsize)
    plt.pie(x=percent, labeldistance=1.1,\
            explode=explode, \
            autopct="%.1f%%", labels=voca, colors=colors, shadow=True, startangle=90,\
            wedgeprops={'linewidth':0.1, 'edgecolor':'black'})
    plt.title(title, fontsize=13)

# sns barplot 그리는 함수
def snsplot_noun(df, figsize, palette, title):
    plt.figure(figsize=figsize)
    splot = sns.barplot(x='Percent', y='Vocabulary', data=df, palette=palette, ci=None)
    for p in splot.patches:
        splot.annotate("%.3f%%" % p.get_width(), xy=(p.get_width(), p.get_y()+p.get_height()/2),
        xytext=(3, 0), textcoords='offset points', ha="left", va="center", size=7)

    plt.title(title, fontsize=10)
    plt.xlabel("Percent of Vocabulary", size=10)
    plt.xticks(fontsize=10)
    
    plt.ylabel(None)
    plt.yticks(fontsize=7)
    sns.despine(left=True)        
    splot.grid(False)
    splot.tick_params(bottom=True, left=False)


# 다양한 시각화 자료를 시각화 할 수 있는 함수

# 함수 매개변수 지정 방법은 아래와 같음
# data: 엑셀에서 읽은 데이터
# num: noun_count, bio_count, noun_percent, bio_percent
# data_type: noun, bio_noun
# num_type: Percent, Count
# chart_type: bar_horizontal, pie, wordcloud, histogram, network
# drop_method: 출력할 때 최대 몇 개만 지정할 것인지 아닌지 (ratio, count, nodrop)
# plot_ratio: 출력할 최대 행 퍼센트 지정 (예시: 상위 10%)
# plot_element_max: 출력할 최대 행 개수 지정 (예시: 상위 10개)
# palette: 그래프의 색깔 지정 (색깔은 seaborn이 팔렛트로 지정)
# title: 그래프에 출력할 제목
def visualizaiton_noun(data, num, data_type = 'noun', num_type = 'Percent', \
        chart_type = "bar_horizontal", drop_method = "nodrop", plot_ratio = 1, plot_element_max = 0,\
        palette = "GnBu_d", title = ""):
   
    gene = data['gene'].tolist()
    noun_list = data[data_type].tolist()
    
    for i, noun_vocab in enumerate(noun_list):        
        noun_target =  noun_vocab.strip('[]').split("', '")
        noun_target = [noun.strip('\'') for noun in noun_target]
        noun_target_sp = []

        for noun in noun_target:
            # 단어가 길어지게 될 경우에 너무 길어지면 시각화 자료에서 보여지기 어렵기 때문에 (...)으로 생략
            # 리스트로 split된 명사 단위를 다시 문자열로 반환 (join)
            if(data_type == "noun"):
                if(len(noun) >= 20): 
                    noun_target_sp.append("".join(noun.split(' ')[0:1]) + "...")
                else: 
                    noun_target_sp.append(noun)
            
            elif(data_type ==  "bio_noun"):
                # 의학용어인 경우 데이터 저장을 의학관련명사:분류타입 (DNA, RNA, CHEMICAL, DISEASE... 등등)으로 저장
                # 그래서 일단 분류타입을 제외하고 의학관련명사만 확인하기 위해 ':'으로 split하고 split된 것을 기준으로 0번 인덱스만 반환
                # 그리고 의학관련명사가 너무 길 경우에는 (...)으로 생략
                # 리스트로 split된 명사 단위를 다시 문자열로 반환 (join)
                if(len(noun.split(':')[0]) >= 20): 
                    noun_target_sp.append("".join(noun.split(':')[0].split(' ')[0:1]) + "...")
                else:
                    noun_target_sp.append(noun.split(':')[0])
        
        # num_type ("Count", "Percent")에 따라서 시각화할 때 기준을 지정할 수 있음
        if (num_type == "Count"):
            data_dict_count = {'Vocabulary' : noun_target_sp, num_type: convert_str_to_int_list(num[i])}
            df  = pd.DataFrame(data_dict_count)
            # sort_values(): 내림차순으로 정렬
            # reset_index(): 이전 인덱스를 열로 추가되지 않게 함
            df = df.sort_values([num_type], ascending=False).reset_index(drop=True)

        elif (num_type == "Percent"):
            data_dict = {'Vocabulary' : noun_target_sp, num_type : num[i]}
            df  = pd.DataFrame(data_dict)
            # sort_values(): 내림차순으로 정렬
            # reset_index(): 이전 인덱스를 열로 추가되지 않게 함
            df = df.sort_values([num_type], ascending=False).reset_index(drop=True)
    
        row_count = df.shape[0] # 정렬된 dataframe의 행의 수 반환
        # drop_method ("ratio", "count")에 따라서 시각화할 때 최상위 비율/개수를 지정할 수 있음
        if (drop_method == "ratio"):
            plot_ratio = min(plot_ratio, 1) # plot_ratio는 1을 넘을 수 없음
            row_count = int(row_count * plot_ratio)

        elif(drop_method == "count"):
            row_count = min(row_count, plot_element_max) 
            # plot_element_max는 최상위 몇 개를 지정할 것인지 넣어줌 (여기서는 10)
            
        # dataframe의 행 몇 개를 drop 시킴
        df = df.drop(df.index[row_count:])
        
        
        if (chart_type == "bar_horizontal"):
            # 행의 수가 몇 개인지에 따라서 그림 사이즈를 다르게 함
            if (row_count >= 110):  figsize = (5, 70)
            elif (row_count >= 90): figsize = (5, 50)
            elif (row_count >= 70): figsize = (5, 30)
            elif (row_count >= 50): figsize = (5, 25)
            elif (row_count >= 30): figsize = (6, 17)
            elif (row_count >= 10): figsize = (6, 10)
            elif (row_count >= 5):  figsize = (6, 8)
            else: figsize = (5, 5)
            snsplot_noun(df, figsize, palette, title + " For " + gene[i]) 
        
        elif(chart_type == "pie"):
            # pie 그래프의 행과 열을 추출함 (dataframe 지원하지 않음)
            voca_dropped = df.iloc[:,0].values # 행 추출
            percent_dropped = df.iloc[:,1].values # 열 추출

            figsize = (7, 7)
            pieplot_noun(figsize, voca_dropped, percent_dropped, title + " For " + gene[i])
        
        elif(chart_type == "wordcloud"):
            figsize = (5, 5)
            
            wordcloud_bl = wordcloud_noun(df, figsize, bgcolor="black", title=title + " For " + gene[i])
            wordcloud_wh = wordcloud_noun(df, figsize, bgcolor="white", title=title + " For " + gene[i])
        
        elif(chart_type == "histogram"):
            # 그래프 그림을 행/열의 수가 몇 개인지에 따라서 사이즈를 지정함
            figsize_x = max(df.shape[0] * 0.2, 5)
            figsize_y =  max(df.shape[1] * 2, 5)
            figsize=(figsize_x, figsize_y)
            barplot_noun(df, figsize, palette, title + " For " + gene[i])

        elif (chart_type == "network"):
            networkplot_noun(df, gene[i], data_type)

        else: return

        # word cloud 파일로 저장
        if(chart_type == "wordcloud"):
            wordcloud_bl.to_file("./" + chart_type + "_bl" + "/" + \
                str(i) + "_" + gene[i]  + "_" + data_type + ".png")
            wordcloud_wh.to_file("./" + chart_type + "_wh" + "/" + \
                str(i) + "_" + gene[i]  + "_" + data_type + ".png")
            
        # network는 html 파일로 저장하기 떄문에 (내부 함수 내에서) pass
        elif(chart_type == "network"): pass    

        # 다른 그래프는 그대로 저장
        else:
            plt.gcf().subplots_adjust(left=0.15)
            plt.tight_layout()

            plt.savefig("./" + chart_type + "/" + \
                str(i) + "_" + gene[i]  + "_" + data_type + ".png")
            
            
            # many numbers of figure are not closed in runtime
            # try to close figure after save it
            plt.close()


# 그림 파일로 저장하기 때문에 엑셀로 추출하는 함수는 사용하지 않음
# def export_excel(filename, data, noun_prob, noun_percent, bio_prob, bio_percent):
#     data_count = DataFrame()
#     data_count['gene'] = data['gene']
    
#     # deduplicate noun
#     data_count['noun'] = data['noun']
#     data_count['noun_count'] = data['noun_count']
#     data_count['noun_prob'] = noun_prob
#     data_count['noun_percent'] = noun_percent
    

#     # deduplicate bio noun
#     data_count['bio_noun'] = data['bio_noun']
#     data_count['bio_noun_count'] = data['bio_noun_count']
#     data_count['bio_noun_prob'] = bio_prob
#     data_count['bio_noun_percent'] = bio_percent

#     data_count.to_excel(filename)


data = load_data("‪./count_noun.xlsx")
noun_percent, noun_count, bio_percent, bio_count = probability(data)



# plot pie chart only 10 labels (사용)
visualizaiton_noun(data=data, num=noun_count, data_type="noun", \
    chart_type="pie", num_type="Count", drop_method="count", plot_element_max=10,\
    title="[General Word Frequencey]\n (%, pie graph) \n")

visualizaiton_noun(data=data, num=bio_count, data_type="bio_noun", \
    chart_type="pie", num_type="Count", drop_method="count", plot_element_max=10,\
    title="[Biomedical Word Frequencey]\n (%, pie graph) \n")


# plot pie chart only 10% (추출된 단어 수가 많아서 오버랩이 많이 됨 (사용 안함))
# visualizaiton_noun(data=data, num=noun_percent, chart_type="pie", drop_method="ratio", plot_ratio= 0.1)
# visualizaiton_noun(data=data, num=bio_percent, chart_type="pie", drop_method="ratio", plot_ratio= 0.1)


# plot sns bar graph (사용)
visualizaiton_noun(data, num=noun_percent, data_type="noun",  chart_type="bar_horizontal",\
     palette="flare", title="[General Word Frequency]\n (%, horizontal bar graph) \n")

visualizaiton_noun(data, num=bio_percent, data_type="bio_noun", chart_type="bar_horizontal",\
     palette="GnBu_d", title="[Biomedical Word Frequency]\n (%, horizontal bar graph) \n")



# histogram (bar_plot) (사용)
visualizaiton_noun(data, num=noun_count, data_type="noun", num_type='Count', \
    chart_type="histogram", palette="flare", title="[General Word Count]\n (histogram) \n")
visualizaiton_noun(data, num=bio_count, data_type="bio_noun", num_type='Count',\
    chart_type="histogram",palette="GnBu_d", title="[Biomedical Word Count]\n (histogram) \n")


 
# plot word cloud (사용)
visualizaiton_noun(data=data, num=noun_count, data_type="noun", \
    num_type='Count', chart_type="wordcloud", title="[General Word Count]\n (wordcloud) \n")
visualizaiton_noun(data=data, num=bio_count, data_type="bio_noun", \
    num_type='Count', chart_type="wordcloud", title="[Biomedical Word Count]\n (wordcloud) \n")


# network (pyviz.network) (사용)
visualizaiton_noun(data, num=noun_percent, data_type="noun", num_type='Percent', \
    chart_type="network", title="[General Word Percent]\n (%, network) \n")
visualizaiton_noun(data, num=bio_percent, data_type="bio_noun", num_type='Percent',\
    chart_type="network", title="[Biomedical Word Percent]\n (%, network) \n")

 