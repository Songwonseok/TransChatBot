

from googletrans import Translator
import json
import re
import requests
import urllib.request
import urllib.parse
from flask import Flask, request
from slack import WebClient
from slack.web.classes import extract_json
from slack.web.classes.blocks import *
from slack.web.classes.elements import *
from slack.web.classes.interactions import MessageInteractiveEvent
from slackeventsapi import SlackEventAdapter
SLACK_TOKEN = 'xoxb-689171290564-694162609175-bxD01DukrTm02hgbNotUzUDU'
SLACK_SIGNING_SECRET = 'a33fc3b244d3917d88402068aaa9962c'


app = Flask(__name__)
# /listening 으로 슬랙 이벤트를 받습니다.
slack_events_adaptor = SlackEventAdapter(SLACK_SIGNING_SECRET, "/listening", app)
slack_web_client = WebClient(token=SLACK_TOKEN)
#각 언어를 key값으로 (구글번역api에 사용되는 값, url)형태에 접근할 수 있다
language_dict = {
  "영어": ['en', 'https://postfiles.pstatic.net/MjAxOTA3MTFfMzMg/MDAxNTYyODI5NjQ2NTYy.cC0',
         'ntPe38bB6qtSqLu8SnZgB29mc1bMuQUmbg7hiAJQg.qrrZQYWel_GbS7Diz_XGbTk',
         '6KzQKifItkxlnSNJETD4g.PNG.dnjstjr7331/미국.png?type=w580'],
  '한국어': ['ko','https://postfiles.pstatic.net/MjAxOTA3MTFfMTU2/MDAxNTYyODI5NjQ2OTYx.L3V',
          'a7qQd_ls2BVAhOjiKa8_65crIqzwv-JPJKzJ2JyUg.MdCnwL-zPCofADDKj-pRzsCshrQ',
          'ob9jxagXO6qWKzowg.PNG.dnjstjr7331/한국.png?type=w580'],
  '일본어': ['ja','https://postfiles.pstatic.net/MjAxOTA3MTFfMjQx/MDAxNTYyODI5NjQ2Nzkx.Stvv',
          'QlC4O0NT4DS1dqRWcqnBzKApjiqaAgzkqW0lbucg.ObEJ9on9thJOdyujDo0hWJHis',
          'jTfGna2AiiVTsqT3k8g.PNG.dnjstjr7331/일본.png?type=w580'],
  '중국어': ['zh-CN','https://postfiles.pstatic.net/MjAxOTA3MTFfMjcg/MDAxNTYyODI5NjQ2OTQw._Po',
          'spie0YW9zY5Ic3uUy0iJ5Kv_QoXuPK8-58BQPaLIg.QPIYGVUjurjIVa4dS5fsivtJQ1i2d',
          'bNcXGYypOT-GAcg.PNG.dnjstjr7331/중국.png?type=w580'],
  '스페인어': ['es', 'https://postfiles.pstatic.net/MjAxOTA3MTFfMTA3/MDAxNTYyODI5NjQ2NTYz.v-C',
           'xtC0RnVqMPEMowWspOzGP9bfAfv49cW1kqwsw8mEg.6DxErVZORhV8fr5UHglA',
           'pQt9mVn2eZOKRRv49gqhksgg.PNG.dnjstjr7331/스페인.png?type=w580'],
  '독일어': ['de', 'https://postfiles.pstatic.net/MjAxOTA3MTFfMjk4/MDAxNTYyODI5NjQ2NTc3.SGW',
          '4f-NoL2s1NXW6TRtNSip7K_tl9vBLTznBh7R0ivgg.EQ8LVxJL_vFxwN5cqpVqG26DQ',
          '82NTkZE-68FeBCMDdYg.PNG.dnjstjr7331/독일.png?type=w580'],
  '프랑스어': ['fr', 'https://postfiles.pstatic.net/MjAxOTA3MTFfNzAg/MDAxNTYyODI5NjQ2ODY0.MY0',
           'ru3LfvaWfV41jHiclZ7qzg7C8nSn9_J4vsdVDv0og.ZqJQO6QsPEscsicCK5IA6jD_gq58',
           'qa9p2lLSdhbLaDcg.PNG.dnjstjr7331/프랑스.png?type=w580'],
  '아랍어': ['ar', 'https://postfiles.pstatic.net/MjAxOTA3MTFfMTcz/MDAxNTYyODI5NjQ2NzQ2.64q',
          '6Ys3wF7IE36iCxDgJRW0JU0NKEXlj8rrQR5ucXLcg.TvTHhFLd-Un5FWVpEEBa7J6C-',
          'amDU5gdPVslxSsLgGgg.PNG.dnjstjr7331/아랍.png?type=w580'],
  '힌디어': ['hi','https://postfiles.pstatic.net/MjAxOTA3MTFfMTAw/MDAxNTYyODI5NjQ2NzY5.gV',
          'DKcdq-vYU1s2g1d8yhAh0SONfWAGzyKarIGzBcB-Ug._jV7IsvbLegF5y_cJMGx66H',
          'T98IkgUpnrOvgBYaHXNgg.PNG.dnjstjr7331/인도.png?type=w580'],
  '이탈리아어': ['it','https://postfiles.pstatic.net/MjAxOTA3MTFfMTU5/MDAxNTYyODI5NjQ2NzQ4.Ns',
            'kpV6VAcPhHhbwHHTsH8GhHXO_MpvW4VbvD-Wwh6xMg.Ia3RWv6E1RjFMKkiid',
            'GzNZR0Pv98Z2Mww8VSKMauANgg.PNG.dnjstjr7331/이태리.png?type=w580'],
   '그리스어': ['el', 'https://postfiles.pstatic.net/MjAxOTA3MTFfMTgx/MDAxNTYyODI5NjQ2NTYy.gN',
           'rzG2GxAk43ePOOXZOByWsjFTEWgtJoAyMtGNi5-4Yg.dDrbeH8mlD1_olZm7l1j-Lb',
           '0ubznnmGpU4BQIGyys5og.PNG.dnjstjr7331/그리스.png?type=w580'],
  '몽골어': ['mn','https://postfiles.pstatic.net/MjAxOTA3MTFfMjgg/MDAxNTYyODI5NjQ2NTYx.7bY',
          '13xLcprpLn3Sb1V1lfiIjmomooqJvqSWGLWnxrzwg.URsauZcoqVFc3XRCxyuQxl0-',
          'eTlFHOyveho1urh7YQUg.PNG.dnjstjr7331/몽골.png?type=w580'],
  '태국어': ['th','https://postfiles.pstatic.net/MjAxOTA3MTFfMjE1/MDAxNTYyODI5NjQ2ODM3.Xm',
          'ByT7hFbg5x1GrMi1Kq1CZ7kEd4vg5ZiH6vW6B9XRgg.E2J4K6vjrpra8RB57upZxyu',
          'uhoQmOLMmaksxum0JNkQg.PNG.dnjstjr7331/태국.png?type=w580'],
  '베트남어': ['vi','https://postfiles.pstatic.net/MjAxOTA3MTFfMjI4/MDAxNTYyODI5NjQ2NTYz.f_pyJ',
           'h9fI2svDFkr8ZNPyB93F0f0sVu8uwLdWoUhwrwg._whVmi3MJQ4YI_L0fy1shdvHuga',
           '0rq0MsFPQHNZFBiQg.PNG.dnjstjr7331/베트남.png?type=w580']
}
#구글 Translator 함수를 소문자로 쓰기 위함
translator = Translator()
#전역변수로 현재 사용중인 번역할 언어와 번역될 언어를 저장
input_lang = []
target_lang = []
stop = []
#블록된 메시지를 보낼 때 사용
def push_message_block(channel, blocks):
    slack_web_client.chat_postMessage(
        channel=channel,
        blocks=extract_json(blocks)
    )
#텍스트 메시지를 보낼 때 사용
def push_message_text(channel, text):
    slack_web_client.chat_postMessage(
        channel=channel,
        text=text
    )
#구글 번역 api
def _google_translate(input_lang, target_lang, text):
    sl = language_dict[input_lang][0]
    tl = language_dict[target_lang][0]
    translated_text = translator.translate(text, src = sl, dest= tl)
    return translated_text.text
#챗봇이 @호출을 받았을 때
@slack_events_adaptor.on("app_mention")
def app_mentioned(event_data):
    global input_lang
    global target_lang
    global stop
    language_list = list(language_dict.keys())
    #이벤트 데이터 객체서 channel과 text 를 저장
    channel = event_data["event"]["channel"]
    text = event_data["event"]["text"]
    #help /들어오는 언어 입력 /변경을 구분하기 위한 정규식 3가지 선언
    help_matches = re.search(r"<@U\w+>\s+(help)",text)
    input_matches = re.search(r"<@U\w+>\s+(\w+)\s+(\w+)", text)
    change_matches = re.search(r"<@U\w+>\s+(#변경|#change)", text)
    stop_matches = re.search(r"<@U\w+>\s+(#그만$)", text)
    #각 정규식에 매칭될 떄
    if help_matches:
        stop = []
        #help메시지를 출력, url 길어서 3부분으로 나눔
        image_url1 = "https://postfiles.pstatic.net/MjAxOTA3MTJfMTI5/MDAxNTYyOTA2OTc4OTA3.Gg"
        image_url2 = "IF9MSZqTj302SYlm25aGdX6hfsQKq1b6FWdR_FwOEg.0uWSsVIG24xi0hPptKpk9H"
        image_url3 = "7VeXou55DSiQYHeoyBCwQg.PNG.dnjstjr7331/메뉴얼2.PNG?type=w580"
        block = ImageBlock(image_url=image_url1+image_url2+image_url3, alt_text="help manual")
        my_blocks = list()
        my_blocks.append(block)
        push_message_block(channel, my_blocks)
    elif input_matches and (input_matches.group(1) in language_list) and (input_matches.group(2) in language_list):
        #현재 입력된 언어가 있으면 #변경부터 하게 하고 없을 경우 입력언어 출력언어를 설정
        if len(input_lang) > 0:
            push_message_text(channel,"우선 '@번역봇 #변경 혹은 #change'를 입력해주세요")
            return
        stop = []
        input_lang.append(input_matches.group(1))
        target_lang.append(input_matches.group(2))
        push_message_text(channel, "현재 {0} --> {1}로 번역하고 있습니다.".format(input_lang[-1], target_lang[-1]))
    elif change_matches:
        #변경을 입력받을 시 현재 입력된 언어들을 초기화 시켜줌
        input_lang = []
        target_lang = []
        push_message_text(channel, "변경하고 싶은 언어로 다시 설정해주세요")
    elif stop_matches:
        #그만둘때
        stop.append("1")
        input_lang = []
        target_lang = []
        push_message_text(channel, "그만두겠습니다.")
        return
    else:
        # 매칭 되지 않는 명령에 대해 도움말을 볼 수 있도록 유도
        push_message_text(channel, "도움말은 @번역봇 help 와 같이 입력하시면 됩니다.")
        return
    return
# @언급이 없는 메시지를 입력받을 때
@slack_events_adaptor.on("message")
def message_pushed(event_data):
    global input_lang
    global target_lang
    global stop
    if len(stop)>0 :
        return
    channel = event_data["event"]["channel"]
    text = event_data["event"]["text"]
    #만약 멘션이라면 실행되지 않도록 return 해줌
    if "<" in text:
        return
    #봇 스스로가 보낸 메시지에 반응하지 않도록 함
    if event_data["event"].get("subtype") != "bot_message":
        #!로 시작된 텍스트만 번역함
        if text.startswith('!'):
            message = _google_translate(input_lang[-1], target_lang[-1], text[1:])
            url_im = ""
            for i in range(1, 4):
                url_im = url_im+language_dict[target_lang[-1]][i]
            block_text = PlainTextObject(text=message)
            block_image = ImageBlock(image_url=url_im, alt_text=target_lang[-1])
            block_entire = ContextBlock(elements=[block_text, block_image])
            push_message_block(channel, [block_entire])
        else:
            push_message_text(channel,"가장 앞에 !를 붙여서 사용해주세요. 자세한 설명은 @번역봇 help 메시지로 볼 수 있습니다." )
            return
@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"
if __name__ == '__main__':
    app.run()
