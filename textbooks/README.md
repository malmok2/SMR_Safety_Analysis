# 교재 원본

슬라이드 덱을 만든 교재(Word)와 그 PDF 다. 수치를 바꿔야 하면 **교재가 기준**이고, 교재와 덱을 같이 고친다.

| 교재 | 덱 | 비고 |
|---|---|---|
| 「SMR 설계요건과 공학적안전설비」 (Rev1.0) | `w02-03_smr-design-requirements` | 이 폴더에 없음 — Word·PDF 원본은 `malmok2/Documents` |
| `THINK Lab SMR 자료를 찾는 법과 PWR형 SMR (Rev1.0).docx` · `.pdf` | `w03-04_smr-data-and-pwr-smrs` | 81쪽 |
| `THINK Lab 물을 쓰지 않는 SMR - VHTR SFR MSR (Rev1.0 수치정정).docx` · `.pdf` | `w05a_htgr-vhtr` · `w05b_sfr` · `w06_msr` | 94쪽. 2026-10 수치 정정 반영(CHANGELOG 참조) |

**PDF 는 Word 에서 굽는다** — 손으로 고치지 않는다. Word 를 고치면 PDF 도 다시 구워 같이 커밋한다.
`malmok2/Documents` 의 교재 키트로 굽는다(LibreOffice 가 목차를 채우고 Pretendard 를 심는다):

```bash
python3 "<Documents>/_kit/scripts/topdf.py" "<교재>.docx" "<교재>.pdf"
```

LibreOffice Math 가 없으면 PDF 에서 수식이 전부 사라진다(키트 `cloud/setup.sh` 가 함께 깐다).

MS World 「수업」 화면이 이 PDF 를 **파일 이름으로** 찾아 주차마다 「교재」 단추를 단다
(`malmok2/MSWorld` 의 `src/data/courses.ts`). 이름을 바꾸면 그쪽도 고친다 — 안 고치면 단추 대신
「교재 PDF 를 찾지 못했습니다」가 뜬다.

이 폴더는 GitHub Pages(`docs/`)로 서빙되지 않는다. 저장소가 공개이므로 GitHub 에서는 누구나 받을 수 있다.
