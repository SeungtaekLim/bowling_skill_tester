from ultralytics import YOLO
import cv2
import os
import numpy as np
import analyze

# 'results' 폴더가 없으면 생성
if not os.path.exists('results'):
    os.makedirs('results')

# YOLO 모델 로드
model = YOLO("model/yolo11m-pose.pt")

# video 폴더에서 mp4 파일 찾기
video_dir = 'video'
video_files = [f for f in os.listdir(video_dir) if f.endswith('.mp4')]
if not video_files:
    raise FileNotFoundError("video 폴더에 mp4 파일이 없습니다.")

video_path = os.path.join(video_dir, video_files[0])
print(f"🎥 처리할 비디오: {video_path}")

# YOLO로 비디오 파일 전체 처리
results = model(video_path, stream=True)

# 비디오 파일 저장 경로 설정
result_video_name = video_path.split('/')[-1].split('.')[0] + '_after.mp4'
result_video_path = os.path.join('results', result_video_name)

print(f"결과 비디오 경로: {result_video_path}")

cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    raise IOError(f"비디오 파일을 열 수 없습니다: {video_path}")

frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# VideoWriter 객체를 비디오 처리 전에 설정
out = cv2.VideoWriter(result_video_path, cv2.VideoWriter_fourcc(*'XVID'), 30, (frame_width, frame_height))

# 키포인트 데이터를 저장할 배열
all_keypoints_data = []

for i, result in enumerate(results):
    print(f"[INFO] 프레임 {i} 처리 중...")
    if len(result) == 0 or result[0].keypoints is None or result[0].keypoints.xy is None:
        all_keypoints_data.append([])
        out.write(result.plot())
        continue

    xy = result[0].keypoints.xy
    frame_keypoints = [(x, y) for x, y in xy[0]]
    all_keypoints_data.append(frame_keypoints)
    out.write(result.plot())

out.release()
cap.release()

# 유효한 키포인트가 하나라도 있는지 확인
has_valid_data = any(len(frame) > 0 for frame in all_keypoints_data)
user_level = "BEGINNER"

if not has_valid_data:
    print("[WARN] 유효한 키포인트 없음")
    final_score = 0
    grade = "BAD"
    guide_good_point = "분석 가능한 자세가 감지되지 않았습니다."
    guide_bad_point = "영상에서 사람 또는 키포인트를 인식하지 못했습니다."
    guide_recommend = "카메라 위치를 조정하거나 조명을 개선해주세요."
    
    print(f"점수: {final_score}")
    print(f"등급: {grade}")
    print(f"잘한 점: {guide_good_point}")
    print(f"부족한 점: {guide_bad_point}")
    print(f"추천: {guide_recommend}")
else:
    print("[INFO] 키포인트 분석 중...")
    final_score, grade, guide_good_point, guide_bad_point, guide_recommend, interpretations  = analyze.analyze(
        all_keypoints_data, frame_width, frame_height, user_level
    )
