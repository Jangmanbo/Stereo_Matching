# Stereo_Matching
![im6](https://user-images.githubusercontent.com/42964968/167449211-1267fab7-cdb1-4785-bfdf-541f0f11bde5.png)
![im6](https://user-images.githubusercontent.com/42964968/167449192-5349496d-b3ec-43cf-a57b-b420de9efce3.png)
  * 2개의 translation image의 corresponding point를 찾아 depth image를 생성한다.<br>
  * 다양한 방법론을 사용하여 최적의 depth image를 찾는다.
  * 이미지 로드, 출력 외 openCV 라이브러리를 사용하지 않는다.
<br>

## 1. Disparity Space Image(DSI) 생성


  * SSD와 NCC, 2가지 방법으로 left image와 right image 사이의 matching point를 찾기

### ◽SSD (Sum of Squared Difference)

![image](https://user-images.githubusercontent.com/42964968/167448464-7dadd22f-5850-44ba-848b-06b4303268f5.png)<br>
두 픽셀의 차를 제곱하여 더한 후 루트를 씌워 SSD를 계산하여 DSI를 생성하였더니<br>
픽셀값이 255가 넘는 경우 흰색으로 보였다.<br>

<br>

![image](https://user-images.githubusercontent.com/42964968/167448598-0b551f8e-6128-4d5e-a88c-2e1568c5e7d7.png)
![image](https://user-images.githubusercontent.com/42964968/167448618-03586769-0145-4d90-8d26-e95e8888438b.png)<br>
(patch size*1.5)로 나눔으로써 픽셀값이 255가 넘지 않도록 하였더니 정상적으로 DSI가 생성되었다.<br>

<br>

### ◽NCC (Normalized Cross Correlation)
![image](https://user-images.githubusercontent.com/42964968/167451315-cc699e39-9195-4cb9-b93a-7644a34facef.png)<br>
![image](https://user-images.githubusercontent.com/42964968/167451349-35773980-3db1-451d-8fa6-53effbb3cf53.png)<br>
Patch의 각 픽셀값의 평균과 분산을 구한다.<br>

<br>

![image](https://user-images.githubusercontent.com/42964968/167451463-613a4ec5-9695-410f-b2f7-2849fb0f4801.png)<br>
각 픽셀을 평균으로 뺀 후 분산으로 나누어 픽셀값의 범위를 [-1, 1]로 정규화 했다.<br>

<br>

![image](https://user-images.githubusercontent.com/42964968/167451532-1a62634a-d4b4-44af-8d09-ccada15ce244.png)<br>
Optimal path를 찾는 dynamic programming을 SSD와 동일하게 최소 cost를 찾는 방식으로 동작하도록 <br>
cross correlation value를 1에서 빼서 max value는 min value, min value는 max value가 되도록 변환하였다.<br>

<br>

![image](https://user-images.githubusercontent.com/42964968/167451633-f76899ad-6124-4d18-a99d-45679fdd9e01.png)<br>
NCC로 생성한 DSI<br>

<br>

### ◽SSD vs NCC
![image](https://user-images.githubusercontent.com/42964968/167452262-47e43c0c-0eee-45ce-bf2e-878ce91bdd33.png)|![image](https://user-images.githubusercontent.com/42964968/167452280-74aa8b2b-6eed-4d79-ac2c-8d1bb9371a52.png)
:---:|:---:|
SSD (patch size=3, cost degree=0.5)|NCC (patch size=3, cost degree=0.3)

<br>

SSD, NCC 각각 최적의 occlusion cost를 찾아 생성한 depth image이다.<br><br>
NCC는 패치의 밝기의 평균을 0으로, 범위를 [-1,1]로 정규화 과정을 거친 후 cross correlation 계산을 하였다.<br>
그러나 SSD는 별도의 정규화 과정이 없었기 때문에 SSD로 만든 depth image는 matching point를 제대로 찾지 못한 부분에서 노이즈 현상이 발생하였다.<br>

<br>

### ◽Patch size
![image](https://user-images.githubusercontent.com/42964968/167452877-44c6d496-46b7-4be4-90cd-5dfed43ebdb5.png)|![image](https://user-images.githubusercontent.com/42964968/167452892-b7360ab9-effd-4462-9b39-4a17f208068f.png)
:---:|:---:|
SSD (patch size=3, cost degree=0.5)|SSD (patch size=9, cost degree=0.7)

<br>

Patch size가 9 * 9인 경우 patch size가 커서 smoothing 효과로 인해 3 * 3보다 물체의 경계선이 깔끔하거나 매우 번져 보이는 현상이 발생하였다. <br>
Patch size가 3 * 3인 경우 경계선이 뚜렷하지는 않지만, 9 * 9에 비해 뭉침, 번짐 현상이 심하지 않았다.<br>

<br><br>

## 2.	Optimal Path

  * 처음 노드부터 마지막 노드까지 최소 cost로 가는 path를 구하기 위해 dynamic programming으로 구현하였다.

<br>

### ◽Occlusion Cost
![image](https://user-images.githubusercontent.com/42964968/167454543-9564785b-90be-49ab-8558-05b3dab9693c.png)<br>
Occlusion cost는 각 DSI(Disparity Space Image)의 픽셀값의 평균에 cost degree를 곱하여 설정하였다.<br>
. | DSI 평균 범위
:---:|:---:|
SSD|[85, 95]
NCC|[120, 130]

<br>

![image](https://user-images.githubusercontent.com/42964968/167454816-0688daed-de2c-449e-8d42-bdec2d6e0838.png)|![image](https://user-images.githubusercontent.com/42964968/167454828-b2b9a158-8cca-44e1-a9c8-986abab4fde3.png)
:---:|:---:|
NCC (patch size=3, cost degree=0.05)|

<br>

occlusion cost가 너무 작으면 path를 찾을 때 occlusion이 실제보다 더 많이 일어났다고 판단하여 filling 했을 때 과도한 smoothing 현상이 일어난다.

<br>

![image](https://user-images.githubusercontent.com/42964968/167534175-ac1c45a1-c89e-4c72-88ca-e2ba84b88623.png)|![image](https://user-images.githubusercontent.com/42964968/167534181-3b0397cc-e5a1-491e-ae32-e45513a9619b.png)
:---:|:---:|
NCC (patch size=3, cost degree=1.0)|

<br>

반면 occlusion cost가 너무 크면 실제로 occlusion이 일어났음에도 occlusion이 일어나지 않았다고 판단하여<br>
filling 전에도 smoothing 현상이 일어났음을 볼 수 있다.

<br>

![image](https://user-images.githubusercontent.com/42964968/167534292-5f8124e2-3bda-4bf3-a8f6-4a41e3f73044.png)|![image](https://user-images.githubusercontent.com/42964968/167534301-3d0c6d4b-9567-4b2b-ab72-dd82025016be.png)
:---:|:---:|
NCC (patch size=3, cost degree=0.3)|

<br>

적절한 cost degree를 찾아 occlusion cost를 설정하였더니 filling 전후 모두 smoothing 현상이 덜 발생했다.

<br>

### ◽Range

![image](https://user-images.githubusercontent.com/42964968/167534352-5304dcab-697a-45fa-be5f-05847fb79ab4.png)|![image](https://user-images.githubusercontent.com/42964968/167534358-4a800e3c-3ede-40c9-85d7-c270a5e5b964.png)
:---:|:---:|
SSD DSI(patch size=3)|NCC DSI(patch size=3)

<br>

Depth의 범위를 [0, 64]로 설정하여 Optimal path를 해당 범위 내에서 구하도록 했다.<br>

<br>

## 3. Depth Image
### ◽Normalization
Normalization을 수행하지 않고 depth image를 생성하였더니 이미지가 전체적으로 어두웠다.<br>
따라서 depth image의 픽셀값의 max value를 찾아 max value의 값을 255로 만들도록 normalize하였다.

![image](https://user-images.githubusercontent.com/42964968/167534488-4ab02889-d769-4f35-8cd0-f5c5539c55be.png)|![image](https://user-images.githubusercontent.com/42964968/167534493-18b5a055-7d19-4104-9ad3-221eb4adf158.png)
:---:|:---:|
NCC (patch size=3, cost degree=0.3)|NCC (patch size=3, cost degree=0.3, normalize)

<br>

Normalization depth image가 더 밝기의 변화폭이 커 물체의 거리감을 잘 나타내는 것을 볼 수 있다. <br>

<br>

### ◽Hole Filling
#### Horizontal Filling
![image](https://user-images.githubusercontent.com/42964968/167534913-331ce07c-ceec-40a0-9060-d6c6ceef72b9.png)|![image](https://user-images.githubusercontent.com/42964968/167534919-49609cac-dc3c-4d73-a0da-a879d3d96879.png)
:---:|:---:|
NCC (patch size=3, cost degree=0.3)|

<br>

Left image가 기준인 경우, Right image에서 보이지 않아 occlusion이 발생한 부분을 채워야 하므로<br>
occlusion이 발생한 픽셀의 왼쪽 픽셀값으로 filling하였다.

![image](https://user-images.githubusercontent.com/42964968/167534988-f9ef2323-f22c-434d-8eda-6ec27bb73c9c.png)|![image](https://user-images.githubusercontent.com/42964968/167534999-4066ecff-1e14-4591-b128-bc548150f934.png)
:---:|:---:|
NCC (patch size=3, cost degree=0.3)|

<br>

Right image가 기준인 경우, Left image에서 보이지 않아 occlusion이 발생한 부분을 채워야 하므로 occlusion이 발생한 픽셀의 오른쪽 픽셀값으로 filling하였다.<br>

#### Vertical Filling
![image](https://user-images.githubusercontent.com/42964968/167535064-e23e3e24-1b90-4bf5-9c76-a28940b06b2c.png)|![image](https://user-images.githubusercontent.com/42964968/167535070-5b8ee889-99d8-46e7-9eed-7a5c6b961452.png)
:---:|:---:|
NCC (patch size=3, cost degree=0.3)|

<br>

occlusion이 발생한 픽셀의 위쪽 픽셀값으로도 filling하였더니 horizontal filling과 비슷한 성능을 보였다.<br>
카메라가 x축 방향으로 translate하여 occlusion이 일어난 부분을 채우는 것이기 때문에 x축 방향으로의 filling을 해야 한다고 생각했던 것에 비해 의외의 결과였다.<br>
이는 occlusion이 발생한 객체의 옆이나 위의 픽셀이 모두 동일한 객체에 속할 확률이 높기 때문으로 보인다. 
