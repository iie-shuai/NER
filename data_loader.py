# -*- coding: utf-8 -*-
"""
@Time ： 2020/5/15 13:07
@Auth ： ds
@File ：data_loader.py
@IDE ：PyCharm
"""

import codecs
import data_utils

def load_sentences(path):
    """
    加载数据集，每行至少包含一个汉字和一个标记，句子间以空格分隔
    :param path: 数据加载路径
    :return: 返回句子集合
    """
    #存放句子集合
    sentences = []

    #存放每个句子
    sentence = []

    for line in codecs.open(path,'r',encoding='utf-8'):
        #去掉头尾空格
        line = line.strip()
        if not line:
            #句子读到结尾
            if len(sentence)>0:
                sentences.append(sentence)
                sentence = []
        else:
            if line[0] == " ":
                continue
            else:
                #空格分隔汉字和标记
                word = line.split()
                assert len(word) >= 2
                sentence.append(word)
    if len(sentence) > 0:
        sentences.append(sentence)
    return sentences

def update_tag_scheme(sentences, tag_scheme):
    """
    更新为BIOES编码
    :param sentences:
    :param tag_scheme:
    :return:
    """
    for i, s in enumerate(sentences):
        tags = [w[-1] for w in s]
        #检查是否是BIO编码
        if not data_utils.check_bio(tags):
            s_str = "\n".join(" ".join(w) for w in s)
            raise Exception("输入的句子应为BIO编码，请检查输入句子%i:\n%s" %(i,s_str))

        if tag_scheme == "BIO":
            for word, new_tag in zip(s, tags):
                word[-1] = new_tag

        if tag_scheme == "BIOES":
            new_tags = data_utils.bio_to_bioes(tags)
            for word, new_tag in zip(s, new_tags):
                word[-1] = new_tag

        else:
            raise Exception("非法目标编码")

def word_mapping(sentences):
    """
    构建字典
    :param sentences:
    :return:
    """
    word_list = [[x[0] for x in s] for s in sentences]
    dico = data_utils.create_dico(word_list)
    dico['<PAD>'] = 10000001
    dico['<UNK>'] = 10000000
    word_to_id, id_to_word = data_utils.create_mapping(dico)
    return dico, word_to_id, id_to_word

def tag_mapping(sentences):
    """
    构建标签字典
    :param sentences:
    :return:
    """
    tag_list = [[x[1] for x in s] for s in sentences]
    dico = data_utils.create_dico(tag_list)
    tag_to_id, id_to_tag = data_utils.create_mapping(dico)
    return dico, tag_to_id, id_to_tag

def prepare_dataset(sentences, word_to_id, tag_to_id, train=True):
    """
    数据预处理，返回list其实包含
    -word_list
    -word_id_list
    -word char indexs
    -tag_id_list
    :param sentences:
    :param word_to_id:
    :param tag_to_id:
    :param train:
    :return:
    """
    none_index = tag_to_id['O']

    data = []
    for s in sentences:
        word_list = [ w[0] for w in s]
        word_id_list = [word_to_id[w if w in word_to_id else '<UNK>'] for w in word_list]
        segs = data_utils.get_seg_features("".join(word_list))
        if train:
            tag_id_list = [tag_to_id[w[-1]] for w in s]
        else:
            tag_id_list = [none_index for w in s]
        data.append([word_list, word_id_list, segs,tag_id_list])

    return data


if __name__ == "__main__":
    path = "data/ner.dev"
    sentences = load_sentences(path)
    update_tag_scheme(sentences, "BIOES")
    _, word_to_id, id_to_word = word_mapping(sentences)
    _, tag_to_id, id_to_tag = tag_mapping(sentences)
    dev_data = prepare_dataset(sentences, word_to_id, tag_to_id)
    data_utils.BatchManager(dev_data, 120)
    print("load_sentences")