한국어 카드 데이터·메뉴·한글 폰트를 포함한 EDOPro iOS ARM64 시험 빌드입니다.

- `EDOPro-Korean-arm64.ipa`: 아이폰/아이패드용 IPA 파일
- `SHA256SUMS.txt`: 파일 검증용 SHA-256
- `resource-manifest.json`: 원본 소스 커밋과 리소스 파일 검증 정보

이 IPA는 ad hoc 코드 서명 상태이며, 일반 아이폰에 설치하려면 사용 중인 사이드로딩 도구나 개발자 인증서로 재서명해야 합니다. 다운로드 링크만 누르는 방식의 OTA 설치 파일은 아닙니다.

자동 빌드 및 리소스 검사를 통과한 시험판이며 실제 기기에서 실행·터치·대전 검증은 아직 진행하지 않았습니다. 공식 카드 이미지 서버와 HTTPS 인증서 묶음을 포함합니다. WindBot AI는 포함하지 않았습니다. 기존 사용자 데이터는 유지하며 첫 실행에 기본 리소스를 Documents에 복사합니다.

원본: [EDOPro](https://github.com/edo9300/edopro), [한국어 패치](https://github.com/Team-AllYGOPro/edopro-korean), [공식 배포 리소스](https://github.com/ProjectIgnis/Distribution), [Noto CJK 폰트](https://github.com/notofonts/noto-cjk). 각 프로젝트의 라이선스를 포함합니다. 이 저장소의 해당 릴리스 태그와 재귀 서브모듈에서 빌드 소스를 확인할 수 있습니다.
