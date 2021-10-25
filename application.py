from flask import Flask, request,jsonify
from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta
import xmltodict
import urllib.request
import requests
import json


app = Flask(__name__)



@app.route('/api/seoulCorona', methods=['POST'])
def seoulCorona():
    body = request.get_json()
    print(body)
    url = 'http://openapi.seoul.go.kr:8088/594e6c44786a68393132324d436c7973/json/TbCorona19CountStatusJCG/1/10/'
    response = urllib.request.urlopen(url)
    result=response.read().decode("utf-8")
    body_json=json.loads(result)
    
    city = body["action"]["params"]["자치구"]
    total_list = body_json['TbCorona19CountStatusJCG']['row']
    today = total_list[0]
    
    total_city = today[city]
    today_city = today[city+"ADD"]
    total_city = "{:,}".format(int(total_city))
    
    city_hangeul = body["action"]["detailParams"]["자치구"]['origin']
    if city_hangeul[-1] != "구":
        city_hangeul = city_hangeul + '구'

    today_city_int=int(today_city)

    day=0
    average_sum=0
    while day <= 9:
        num=int(total_list[day][city+"ADD"])
        average_sum=average_sum+num
        day+=1
    average=round(average_sum/10)
    print(average)

    if today_city_int > average*1.2:
        text= "\"위험\""
    elif today_city_int <average*0.5:
        text="\"안전\""
    else:
        text="\"주의\""
    print(today_city)
    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": f"{city_hangeul}의 전체 확진자 수는 {total_city}명 입니다.\n{city_hangeul}의 금일 확진자 수는 {today_city}명 입니다.\n{city_hangeul}의 10일간의 평균 확진자수는 {average}명이며,\n외출난이도는 {text}입니다."
                        
                    }
                }
            ]
        }
    }
@app.route('/api/koreaCorona', methods=['POST'])
def koreaCorona():
    body = request.get_json()
    print(body)
    global covid_level

    input_k_city = body["action"]["params"]["시도"]

    today = date.today()
    days = timedelta(days=-1)
    dataday = today+days
    dataday = dataday.strftime('%Y%m%d')

    url = 'http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19SidoInfStateJson?serviceKey=h327OuruPqwMMgLZ5kmrI2I6i2ORzZcmBZpFecofBV%2Bp8KGrSC1VOgKlv5OmAxgNc2Ri7afVgSl%2FW19yh8Z94Q%3D%3D&pageNo=1&numOfRows=10&startCreateDt='+dataday
    response = urllib.request.urlopen(url)
    result=response.read().decode("utf-8")
    results_to_json = xmltodict.parse(result)
    data = json.loads(json.dumps(results_to_json))
    
    url = 'https://www.data.go.kr/tcs/dss/selectHistAndCsvData.do?publicDataPk=15089317&publicDataDetailPk=uddi%3A23f5d02f-0047-46c8-a938-defadc2ab47c&url=%2Ftcs%2Fdss%2FselectHistAndCsvData.do'
    response = urllib.request.urlopen(url)
    result=response.read().decode("utf-8")
    results_to_json = xmltodict.parse(result)
    data_2 = json.loads(json.dumps(results_to_json))

    for i in range(19):
        if input_k_city == data["response"]["body"]["items"]["item"][i]['gubun']:
            total_k_city = data["response"]["body"]["items"]["item"][i]['defCnt']
            add_k_city = data["response"]["body"]["items"]["item"][i]['incDec']

    for i in range(1, 18):
        if input_k_city == data_2["div"]["div"][1]["div"]["table"]["tr"][i]["td"][1]["#text"]:
            covid_level = data_2["div"]["div"][1]["div"]["table"]["tr"][i]["td"][2]["#text"]
            level_plus = data_2["div"]["div"][1]["div"]["table"]["tr"][i]["td"][3]["#text"]

    if input_k_city == "강원" or input_k_city == "제주" or input_k_city == "경기":
        input_k_city = input_k_city + "도"

    total_k_city = "{:,}".format(int(total_k_city))
    add_k_city = "{:,}".format(int(add_k_city))

    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": f"{input_k_city}의 총 확진자 수는 {total_k_city}명 입니다. \n{input_k_city}의 오늘 확진자 수는 {add_k_city}명 입니다."
                    }
                },
                {
                    "simpleText": {
                        "text": f"{input_k_city}의 거리두기 단계는 {covid_level}단계 입니다. \n*추가정보*\n{level_plus}"
                    }
                }
                
            ],
             "quickReplies": [
                  {
        "messageText":f"{covid_level}단계기준 규제정보",
        "action": "message",
        "label": f"{input_k_city}의 거리두기 규범조회"
      }
    ]
        }
    }

@app.route('/api/coronaRules', methods=['POST'])
def coronaRules():
    body = request.get_json()
    print(body)
    place_Typet = body["action"]["params"]["규제정보"]

    if place_Typet == "1모임" or place_Typet == "모임1":
        textt= "모임인원의 1단계 거리두기 수칙은 다음과 같습니다.\n방역수칙 준수\n(인원제한없음)"
        
    elif place_Typet=="1종교시설" or place_Typet == "종교시설1":
        textt="해당장소의 1단계 거리두기 수칙은 다음과 같습니다.\n수용인원의 50% (좌석 한 칸 띄우기)\n모임/행사, 식사, 숙박 자제\n500인 이상 모임·행사 시 지자체 사전승인"
        
    elif place_Typet=="1식당" or place_Typet=="식당1" or place_Typet=="1카페" or place_Typet=="카페1":
        textt="해당장소의 1단계 거리두기 수칙은 다음과 같습니다.\n테이블간 1m거리두기 또는 좌석/테이블 한 칸 띄우기 또는 테이블 간 칸막이 설치\n(50㎡이상 시설)\n운영시간 제한×"
        
    elif place_Typet=="1pc방" or place_Typet=="pc방1":
        textt="해당장소의 1단계 거리두기 수칙은 다음과 같습니다.\n좌석 띄우기없음\n운영시간 제한×"
        
    elif place_Typet=="1노래방" or place_Typet=="노래방1":
        textt="해당장소의 1단계 거리두기 수칙은 다음과 같습니다.\n시설면적 6㎡ 당 1명\n운영시간 제한×\n시설 내 음식섭취 금지"  
        
    elif place_Typet=="1학교" or place_Typet == "학교1":
        textt="해당장소의 1단계 거리두기 수칙은 다음과 같습니다.\n기본 방역수칙 준수 및 전면등교 가능(1~2단계)\n※ 단계 조정 시 학교는 일주일 준비기간 부여, 단 단계 상향 시에는 신속 조정(교육부)"
        
    elif place_Typet=="1독서실" or place_Typet=="독서실1" or place_Typet=="1스터디카페" or place_Typet=="스터디카페1":
        textt="해당장소의 1단계 거리두기 수칙은 다음과 같습니다.\n좌석 한칸 띄우기(칸막이 있는 경우 제외)(1~4단계)\n운영시간 제한×"
        
    elif place_Typet=="1오락실" or place_Typet=="오락실1":
        textt="해당장소의 1단계 거리두기 수칙은 다음과 같습니다.\n시설면적 6㎡ 당 1명\n운영시간 제한×"
        
    elif place_Typet=="1실내체육시설" or place_Typet=="실내체육시설1":
        textt="해당장소의 1단계 거리두기 수칙은 다음과 같습니다.\n시설면적 6㎡ 당 1명(체육도장, GX운동 시설은 4㎡당 1명)\n운영시간 제한×"     
        
    elif place_Typet=="1목욕탕" or place_Typet == "목욕탕1":
        textt="해당장소의 1단계 거리두기 수칙은 다음과 같습니다.\n시설면적 6㎡ 당 1명\n운영시간 제한×"
        
    elif place_Typet=="1유흥시설" or place_Typet=="유흥시설1" or place_Typet=="1술집" or place_Typet=="술집1":
        textt="해당장소의 1단계 거리두기 수칙은 다음과 같습니다.\n시설면적 6㎡ 당 1명(클럽, 나이트 8㎡당 1명)\n운영시간 제한×\n(감성주점, 헌팅포차 추가조치) 노래금지 및 객석 외 춤추기 금지 (1~3단계)"
        
    elif place_Typet=="1장례식" or place_Typet=="장례식1" or place_Typet=="1결혼식" or place_Typet=="결혼식1":
        textt="해당장소의 1단계 거리두기 수칙은 다음과 같습니다.\n4㎡ 당 1명"
        
    elif place_Typet=="1마트" or place_Typet=="마트1" or place_Typet=="1상점" or place_Typet=="상점1"or place_Typet=="1백화점" or place_Typet=="백화점1":
        textt="해당장소의 1단계 거리두기 수칙은 다음과 같습니다.\n운영시간 제한×"
        
    elif place_Typet=="1영화관" or place_Typet=="영화관1" or place_Typet=="1공연장" or place_Typet=="공연장1":
        textt="해당장소의 1단계 거리두기 수칙은 다음과 같습니다.\n좌석 띄우기없음\n운영시간 제한×\n상영관, 공연장 내 음식섭취 금지"


    res = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": textt
                    }
                }
            ]
        }
    }

    # 답변 전송
    return jsonify(res)

@app.route('/api/coronaRules2', methods=['POST'])
def coronaRules2():
    body = request.get_json()
    print(body)
    place_Type = body["action"]["params"]["규제정보둘"]

    if place_Type == "2모임" or place_Type == "모임2":
        text="모임인원의 2단계 거리두기 수칙은 다음과 같습니다.\n8명까지 모임 가능\n(9인 이상 사적모임 금지)"

    elif place_Type=="2종교시설" or place_Type == "종교시설2":
        text="해당장소의 2단계 거리두기 수칙은 다음과 같습니다.\n수용인원의 30% (좌석 두 칸 띄우기)\n모임/행사, 식사, 숙박 금지\n실외행사 가능(100인 미만)"
        
    elif place_Type=="2식당" or place_Type=="식당2" or place_Type=="2카페" or place_Type=="카페2":
        text="해당장소의 2단계 거리두기 수칙은 다음과 같습니다.\n테이블간 1m거리두기 또는 좌석/테이블 한 칸 띄우기 또는 테이블 간 칸막이 설치\n(50㎡이상 시설)\n24시이후 포장배달만 허용"
        
    elif place_Type=="2pc방" or place_Type=="pc방2":
        text="해당장소의 2단계 거리두기 수칙은 다음과 같습니다.\n좌석 한 칸 띄우기(칸막이 있는 경우 좌석띄우기 없음)\n운영시간 제한×"
        
    elif place_Type=="2노래방" or place_Type=="노래방2":
        text="해당장소의 2단계 거리두기 수칙은 다음과 같습니다.\n시설면적 8㎡당 1명\n24시이후 운영‧이용제한\n시설 내 음식섭취 금지"       
        
    elif place_Type=="2학교" or place_Type == "학교2":
        text="해당장소의 2단계 거리두기 수칙은 다음과 같습니다.\n기본 방역수칙 준수 및 전면등교 가능(1~2단계)\n※ 단계 조정 시 학교는 일주일 준비기간 부여, 단 단계 상향 시에는 신속 조정(교육부)"
        
    elif place_Type=="2독서실" or place_Type=="독서실2" or place_Type=="2스터디카페" or place_Type=="스터디카페2":
        text="해당장소의 2단계 거리두기 수칙은 다음과 같습니다.\n좌석 한칸 띄우기(칸막이 있는 경우 제외)(1~4단계)\n운영시간 제한×"
        
    elif place_Type=="2오락실" or place_Type=="오락실2":
        text="해당장소의 2단계 거리두기 수칙은 다음과 같습니다.\n시설면적 8㎡ 당 1명\n운영시간 제한×"
        
    elif place_Type=="2실내체육시설" or place_Type=="실내체육시설2":
        text="해당장소의 2단계 거리두기 수칙은 다음과 같습니다.\n시설면적 8㎡당 1명(2~4단계)\n(체육도장, GX운동 시설은 6㎡당 1명)\n(체육도장) 상대방과 직접 접촉이 일어나는 운동(겨루기, 대련, 시합 등) 제한(권고)\n운영시간 제한×" 
        
    elif place_Type=="2목욕탕" or place_Type == "목욕탕2":
        text="해당장소의 2단계 거리두기 수칙은 다음과 같습니다.\n시설면적 8㎡당 1명(2~4단계)\n운영시간 제한×"
        
    elif place_Type=="2유흥시설" or place_Type=="유흥시설2" or place_Type=="2술집" or place_Type=="술집2":
        text="해당장소의 2단계 거리두기 수칙은 다음과 같습니다.\n시설면적 8㎡당 1명(2~3단계)\n(클럽, 나이트 10㎡당 1명/2~3단계)\n24시이후 운영‧이용제한\n(감성주점, 헌팅포차 추가조치) 노래금지 및 객석 외 춤추기 금지 (1~3단계)"
        
    elif place_Type=="2장례식" or place_Type=="장례식2" or place_Type=="2결혼식" or place_Type=="결혼식2":
        text="해당장소의 2단계 거리두기 수칙은 다음과 같습니다.\n 100인 미만 + 4㎡ 당 1명"
        
    elif place_Type=="2마트" or place_Type=="마트2" or place_Type=="2상점" or place_Type=="상점2"or place_Type=="2백화점" or place_Type=="백화점2":
        text="해당장소의 2단계 거리두기 수칙은 다음과 같습니다.\n판촉용 시음,시식, 마스크를 벗는 견본품 제공, 이용자 휴게공간 이용, 집객행사 금지\n운영시간 제한×"
        
    elif place_Type=="2영화관" or place_Type=="영화관2" or place_Type=="2공연장" or place_Type=="공연장2":
        text="해당장소의 2단계 거리두기 수칙은 다음과 같습니다.\동행자 외 좌석 한 칸 띄우기\n운영시간 제한×\n상영관, 공연장 내 음식섭취 금지"


    res = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": text
                    }
                }
            ]
        }
    }

    # 답변 전송
    return jsonify(res)

@app.route('/api/coronaRules3', methods=['POST'])
def coronaRules3():
    body = request.get_json()
    print(body)
    place_Typer = body["action"]["params"]["규제정보셋"]

    if place_Typer == "3모임" or place_Typer == "모임3":
        textr="모임인원의 3단계 거리두기 수칙은 다음과 같습니다.\n4명까지 모임 가능\n(5인 이상 사적모임 금지)"
        
    elif place_Typer=="3종교시설" or place_Typer == "종교시설3":
        textr="해당장소의 3단계 거리두기 수칙은 다음과 같습니다.\n수용인원의 20% (좌석 네 칸 띄우기)\n접종 완료자로만 구성시 30%\n모임/행사, 식사, 숙박 금지\n실외행사 가능(50인 미만)"
        
    elif place_Typer=="3식당" or place_Typer=="식당3" or place_Typer=="3카페" or place_Typer=="카페3":
        textr="해당장소의 3단계 거리두기 수칙은 다음과 같습니다.\n테이블간 1m거리두기 또는 좌석/테이블 한 칸 띄우기 또는 테이블 간 칸막이 설치\n(50㎡이상 시설)\n22시이후 포장배달만 허용"
        
    elif place_Typer=="3pc방" or place_Typer=="pc방3":
        textr="해당장소의 3단계 거리두기 수칙은 다음과 같습니다.\n좌석 한 칸 띄우기(칸막이 있는 경우 좌석띄우기 없음)\n운영시간 제한×"
        
    elif place_Typer=="3노래방" or place_Typer=="노래방3":
        textr="해당장소의 3단계 거리두기 수칙은 다음과 같습니다.\n시설면적 8㎡당 1명\n22시이후 운영‧이용제한\n시설 내 음식섭취 금지"       
        
    elif place_Typer=="3학교" or place_Typer == "학교3":
        textr="해당장소의 3단계 거리두기 수칙은 다음과 같습니다.\n밀집도 1/3~2/3(고등학교 2/3 이내)\n※ 단계 조정 시 학교는 일주일 준비기간 부여, 단 단계 상향 시에는 신속 조정(교육부)"
        
    elif place_Typer=="3독서실" or place_Typer=="독서실3" or place_Typer=="3스터디카페" or place_Typer=="스터디카페3":
        textr="해당장소의 3단계 거리두기 수칙은 다음과 같습니다.\n좌석 한칸 띄우기(칸막이 있는 경우 제외)(1~4단계)\n운영시간 제한×"
        
    elif place_Typer=="3오락실" or place_Typer=="오락실3":
        textr="해당장소의 3단계 거리두기 수칙은 다음과 같습니다.\n시설면적 8㎡ 당 1명\n운영시간 제한×"
        
    elif place_Typer=="3실내체육시설" or place_Typer=="실내체육시설3":
        textr="해당장소의 3단계 거리두기 수칙은 다음과 같습니다.\n시설면적 8㎡당 1명(2~4단계)\n(체육도장, GX운동 시설은 6㎡당 1명)\n(탁구) 시설 내 머무는 시간 최대 2시간 이내 복식경기 및 대회금지, 샤워실 운영금지, 탁구대 간격 2m 유지 및 안내\n(배드민턴, 테니스, 스쿼시 등) 시설 내 머무는 시간 최대 2시간 이내, 샤워실 운영금지 및 안내\n(실내풋살, 실내농구 등) 시설 내 머무는 시간 최대 2시간 이내,, 운동종목별 경기인원의 1.5배(예:실내풋살 15명) 초과 금지, 대회금지, 샤워실 운영금지 및 안내\n(GX류) 음악속도 100~120bpm 유지(고강도 유산소 운동→저강도 또는 유연성 운동으로 대체), 샤워실 운영금지\n(체육도장) 상대방과 직접 접촉이 일어나는 운동(겨루기, 대련, 시합 등) 금지, 샤워실 운영금지\n(피트니스) 러닝머신 속도 6㎞ 이하 유지·안내\n(고강도 유산소 운동→저강도 유산소 운동으로 대체) 샤워실 운영금지\n운영시간 제한×\n(수영장은 22시 운영‧이용제한)\n3단계 샤워실 운영제한 해제" 
        
    elif place_Typer=="3목욕탕" or place_Typer == "목욕탕3":
        textr="해당장소의 3단계 거리두기 수칙은 다음과 같습니다.\n시설면적 8㎡당 1명(2~4단계)\n22시이후 운영‧이용제한"
        
    elif place_Typer=="3유흥시설" or place_Typer=="유흥시설3" or place_Typer=="3술집" or place_Typer=="술집3":
        textr="해당장소의 3단계 거리두기 수칙은 다음과 같습니다.\n시설면적 8㎡당 1명(2~3단계)\n(클럽, 나이트 10㎡당 1명/2~3단계)\n22시이후 운영‧이용제한\n(감성주점, 헌팅포차 추가조치) 노래금지 및 객석 외 춤추기 금지 (1~3단계)"
        
    elif place_Typer=="3장례식" or place_Typer=="장례식3" or place_Typer=="3결혼식" or place_Typer=="결혼식3":
        textr="해당장소의 3단계 거리두기 수칙은 다음과 같습니다.\n50인 미만 + 4㎡ 당 1명\n결혼식의 경우 최대250명까지 가능"
        
    elif place_Typer=="3마트" or place_Typer=="마트3" or place_Typer=="3상점" or place_Typer=="상점3"or place_Typer=="3백화점" or place_Typer=="백화점3":
        textr="해당장소의 3단계 거리두기 수칙은 다음과 같습니다.\n판촉용 시음,시식, 마스크를 벗는 견본품 제공, 이용자 휴게공간 이용, 집객행사 금지\n출입명부 작성‧관리(3,000㎡ 이상 대규모점포)\n운영시간 제한×"
        
    elif place_Typer=="3영화관" or place_Typer=="영화관3" or place_Typer=="3공연장" or place_Typer=="공연장3":
        textr="해당장소의 3단계 거리두기 수칙은 다음과 같습니다.\동행자 외 좌석 한 칸 띄우기\n운영시간 제한×\n상영관, 공연장 내 음식섭취 금지\n(정규공연시설 외 공연)6㎡당 1명+최대 2,000명 이내"


    res = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": textr
                    }
                }
            ]
        }
    }

    # 답변 전송
    return jsonify(res)

@app.route('/api/coronaRules4', methods=['POST'])
def coronaRules4():
    body = request.get_json()
    print(body)
    place_Typef = body["action"]["params"]["규제정보넷"]
   
    if place_Typef == "4모임" or place_Typef == "모임4":
        textf="모임인원의 4단계 거리두기 수칙은 다음과 같습니다.\미접종자는 4명까지 모임 가능\n접종 완료자 포함하여 8인까지 가능"
        
    elif place_Typef=="4종교시설" or place_Typef == "종교시설4":
        textf="해당장소의 4단계 거리두기 수칙은 다음과 같습니다.\n수용인원의 10%(최대99명)\n접종 완료자로만 구성시 20%까지 가능\n모임/행사, 식사, 숙박 금지"
        
    elif place_Typef=="4식당" or place_Typef=="식당4" or place_Typef=="4카페" or place_Typef=="카페4":
        textf="해당장소의 4단계 거리두기 수칙은 다음과 같습니다.\n테이블간 1m거리두기 또는 좌석/테이블 한 칸 띄우기 또는 테이블 간 칸막이 설치\n(50㎡이상 시설)\n22시이후 포장배달만 허용"
        
    elif place_Typef=="4pc방" or place_Typef=="pc방4":
        textf="해당장소의 4단계 거리두기 수칙은 다음과 같습니다.\n좌석 한 칸 띄우기(칸막이 있는 경우 좌석띄우기 없음)\n24시이후 운영‧이용제한"
        
    elif place_Typef=="4노래방" or place_Typef=="노래방4":
        textf="해당장소의 4단계 거리두기 수칙은 다음과 같습니다.\n시설면적 8㎡당 1명\n22시이후 운영‧이용제한\n시설 내 음식섭취 금지"       
        
    elif place_Typef=="4학교" or place_Typef == "학교4":
        textf="해당장소의 4단계 거리두기 수칙은 다음과 같습니다.\n원격수업\n※ 단계 조정 시 학교는 일주일 준비기간 부여, 단 단계 상향 시에는 신속 조정(교육부)"
        
    elif place_Typef=="4독서실" or place_Typef=="독서실4" or place_Typef=="4스터디카페" or place_Typef=="스터디카페4":
        textf="해당장소의 4단계 거리두기 수칙은 다음과 같습니다.\n좌석 한칸 띄우기(칸막이 있는 경우 제외)\n24시이후 운영‧이용제한"
        
    elif place_Typef=="4오락실" or place_Typef=="오락실4":
        textf="해당장소의 4단계 거리두기 수칙은 다음과 같습니다.\n시설면적 8㎡ 당 1명\n22시이후 운영‧이용제한"
        
    elif place_Typef=="4실내체육시설" or place_Typef=="실내체육시설4":
        textf="해당장소의 4단계 거리두기 수칙은 다음과 같습니다.\n시설면적 8㎡당 1명(2~4단계)\n(체육도장, GX운동 시설은 6㎡당 1명)\n(탁구) 시설 내 머무는 시간 최대 2시간 이내 복식경기 및 대회금지, 샤워실 운영금지, 탁구대 간격 2m 유지 및 안내\n(배드민턴, 테니스, 스쿼시 등) 시설 내 머무는 시간 최대 2시간 이내, 샤워실 운영금지 및 안내\n(실내풋살, 실내농구 등) 시설 내 머무는 시간 최대 2시간 이내,, 운동종목별 경기인원의 1.5배(예:실내풋살 15명) 초과 금지, 대회금지, 샤워실 운영금지 및 안내\n(GX류) 음악속도 100~120bpm 유지(고강도 유산소 운동→저강도 또는 유연성 운동으로 대체), 샤워실 운영금지\n(체육도장) 상대방과 직접 접촉이 일어나는 운동(겨루기, 대련, 시합 등) 금지, 샤워실 운영금지\n(피트니스) 러닝머신 속도 6㎞ 이하 유지·안내\n(고강도 유산소 운동→저강도 유산소 운동으로 대체) 샤워실 운영금지\n22시이후 운영‧이용제한" 
        
    elif place_Typef=="4목욕탕" or place_Typef == "목욕탕4":
        textf="해당장소의 4단계 거리두기 수칙은 다음과 같습니다.\n시설면적 8㎡당 1명(2~4단계)\n22시이후 운영‧이용제한"
        
    elif place_Typef=="4유흥시설" or place_Typef=="유흥시설4" or place_Typef=="4술집" or place_Typef=="술집4":
        textf="해당장소의 4단계 거리두기 수칙은 다음과 같습니다.\n집합금지"
        
    elif place_Typef=="4장례식" or place_Typef=="장례식4" or place_Typef=="4결혼식" or place_Typef=="결혼식4":
        textf="해당장소의 4단계 거리두기 수칙은 다음과 같습니다.\n 50인 미만 + 4㎡ 당 1명\n결혼식의 경우 최대250명까지 가능"
        
    elif place_Typef=="4마트" or place_Typef=="마트4" or place_Typef=="4상점" or place_Typef=="상점4"or place_Typef=="4백화점" or place_Typef=="백화점4":
        textf="해당장소의 4단계 거리두기 수칙은 다음과 같습니다.\n판촉용 시음,시식, 마스크를 벗는 견본품 제공, 이용자 휴게공간 이용, 집객행사 금지\n출입명부 작성‧관리(3,000㎡ 이상 대규모점포)\n22시이후 운영‧이용제한"
        
    elif place_Typef=="4영화관" or place_Typef=="영화관4" or place_Typef=="4공연장" or place_Typef=="공연장4":
        textf="해당장소의 4단계 거리두기 수칙은 다음과 같습니다.\n동행자 외 좌석 한 칸 띄우기\n24시이후 운영‧이용제한\n상영관, 공연장 내 음식섭취 금지\n정규공연시설 외 공연금지"


    res = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": textf
                    }
                }
            ]
        }
    }

    # 답변 전송
    return jsonify(res)


@app.route('/api/coronaRulesCh', methods=['POST'])
def coronaRulesCh():
    body = request.get_json()
    print(body)
    place_Typ = body["action"]["params"]["지정된규제정보"]
    
    global tex
    
    if covid_level == "1":
        if place_Typ == "모임":
            tex= "모임인원의 1단계 거리두기 수칙은 다음과 같습니다.\n방역수칙 준수\n(인원제한없음)"
        
        elif place_Typ=="종교시설":
            tex="해당장소의 1단계 거리두기 수칙은 다음과 같습니다.\n수용인원의 50% (좌석 한 칸 띄우기)\n모임/행사, 식사, 숙박 자제\n500인 이상 모임·행사 시 지자체 사전승인"
        
        elif place_Typ=="식당" or  place_Typ=="카페":
            tex="해당장소의 1단계 거리두기 수칙은 다음과 같습니다.\n테이블간 1m거리두기 또는 좌석/테이블 한 칸 띄우기 또는 테이블 간 칸막이 설치\n(50㎡이상 시설)\n운영시간 제한×"
        
        elif place_Typ=="pc방":
            tex="해당장소의 1단계 거리두기 수칙은 다음과 같습니다.\n좌석 띄우기없음\n운영시간 제한×"
        
        elif place_Typ=="노래방":
            tex="해당장소의 1단계 거리두기 수칙은 다음과 같습니다.\n시설면적 6㎡ 당 1명\n운영시간 제한×\n시설 내 음식섭취 금지"  
        
        elif place_Typ=="학교":
            tex="해당장소의 1단계 거리두기 수칙은 다음과 같습니다.\n기본 방역수칙 준수 및 전면등교 가능(1~2단계)\n※ 단계 조정 시 학교는 일주일 준비기간 부여, 단 단계 상향 시에는 신속 조정(교육부)"
        
        elif place_Typ=="독서실" or place_Typ=="스터디카페":
            tex="해당장소의 1단계 거리두기 수칙은 다음과 같습니다.\n좌석 한칸 띄우기(칸막이 있는 경우 제외)(1~4단계)\n운영시간 제한×"
        
        elif place_Typ=="오락실":
            tex="해당장소의 1단계 거리두기 수칙은 다음과 같습니다.\n시설면적 6㎡ 당 1명\n운영시간 제한×"
        
        elif place_Typ=="실내체육시설":
            tex="해당장소의 1단계 거리두기 수칙은 다음과 같습니다.\n시설면적 6㎡ 당 1명(체육도장, GX운동 시설은 4㎡당 1명)\n운영시간 제한×"     
        
        elif place_Typ=="목욕탕":
            tex="해당장소의 1단계 거리두기 수칙은 다음과 같습니다.\n시설면적 6㎡ 당 1명\n운영시간 제한×"
        
        elif place_Typ=="유흥시설" or place_Typ=="술집":
            tex="해당장소의 1단계 거리두기 수칙은 다음과 같습니다.\n시설면적 6㎡ 당 1명(클럽, 나이트 8㎡당 1명)\n운영시간 제한×\n(감성주점, 헌팅포차 추가조치) 노래금지 및 객석 외 춤추기 금지 (1~3단계)"
        
        elif place_Typ=="장례식" or place_Typ=="결혼식":
            tex="해당장소의 1단계 거리두기 수칙은 다음과 같습니다.\n4㎡ 당 1명"
        
        elif place_Typ=="마트" or place_Typ=="상점" or place_Typ=="백화점":
            tex="해당장소의 1단계 거리두기 수칙은 다음과 같습니다.\n운영시간 제한×"
        
        elif place_Typ=="영화관" or place_Typ=="공연장":
            tex="해당장소의 1단계 거리두기 수칙은 다음과 같습니다.\n좌석 띄우기없음\n운영시간 제한×\n상영관, 공연장 내 음식섭취 금지"
    
    elif covid_level == "2":
        if place_Typ == "모임":
            tex= "모임인원의 2단계 거리두기 수칙은 다음과 같습니다.\n8명까지 모임 가능\n(9인 이상 사적모임 금지)"
        
        elif place_Typ=="종교시설":
            tex="해당장소의 2단계 거리두기 수칙은 다음과 같습니다.\n수용인원의 30% (좌석 두 칸 띄우기)\n모임/행사, 식사, 숙박 금지\n실외행사 가능(100인 미만)"
        
        elif place_Typ=="식당" or  place_Typ=="카페":
            tex="해당장소의 2단계 거리두기 수칙은 다음과 같습니다.\n테이블간 1m거리두기 또는 좌석/테이블 한 칸 띄우기 또는 테이블 간 칸막이 설치\n(50㎡이상 시설)\n24시이후 포장배달만 허용"
        
        elif place_Typ=="pc방":
            tex="해당장소의 2단계 거리두기 수칙은 다음과 같습니다.\n좌석 한 칸 띄우기(칸막이 있는 경우 좌석띄우기 없음)\n운영시간 제한×"
            
        elif place_Typ=="노래방":
            tex="해당장소의 2단계 거리두기 수칙은 다음과 같습니다.\n시설면적 8㎡당 1명\n24시이후 운영‧이용제한\n시설 내 음식섭취 금지"  
        
        elif place_Typ=="학교":
            tex="해당장소의 2단계 거리두기 수칙은 다음과 같습니다.\n기본 방역수칙 준수 및 전면등교 가능(1~2단계)\n※ 단계 조정 시 학교는 일주일 준비기간 부여, 단 단계 상향 시에는 신속 조정(교육부)"
        
        elif place_Typ=="독서실" or place_Typ=="스터디카페":
            tex="해당장소의 2단계 거리두기 수칙은 다음과 같습니다.\n좌석 한칸 띄우기(칸막이 있는 경우 제외)(1~4단계)\n운영시간 제한×"
        
        elif place_Typ=="오락실":
            tex="해당장소의 2단계 거리두기 수칙은 다음과 같습니다.\n시설면적 8㎡ 당 1명\n운영시간 제한×"
        
        elif place_Typ=="실내체육시설":
            tex="해당장소의 2단계 거리두기 수칙은 다음과 같습니다.\n시설면적 8㎡당 1명(2~4단계)\n(체육도장, GX운동 시설은 6㎡당 1명)\n(체육도장) 상대방과 직접 접촉이 일어나는 운동(겨루기, 대련, 시합 등) 제한(권고)\n운영시간 제한×" 
        
        elif place_Typ=="목욕탕":
            tex="해당장소의 2단계 거리두기 수칙은 다음과 같습니다.\n시설면적 8㎡당 1명(2~4단계)\n운영시간 제한×"
        
        elif place_Typ=="유흥시설" or place_Typ=="술집":
            tex="해당장소의 2단계 거리두기 수칙은 다음과 같습니다.\n시설면적 8㎡당 1명(2~3단계)\n(클럽, 나이트 10㎡당 1명/2~3단계)\n24시이후 운영‧이용제한\n(감성주점, 헌팅포차 추가조치) 노래금지 및 객석 외 춤추기 금지 (1~3단계)"
        
        elif place_Typ=="장례식" or place_Typ=="결혼식":
            tex="해당장소의 2단계 거리두기 수칙은 다음과 같습니다.\n100인 미만 + 4㎡ 당 1명"
        
        elif place_Typ=="마트" or place_Typ=="상점" or place_Typ=="백화점":
            tex="해당장소의 2단계 거리두기 수칙은 다음과 같습니다.\n판촉용 시음,시식, 마스크를 벗는 견본품 제공, 이용자 휴게공간 이용, 집객행사 금지\n운영시간 제한×"
        
        elif place_Typ=="영화관" or place_Typ=="공연장":
            tex="해당장소의 2단계 거리두기 수칙은 다음과 같습니다.\동행자 외 좌석 한 칸 띄우기\n운영시간 제한×\n상영관, 공연장 내 음식섭취 금지"
       
    elif covid_level == "3":
        if place_Typ == "모임":
            tex="모임인원의 3단계 거리두기 수칙은 다음과 같습니다.\미접종자 4명까지 모임 가능\n접종 완료자 포함10명까지 포함가능"
        
        elif place_Typ=="종교시설":
            tex="해당장소의 3단계 거리두기 수칙은 다음과 같습니다.\n수용인원의 20% (좌석 네 칸 띄우기)\n접종 완료자로만 구성시 30%\n모임/행사, 식사, 숙박 금지\n실외행사 가능(50인 미만)"
        
        elif place_Typ=="식당" or place_Typ=="카페":
            tex="해당장소의 3단계 거리두기 수칙은 다음과 같습니다.\n테이블간 1m거리두기 또는 좌석/테이블 한 칸 띄우기 또는 테이블 간 칸막이 설치\n(50㎡이상 시설)\n24시이후 포장배달만 허용"
        
        elif place_Typ=="pc방":
            tex="해당장소의 3단계 거리두기 수칙은 다음과 같습니다.\n좌석 한 칸 띄우기(칸막이 있는 경우 좌석띄우기 없음)\n운영시간 제한×"
        
        elif place_Typ=="노래방":
            tex="해당장소의 3단계 거리두기 수칙은 다음과 같습니다.\n시설면적 8㎡당 1명\n22시이후 운영‧이용제한\n시설 내 음식섭취 금지"       
        
        elif place_Typ=="학교":
            tex="해당장소의 3단계 거리두기 수칙은 다음과 같습니다.\n밀집도 1/3~2/3(고등학교 2/3 이내)\n※ 단계 조정 시 학교는 일주일 준비기간 부여, 단 단계 상향 시에는 신속 조정(교육부)"
        
        elif place_Typ=="독서실" or place_Typ=="스터디카페":
            tex="해당장소의 3단계 거리두기 수칙은 다음과 같습니다.\n좌석 한칸 띄우기(칸막이 있는 경우 제외)(1~4단계)\n운영시간 제한×"
        
        elif place_Typ=="오락실":
            tex="해당장소의 3단계 거리두기 수칙은 다음과 같습니다.\n시설면적 8㎡ 당 1명\n운영시간 제한×"
        
        elif place_Typ=="실내체육시설":
            tex="해당장소의 3단계 거리두기 수칙은 다음과 같습니다.\n시설면적 8㎡당 1명(2~4단계)\n(체육도장, GX운동 시설은 6㎡당 1명)\n(탁구) 시설 내 머무는 시간 최대 2시간 이내 복식경기 및 대회금지, 샤워실 운영금지, 탁구대 간격 2m 유지 및 안내\n(배드민턴, 테니스, 스쿼시 등) 시설 내 머무는 시간 최대 2시간 이내, 샤워실 운영금지 및 안내\n(실내풋살, 실내농구 등) 시설 내 머무는 시간 최대 2시간 이내,, 운동종목별 경기인원의 1.5배(예:실내풋살 15명) 초과 금지, 대회금지, 샤워실 운영금지 및 안내\n(GX류) 음악속도 100~120bpm 유지(고강도 유산소 운동→저강도 또는 유연성 운동으로 대체), 샤워실 운영금지\n(체육도장) 상대방과 직접 접촉이 일어나는 운동(겨루기, 대련, 시합 등) 금지, 샤워실 운영금지\n(피트니스) 러닝머신 속도 6㎞ 이하 유지·안내\n(고강도 유산소 운동→저강도 유산소 운동으로 대체) 샤워실 운영금지\n운영시간 제한×\n(수영장은 22시 운영‧이용제한)\n3단계 샤워실 운영제한 해제" 
        
        elif place_Typ=="목욕탕":
            tex="해당장소의 3단계 거리두기 수칙은 다음과 같습니다.\n시설면적 8㎡당 1명(2~4단계)\n22시이후 운영‧이용제한"
        
        elif place_Typ=="유흥시설" or place_Typ=="술집":
            tex="해당장소의 3단계 거리두기 수칙은 다음과 같습니다.\n시설면적 8㎡당 1명(2~3단계)\n(클럽, 나이트 10㎡당 1명/2~3단계)\n22시이후 운영‧이용제한\n(감성주점, 헌팅포차 추가조치) 노래금지 및 객석 외 춤추기 금지 (1~3단계)"
        
        elif place_Typ=="장례식" or place_Typ=="결혼식":
            tex="해당장소의 3단계 거리두기 수칙은 다음과 같습니다.\n50인 미만 + 4㎡ 당 1명\n결혼식의 경우 최대250명"
        
        elif place_Typ=="마트" or place_Typ=="상점" or place_Typ=="백화점":
            tex="해당장소의 3단계 거리두기 수칙은 다음과 같습니다.\n판촉용 시음,시식, 마스크를 벗는 견본품 제공, 이용자 휴게공간 이용, 집객행사 금지\n출입명부 작성‧관리(3,000㎡ 이상 대규모점포)\n운영시간 제한×"
        
        elif place_Typ=="영화관" or place_Typ=="공연장":
            tex="해당장소의 3단계 거리두기 수칙은 다음과 같습니다.\동행자 외 좌석 한 칸 띄우기\n운영시간 제한×\n상영관, 공연장 내 음식섭취 금지\n(정규공연시설 외 공연)6㎡당 1명+최대 2,000명 이내"
        
    elif covid_level == "4":
        
        if place_Typ == "모임":
            tex="모임인원의 4단계 거리두기 수칙은 다음과 같습니다.\n18시 이후 2명까지 모임 가능\n(3인 이상 사적모임 금지)"
        
        elif place_Typ =="종교시설":
            tex="해당장소의 4단계 거리두기 수칙은 다음과 같습니다.\n수용인원의 10%(최대99명)\n접종 완료자로만 구성시 20%까지 가능\n모임/행사, 식사, 숙박 금지"
        
        elif place_Typ=="식당" or place_Typ=="카페":
            tex="해당장소의 4단계 거리두기 수칙은 다음과 같습니다.\n테이블간 1m거리두기 또는 좌석/테이블 한 칸 띄우기 또는 테이블 간 칸막이 설치\n(50㎡이상 시설)\n22시이후 포장배달만 허용"
        
        elif place_Typ=="pc방":
            tex="해당장소의 4단계 거리두기 수칙은 다음과 같습니다.\n좌석 한 칸 띄우기(칸막이 있는 경우 좌석띄우기 없음)\n22시이후 운영‧이용제한"
        
        elif place_Typ=="노래방":
            tex="해당장소의 4단계 거리두기 수칙은 다음과 같습니다.\n시설면적 8㎡당 1명\n22시이후 운영‧이용제한\n시설 내 음식섭취 금지"       
        
        elif place_Typ=="학교":
            tex="해당장소의 4단계 거리두기 수칙은 다음과 같습니다.\n원격수업\n※ 단계 조정 시 학교는 일주일 준비기간 부여, 단 단계 상향 시에는 신속 조정(교육부)"
        
        elif place_Typ=="독서실" or place_Typ=="스터디카페":
            tex="해당장소의 4단계 거리두기 수칙은 다음과 같습니다.\n좌석 한칸 띄우기(칸막이 있는 경우 제외)\n24시이후 운영‧이용제한"
        
        elif place_Typ=="오락실":
            tex="해당장소의 4단계 거리두기 수칙은 다음과 같습니다.\n시설면적 8㎡ 당 1명\n22시이후 운영‧이용제한"
        
        elif place_Typ=="실내체육시설":
            tex="해당장소의 4단계 거리두기 수칙은 다음과 같습니다.\n시설면적 8㎡당 1명(2~4단계)\n(체육도장, GX운동 시설은 6㎡당 1명)\n(탁구) 시설 내 머무는 시간 최대 2시간 이내 복식경기 및 대회금지, 샤워실 운영금지, 탁구대 간격 2m 유지 및 안내\n(배드민턴, 테니스, 스쿼시 등) 시설 내 머무는 시간 최대 2시간 이내, 샤워실 운영금지 및 안내\n(실내풋살, 실내농구 등) 시설 내 머무는 시간 최대 2시간 이내,, 운동종목별 경기인원의 1.5배(예:실내풋살 15명) 초과 금지, 대회금지, 샤워실 운영금지 및 안내\n(GX류) 음악속도 100~120bpm 유지(고강도 유산소 운동→저강도 또는 유연성 운동으로 대체), 샤워실 운영금지\n(체육도장) 상대방과 직접 접촉이 일어나는 운동(겨루기, 대련, 시합 등) 금지, 샤워실 운영금지\n(피트니스) 러닝머신 속도 6㎞ 이하 유지·안내\n(고강도 유산소 운동→저강도 유산소 운동으로 대체) 샤워실 운영금지\n22시이후 운영‧이용제한" 
        
        elif place_Typ=="목욕탕":
            tex="해당장소의 4단계 거리두기 수칙은 다음과 같습니다.\n시설면적 8㎡당 1명(2~4단계)\n22시이후 운영‧이용제한"
        
        elif place_Typ=="유흥시설" or place_Typ=="술집":
            tex="해당장소의 4단계 거리두기 수칙은 다음과 같습니다.\n집합금지"
        
        elif place_Typ=="장례식" or place_Typ=="결혼식":
            tex="해당장소의 4단계 거리두기 수칙은 다음과 같습니다.\n 50인 미만 + 4㎡ 당 1명"
        
        elif place_Typ=="마트" or place_Typ=="상점" or place_Typ=="백화점":
            tex="해당장소의 4단계 거리두기 수칙은 다음과 같습니다.\n판촉용 시음,시식, 마스크를 벗는 견본품 제공, 이용자 휴게공간 이용, 집객행사 금지\n출입명부 작성‧관리(3,000㎡ 이상 대규모점포)\n22시이후 운영‧이용제한"
        
        elif place_Typ=="영화관" or place_Typ=="공연장":
            tex="해당장소의 4단계 거리두기 수칙은 다음과 같습니다.\n동행자 외 좌석 한 칸 띄우기\n24시이후 운영‧이용제한\n상영관, 공연장 내 음식섭취 금지\n정규공연시설 외 공연금지"


    res = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": tex
                    }
                }
            ]
        }
    }

    # 답변 전송
    return jsonify(res)

@app.route('/api/seoulCheck', methods=['POST'])
def seoulCheck():
    body = request.get_json()
    print(body)
    url = 'https://ncv.kdca.go.kr/restApi/traffic/?cid=naver&key=19acaddba0774badb8de6deb17f0eecc'
    response = urllib.request.urlopen(url)
    result=response.read().decode("utf-8")
    body_json=json.loads(result)

    list_check = []
    sort_check = []
    sort_name = []
    congestion = []
    city = body["action"]["params"]["검사소위치"]
    city = city.split()
    gu_name = city[0]
    seoul_list = body_json["seoul"]["body"]
    for i in range(len(seoul_list)):
        if gu_name == seoul_list[i]["COT_GU_NAME"]:
            list_check.append(seoul_list[i])

    for i in range(len(list_check)):
        if list_check[i]["COT_THEME_SUB_ID"] == "1":
            sort_check.append(list_check[i])
            congestion.append("보통 (30분 이내 검사가능)")
    for i in range(len(list_check)):
        if list_check[i]["COT_THEME_SUB_ID"] == "2":
            sort_check.append(list_check[i])
            congestion.append("붐빔 (60분 내외 검사가능)")
    for i in range(len(list_check)):
        if list_check[i]["COT_THEME_SUB_ID"] == "3":
            sort_check.append(list_check[i])
            congestion.append("혼잡 (검사시간 90분 이상 소요예정)")
    for i in range(len(list_check)):
        if list_check[i]["COT_THEME_SUB_ID"] == "43":
            sort_check.append(list_check[i])
            congestion.append("혼잡도 조사중")
    for i in range(len(list_check)):
        if list_check[i]["COT_THEME_SUB_ID"] == "7":
            sort_check.append(list_check[i])
            congestion.append("소독 등 잠시중단")
    for i in range(len(sort_check)):
        sort_name.append(sort_check[i]["COT_CONTS_NAME"])
    for i in range(4):
        sort_name.append("")
        congestion.append("")

    return {
      "version": "2.0",
      "template": {
        "outputs": [
          {
            "listCard": {
              "header": {
                "title": f"{gu_name} 근처 선별검사소 목록"
              },
              "items": [
                {
                  "title": f"{sort_name[0]}",
                  "description": f"{congestion[0]}",
                  "link": {
                    "web": f"https://map.kakao.com/?map_type=TYPE_MAP&q={sort_name[0]}"
                  }
                },
                {
                  "title": f"{sort_name[1]}",
                  "description": f"{congestion[1]}",
                  "link": {
                    "web": f"https://map.kakao.com/?map_type=TYPE_MAP&q={sort_name[1]}"
                  }
                },
                {
                  "title": f"{sort_name[2]}",
                  "description": f"{congestion[2]}",
                  "link": {
                    "web": f"https://map.kakao.com/?map_type=TYPE_MAP&q={sort_name[2]}"
                  }
                },
                {
                  "title": f"{sort_name[3]}",
                  "description": f"{congestion[3]}",
                  "link": {
                    "web": f"https://map.kakao.com/?map_type=TYPE_MAP&q={sort_name[3]}"
                  }
                }
              ],
              "buttons": [
                {
                  "label": "자세한 정보 확인",
                  "action": "webLink",
                  "webLinkUrl": "https://map.seoul.go.kr/smgis2/short/6NjT7"
                }
              ]
            }
          }
        ]
      }
    }

######################################################20211025

maskSelect = [0, 0, 0, 0, 0]

maskQues1 = {
    "version": "2.0",
    "template": {"outputs": [{"simpleText": {"text": "일회용마스크인가요?\n다회용마스크인가요?"}}], 
                 "quickReplies": [
                     {"messageText":"일회용","action": "message","label": "일회용마스크" },
                     {"messageText":"다회용","action": "message","label": "다회용마스크" },
                     {"messageText":"초기화","action": "message","label": "초기화" }
                 ]
                }
}

maskQues2 = {
    "version": "2.0",
    "template": {"outputs": [{"simpleText": {"text": "피부가 예민하신가요?"}}],
                 "quickReplies": [
                     {"messageText":"민감함","action": "message","label": "민감해요" },
                     {"messageText":"민감하지않음","action": "message","label": "민감하지 않아요" },
                     {"messageText":"초기화","action": "message","label": "초기화" }
                 ]
                }
}

maskQues3 = {
    "version": "2.0",
    "template": {"outputs": [{"simpleText": {"text": "김서림 방지기능이 필요하신가요?"}}],
                 "quickReplies": [
                     {"messageText":"김서림방지","action": "message","label": "필요해요" },
                     {"messageText":"김서링방지필요없음","action": "message","label": "필요하지 않아요" },
                     {"messageText":"초기화","action": "message","label": "초기화" }
                 ]
                }
}

maskQues4 = {
    "version": "2.0",
    "template": {"outputs": [{"simpleText": {"text": "차단지수를 선택해주세요"}}],
                 "quickReplies": [
                     {"messageText":"KF99","action": "message","label": "KF-99" },
                     {"messageText":"KF94","action": "message","label": "KF-94" },
                     {"messageText":"KF80","action": "message","label": "KF-80" },
                     {"messageText":"KFAD","action": "message","label": "KF-AD" },
                     {"messageText":"초기화","action": "message","label": "초기화" }
                 ]
                }
}

@app.route('/api/mask', methods=['POST'])
def mask():
    body = request.get_json()
    select = body['userRequest']
    select = select['utterance']
    
    global maskQues1
    global maskQues2
    global maskQues3
    global maskQues4
    global maskAns
    global maskSelect
    
    if select == "일회용":
        response_data=maskQues2
        maskSelect[0] = 0
    elif select == "다회용":
        response_data=maskQues2
        maskSelect[0] = 1
    elif select == "민감함":
        response_data=maskQues3
        maskSelect[1] = 0
    elif select == "민감하지않음":
        response_data=maskQues3
        maskSelect[1] = 1
    elif select == "김서림방지":
        response_data=maskQues4
        maskSelect[2] = 0
    elif select == "김서림방지필요없음":
        response_data=maskQues4
        maskSelect[2] = 1
    elif select == "KF99":
        maskSelect[3] = 0
        maskSelect[4] = 1
    elif select == "KF94":
        maskSelect[3] = 1
        maskSelect[4] = 1
    elif select == "KF80":
        maskSelect[3] = 2
        maskSelect[4] = 1
    elif select == "KFAD":
        maskSelect[3] = 3
        maskSelect[4] = 1
    elif select == "초기화":
        maskSelect = [0, 0, 0, 0, 0]
        response_data = maskQues1
    
    else:
        maskSelect = [0, 0, 0, 0, 0]
        response_data = maskQues1
    
    if maskSelect[4] == 1:
        response_data = maskQues1 
        print("good")
        
        maskSelect[4] = 0
    
    return jsonify(response_data)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)