import streamlit as st
from pydub import AudioSegment
import io

# 1. 앱 제목 설정
st.title("🎵 나만의 오디오 편집기")
st.write("MP3 파일을 올리고 원하는 구간을 잘라보세요!")

# 2. 파일 업로드 기능 (HTML 없이 파이썬 한 줄로 끝!)
uploaded_file = st.file_uploader("음원 파일을 선택하세요", type=["mp3", "wav"])

if uploaded_file is not None:
    # 3. 파일 로딩 (업로드된 파일을 pydub으로 읽기)
    # Streamlit은 파일을 메모리에 임시 저장하므로 바로 읽을 수 있습니다.
    st.audio(uploaded_file, format="audio/mp3")  # 원본 재생 바 표시

    # pydub으로 오디오 객체 생성
    song = AudioSegment.from_file(uploaded_file)

    # 전체 길이 계산 (초 단위)
    total_seconds = len(song) / 1000
    st.write(f"총 길이: {total_seconds:.1f}초")

    # 4. 슬라이더로 구간 선택 (Colab보다 더 예쁜 UI가 자동 생성됨)
    # value는 기본 선택 구간, min/max는 슬라이더 범위
    start_sec, end_sec = st.slider(
        "자를 구간을 선택하세요 (초)",
        min_value=0.0,
        max_value=total_seconds,
        value=(0.0, 10.0),  # 기본값: 0~10초
    )

    # 5. 자르기 버튼
    if st.button("✂️ 자르기 실행"):
        # 자르기 로직 (이전과 동일)
        start_ms = start_sec * 1000
        end_ms = end_sec * 1000
        cut_audio = song[start_ms:end_ms]

        # 6. 결과 보여주기 및 다운로드
        st.success(f"{start_sec}초 ~ {end_sec}초 구간이 잘렸습니다!")

        # 메모리 버퍼에 저장 (파일로 저장하지 않고 다운로드 버튼에 바로 넘기기 위함)
        buffer = io.BytesIO()
        cut_audio.export(buffer, format="mp3")

        # 다운로드 버튼 생성
        st.download_button(
            label="💾 잘린 파일 다운로드",
            data=buffer,
            file_name="cut_result.mp3",
            mime="audio/mp3",
        )
