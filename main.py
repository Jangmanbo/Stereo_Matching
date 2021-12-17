import cv2
import time
import numpy as np

left = cv2.imread("images/im2.png", cv2.IMREAD_GRAYSCALE) # 이미지 불러오기
right = cv2.imread("images/im6.png", cv2.IMREAD_GRAYSCALE) # 이미지 불러오기

y=left.shape[0]
x=left.shape[1]

kernel_size=3
div=(kernel_size**3)*2

DSI_size=x-kernel_size+1
optimal_size=DSI_size-1

disparity_list=[]

#SSD 계산
def SSD(i, j, k):
    ans=0.0
    for a in range(kernel_size):
        for b in range(kernel_size):
            ans+=((right[i+a][j+b] - left[i+a][k+b])/div)**2    #kernel size에 기반하여 SSD 계산
    return round(ans)

#DSI 생성해서 disparity 폴더에 저장
def create_DSI():
    for i in range(y-kernel_size+1):
        disparity_list.append([])
        for j in range(DSI_size): #하나의 disparity space image 생성
            disparity_list[i].append([])
            for k in range(DSI_size):
                d=SSD(i, j, k)
                disparity_list[i][j].append(d)
        arr=np.array(disparity_list[i])
        cv2.imwrite('disparity/disparity'+str(i)+'.jpeg', arr)

#cost 구하기 (mean of DSI)
def calculate_cost(DSI):
    cost=0
    for i in range(DSI_size):
        sum=0
        for j in range(DSI_size):
            sum+=DSI[i][j]
        cost+=sum/DSI_size
    cost/=DSI_size
    return cost/1.5

def init_CM(C, M):
    for i in range(1, len(C)):
            C[i][0]=10*i
            M[i][0]=3
            C[0][i]=10*i
            M[0][i]=2

def dynamic_programming(DSI, C, M, cost):
    for i in range(optimal_size):
        for j in range(optimal_size):
            min1=C[i][j]+DSI[i+1][j+1]
            min2=C[i][j+1]+cost
            min3=C[i+1][j]+cost
            if(i<=j):
                C[i+1][j+1]=cmin=min(min1, min3)
            else:
                C[i+1][j+1]=cmin=min(min1, min2, min3)
            if (min1==cmin):
                M[i+1][j+1]=1
            elif (min3==cmin):
                M[i+1][j+1]=3
            elif (min2==cmin):
                M[i+1][j+1]=2

def create_path_img(i, j, DSI, M, num):
    while(True):
            if M[i][j]==1:
                i-=1
                j-=1
                DSI[i][j]=255
            elif M[i][j]==2:
                j-=1
                DSI[i][j]=255
            elif M[i][j]==3:
                i-=1
                DSI[i][j]=255
            else:
                break

    arr=np.array(DSI)
    cv2.imwrite('path/path'+str(num)+'.jpeg', arr)

#DSI를 이용해 optimal path 계산
def calculate_optimalpath():
    for i in range(DSI_size):
        DSI = cv2.imread("disparity/disparity"+str(i)+".jpeg", cv2.IMREAD_GRAYSCALE) # 이미지 불러오기
        cost = calculate_cost(DSI)

        C = [[0 for col in range(x-kernel_size+1)] for row in range(x-kernel_size+1)]
        M = [[0 for col in range(x-kernel_size+1)] for row in range(x-kernel_size+1)]

        init_CM(C, M)
        dynamic_programming(DSI, C, M, cost)
        create_path_img(optimal_size, optimal_size, DSI, M, i)

calculate_optimalpath()





#cv2.imshow("im2", left) # 불러온 이미지를 im2라는 이름으로 창 표시.
#cv2.waitKey() # 키보드 입력이 들어올 때까지 창을 유지
#cv2.destroyAllWindows() # 모든 윈도우 창을 제거
