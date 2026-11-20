한국어 카드 데이터·메뉴·한글 폰트를 포함한 EDOPro iOS ARM64 시험 빌드입니다.

- 터치 좌표 보정: iOS 화면 배율과 실제 렌더링 해상도 차이를 반영합니다. 메뉴, 덱 편집, 듀얼의 클릭과 드래그에 공통 적용됩니다.
- 인게임 화면 스케일링 기본값 200%. 기존 설치도 업데이트 후 최초 실행에 200%로 전환하며 이후 사용자가 바꾼 배율은 유지합니다.
- 기존 앱과 같은 번들 ID를 사용합니다. 같은 서명 설정으로 업데이트 설치하면 덱과 사용자 데이터를 유지할 수 있습니다.

- `EDOPro-Korean-arm64.ipa`: 아이폰/아이패드용 IPA 파일
- `SHA256SUMS.txt`: 파일 검증용 SHA-256
- `resource-manifest.json`: 원본 소스 커밋과 리소스 파일 검증 정보

이 IPA는 ad hoc 코드 서명 상태이며, 일반 아이폰에 설치하려면 사용 중인 사이드로딩 도구나 개발자 인증서로 재서명해야 합니다. 다운로드 링크만 누르는 방식의 OTA 설치 파일은 아닙니다.

기존 버전에서 보고된 터치 어긋남을 수정한 시험판입니다. 좌표 계산과 설정 이전은 자동 검사하며, 수정 후 실제 기기의 터치·대전 확인은 별도로 필요합니다. 공식 카드 이미지 서버와 HTTPS 인증서 묶음을 포함합니다. WindBot AI는 포함하지 않았습니다. 첫 실행에 기본 리소스를 Documents에 복사합니다.

원본: [EDOPro](https://github.com/edo9300/edopro), [한국어 패치](https://github.com/Team-AllYGOPro/edopro-korean), [공식 배포 리소스](https://github.com/ProjectIgnis/Distribution), [Noto CJK 폰트](https://github.com/notofonts/noto-cjk). 각 프로젝트의 라이선스를 포함합니다. 이 저장소의 해당 릴리스 태그와 재귀 서브모듈에서 빌드 소스를 확인할 수 있습니다.
