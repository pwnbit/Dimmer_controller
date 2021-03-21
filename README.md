# Dimmer Controller.py

![version](https://img.shields.io/github/v/release/pwnbit/Dimmer_controller)

Wifi LED Cotroller를 PC에서 제어하기 위한 Python 프로그램으로,
[flux_led](https://github.com/beville/flux_led) 를 기반으로 하고 있습니다.

## 호환 제품
* Magic Home Pro 앱을 사용하는 Wifi Dimmer 제품.
    * [Android App Store](https://play.google.com/store/apps/details?id=com.zengge.wifi&hl=en&gl=us)
    * [Apple App Store](https://apps.apple.com/us/app/magic-home-pro/id1187808229)
    * [AliExpress](https://ko.aliexpress.com/wholesale?catId=0&initiative_id=SB_20210307042017&origin=y&SearchText=magic+home+wifi+controller)

## 다운로드
* [Github release](https://github.com/pwnbit/Dimmer_controller/releases)

## 기능 소개
#### 2021-03-05 v0.1
* Wifi LED Controller 연결
* Controller의 시간 확인
* 0 ~ 100% 밝기 조절
* 0, 20, 40, 60, 80, 100% Presets 밝기 조절
* 사용자 입력 밝기 조절
* 설정된 타이머 표시

#### 2021-03-07 v0.1.1
* LICENSE 파일 추가 _(LGPL-3.0 License)_
* README.md 파일 추가
* Controller response 주석 제거
* percent_to_byte(), byte_to_percent() 결과를 반올림 처리
* IP 입력란의 기본값 제거
* Blog, Github URL 추가

#### 2021-03-07 v0.1.2
* Disconnect 기능 추가
* Controller 시간 동기화 기능 추가
* 코드 최적화

#### 2021-03-11 v0.1.3
* percent_to_byte(), byte_to_percent() 함수의 버그 수정
* 버튼 크기 조정

#### 2021-03-11 v1.0.0
* 실행파일(exe) 배포

#### 2021-03-12 v1.1.0
* 입력 값 검증 추가
* 경고창 기능 추가

#### 2021-03-12 v1.1.1
* exe 파일 경고창 에러 수정
* IP 기본값 제거

#### 2021-03-21 v1.3.0
* 인터페이스 수정
* Wifi Dimmer 스캐닝 기능 추가
* 기타 버그 수정