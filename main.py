import cv2
import time
import numpy as np

left = cv2.imread("images/im2.png", cv2.IMREAD_GRAYSCALE) # 이미지 불러오기
right = cv2.imread("images/im6.png", cv2.IMREAD_GRAYSCALE) # 이미지 불러오기

y=left.shape[0]
x=left.shape[1]

kernel_size=3
div=(kernel_size**3)*2

def SSD(i, j, k):
    ans=0.0
    for a in range(kernel_size):
        for b in range(kernel_size):
            ans+=((right[i+a][j+b] - left[i+a][k+b])/div)**2
    return round(ans)

print(left)
print(right)
li=[]


for i in range(y-kernel_size+1):
    li.append([])
    for j in range(x-kernel_size+1): #하나의 disparity space image 생성
        li[i].append([])
        for k in range(x-kernel_size+1):
            d=SSD(i, j, k)
            li[i][j].append(d)
    arr=np.array(li[i])
    cv2.imwrite('disparity'+str(i)+'.jpeg', arr)
    








#cv2.imshow("im2", left) # 불러온 이미지를 im2라는 이름으로 창 표시.
#cv2.waitKey() # 키보드 입력이 들어올 때까지 창을 유지
#cv2.destroyAllWindows() # 모든 윈도우 창을 제거
