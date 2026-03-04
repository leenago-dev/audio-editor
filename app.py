import streamlit as st
from pydub import AudioSegment
import io
import base64
import streamlit.components.v1 as components
import uuid
import os
import tempfile
from yt_dlp import YoutubeDL


# 시간 형식 변환 함수
def seconds_to_time_format(seconds):
    """초를 'MM:SS.mmm' 형식으로 변환 (분:초.밀리초)"""
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    # MM:SS.mmm 형식 (예: 03:25.500)
    return f"{minutes:02d}:{remaining_seconds:06.3f}"


# YouTube 음원 다운로드 함수
def download_youtube_audio(url):
    """YouTube에서 최고 음질의 오디오 다운로드"""
    # UUID로 고유한 파일명 생성 (파일명 충돌 방지)
    unique_id = str(uuid.uuid4())
    temp_dir = tempfile.gettempdir()
    output_path = os.path.join(temp_dir, f"yt_audio_{unique_id}")

    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320",  # 최고 음질
            }
        ],
        "outtmpl": output_path,
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            # 다운로드된 파일 경로
            downloaded_file = f"{output_path}.mp3"

            # 파일을 메모리로 읽어들임
            with open(downloaded_file, "rb") as f:
                audio_bytes = f.read()

            # 임시 파일 삭제 (찌꺼기 파일 방지)
            os.remove(downloaded_file)

            return audio_bytes, info
    except Exception as e:
        # 에러 발생 시에도 임시 파일 정리
        if os.path.exists(f"{output_path}.mp3"):
            os.remove(f"{output_path}.mp3")
        raise e


# 커스텀 오디오 플레이어 함수
def custom_audio_player(audio_bytes, duration_text, player_id="audio_player"):
    """밀리초까지 표시하는 커스텀 오디오 플레이어"""
    # 오디오를 base64로 인코딩
    audio_base64 = base64.b64encode(audio_bytes).decode()

    html_code = f"""
    <div style="padding: 15px; background-color: #f0f2f6; border-radius: 10px; margin: 10px 0;">
        <audio id="{player_id}" style="display:none;">
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>

        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
            <button id="playBtn_{player_id}" style="background: #FF4B4B; color: white; border: none; border-radius: 5px; padding: 10px 20px; cursor: pointer; font-size: 16px;">
                ▶️ 재생
            </button>
            <span id="currentTime_{player_id}" style="font-family: monospace; font-size: 16px; font-weight: bold;">00:00.000</span>
            <span style="color: #666;">/</span>
            <span style="font-family: monospace; font-size: 14px; color: #666;">{duration_text}</span>
        </div>

        <input type="range" id="seekBar_{player_id}" value="0" step="0.001" style="width: 100%; height: 8px; cursor: pointer;">

        <div style="display: flex; gap: 10px; margin-top: 10px;">
            <button id="speed_{player_id}" style="background: #E0E0E0; border: none; border-radius: 5px; padding: 5px 10px; cursor: pointer; font-size: 12px;">
                속도: 1.0x
            </button>
            <input type="range" id="volume_{player_id}" min="0" max="100" value="100" style="width: 100px;">
            <span style="font-size: 12px; color: #666;">🔊</span>
        </div>
    </div>

    <script>
        (function() {{
            const audio = document.getElementById('{player_id}');
            const playBtn = document.getElementById('playBtn_{player_id}');
            const seekBar = document.getElementById('seekBar_{player_id}');
            const currentTimeDisplay = document.getElementById('currentTime_{player_id}');
            const speedBtn = document.getElementById('speed_{player_id}');
            const volumeSlider = document.getElementById('volume_{player_id}');

            let speeds = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0];
            let currentSpeedIndex = 2;

            // 시간 포맷 함수 (MM:SS.mmm)
            function formatTime(seconds) {{
                const mins = Math.floor(seconds / 60);
                const secs = seconds % 60;
                return mins.toString().padStart(2, '0') + ':' + secs.toFixed(3).padStart(6, '0');
            }}

            // 재생/일시정지
            playBtn.addEventListener('click', function() {{
                if (audio.paused) {{
                    audio.play();
                    playBtn.textContent = '⏸️ 일시정지';
                    playBtn.style.background = '#666';
                }} else {{
                    audio.pause();
                    playBtn.textContent = '▶️ 재생';
                    playBtn.style.background = '#FF4B4B';
                }}
            }});

            // 오디오 메타데이터 로드 완료 시 seekBar 최대값 설정
            audio.addEventListener('loadedmetadata', function() {{
                seekBar.max = audio.duration;
            }});

            // 재생 시간 업데이트
            audio.addEventListener('timeupdate', function() {{
                seekBar.value = audio.currentTime;
                currentTimeDisplay.textContent = formatTime(audio.currentTime);
            }});

            // Seek bar 변경
            seekBar.addEventListener('input', function() {{
                audio.currentTime = seekBar.value;
            }});

            // 재생 속도 변경
            speedBtn.addEventListener('click', function() {{
                currentSpeedIndex = (currentSpeedIndex + 1) % speeds.length;
                audio.playbackRate = speeds[currentSpeedIndex];
                speedBtn.textContent = '속도: ' + speeds[currentSpeedIndex] + 'x';
            }});

            // 볼륨 조절
            volumeSlider.addEventListener('input', function() {{
                audio.volume = volumeSlider.value / 100;
            }});

            // 재생 종료 시
            audio.addEventListener('ended', function() {{
                playBtn.textContent = '▶️ 재생';
                playBtn.style.background = '#FF4B4B';
            }});
        }})();
    </script>
    """

    components.html(html_code, height=150)


# 1. 앱 제목 설정
st.title("🎵 나만의 오디오 편집기")

# Session State 초기화
if "downloaded_audio" not in st.session_state:
    st.session_state.downloaded_audio = None
if "downloaded_info" not in st.session_state:
    st.session_state.downloaded_info = None

# 탭 생성
tab1, tab2 = st.tabs(["📥 YouTube 다운로드", "✂️ 파일 편집"])

# ========== YouTube 다운로드 탭 ==========
with tab1:
    st.write("### YouTube 음원 다운로드")
    st.write("YouTube 영상에서 최고 음질(320kbps)의 오디오를 추출합니다.")

    youtube_url = st.text_input(
        "YouTube URL을 입력하세요",
        placeholder="https://www.youtube.com/watch?v=...",
    )

    if st.button("🎵 다운로드", type="primary", use_container_width=True):
        if not youtube_url:
            st.error("YouTube URL을 입력해주세요!")
        else:
            try:
                with st.spinner("다운로드 중... 잠시만 기다려주세요."):
                    audio_bytes, info = download_youtube_audio(youtube_url)

                    # Session State에 저장
                    st.session_state.downloaded_audio = audio_bytes
                    st.session_state.downloaded_info = info

                st.success("✅ 다운로드 완료!")

                # 메타데이터 표시
                title = info.get("title", "제목 없음")
                uploader = info.get("uploader", "업로더 정보 없음")
                duration = info.get("duration", 0)

                st.info(
                    f"**제목**: {title}\n\n**업로더**: {uploader}\n\n**길이**: {seconds_to_time_format(duration)}"
                )

                # 미리듣기
                st.write("**🎧 다운로드된 음원 미리듣기**")
                custom_audio_player(
                    audio_bytes, seconds_to_time_format(duration), "youtube_preview"
                )

                # 직접 다운로드 버튼
                st.download_button(
                    label="💾 음원 다운로드 (편집 없이)",
                    data=audio_bytes,
                    file_name=f"{title}.mp3",
                    mime="audio/mp3",
                    use_container_width=True,
                )

                # 편집 안내
                st.info(
                    "💡 **음원을 편집하려면** '파일 편집' 탭으로 이동하세요!\n\n다운로드한 음원이 자동으로 로드됩니다."
                )

            except Exception as e:
                st.error(f"❌ 다운로드 실패: {str(e)}")
                st.write(
                    "다음을 확인해주세요:\n- YouTube URL이 올바른지\n- 인터넷 연결 상태\n- FFmpeg가 설치되어 있는지"
                )

# ========== 파일 편집 탭 ==========
with tab2:
    st.write("### 음원 편집")

    # 음원 소스 선택
    if st.session_state.downloaded_audio is not None:
        audio_source = st.radio(
            "음원 소스 선택",
            ["YouTube 다운로드", "파일 업로드"],
            help="YouTube에서 다운로드한 음원 또는 직접 파일을 업로드할 수 있습니다.",
        )
    else:
        audio_source = "파일 업로드"
        st.info(
            "💡 YouTube 다운로드 탭에서 음원을 다운로드하거나, 아래에서 파일을 업로드하세요."
        )

    # 파일 업로드 방식
    if audio_source == "파일 업로드":
        uploaded_file = st.file_uploader("음원 파일을 선택하세요", type=["mp3", "wav"])
        audio_file = uploaded_file
    else:
        # YouTube 다운로드 사용
        audio_file = io.BytesIO(st.session_state.downloaded_audio)
        audio_file.name = "youtube_audio.mp3"
        st.success(
            f"✅ YouTube에서 다운로드한 음원: **{st.session_state.downloaded_info.get('title', '제목 없음')}**"
        )

    if audio_file is not None:
        # 3. 파일 로딩 (업로드된 파일을 pydub으로 읽기)
        # Streamlit은 파일을 메모리에 임시 저장하므로 바로 읽을 수 있습니다.

        # pydub으로 오디오 객체 생성
        song = AudioSegment.from_file(audio_file)

        # 전체 길이 계산 (초 단위)
        total_seconds = len(song) / 1000
        total_minutes = int(total_seconds // 60)
        total_remaining_seconds = total_seconds % 60

        # 음원 재생 (시간 정보와 함께 표시)
        st.write(
            f"**🎵 원본 음원 재생** | 총 길이: `{seconds_to_time_format(total_seconds)}`"
        )
        # 커스텀 오디오 플레이어 사용
        audio_file.seek(0)  # 파일 포인터를 처음으로 이동
        original_audio_bytes = audio_file.read()
        custom_audio_player(
            original_audio_bytes, seconds_to_time_format(total_seconds), "original"
        )

        # 4. 구간 선택 UI (분과 초를 따로 입력)
        st.write("### ✂️ 자를 구간 선택")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**시작 시간**")
            start_min = st.number_input(
                "분",
                min_value=0,
                max_value=total_minutes,
                value=0,
                step=1,
                key="start_min",
            )
            start_sec_input = st.number_input(
                "초 (밀리초 포함)",
                min_value=0.0,
                max_value=59.999,
                value=0.0,
                step=0.001,
                format="%.3f",
                key="start_sec",
            )

        with col2:
            st.write("**종료 시간**")
            end_min = st.number_input(
                "분",
                min_value=0,
                max_value=total_minutes,
                value=0,
                step=1,
                key="end_min",
            )
            end_sec_input = st.number_input(
                "초 (밀리초 포함)",
                min_value=0.0,
                max_value=59.999,
                value=min(10.0, total_seconds),
                step=0.001,
                format="%.3f",
                key="end_sec",
            )

        # 총 초로 변환
        start_sec = start_min * 60 + start_sec_input
        end_sec = end_min * 60 + end_sec_input

        # 유효성 검사
        if start_sec >= end_sec:
            st.error("⚠️ 시작 시간은 종료 시간보다 작아야 합니다!")
        elif end_sec > total_seconds:
            st.error(
                f"⚠️ 종료 시간이 총 길이({seconds_to_time_format(total_seconds)})를 초과했습니다!"
            )
        else:
            # 선택된 구간을 분:초 형식으로 표시
            st.success(
                f"선택한 구간: **{seconds_to_time_format(start_sec)}** ~ **{seconds_to_time_format(end_sec)}** (총 {seconds_to_time_format(end_sec - start_sec)})"
            )

            # 5. 기능 선택 버튼 (2개의 열로 배치)
            st.write("---")
            btn_col1, btn_col2 = st.columns(2)

            with btn_col1:
                extract_button = st.button(
                    "📥 구간 추출하기",
                    type="primary",
                    help="선택한 구간만 저장합니다",
                    use_container_width=True,
                )

            with btn_col2:
                cut_button = st.button(
                    "✂️ 구간 잘라내기",
                    type="secondary",
                    help="선택한 구간을 제거하고 앞뒤를 합칩니다",
                    use_container_width=True,
                )

            # 구간 추출 기능
            if extract_button:
                # 선택한 구간만 추출
                start_ms = start_sec * 1000
                end_ms = end_sec * 1000
                extracted_audio = song[start_ms:end_ms]

                # 결과 보여주기
                extracted_duration = end_sec - start_sec
                st.success(
                    f"✅ {seconds_to_time_format(start_sec)} ~ {seconds_to_time_format(end_sec)} 구간을 추출했습니다!"
                )
                st.info(
                    f"📊 추출된 파일 길이: `{seconds_to_time_format(extracted_duration)}`"
                )

                # 메모리 버퍼에 저장
                buffer = io.BytesIO()
                extracted_audio.export(buffer, format="mp3")
                buffer.seek(0)

                # 미리듣기
                st.write(
                    f"**🎧 추출된 구간 미리듣기** | 길이: `{seconds_to_time_format(extracted_duration)}`"
                )
                # 커스텀 오디오 플레이어 사용
                extracted_audio_bytes = buffer.getvalue()
                custom_audio_player(
                    extracted_audio_bytes,
                    seconds_to_time_format(extracted_duration),
                    "extracted",
                )

                # 다운로드용 버퍼 생성
                buffer_download = io.BytesIO()
                extracted_audio.export(buffer_download, format="mp3")

                # 다운로드 버튼 생성
                st.download_button(
                    label="💾 추출한 구간 다운로드",
                    data=buffer_download,
                    file_name="extracted_audio.mp3",
                    mime="audio/mp3",
                )

            # 구간 잘라내기 기능
            if cut_button:
                # 선택한 구간을 제거하고 앞뒤를 합침
                start_ms = start_sec * 1000
                end_ms = end_sec * 1000

                # 시작 전 부분 + 종료 후 부분 합치기
                before_cut = song[:start_ms]
                after_cut = song[end_ms:]
                final_audio = before_cut + after_cut

                # 결과 계산
                removed_duration = end_sec - start_sec
                final_duration = total_seconds - removed_duration

                # 결과 보여주기
                st.success(
                    f"✅ {seconds_to_time_format(start_sec)} ~ {seconds_to_time_format(end_sec)} 구간을 제거했습니다!"
                )
                st.info(
                    f"📊 제거된 구간: `{seconds_to_time_format(removed_duration)}` | 최종 길이: `{seconds_to_time_format(final_duration)}`"
                )

                # 메모리 버퍼에 저장
                buffer = io.BytesIO()
                final_audio.export(buffer, format="mp3")
                buffer.seek(0)

                # 미리듣기
                st.write(
                    f"**🎧 편집된 음원 미리듣기** | 길이: `{seconds_to_time_format(final_duration)}`"
                )
                # 커스텀 오디오 플레이어 사용
                cut_audio_bytes = buffer.getvalue()
                custom_audio_player(
                    cut_audio_bytes, seconds_to_time_format(final_duration), "cut"
                )

                # 다운로드용 버퍼 생성
                buffer_download = io.BytesIO()
                final_audio.export(buffer_download, format="mp3")

                # 다운로드 버튼 생성
                st.download_button(
                    label="💾 잘라낸 파일 다운로드",
                    data=buffer_download,
                    file_name="cut_audio.mp3",
                    mime="audio/mp3",
                )
