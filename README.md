# 포모도로+

`포모도로+`는 화면 우측 하단에 작게 띄워두고 쓰는 데스크톱 포모도로 시간관리 앱입니다. 오늘 바로 사용할 수 있는 macOS MVP를 먼저 완성하고, 같은 코드베이스에서 Windows/Linux 빌드로 확장할 수 있도록 구성했습니다.

## 프로젝트 목표

- 실행 시 우측 하단에 작은 플로팅 타이머 표시
- 집중 시간과 유휴/휴식 시간을 빠르게 시작, 중단, 재시작
- 항상 화면 위 표시 옵션 제공
- 집중/휴식 명칭과 시간을 사용자가 설정 가능
- 집중/휴식 상태에 맞는 귀여운 랜덤 애니메이션 슬롯 제공
- Python 3.12+ 기반으로 macOS, Windows, Linux 실행 파일 빌드 가능

## 현재 구현 상태

MVP 구현 완료:

- PySide6 기반 데스크톱 GUI
- 프레임 없는 작은 플로팅 창
- 기본 위치: 화면 우측 하단
- 마우스 드래그로 창 이동 가능
- 시작 / 중단 / 재시작 버튼
- 집중 / 휴식 모드 전환 버튼
- 설정창 제공
- 설정값 JSON 저장
- 항상 위 표시 옵션
- 집중/휴식별 랜덤 이모지 애니메이션 슬롯 12개씩
- macOS PyInstaller 빌드 성공
- 테스트 코드 작성 및 통과

2차 고도화 완료:

- 시스템 트레이 아이콘 + 컨텍스트 메뉴 (창 보기/시작/중단/재시작/오늘 통계/종료)
- 트레이로 최소화 (✕) 버튼 — 백그라운드 유지
- 타이머 종료 OS 네이티브 알림 (트레이 말풍선)
- 타이머 종료 알림음 (macOS: afplay, Linux: paplay, Windows: winsound)
- 자동 집중/휴식 사이클 (설정에서 활성화)
- 일별 집중/휴식 횟수·시간 통계 (📊 버튼)
- 메인 창 하단 오늘 현황 한줄 표시

아직 추가 고도화 대상:

- 실제 GIF/APNG 캐릭터 애니메이션 적용 (현재 PNG 정적 이미지)
- 알림음 사용자 지정 (WAV/MP3 파일 선택)
- 주간/월간 통계 히스토리
- Windows/Linux 실제 빌드 검증

## 주요 스펙

기술 스택:

- Python 3.12+
- PySide6
- platformdirs
- PyInstaller
- pytest

기본 설정:

- 집중 명칭: `업무`
- 집중 시간: `25분`
- 휴식 명칭: `휴식`
- 휴식 시간: `5분`
- 항상 위 표시: 꺼짐

설정 가능 범위:

- 집중 시간: `10분 ~ 60분`
- 휴식 시간: `5분 ~ 20분`
- 집중/휴식 명칭: 최대 20자

## 프로젝트 구조

```text
captain-pomodoro/
├── README.md
├── AGENTS.md
├── pyproject.toml
├── scripts/
│   ├── build_macos.sh
│   ├── build_windows.ps1
│   └── build_linux.sh
├── src/
│   └── pomodoro_plus/
│       ├── __main__.py
│       ├── app.py
│       ├── timer.py
│       ├── settings.py
│       ├── assets.py
│       ├── ui/
│       │   ├── main_window.py
│       │   └── settings_dialog.py
│       └── assets/
│           ├── focus/
│           └── break/
└── tests/
    ├── test_timer.py
    └── test_settings.py
```

핵심 파일:

- `src/pomodoro_plus/app.py`: Qt 앱 진입 구성
- `src/pomodoro_plus/ui/main_window.py`: 플로팅 타이머 메인 창
- `src/pomodoro_plus/ui/settings_dialog.py`: 설정창
- `src/pomodoro_plus/timer.py`: UI와 분리된 타이머 엔진
- `src/pomodoro_plus/settings.py`: 설정 저장/로드/검증
- `src/pomodoro_plus/assets.py`: 집중/휴식 랜덤 애니메이션 슬롯

## 개발 환경 준비

Python 3.12 이상이 필요합니다.

```bash
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
```

이미 이 폴더에는 개발용 `.venv`가 생성되어 있습니다.

## 개발 실행

가상환경 활성화 후 실행:

```bash
. .venv/bin/activate
pomodoro-plus
```

또는 직접 실행:

```bash
.venv/bin/python -m pomodoro_plus
```

## macOS 앱 실행

현재 macOS 빌드 결과물은 `dist/` 아래에 있습니다.

```bash
open dist/PomodoroPlus.app
```

CLI 형태로 실행하려면:

```bash
./dist/PomodoroPlus/PomodoroPlus
```

## 테스트

```bash
.venv/bin/python -m pytest
```

현재 검증 결과:

```text
5 passed
```

추가로 Qt 메인 창 초기화도 확인했습니다.

```bash
QT_QPA_PLATFORM=offscreen .venv/bin/python -c "from PySide6.QtWidgets import QApplication; from pomodoro_plus.ui.main_window import MainWindow; app=QApplication([]); w=MainWindow(); print(w.windowTitle(), w.width(), w.height())"
```

확인된 출력:

```text
포모도로+ 260 330
```

## 빌드

빌드 스크립트는 프로젝트 내부 `.venv`가 있으면 우선 사용합니다. PyInstaller 캐시도 프로젝트 내부 `.pyinstaller-cache/`를 사용하도록 설정했습니다.

macOS:

```bash
./scripts/build_macos.sh
```

Windows PowerShell:

```powershell
.\scripts\build_windows.ps1
```

Linux:

```bash
./scripts/build_linux.sh
```

빌드 결과:

```text
dist/
├── PomodoroPlus.app
└── PomodoroPlus/
```

macOS 빌드는 현재 환경에서 성공 확인했습니다.

## 애니메이션 리소스 확장

현재 MVP는 코드에 내장된 이모지 슬롯으로 동작합니다.

집중 슬롯 예:

- 공부 중
- 열일 중
- 삽질 중
- 코딩 중
- 문서 작성

휴식 슬롯 예:

- 커피 한잔
- 멍때리기
- 노래 듣기
- 산책
- 스트레칭

이후 실제 GIF/APNG 파일을 추가할 위치:

```text
src/pomodoro_plus/assets/focus/
src/pomodoro_plus/assets/break/
```

다음 단계에서는 이 폴더의 리소스를 자동 탐색해서 `QMovie`로 재생하도록 바꾸면 됩니다.

## 설정 저장

설정은 `platformdirs`가 제공하는 OS별 사용자 설정 경로에 JSON으로 저장됩니다.

저장 항목:

- `focus_label`
- `focus_minutes`
- `break_label`
- `break_minutes`
- `always_on_top`

파일이 없거나 깨져 있으면 기본값으로 복구됩니다.

## 진행 내역

2026-05-16:

- 프로젝트 초기 구조 생성
- Python 패키지 설정 추가
- PySide6 GUI 구현
- 타이머 엔진 구현
- 설정 저장/검증 구현
- 집중/휴식 랜덤 애니메이션 슬롯 구현
- 테스트 추가
- macOS 빌드 스크립트 작성
- Windows/Linux 빌드 스크립트 초안 작성
- macOS 빌드 성공
- 빌드된 앱 실행 확인

## 다음 작업 추천

1. 실제 캐릭터 GIF/APNG 리소스 적용
2. 시스템 트레이 최소화 지원
3. 타이머 종료 알림음/알림창 개선
4. 집중 완료 후 휴식 전환 자동화 옵션
5. 하루 집중 횟수와 누적 집중 시간 저장
6. Windows 빌드 검증
7. Linux 빌드 검증
