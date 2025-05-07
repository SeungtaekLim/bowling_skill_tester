
# 자세 분석 수식 정리

## 1. 어깨 각도 차이

**정의**  
오른쪽 어깨 각도는 다음 세 점을 기준으로 정의됩니다:  
- A = Left Shoulder  
- B = Right Shoulder  
- C = Right Elbow  

오른팔 각도는 다음과 같이 계산됩니다:

$$

\theta_{\text{shoulder}} = \min \left( \angle ABC, \angle CBA \right)

$$

90도 기준 편차는 다음과 같습니다:

$$

\Delta \theta = \left| \theta_{\text{shoulder}} - 90^\circ \right|

$$

**평균 어깨 각도 차이**

$$

\bar{\Delta \theta} = \frac{1}{N} \sum_{i=1}^{N} \Delta \theta_i

$$

---

## 2. 상체 중심 이동 거리

**중심 좌표 계산**  
프레임 \( t \)에서의 상체 중심은 다음과 같이 계산됩니다:

$$

C_t = \frac{1}{2} \left( \frac{P_{\text{LS}}^t + P_{\text{RS}}^t}{2} + \frac{P_{\text{LH}}^t + P_{\text{RH}}^t}{2} \right)

$$

**정규화된 거리 계산**  
프레임 \( t \)와 \( t-1 \) 간의 상체 이동 거리는 다음과 같습니다:

$$

d_t = \sqrt{ \left( \frac{x_t - x_{t-1}}{W} \right)^2 + \left( \frac{y_t - y_{t-1}}{H} \right)^2 }

$$

여기서 \( W \)는 프레임 너비, \( H \)는 프레임 높이입니다.

**평균 이동 거리**

$$

\bar{d} = \frac{1}{N-1} \sum_{t=2}^{N} d_t

$$

---

## 3. 손목 이동 거리 누적

오른쪽 손목의 누적 이동 거리는 다음과 같습니다:

$$

D_{\text{wrist}} = \sum_{t=2}^{N} \sqrt{ \left( \frac{x_t - x_{t-1}}{W} \right)^2 + \left( \frac{y_t - y_{t-1}}{H} \right)^2 }

$$

단, \( (x_t, y_t) \)는 프레임 \( t \)에서의 오른쪽 손목 좌표입니다.

---

## 4. 발목 위치 변화 횟수

**조건 정의**  
프레임 간 발목 y좌표가 다음 조건을 만족할 경우 위치 변화 이벤트로 간주합니다:

$$

\Delta y_t = \left| y_t - y_{t-1} \right|

$$

$$

\text{Switch}_t =
\begin{cases}
1, & \text{if } \Delta y_t > \frac{H}{30} \text{ and } y_t \ne 0 \\
0, & \text{otherwise}
\end{cases}

$$

**총 변화 횟수**

$$

A = \sum_{t} \text{Switch}_t

$$

---

## 5. 유효 프레임 비율

얼굴 또는 귀 키포인트가 감지된 프레임의 비율입니다:

$$

\text{Face Ratio} = \frac{N_{\text{face}}}{N}, \quad \text{Ear Ratio} = \frac{N_{\text{ear}}}{N}

$$

---

## 6. 최종 점수 함수 및 등급 분류

위 분석 지표들을 바탕으로 최종 점수는 다음 함수로 계산됩니다:

$$

\text{Score} = f\left( \bar{\Delta \theta}, \bar{d}, D_{\text{wrist}}, A, \text{User Level} \right)

$$

**등급 분류 기준**

$$

\text{Grade} =
\begin{cases}
\text{EXCELLENT}, & \text{if } \text{Score} \ge 80 \\
\text{GOOD}, & \text{if } 74 \le \text{Score} < 80 \\
\text{COMMON}, & \text{if } 66 \le \text{Score} < 74 \\
\text{BAD}, & \text{otherwise}
\end{cases}

$$
