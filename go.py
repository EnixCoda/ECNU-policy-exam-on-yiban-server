# coding: utf-8
import random
import os
import sys
import json
import re
import urllib
import time
import requests

poster = requests.session()


def login(username, password):
    login_url = 'https://www.yiban.cn/login/doLoginAjax'
    user = {
        'account': username,
        'password': password,
        'captcha': None
    }
    poster.post(login_url, user)

    check_login_url = 'http://www.yiban.cn/ajax/my/getLogin'
    check_login_response_content = poster.post(check_login_url).content
    # check login
    try:
        if not json.loads(check_login_response_content)['data']['isLogin']:
            return False
        else:
            return check_login_response_content
    except Exception, e:
        print e
        return False


def get_paper(paper_list_url):
    response_papers = poster.post(paper_list_url)
    papers = response_papers.content.replace('   ', ' ')
    if papers.find('请填写真实信息，以便为您匹配合适题库') > -1:
        return False
    # pick the first paper, which contains 7 input elements as a bundle
    inputs = re.findall(r'<input type="hidden" id="(.*?)" name="(.*?)" value="(.*?)" />', papers)
    paper_info = {}
    count_input = 0
    for dom_input in inputs:
        key = dom_input[0]
        if key.find('_') > -1:
            key = key.split('_')[1]
        value = dom_input[2]
        paper_info[key] = value
        count_input += 1
        if count_input == 7:
            break
    get_paper_url = 'http://www.yiban.cn/t/student/showsj'
    # request the paper with the inputs we got
    response_paper_content = poster.post(
        get_paper_url,
        paper_info,
        headers={
            'Referer': 'http://www.yiban.cn/t/student/showtk',
            'Host': 'www.yiban.cn'
        }).content
    return response_paper_content


def load_answer():
    """
    answers are stored in the file 'answer.json'
    """
    if not os.path.exists('answer.json'):
        with open('answer.json', 'w') as answers_file:
            answers_file.write('{}')
    with open('answer.json', 'r') as answers_file:
        answers = json.load(answers_file)
    return answers


def save_answer(answers):
    with open('answer.json', 'w') as answers_file:
        json.dump(answers, answers_file)


def make_answer(key, answers):
    def ABCDto1234(ABCD):
        return '-ABCDEFGHIJKLMN'.find(ABCD)
    """
    from key:  12345_dan_key / 12345_duo_key
    to:        12345_dan     / 12345_duo[]
    """
    question_id = key.split('_')[0]
    made_answer = []
    key_in_form = ''
    if key.find('dan') > -1:
        key_in_form = key.replace('_key', '')
    if key.find('duo') > -1:
        key_in_form = key.replace('_key', '[]')
    if (question_id in answers):
        for answer in answers[question_id].split(','):
            made_answer.append([key_in_form, ABCDto1234(answer)])
    else:
        # default answer is 'A', answer for result-analyse
        made_answer.append([key_in_form, ABCDto1234('A')])
    return made_answer


def answer_paper(paper):
    questions = {}
    dom_question_inputs = re.findall(r'<input class="ep_radio" type="(checkbox|radio)" name="(.*?)"', paper)
    for dom_input in dom_question_inputs:
        [_, input_name] = dom_input
        if not input_name in questions:
            questions[input_name] = 0

    answer = load_answer()
    found_answers = []
    count_match = 0
    for key in questions:
        question_id = key.split('_')[0]
        if question_id in answer:
            count_match += 1
        found_answers += make_answer(key, answer)
    # make sure the user gets a good score
    if count_match / len(questions) < 60 / 100:
        return False

    paper_info = ''
    for answer in found_answers:
        paper_info += '&' + urllib.urlencode({answer[0]: answer[1]})
    if paper_info[0] == '&':
        paper_info = paper_info[1:]

    # answer time is calc on yiban, to prevent being banned, wait for a while before submitting
    submit_url = 'http://www.yiban.cn/t/student/submitsj'
    # comment out the line bellow to skip waiting
    time_to_sleep = random.randint(15 * 60, 25 * 60)
    print('gonna sleep for ' + str(time_to_sleep) + ' seconds')
    time.sleep(time_to_sleep)
    response_score = poster.post(
        submit_url,
        paper_info,
        headers={
            'Accept': '*/*',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'http://www.yiban.cn',
            'Referer': 'http://www.yiban.cn/t/student/showsj',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Length': str(len(paper_info))
        }
    ).content
    return response_score


def analyse_result():
    """
    the more times we try,
    the higher score we get
    """
    page_number = 1
    wrong_answers_page_url = 'http://www.yiban.cn/t/student/showmisinfo/name/' + urllib.quote('2017年2月形势与政策测验') + '/courseid/1618'
    not_last_page = True
    answers = load_answer()
    while not_last_page:
        wrong_answers_page_content = poster.get(wrong_answers_page_url + '/page/' + str(page_number)).content
        page_number += 1
        question_id_groups = re.findall(r'href="javascript:void\(0\)" id="(\d+)_collect"', wrong_answers_page_content)
        answer_groups = re.findall(r'正确答案：<b>(.*?)</b>', wrong_answers_page_content)
        i = 0
        while i < len(question_id_groups):
            question_id = question_id_groups[i]
            if question_id not in answers:
                answers[question_id] = answer_groups[i]
            i += 1
        disabled_next_page_button = re.findall(r'<a href="javascript:void\(0\);" class="e_previous no_previous"><em class="em_icon"></em>下一页</a>', wrong_answers_page_content)
        if len(disabled_next_page_button) > 0:
            not_last_page = False
    save_answer(answers)
    return True


def main():
    if len(sys.argv) == 3:
        username, password = sys.argv[1], sys.argv[2]
    else:
        return

    login_response_content = login(username, password)
    if login_response_content is False:
        print 'FAKE'
        return

    try:
        nav = json.loads(login_response_content)['data']['subNav']
        url_to_tk = re.findall(r'http://www\.yiban\.cn/t', nav)
        if len(url_to_tk) != 1:
            print 'UNREGISTERED'
            return
        paper_list_url = 'http://www.yiban.cn/t/'
        paper = get_paper(paper_list_url)
        if not paper:
            print 'UNREGISTERED'
            return
    except Exception, e:
        print 'UNREGISTERED'
        return

    # answer paper
    response_score = answer_paper(paper)
    if response_score:
        response_score = json.loads(response_score)
    if not ('status' in response_score and response_score['status'] == 'true'):
        print 'ANSWER_FAILED'
        return

    analyse_result()
    print 'SUCCESS'
    return


if __name__ == '__main__':
    main()
