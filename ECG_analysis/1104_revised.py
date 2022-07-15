
# coding: utf-8

# In[9]:
import os
import sys
import numpy as np
import scipy as sp
from scipy import signal
import matplotlib
from matplotlib import rcParams as rc
import matplotlib.pyplot as plt
import statistics
import pandas as pd
import time, datetime

	
'''-------------------------------'''

def R_peak(start,inverse_end, f_ECG):
    peak=0
    peak_num=0
    peak_point=[]
    peak_point_x=[]; peak_point_y=[]
    x=[]; y=[]
    wave_range=[]
    
    end= len(f_ECG)+inverse_end				#計算到倒數10秒
    bs= statistics.mean(f_ECG[start:end])	#全段平均
    sd= statistics.stdev(f_ECG[start:end])	#標準差
    R_thr= bs+ 2*sd							#R點需超過的值
    
    for i in range(start,end):			   #10~ -10秒
        x.append(i); y.append(f_ECG[i])    #畫心電圖
        if (int(f_ECG[i])-int(f_ECG[i-20]))>10:                   	#20單位時間內,電壓上升超過10單位,視為進入陡坡, 陡坡最大者稱為peak
            if (int(f_ECG[i])>=peak) and (f_ECG[i] > f_ECG[i-1]):
                peak = f_ECG[i]										#之後進下個迴圈，i自動+1
 

            elif (int(f_ECG[i])< peak) and (f_ECG[i-1]>=f_ECG[i-2]) and (f_ECG[i-1]==peak) and peak >= R_thr:
                peak_num+=1
                #print('R_peak',peak_num, '(x,y)=',i-1,peak)  
                peak_point_x.append(i-1)
                peak_point_y.append(peak)						#R點座標=(i-1, peak)
                wave_range.append([i-1-120,i-1+180])
                                                                #以R_peak(i-1)為零分格，前120,後180 訂為wave_range #(前後值待討論修改!)
                peak=0                    						#peak歸零,方便找下一個陡波
        else:
            peak=0                        						#雜訊太多時,不在條件內, 也要歸零

    return (peak_num, wave_range,peak_point_x,peak_point_y, x,y)

print()    




'''--------------------------------------'''

def split_wave(wave_range, peak_num, f_ECG):							#依R點為基準,做分割
    wave_y_list=[]
    for j in range (0,peak_num):
       wave_y_list.append(f_ECG[ wave_range[j][0]:wave_range[j][1] ]) #每個wave的初值,終值為: (wave_range[j][0],wave_range[j][1])
        
    return np.array(wave_y_list)      								   #將list轉成array(numpy)

'''--------------------------------------'''

def avg_wave(wave_y):
    matplotlib.rcParams['figure.figsize'] = (10.0, 5.0)
    sum = np.zeros((300,))    #創造一個'形狀'為300的 array,一開始裡面每個都是0
    for i in wave_y:          #此時的wave_y是def split wav回傳結果(np.array(wave_y_list) )
        sum = sum + i         #將wave_y中的每個項目加起來[[1],[2],[3]...} -> [1+2+3...]
    avg = sum/(len(wave_y))
    #plt.plot(avg,lw=3)       #畫修正偏差前的平均
    #plt.title('Average ECG')
    #plt.show()
    
    #print(wave_y.shape); print(avg.shape); print(len(wave_y))

    num=0
    new_wave=[]
    for i in wave_y:
        total_dev= 0			#total_dev要在wave_y迴圈內歸零,不然會一直遞增上去
        for j in range(0,300):
            dev=(i[j]-avg[j])**2 
            total_dev+=dev		#算wave各點與avg差值的平方和
        num+=1
        if total_dev > 60000:   #過大偏差的之後印出,此處不納入
            continue
			
        elif total_dev < 60000: #偏差不大的,列入new_wave  #(數值待討論)
            new_wave.append(i)
    '''
	print('detected: ', len(wave_y))              #原先抓到的peak數量
    print('new: ',      len(np.array(new_wave)))  #刪去偏差後的peak數量
    '''
	
    text1=""
    text1= "detected: "+ str((len(wave_y)))+ '\n' + "new:      "+ str(len(np.array(new_wave))) #存寫入text中
    
    new_wave_y = np.array(new_wave)
    sum= np.zeros((300,))			#設形狀為300的array,計算去除偏差後的平均波型
    for i in new_wave_y:
        sum = sum +i
    m_avg = sum/len(new_wave_y)
    return m_avg, wave_y, text1

'''--------------------------------------'''

        
def avg_sd_plot(m_avg, wave_y,filename, pwd):

	os.chdir(pwd)                                                         #將路徑移至相對位置的資料夾(開exe檔時的資料夾),待圖片存入
	os.chdir("./result/" +filename)        #將之後圖片存入新建資料夾

	x_major_ticks=np.arange(0,301,100)			#x軸100單位=心電圖上一大格= 200ms
	y_major_ticks=np.arange(-122.3,150,61.156)  #y軸上61.15單位=心電圖上一大格= 0.5mV
    
	x_minor_ticks=np.arange(0,301,20)
	y_minor_ticks=np.arange(-122.3,150,12.231111)
   
	sd= np.std(wave_y, axis=0)   #算標準差
	m_plus=np.zeros((300,))		 #設定300*1的array,方便運算
	m_minus=np.zeros((300,))
	m_plus=  m_avg+(sd)
	m_minus= m_avg-(sd)
    
	matplotlib.rcParams['figure.figsize'] = (10.0, 5.0)   #圖片大小
    
	rc['grid.linestyle']= '--'
	rc['grid.color']='red'
	rc['grid.linewidth']= '0.3'
	big= plt.gca()
	big.set_xticks(x_major_ticks)  #設定圖中格線
	big.set_yticks(y_major_ticks)
    
	plt.plot(m_avg, lw=3)          #畫平均&標準差
	plt.plot(m_plus, 'g:')
	plt.plot(m_minus, 'g:')
	plt.title('avg ECG (del dev) +/- 1sd', fontsize=18)
	plt.ylim(-50,150)
	big.grid()					   #畫出圖中格線
	plt.savefig('1_avg ECG.jpg')   #圖片存檔
	plt.clf()					   #清除資訊,免得下個圖畫進去(clean fig)
    

    
'''--------------------------------------'''


def normal_R(peak_point_x, wave_y, text1):
    sum = np.zeros((300,))    
    for i in wave_y:          
        sum = sum + i       
    avg = sum/(len(wave_y))
    
    num=0
    new_wave=[]
    del_list=[]
    for i in wave_y:
        total_dev= 0
        for j in range(0,300):
            dev=(i[j]-avg[j])**2
            total_dev+=dev
        num+=1
        if total_dev > 60000:   
            del_list.append(num-1)
    normal_R= [x for x in peak_point_x if peak_point_x.index(x) not in del_list]  ##新招 學起來!!
    #del_list是要刪除的序列[2,5,8...], 不在del_list中的index, 就保留為normal_R
    
	#print(len(peak_point_x)); print(len(normal_R)); print(normal_R)
    
    #for i,x in enumerate(normal_R):
        #print(i,x)
    
    HR=[]
    for i in range(1,len(normal_R)):
        RR= (normal_R[i]-normal_R[i-1]) / 500
        #print(RR)
        if int(60/RR)> 20 and int(60/RR) <200:
                HR.append(60/ RR)
    
    HR_avg= statistics.mean(HR)
    RR= 60 / HR_avg
    '''print ('HR: ', int(HR_avg) )'''
    
    text2=""
    text2 = text1 + '\n'+'HR: '+ str( int(HR_avg) )+'\n'
    
    return   RR, text2

'''--------------------------------------'''

def PQRST_anl(m_avg):
# R    
    Ry= (m_avg[120]) 

# P                        #選0~100最大值為p點y值
    list_p= m_avg[0:100]   #將array轉成list,才能算max
    py= max(list_p) 
    px=[]
    for i in range(0,100):
        if (py - m_avg[i]) == 0:
            px.append(i)   #找px
    px= px[0]

# T                        #選140~199最大值為t點y值
    list_t= m_avg[140:299] #將array轉成list,才能算max
    ty= max(list_t)
    tx=[]
    for i in range(140,299):
        if (ty- m_avg[i] ) == 0:
            tx.append(i)
    tx=tx[0]
 
#Q_new
    slope=[]									 #Q,S點不一定是minimum,因此想到以下方法來抓Q,S點(概念: m[i+8]-m[i]/m[i]-m[i-3] ),再加條件修正
    q=[]
    for i in range(px+10,120):
        if abs(m_avg[i] - m_avg[i-3]) <= 1:      #m[i]-m[i-3]升幅太小or為負的,直接視為1,相除才不會出問題
            a= abs(m_avg[i] - m_avg[i-3])
            a= 1
            s= ( abs(m_avg[i+8]-m_avg[i]) / a )
            slope.append(s)
        elif abs(m_avg[i] - m_avg[i-3]) > 1:     #紀錄前後升幅,8單位時間內上升(m[i+8]-m[i])最大的起點訂為Q點(同時除以前3單位時間變化,才能找到轉折點)
            b= abs(m_avg[i] - m_avg[i-3])
            s = ( abs(m_avg[i+8]-m_avg[i]) / b )
            slope.append(s)
    maxi= max(slope)                             #找到最大斜率
    #print(slope, 'max_Q', maxi)
    for i in range(px+10,120):
        if abs(m_avg[i] - m_avg[i-3]) <= 1:
            a= abs(m_avg[i] - m_avg[i-3])
            a= 1
            s= ( abs(m_avg[i+8]-m_avg[i]) / a )
            slope.append(s)
        elif abs(m_avg[i] - m_avg[i-3]) > 1:
            b= abs(m_avg[i] - m_avg[i-3])
            s = ( abs(m_avg[i+8]-m_avg[i]) / b )
            slope.append(s)
        if s == maxi:                           #找與最大斜率相對應的s點
            q.append(i)
    qx= q[0]; qy= m_avg[qx]

    
#S_new
    slope=[]                                    #與Q點概念相仿,只是正負顛倒
    ss=[]
    for i in range(120,200):
        if abs(m_avg[i+3] - m_avg[i]) <= 1:
            a= abs(m_avg[i+3] - m_avg[i] )
            a= 1
            s= ( abs(m_avg[i]-m_avg[i-8]) / a )
            slope.append(s)
        elif abs(m_avg[i+3] - m_avg[i]):
            b= abs(m_avg[i+3] - m_avg[i])
            s = ( abs(m_avg[i]-m_avg[i-8]) / b )
            slope.append(s)
    maxi= max(slope)
    #print(slope, 'max_S', maxi)
    for i in range(120,200):
        if abs(m_avg[i+3] - m_avg[i]) <= 1:
            a= abs(m_avg[i+3] - m_avg[i] )
            a= 1
            s= ( abs(m_avg[i]-m_avg[i-8]) / a )
            slope.append(s)
        elif abs(m_avg[i+3] - m_avg[i]) :
            b= abs(m_avg[i+3] - m_avg[i])
            s = ( abs(m_avg[i]-m_avg[i-8]) / b )
            slope.append(s)
        if s == maxi:
            ss.append(i)
    sx= ss[0]; sy= m_avg[sx]

    
#波型細節

    import statistics
  
    int_m=[]
    for i in range(0,300):
        int_m.append(round(m_avg[i]))     #將波型數值轉為整數,方便看觀察數值分布
    bs= statistics.median(int_m)		  #找中位數(就相當於眾數)作為baseline,不找眾數原因:若有兩個眾數則無法判斷
    
    #訂P波起點
    int_m_0p=[]
    for i in range(0,px):
        int_m_0p.append(round(m_avg[i]))
    bs_0p= statistics.median(int_m_0p)    #bs_0p為起點至P點的baseline
    ps=[]
    for i in range(0,px):
        if abs(round(m_avg[i]) - bs_0p ) <= 1:      
            ps.append(i)
    psx= ps[-1]; psy= (m_avg[psx])        #屬於baseline的最後一個點(離開baseline的第一個點),為P波起點
    
    #訂P波終點,Q波起點
    int_m_pq=[]
    for i in range(px,qx):
        int_m_pq.append(round(m_avg[i]))
    bs_pq= statistics.median(int_m_pq)
    
    pe=[]
    for i in range (px,qx):
        if  abs(round(m_avg[i] - bs_pq)) <=1:
            pe.append(i)
    pex=pe[0]; pey= (m_avg[pex])        #從P波進入baseline的第一個點,訂為P波終點
    qsx=pe[-1]; qsy=(m_avg[qsx])		#屬於baseline的最後一點, 訂為Q波起點

    
    #訂T波起點終點
    ts=[]; te=[]
    
    if (qy- bs_pq) <= 0:                        #典型狀況:Q點低於baseline
												#為何用P至Q的baseline:定義,ST segment有無elevation or depression,是以PQ段的baseline為準
        for i in range(sx,tx):
            if abs(round (m_avg[i]-bs_pq) ) <=1:
                ts.append(i)
        tsx = ts[-1]; tsy = m_avg[tsx]          #S,T段中屬於baseline的最後一個點(脫離basleine的第一個點),訂為T波起點
    
        for i in range(tx,300):
            if abs(round (m_avg[i]-bs_pq) ) <=1:
                te.append(i)
        tex= te[0]; tey= m_avg[tex]             #T至結束中,第一個進入baseline的點,訂為T波終點

    

    mean_st = statistics.mean(m_avg[sx:tx])

    if (qy- bs_pq) > 0:                        #非典型狀況:Q點高於baseline
        for i in range(sx,tx):
            if abs(round (m_avg[i]- mean_st)) <=1:
                ts.append(i)
        tsx = ts[-1]; tsy = m_avg[tsx]
    
        for i in range(tx,300):
            if abs(round (m_avg[i]- mean_st)) <=1:
                te.append(i)
        tex= te[0]; tey= m_avg[tex]
    
    return Ry, px,py, tx,ty, qx,qy, sx,sy,   psx,psy, pex,pey, qsx,qsy,  tsx,tsy, tex,tey #, qex,qey
       
'''--------------------------------------'''

def avg_point_plot(m_avg, Ry, px,py, tx,ty, qx,qy, sx,sy, psx,psy, pex,pey, qsx,qsy, tsx,tsy, tex,tey, filename, pwd ): #, qex,qey

    os.chdir(pwd)														#切換至現在路徑(執行EXE檔時的路徑)
    os.chdir("./result/"+filename)		#切換至新建的資料夾

    x_major_ticks=np.arange(0,301,100)									#同AVG,設定格線大小
    y_major_ticks=np.arange(-122.3,150,61.156)
    x_minor_ticks=np.arange(0,301,20)
    y_minor_ticks=np.arange(-122.3,150,12.231111)
    
    rc['grid.color']='red'; rc['grid.linestyle']='--'; rc['grid.linewidth']='0.3'
    big= plt.gca()
    big.set_xticks(x_major_ticks)
    big.set_yticks(y_major_ticks)
    
    rc['figure.figsize'] = (10.0, 5.0)
    plt.plot(m_avg, lw=2, color='blue')
    
    plt.scatter(120, m_avg[120], color='red')			#點出PQRST(紅色)
    plt.scatter(px,py, color='red')
    plt.scatter(tx,ty, color='red')
    plt.scatter(qx,qy, color='red')
    plt.scatter(sx,sy, color='red')
    
    plt.scatter(psx,psy, color='cyan'); plt.scatter(pex,pey, color='cyan')      #點出P波,T波起點終點(cyan,magenta色)
    plt.scatter(tsx,tsy, color='magenta');plt.scatter(tex,tey, color='magenta')
    
    plt.title('avg ECG (del dev)', fontsize=18)
    plt.ylim(-50,150)
    big.grid()
    plt.savefig('2_PQRST.jpg')                          #存檔
    plt.clf()											#清除資料(clean fig)

'''
def ECG_plot(peak_x,peak_y,x,y, filename):
    
    #os.chdir("D:/pyth_file/guo_lab/result/"+str(today)+"_"+str(timing)+"_"+filename)
    rc['figure.figsize'] = (40.0,15.0)
    plt.title('total ECG with high pass filter')
    plt.scatter(peak_x, peak_y, color='red')
    plt.plot(x,y,'g-')
    plt.savefig('3.total ECG.jpg')
    plt.clf()
'''

def plot_dev(m_avg,wave_y, filename, pwd):                           #印出偏差過大的心律
	
	os.chdir(pwd)
	os.chdir("./result/"+filename+"/deviation" )     #同之前
	num=0
	d_num=0
	for i in wave_y:
		total_dev= 0
		for j in range(0,300):
			dev=(i[j]-m_avg[j])**2
			total_dev+=dev
		if total_dev > 60000:   #待研究
			d_num+=1
			rc['figure.figsize'] = (2.0 , 1.0)
			plt.suptitle('Deviation wave',fontsize=14)
			plt.title('wave: '+ str(d_num) +'\n'+ 'dev: '+ str(total_dev), fontsize=10)
			plt.plot(i, color='orange')
			plt.savefig(str(d_num)+"dev_wave.jpg") 
			plt.clf()
			
def Ana(m,qx,psx,sx,Ry,py,qy,sy,ty,tex,RR,qsx, text2):
	int_m=[]
	for i in range(0,300):
		int_m.append(int(m[i]))
	bs= statistics.median(int_m)				#設定baseline,voltage以此為標準


	PR_i= int( (( qx - psx )/500 ) *1000 )      #PR interval= P波起點~Q波
	QRS = int( ((sx -qx)/500) *1000      )		#QRS duration=Q波~S波	
	R   = ( (Ry- bs) * (1000* (1.8/(256*860)))  )
	P   = ( (py- bs) * (1000* (1.8/(256*860)) ) )
	Q   = ( (qy- bs) * (1000* (1.8/(256*860)) ) )
	S   = ( (sy- bs) * (1000* (1.8/(256*860)) ) )
	T   = ( (ty- bs) * (1000* (1.8/(256*860)) ) )
	QT  = int( ((tex-qx)/500)* 1000 )           #QT interval= Q波~T波終點
	QTc = int( ((tex-qx)/500)* 1000 / (RR**(1/2)) ) #標準化QT
	RR  =  int(RR*1000)
	Qwave_dura= ((qx-qsx)/500)*1000
	'''
	print('\n','PR_interval (ms)',PR_i,
      '\n','QRS duration(ms)',QRS,
      '\n','RR interval (ms)',RR,
      '\n','QT          (ms)',QT,
      '\n','QTc         (ms)',QTc,
      '\n','R_voltage(mV): ',"%.2f" %R, 
      '\n','P wave (mV):   ',"%.2f" %P,
      '\n','T wave (mV):   ',"%.2f" %T,
      '\n', 'Q wave (mV):   ',"%.2f" %Q,
      '\n', 'S wave (mV):   ',"%.2f" %S)
    '''	
	text3=""
	text3= text2+ '\n'+ '[Analysis]'+ '\n'+'PR_interval (ms)'+str(PR_i)+'\n'+  'QRS duration(ms)'+str(QRS) +'\n'+  'RR interval (ms)'+str(RR)  +'\n'+  'QT          (ms)'+str(QT)  +'\n'+  'QTc         (ms)'+str(QTc)+'\n'+ 'R_voltage(mV): '  +str("%.2f" %R)+ '\n'+'P wave (mV):   '+str("%.2f" %P)+'\n'+'T wave (mV):   '+str("%.2f" %T)+'\n'+ 'Q wave (mV):   '+str("%.2f" %Q)+'\n'+ 'S wave (mV):   '+str("%.2f" %S)
	#就是把print的那一串寫入text
	
	return PR_i, QRS, R, Q, QTc, Qwave_dura, S, text3
	
def Ana_problem(PR_i, QRS, R, Q, QTc, Qwave_dura, S, qx,sx, tsx, m, text3):
	'''print('[analysis and suspected cardiac problem]')'''

#check LVH
	
	if R >= 1.4:
		a= 'high R voltage, suspected LVH'
	else:
		a= 'LVH(-)'

	text4=""
	text4= text3+ '\n'+'\n'+'[Suspected cardiac problem]'+'\n'+ a

#check RVH(+/-)
	if abs(Q)>= R:
		b= 'suspected RVH or post.LBBB'
	else:
		b='RVH(-)'

	text4+= '\n'+ b
	
#check ST段
	mean_st = statistics.mean(m[sx:tsx])
	ss=[]
	for i in range(0,qx):
		ss.append(round(m[i]))
	bs_pq   = statistics.median(ss)
#print('mean_ST:',mean_st,'bs:', bs_pq)

	ST= (mean_st - bs_pq)
	if ST >= 12:
		c='probable ST_elevation, suspected STEMI or pericarditis'
	elif ST <= (-6):
		c='probable ST_depression, suspected NSTEMI or measured error'
	else:
		c='normal ST segment'
	
	text4+= '\n'+ c
    

#check 深Q波    
	if ( abs(Q) >= 1/3*R ) and  (  Qwave_dura > 40 ):
		d='deep Q wave, suspected AMI'
	else:
		d='no deep Q wave'
		
	text4+= '\n'+d
	
#check 1st AV block
	if PR_i > 200:
		e='long PR interval, suspected 1st AV block'
	else:
		e='1st AV block(-)'

	text4+= '\n'+e
	
#check VA, BBB
	if QRS >= 120:
		f='long QRS, suspected VA or BBB'
	else:
		f='normal QRS duration'
	text4+= '\n'+f
	
#check PE
	if abs(S) >0.5:
		g='deep S wave, suspected pulmonary embolism, check Q wave on lead3 and d-dimer'
	else:
		g='no deep S wave, pulmonary embolism(-)'
		
	text4+= '\n'+g
	
	if QTc >=440:
		h='prolong QTc'
	else:
		h='normal QTc'

	text4+= '\n'+ h
	text= text4
	return text
	
def Txt(pwd, filename, text):
	os.chdir(pwd)
	os.chdir("./result/"+filename )
	file= open('result.txt','w')
	file.write(text)
	file.close()





'''-----------'''
def main():
	from tkinter.filedialog import askopenfilename
	pwd = os.getcwd()
	file=sys.argv[1]
	filename= os.path.split(file)[1]
	#print(file, '\n', filename)
	with open (file,'rb') as file_1:           #開檔,read binary
		a= np.fromfile(file_1, dtype=np.uint8) #16進位轉10進位, 以numpy表示
		file_1.close()
		ECG=a[512:]                            #前512個點非心電資訊


	fps=500
	def butter_highpass(cutoff, fs, order=5):  #做high pass filter
		#nyq = 0.5 * fs
		#ormal_cutoff = cutoff / nyq
		b, a = signal.butter(order,cutoff /(2 * fs), btype='high', analog=False)
		return b, a

	def butter_highpass_filter(data, cutoff, fs, order=5):
		b, a = butter_highpass(cutoff, fs, order=order)
		y = signal.filtfilt(b, a, ECG)
		return y

	f_ECG = butter_highpass_filter(ECG,2,fps)



	os.chdir(pwd)					#轉換成現在的路徑
	os.chdir("./result")
	os.makedirs(filename)
	os.chdir(filename)
	os.mkdir("deviation")

	
	
	start= 10  *500
	inverse_end=   (-10)  *500

	peak_num,wave_x, peak_x,peak_y, x,y =   R_peak(start,inverse_end, f_ECG)
	wave_y=                                 split_wave( wave_x,peak_num, f_ECG)
	m,wave_y, text1=                        avg_wave(wave_y)

	avg_sd_plot(m,wave_y, filename,pwd)

	RR, text2     =                          normal_R(peak_x, wave_y, text1)

	Ry, px,py, tx,ty, qx,qy, sx,sy , psx,psy, pex,pey,  qsx,qsy, tsx,tsy, tex,tey             =PQRST_anl(m)  
	avg_point_plot(m, Ry, px,py, tx,ty, qx,qy, sx,sy, psx,psy, pex,pey, qsx,qsy, tsx,tsy, tex,tey,filename ,pwd)        

	PR_i, QRS, R, Q,  QTc,Qwave_dura, S,text3 =       Ana(m,qx,psx,sx,Ry,py,qy,sy,ty,tex,RR,qsx, text2)
	text=                                             Ana_problem(PR_i, QRS, R , Q, QTc, Qwave_dura,S, qx, sx, tsx, m, text3)
	
	Txt(pwd, filename, text)
	
	plot_dev(m, wave_y, filename,pwd)
	#ECG_plot(peak_x,peak_y,x,y)

if __name__ == "__main__":
	main()


#%%
    
