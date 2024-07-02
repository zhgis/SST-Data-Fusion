
import pandas as pd
import numpy as np
from scipy import optimize
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from scipy.stats import linregress, gaussian_kde
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error


plt.rcParams['font.family'] = ['Arial']
data = np.loadtxt('valid_fy3e_fusion_415.txt')
print(data.shape)
m, n = data.shape
x = []
y = []
data_num = 0
for i in range (0,m):
    if (data[i][0] != -999 and (abs(data[i][0] - data[i][1]) < 5) ):
        x.append(data[i][1])
        y.append(data[i][0])
        data_num += 1
print(data_num)

x = np.array(x)
y = np.array(y)
xy = np.vstack([x,y])
z = gaussian_kde(xy)(xy)

C = round(r2_score(x,y),4)
rmse = round(np.sqrt(mean_squared_error(x,y)),3)
mae = round(mean_absolute_error(x,y),3)
# 绘制拟合线
x2 = np.linspace(-2,35)
y2 = x2
def f_1(x,A,B):
    return A*x + B
A1, B1 = optimize.curve_fit(f_1,x,y)[0]
print(A1,B1)
y3 = A1*x + B1
# 绘图
fig, ax = plt.subplots(figsize=(7,5),dpi=200)
dian = plt.scatter(x,y,cmap='furbo',edgecolors=None, c='k', s=16, marker='s')
ax.plot(x2,y2,color='k',linewidth=1.5,linestyle='--')
ax.plot(x,y3,color='r',linewidth=2,linestyle='-')
fontdict = {"size":17,"color":"k",'family':'Times New Roman'}
ax.text(2,32,r'$R^2=$'+str(round(C,3)),fontdict=fontdict)
ax.text(2,29,r'RMSE='+str(rmse),fontdict=fontdict)
ax.text(2,26,r'MAE='+str(mae),fontdict=fontdict)

ax.text(2,20,r'$N=$'+str(data_num),fontdict=fontdict)
ax.grid(False)
ax.set_xlim((0,10))
ax.set_ylim((0,10))
ax.set_xticks(np.arange(0,38,step=5))
ax.set_yticks(np.arange(0,38,step=5))
#设置刻度字体
labels = ax.get_xticklabels() + ax.get_yticklabels()
[label.set_fontname('Times New Roman') for label in labels]

for spine in ['top','bottom','left','right']:
    ax.spines[spine].set_color('k')
ax.tick_params(left=True,bottom=True,direction='in',labelsize=14)
#添加题目
titlefontdict = {"size":18,"color":"k",'family':'Times New Roman'}
ax.set_title('Fusion SST Data Valid',titlefontdict,pad=20)
fontdict1 = {"size":17,"color":"k",'family':'Times New Roman'}
ax.set_xlabel("Argo Values", fontdict=fontdict1)
ax.set_ylabel("Estimated Values ",fontdict=fontdict1)

if (B1<0):
    ax.text(2, 23, r'$y=$' + str(round(A1, 3)) + '$x$' + " - " + str(round(abs(B1), 3)), fontdict=fontdict)
else:
    ax.text(2, 23, r'$y=$' + str(round(A1, 3)) + '$x$' + " + " + str(round(B1, 3)), fontdict=fontdict)

text_font = {'family':'Times New Roman','size':'22','weight':'bold','color':'black'}

plt.savefig('valid_fy3e_fusion_415.png' ,dpi=300)
plt.show()



