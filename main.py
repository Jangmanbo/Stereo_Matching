import cv2
import numpy as np
import time

left = cv2.imread("images/im2.png", cv2.IMREAD_GRAYSCALE) # 이미지 불러오기
right = cv2.imread("images/im6.png", cv2.IMREAD_GRAYSCALE) # 이미지 불러오기

y=left.shape[0]
x=left.shape[1]

kernel_size=3       #kernel size
cost_degree=0.3     #occlusion cost에 곱하는 값
criteria_right=1    #1이면 right 이미지가 기준, 0이면 left 이미지가 기준

DSI_size=x-kernel_size+1    #depth 이미지 가로 사이즈
depth_size=y-kernel_size+1  #depth 이미지 세로 사이즈
optimal_size=DSI_size-1

disparity_list=[]
depth_list=[]

#SSD 계산
def SSD(i, j, k):
    ans=0.0
    for a in range(kernel_size):
        for b in range(kernel_size):
            ans+=(right[i+a][j+b] - left[i+a][k+b])**2  #픽셀값이 차의 제곱을 더하기
    return (ans**0.5)/(kernel_size*1.5) #픽셀값이 255가 넘지 않도록 나눔

def NCC(i, j, k):
    ans=0
    #커널 사이즈에 맞게 슬라이싱
    right_kernel=right[i:i+kernel_size, j:j+kernel_size]
    left_kernel=left[i:i+kernel_size, k:k+kernel_size]
    #오른쪽, 왼쪽 커널 normalize
    right_kernel=normalize_kernel(right_kernel)
    left_kernel=normalize_kernel(left_kernel)
    for a in range(kernel_size):
        for b in range(kernel_size):
            ans+=(right_kernel[a][b] * left_kernel[a][b])   #cross correlation
    #SSD와 동일한 dynamic programming을 위해 1에서 빼기
    return 127.5 * (1 - ans)

def normalize_kernel(kernel):
    #이미지 리스트를 슬라이싱하면 양수로만 저장되는 문제
    #새 리스트를 생성하여 리턴
    new_kernel=[[0 for col in range(kernel_size)] for row in range(kernel_size)]

    #커널 내 픽셀값의 평균 구하기
    mean=0
    for i in range(kernel_size):
        for j in range(kernel_size):
            mean+=kernel[i][j]  #각 커널값을 더함
    mean /= kernel_size**2  #커널 개수로 나눔->평균

    #평균을 0으로 맞추고 분산 구하기
    sum=0
    for i in range(kernel_size):
        for j in range(kernel_size):
            new_kernel[i][j] = (kernel[i][j] - mean)    #각 픽셀값에 평균을 빼서 평균을 0으로
            sum+=new_kernel[i][j] ** 2
    variance=sum**0.5   #분산

    #분산으로 나누어 normalization
    #->픽셀값의 범위가 [-1,1]
    for i in range(kernel_size):
        for j in range(kernel_size):
            new_kernel[i][j] /= variance
    return new_kernel
    
    
            


#DSI 생성해서 disparity 폴더에 저장
def create_DSI():
    for i in range(depth_size):
        disparity_list.append([])
        for j in range(DSI_size): #하나의 disparity space image 생성
            disparity_list[i].append([])
            for k in range(DSI_size):
                d=SSD(i, j, k)
                disparity_list[i][j].append(d)
        #disparity 폴더에 저장
        arr=np.array(disparity_list[i])
        cv2.imwrite('disparity'+str(kernel_size)+'/disparity'+str(i)+'.jpeg', arr)
        print(i)

#cost 구하기
#DSI 픽셀값의 평균을 cost로 설정
def calculate_cost(DSI):
    cost=0
    for i in range(DSI_size):
        sum=0
        for j in range(DSI_size):
            sum+=DSI[i][j]
        cost+=sum/DSI_size
    cost/=DSI_size
    return cost*cost_degree #cost_degree를 곱해 occlusion cost 조정

#cost, 방향 리스트 초기화
def init_CM(C, M, cost):
    for i in range(1, DSI_size):
        C[i][0]=cost*i
        M[i][0]=2
        C[0][i]=cost*i
        M[0][i]=3

def dynamic_programming(DSI, C, M, cost):
    for i in range(1, DSI_size):
        for j in range(1, DSI_size):
            min1=C[i-1][j-1]+DSI[i][j]  #대각선 이동 시 cost
            min2=C[i-1][j]+cost         #아래로 이동 시 cost
            min3=C[i][j-1]+cost         #오른쪽 이동 시 cost
            C[i][j]=cmin=min(min1, min2, min3)  #지금까지의 최소 cost
            if (min1==cmin):    #occlusion이 일어나지 않음
                M[i][j]=1
            elif (min2==cmin):  #아래로 이동 (occlusion 발생)
                M[i][j]=2
            elif (min3==cmin):  #오른쪽으로 이동 (occlusion 발생)
                M[i][j]=3
            
#optimal path를 찾고 depth 이미지 생성
def create_path_img(i, j, DSI, M, num):
    depth_list.append([0])
    if criteria_right:  #right 이미지로 depth image 생성
        while(True):
            if j - i > 64:  #depth 범위 설정
                j-=1
                DSI[i][j]=255
                continue
            elif i > j and i != 0:  #depth 범위 설정
                i-=1
                DSI[i][j]=255
                depth_list[num].insert(0, j-i)
                continue
            if M[i][j]==1:  #occlusion이 일어나지 않음, depth 저장
                i-=1
                j-=1
                DSI[i][j]=255
                depth_list[num].insert(0, j-i)
            elif M[i][j]==2:    #occlusion이 일어남
                i-=1
                DSI[i][j]=255
                depth_list[num].insert(0, 0)
            elif M[i][j]==3:
                j-=1
                DSI[i][j]=255
            else:
                break
    else:   #left 이미지로 depth image 생성
        while(True):
            if j - i > 64:  #depth 범위 설정
                j-=1
                DSI[i][j]=255
                depth_list[num].insert(0, 0)
                continue
            elif i > j and i != 0:  #depth 범위 설정
                i-=1
                DSI[i][j]=255
                continue
            if M[i][j]==1:  #occlusion이 일어나지 않음, depth 저장
                i-=1
                j-=1
                DSI[i][j]=255
                depth_list[num].insert(0, j-i)
            elif M[i][j]==2:
                i-=1
                DSI[i][j]=255
            elif M[i][j]==3:    #occlusion이 일어남
                j-=1
                DSI[i][j]=255
                depth_list[num].insert(0, 0)
            else:
                break


    #optimal path를 그린 DSI를 path 폴더에 저장
    arr=np.array(DSI)
    cv2.imwrite('path'+str(kernel_size)+'/path'+str(num)+'.jpeg', arr)

#DSI를 이용해 optimal path 계산
def calculate_optimalpath():
    for i in range(depth_size):
        print(i)    #진행상황 체크
        DSI = cv2.imread("NCC"+str(kernel_size)+"/disparity"+str(i)+".jpeg", cv2.IMREAD_GRAYSCALE) # 이미지 불러오기
        cost = calculate_cost(DSI)  #DSI 이미지마다 cost 계산

        C = [[0 for col in range(DSI_size)] for row in range(DSI_size)]
        M = [[0 for col in range(DSI_size)] for row in range(DSI_size)]

        init_CM(C, M, cost)
        dynamic_programming(DSI, C, M, cost)
        create_path_img(DSI_size-1, DSI_size-1, DSI, M, i)  #optimal path와 depth 이미지 생성

#depth image의 밝기 변화를 크게
def normalize_depth():
    #max value 찾기
    max=0
    for i in range(depth_size):
        for j in range(DSI_size):
            if depth_list[i][j] > max:
                max=depth_list[i][j]

    #depth의 최대값이 255가 되도록 normalization
    mul=255.0/max
    for i in range(depth_size):
        for j in range(DSI_size):
            depth_list[i][j] *= mul

#depth image 폴더에 저장
def create_depth_img():
    arr=np.array(depth_list)
    cv2.imwrite('depth'+str(kernel_size)+'.jpeg', arr)

#x축 방향으로 hole filling
def horizontal_hole_filling():
    if (criteria_right):    #right 이미지인 경우
        for i in range(depth_size):
            for j in reversed(range(DSI_size - 1)):
                #occlusion인 경우 오른쪽 depth value로 filling
                if depth_list[i][j] == 0:
                    depth_list[i][j] = depth_list[i][j + 1]
    else:   #left 이미지인 경우
        for i in range(depth_size):
            for j in range(1, DSI_size):
                #occlusion인 경우 왼쪽 depth value로 filling
                if depth_list[i][j] == 0:
                    depth_list[i][j] = depth_list[i][j - 1]

#y축 방향으로 hole filling
def vertical_hole_filling():
    for i in range(DSI_size):
        for j in (range(1, depth_size)):
            #occlusion인 경우 위쪽 depth value로 filling
            if depth_list[j][i] == 0:
                depth_list[j][i] = depth_list[j - 1][i]

create_DSI()
calculate_optimalpath()
normalize_depth()
horizontal_hole_filling()
create_depth_img()