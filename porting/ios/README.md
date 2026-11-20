# EDOPro 한국어 iOS 포팅

이 폴더는 iOS ARM64 포팅의 초기 작업 기반입니다. 실제 iOS 컴파일과 기기 실행은 아직 검증하지 않았습니다.

2026-11-20 로컬 검증: 리소스 21,423개 생성, 한국어 DB 6종 SQLite 무결성 검사, 현대 한글 11,172자 폰트 검사, 통합 검사 4개, Python 구문·Bash 구문·`git diff --check` 통과. 기본 한국어 `cards.cdb`에는 14,546개 항목이 있고 그중 14,459개 이름에 한글이 포함되어 있습니다. 이는 번역 완성률을 뜻하지 않습니다.

## 가져온 소스

- EDOPro: https://github.com/edo9300/edopro (`origin`)
- 듀얼 엔진과 Lua: 기존 `ocgcore` 재귀 서브모듈
- 한국어 카드 DB/메뉴: https://github.com/Team-AllYGOPro/edopro-korean (`localization/korean`)
- 공식 배포 리소스: https://github.com/ProjectIgnis/Distribution (`porting/ios/distribution`)
- 한국어 폰트: https://github.com/notofonts/noto-cjk, 커밋 `165c01b46ea533872e002e0785ff17e44f6d97d8`, `Sans/OTF/Korean/NotoSansCJKkr-Regular.otf`

한국어 패치는 정식 저장소를 사용합니다. `edopro-korean-delta` 테스트 패치는 포함하지 않습니다. 카드의 게임 규칙은 공식 DB에서 읽고 한국어 DB는 언어팩으로 읽습니다. 각 원본 라이선스도 리소스에 함께 복사합니다.

## 로컬 리소스 준비

저장소 루트에서 Python 3.9 이상으로 실행합니다. 별도 Python 패키지는 필요하지 않습니다.

```powershell
git submodule update --init --recursive
python porting/ios/prepare_resources.py
```

결과: `build/ios-korean/EDOProResources/`

현재 Windows 작업 환경에서는 다음 명령으로 설치된 Python(또는 Codex에 포함된 Python)을 찾아 리소스 준비와 검증을 함께 실행할 수 있습니다.

```powershell
& ./porting/ios/prepare.ps1
# 리소스가 이미 준비된 경우 검증만 실행
& ./porting/ios/prepare.ps1 -VerifyOnly
```

- 공식 텍스처, 설정, 카드 DB, 카드 스크립트, 덱, 사운드와 퍼즐
- `config/languages/Korean/`: 한국어 카드 DB 6종, `strings.conf`, 라이선스
- 한국어 기본 언어 설정과 Noto Sans CJK KR 폰트
- 정식 한국어 저장소에서 번역을 갱신하는 언어 저장소 설정
- 원본 커밋과 파일 SHA-256을 기록한 `resource-manifest.json`

준비 스크립트는 생성 폴더만 다시 만들며 소스 서브모듈은 수정하지 않습니다. SQLite 무결성, 한국어 카드 이름/메뉴, 현대 한글 11,172자의 폰트 수록 여부를 검사합니다.

## iOS 빌드

Windows PowerShell만으로 iOS 바이너리를 컴파일할 수는 없습니다. 이 작업은 원본과 같은 **Linux cctools 교차 컴파일 환경**을 사용하도록 준비했습니다. 현재 PC에서 이 환경은 확인되지 않았습니다.

`.github/workflows/ios-korean.yml`에 수동 실행용 GitHub Actions 절차가 있습니다. 이 파일은 로컬에만 준비했으며 GitHub 저장소 생성/업로드/실행은 하지 않았습니다. 전체 변경사항을 보존한 저장소에서 워크플로를 실행하면 다음을 시도합니다.

1. 원본의 cctools iOS 툴체인과 ARM64 vcpkg 의존성 설치
2. `bash porting/ios/build.sh` 실행: 정적 듀얼 엔진/Lua를 포함한 `ygopro` 타깃 빌드
3. `package_app.py`로 앱, 한국어 리소스, Info.plist 조립
4. ad hoc 서명 후 `EDOPro-Korean-arm64.ipa`를 Actions 아티팩트로 생성

Linux 환경을 직접 준비한 경우 같은 `build.sh`를 사용할 수 있습니다. 기본 경로는 `/opt/cctools`, `./vcpkg2`, `./premake5`이며 설치 명령은 워크플로에 있습니다. 의존성 캐시는 원본처럼 `latest`를 사용하므로 최초 실제 빌드 성공 후 툴체인/캐시까지 고정할 필요가 있습니다.

ad hoc 서명은 일반 아이폰 설치용 개발자 서명이 아닙니다. 기기 설치에는 별도 사이드로딩/개발자 재서명이 필요합니다. 서명 인증서와 계정 정보는 이 저장소에 넣지 않습니다.

## 초기 iOS 변경

`gframe/iOS/porting_ios.mm`에서 앱 안의 `EDOProResources`를 Documents 폴더에 복사한 후 시작하도록 연결했습니다. 이미 존재하는 파일은 건드리지 않아 설정·덱을 보존합니다. 번역 갱신은 언어 저장소가 담당합니다. 번들 리소스 자체의 업그레이드 정책은 후속 작업입니다.

## 아직 검증할 항목

- 최초 ARM64 컴파일/링크, IPA 재서명과 실제 기기 실행
- 첫 실행 복사 시간, 한글 입력·글꼴·터치·가로 화면·안전 영역
- 카드 이미지 다운로드 주소: 원본은 빌드 비밀값을 사용하며 현재 포트에는 그 주소가 설정되지 않음
- 온라인 방 목록/대전, 로컬 네트워크 권한, 덱 편집, 리플레이
- 최신 엔진과 배포본의 카드 데이터/스크립트 조합 및 자동 업데이트
- iOS용 WindBot은 포함하지 않았으므로 AI 대전 지원 여부는 별도로 검토

검증 명령:

```powershell
python -m unittest discover -s porting/ios/tests -v
git diff --check
```
