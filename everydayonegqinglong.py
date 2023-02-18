import requests
import json
import time
import random
import re
import os
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

#注意事项：
'''
注意事项：
    
    脚本优先领取每日1G，领取每日1G完成后才会触发，7天10G和我的特权签到功能
    
    仅限广州电信号码，仅限广州电信号码，仅限广州电信号码，仅限广州电信号码

    
    CK有效期30分钟，脚本随机等在2分钟内，所以脚本在25分钟内必须运行2次，
    才能有保证容许1次网络不通的情况，确保1次网络不通CK不失效，提高可用性
    
    建议最少每12分钟运行一次脚本，确保容许1次网络不通CK不失效，设置定时参考:    50 0/11 * * * ? 

    
    获取ck地址：
    https://vip.mini189.cn/yqt_fans/html/wechatIndex/index.html

'''

#CK配置 
dx_cookies=[    
    #多个账户复制粘贴多行并修改
    #参考示例：是否启用总开关(必须),是否7天10G(必须),是否特权签到(必须),ck值(必须),昵称/手机号(可选)

    {"status":True,"sevenG":True,"sign":True,"ck":"JSESSIONID=xxxxxxx.mini189c","user":"  "},

]

#是否发送青龙通知
sendNotify=True
#收集通知内容
msgg=[]
#通知的标题
title='广州电信每日1G青龙脚本'

#锁住多线程
lock = Lock() 


#入口，处理配置文件
def main():
    try:         
        start = time.time()
        i=1;
        with ThreadPoolExecutor(20) as  thread_pool:#定义20个线程池执行此任务
            for item in dx_cookies:
                if item['status']:
                    thread_pool.submit(distribute,[i,item])    #开启线程                
                    i+=1
                else:
                    print(f'{item["user"]}:总开关未启用')
        size = len(dx_cookies)
        end = time.time()
        print(f'总共耗时:{int(end - start)}秒,共{size}条记录，运行{i-1}条')    
    except Exception as e:
        print(f'每日1G青龙脚本运行出错,{e}')
        msgg.append(f'每日1G青龙脚本运行出错,{e}')
    finally:
        #有异常则，发送青龙通知
        if sendNotify and os.path.exists("./sendNotify.js") and msgg:
            if not os.path.exists("./invoke_notify.js"):
                invoke_notify='''
                    const notify = require('./sendNotify.js');
                    const title = process.argv[2];
                    const content = process.argv[3];
                    notify.sendNotify(`${title}`, `${content}`);
                '''
                with open("./invoke_notify.js",'w',encoding='utf-8') as f:
                    f.write(invoke_notify)
                    f.close()
            content='\n'.join(msgg)
            os.system(f"node invoke_notify.js '{title}\n' '{content}'")
            
#分发任务
def distribute(args):
    t=args[0]
    item=args[1]
    ck=item['ck']
    user = getUserName(ck)
    t = 10 if t>10 else t
    tt = random.randint(t*10,t*10+20)
    print(f'{args[0]}:{user};随机等待{tt}秒')    
    time.sleep(tt)
    #每日1G
    ret = getEveryDay1G(ck)
    #每日1G开通成功后才触发710和特权签到
    if  ret : 
        #7天10G
        if item['sevenG']:
            getSummer10GActivityZg(ck)
        #特权签到
        if  item['sign']:
            getGrowthTaskExperienceDetail(ck)    


#   提交7天10G
def submitModelOrder10G(userInfoId,customerNumber,ck,checkMd):
    try:
        user = getUserName(ck)
        url = 'https://vip.mini189.cn/yqt_fans/orders/submitModelOrder'
        headers={
            "User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",    
            "Cookie":ck
        }    
        data_10Gbody={
            "credentialsType":"身份证",
            "applyCustomerModel":"true",
            "remark":"",
            "specStr1":"",
            "specStr2":"WAP",
            "productName":"280",
            "goodsName":"7天10GB流量包",
            "payType":"",
            "goodsPrice":"0",
            "userActivityStgId":"",
            "userActivityId":"1958",
            "businessType":"7",
            "orderType":"7",
            "jobNumber":"33000682",
            "userInfoId":userInfoId,
            "isPushZn":"1",
            "agreementTypeName":"增值业务",
            "userActivityIsVali":"1",
            "refer":"gzdxYLYHD-10G",
            "autoFillCustomer":"1",
            "customerNumber":customerNumber,
            "number":customerNumber,
            "activityInfoModel":"true",
            "agreeGw":"0",
            "mpopenid":"",
            "zwNum":"",
            "busiNo":"",
            "aiNum":"",
            "checkMd":checkMd        
        }
        # response = requests.post(url=url,data=data_10Gbody,headers=headers)
        response = mypost(url=url,data=data_10Gbody,headers=headers,name='提交7天10G')               
        if response == None:
            return None
        # jsont = response.json()
        
        html_text = response.text;
        obj = re.compile(r'提交失败',re.S)
        m = obj.search(html_text)
        obj2 = re.compile(r'提交成功',re.S)
        m2 = obj2.search(html_text)
        if m:
            #结果
            sc1 = re.search('p10">(?P<result>.*?)</p>',html_text)
            #原因
            sc2 = re.search('mt10">(?P<reson>.*?)<',html_text)        
            if sc1 and sc2:            
                sc1s = sc1.group('result')
                sc2s = sc2.group('reson')
                print(f'{user}:7天10G:{sc1s}--->{sc2s}')
                msgg.append(f'{user}:7天10G:{sc1s}--->{sc2s}')
        elif m2:
            resp = re.search('</i>(?P<resp>.*?)！',html_text)
            order = re.search('fwb">(?P<order>.*?)</p>',html_text)
            tip = re.search('fcgray">(?P<tip>.*?)</p>',html_text)
            if resp and order and tip:            
                respt = resp.group('resp')
                ordert = order.group('order')
                tipt = tip.group('tip')
                print(f'{user}:7天10G:{respt}--->{ordert}--->{tipt}')
                msgg.append(f'{user}:7天10G:{respt}--->{ordert}--->{tipt}')
    except Exception as e:
        print(f'提交7天10G出错,{e}')
        msgg.append(f'提交7天10G出错,{e}')            

#查询7天10G资格
def getSummer10GActivityZg(ck):
    try:
        user = getUserName(ck)
        url = 'https://vip.mini189.cn/yqt_fans/activtiyById/getSummer10GActivityZg'
        headers={
            "User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",    
            "Cookie":ck
        }
        data={
            "roadType":"gzdxYLYHD-10G"
        }
        # jsont = requests.post(url=url,data=data,headers=headers).json()
        response = mypost(url=url,data=data,headers=headers,name='查询7天10G资格')               
        if response == None:
            return None
        jsont = response.json()
        
        #logger.debug(jsont)
        if  jsont['status'] != 'success':
            print(f'{user}:查询7天10G资格异常,{jsont["msg"]}')
            msgg.append(f'{user}:查询7天10G资格异常,{jsont["msg"]}')
        else:
            if jsont['data']['accountList']:
               userInfoId= jsont['data']['userInfoId']  #获取用户ID
               customerNumber=jsont['data']['loginNumber']  #获取手机号
               checkMd=jsont['data']['accountMap'][customerNumber]  #获取校验码
               #print(f'{user}:查询7天10G,可以领取啦') 
               submitModelOrder10G(userInfoId,customerNumber,ck,checkMd)    #领取7天10G
            else:
                print(f'{user}:查询7天10G,暂不可领取')
    except Exception as e:
        print(f'查询7天10G资格出错,{e}')
        msgg.append(f'查询7天10G资格出错,{e}')
        
#获取签到当前用户等级
def getUserVipGradeInfo(ck):
    try:
        user = getUserName(ck)
        url = 'https://vip.mini189.cn/yqt_fans/vipGradeExperienceInfo/getUserVipGradeInfo'
        headers={
            "User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",    
            "Cookie":ck
        }
        # jsont = requests.post(url=url,headers=headers).json()
        response = mypost(url=url,headers=headers,name='获取签到当前用户等级')               
        if response == None:
            return None
        jsont = response.json()
        
        if jsont['status'] != 'success':
            print(f'{user}:获取特权签到异常,{jsont["msg"]}')
            print(jsont)
        else:
            hasSendUpgrade = jsont['data']['hasSendUpgrade']   #是否升级
            if hasSendUpgrade != 0 :
                #升级领取经验值
                receiveGradeUpgrade(ck)
                time.sleep(2)
                #递归自调
                getUserVipGradeInfo(ck)
                return                
            currentGrade = jsont['data']['currentGrade']   #当前等级
            currentGradeContent = jsont['data']['currentGradeContent']  #当前称号
            currentMonthGrade = jsont['data']['currentMonthGrade']  #本月已获得
            total = jsont['data']['total']  #总经验
            nextGradeDifferExperience = jsont['data']['nextGradeDifferExperience']  #下一级还需
            nextGradeExperience = jsont['data']['nextGradeExperience']  #下一级经验
            print(f'{user}:特权签到,当前经验:{total},等级:V{currentGrade}级,称号:{currentGradeContent},下一级还需:{nextGradeDifferExperience},本月已获得:{currentMonthGrade}')
            msgg.append(f'{user}:特权签到,当前经验:{total},等级:V{currentGrade}级,称号:{currentGradeContent},下一级还需:{nextGradeDifferExperience},本月已获得:{currentMonthGrade}')
    except Exception as e:
        print(f'获取签到用户等级出错,{e}')
        msgg.append(f'获取签到用户等级出错,{e}')
        
        
#升级领取经验值
def receiveGradeUpgrade(ck):
    try:
        user = getUserName(ck)
        url = 'https://vip.mini189.cn/yqt_fans/vipGradeExperienceInfo/receiveGradeUpgrade'
        headers={
            "User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",    
            "Cookie":ck
        }        
        # jsont = requests.post(url=url,headers=headers).json()
        response = mypost(url=url,headers=headers,name='升级领取经验值')               
        if response == None:  
            return None
        jsont = response.json()
        #logger.debug(jsont)
        if jsont['status'] != 'success':
            print(f'{user}:升级领取经验值异常,{jsont["msg"]}')
            print(jsont)
        else:
            exp = jsont['data']
            print(f'{user}:升级领取经验值成功！获得{exp}经验')
            msgg.append(f'{user}:升级领取经验值成功！获得{exp}经验')
    except Exception as e:
        print(f'升级领取经验值,{e}')
        msgg.append(f'升级领取经验值,{e}') 
        

#领取经验值
def receiveExperience(ck,vname,vdata):
    try:
        # https://vip.mini189.cn/yqt_fans/vipGradeExperienceDetail/receiveExperience?type=3&orderNo=184112
        user = getUserName(ck)
        url = 'https://vip.mini189.cn/yqt_fans/vipGradeExperienceDetail/receiveExperience'
        headers={
            "User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",    
            "Cookie":ck
        }        
        # jsont = requests.post(url=url,data=vdata,headers=headers).json()
        response = mypost(url=url,data=vdata,headers=headers,name='领取经验值')               
        if response == None:  
            return None
        jsont = response.json()
        #logger.debug(jsont)
        if jsont['status'] != 'success':
            print(f'{user}:{vname}异常,{jsont["msg"]}')
            print(jsont)
        else:
            exp = jsont['data']['currentGiftExp']
            print(f'{user}:{vname}成功！获得{exp}经验')
            msgg.append(f'{user}:{vname}成功！获得{exp}经验')
    except Exception as e:
        print(f'领取经验值出错,{e}')
        msgg.append(f'领取经验值出错,{e}') 



#获取特权签信息
def getGrowthTaskExperienceDetail(ck):
    try:
        user = getUserName(ck)
        url = 'https://vip.mini189.cn/yqt_fans/vipGradeExperienceDetail/getGrowthTaskExperienceDetail'
        headers={
            "User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",    
            "Cookie":ck
        }
        # jsont = requests.post(url=url,headers=headers).json()
        response = mypost(url=url,headers=headers,name='获取特权签信息')               
        if response == None:  
            return None
        jsont = response.json()
        
        if jsont['status'] != 'success':
            print(f'{user}:获取特权签信息异常,{jsont["msg"]}')
            print(jsont)
        else:
            # 签到 1
            if not jsont['data']['isSign']:
                receiveExperience(ck,"签到领取经验",{"type":1,"couponId":None,"orderNo":None})            
            else:
                print(f'{user}:特权签到,今日已签到')
            #使用1个权益 2
            actIds = jsont['data']['actIds']   
            if actIds :
                print(f'{user}:使用1个权益领取经验')
                msgg.append(f'{user}:使用1个权益领取经验')
                for item in actIds:                
                    receiveExperience(ck,"使用1个权益领取经验",{"type":2,"couponId":item,"orderNo":None})
                    time.sleep(5)
            #办理1个优惠业务   3
            discountIds = jsont['data']['discountIds']
            if discountIds :
                print(f'{user}:办理1个优惠业务领取经验')
                msgg.append(f'{user}:办理1个优惠业务领取经验')
                for item in discountIds:
                    receiveExperience(ck,"办理1个优惠业务领取经验",{"type":3,"couponId":None,"orderNo":item})
                    time.sleep(5)
            #办理1个升级业务   4
            upgradeIds = jsont['data']['upgradeIds']
            if upgradeIds :
                print(f'{user}:办理1个升级业务领取经验')
                msgg.append(f'{user}:办理1个升级业务领取经验')
                for item in upgradeIds:                
                    receiveExperience(ck,"办理1个升级业务领取经验",{"type":4,"couponId":None,"orderNo":item})
                    time.sleep(5)
            #查询用户等级
            getUserVipGradeInfo(ck)
    except Exception as e:
        print(f'获取特权签信息出错,{e}')
        msgg.append(f'获取特权签信息出错,{e}')        



#每日1G提交
def submitOrder1G(userInfoId,customerNumber,ck):
    try:
        user = getUserName(ck)
        url = 'https://vip.mini189.cn/yqt_fans/orders/submitModelOrder'
        submit_body={
            "credentialsType":"身份证",
            "applyCustomerModel":"true",
            "remark":"roadType\":\"undefined",
            "specStr1":"",
            "specStr2":"WAP",
            "productName":"2703",
            "goodsName":"0元1G国内流量日包201511",
            "payType":"",
            "goodsPrice":"0",
            "userActivityStgId":"",
            "userActivityId":"1908",
            "businessType":"7",
            "orderType":"7",
            "jobNumber":"33000682",
            "userInfoId":userInfoId,
            "isPushZn":"1",
            "agreementTypeName":"增值业务",
            "userActivityIsVali":"1",
            "refer":"mr1G-qwyrym",
            "autoFillCustomer":"1",
            "customerNumber":customerNumber,
            "number":customerNumber,
            "activityInfoModel":"true",
            "couponId":""
        }
        headers={
            "User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",    
            "Cookie":ck
        }
        # response = requests.post(url=url,data=submit_body,headers=headers)        
        response = mypost(url=url,data=submit_body,headers=headers,name='提交每日1G')               
        if response == None:  
            return None
        # jsont = response.json()
        
        html_text = response.text;
        obj = re.compile(r'提交失败',re.S)
        m = obj.search(html_text)
        obj2 = re.compile(r'提交成功',re.S)
        m2 = obj2.search(html_text)
        if m:
            #结果
            sc1 = re.search('p10">(?P<result>.*?)</p>',html_text)
            #原因
            sc2 = re.search('mt10">(?P<reson>.*?)<',html_text)        
            if sc1 and sc2:            
                sc1s = sc1.group('result')
                sc2s = sc2.group('reson')
                print(f'{user}:每日1G,{sc1s}--->{sc2s}')
                msgg.append(f'{user}:每日1G,{sc1s}--->{sc2s}')
        elif m2:
            resp = re.search('</i>(?P<resp>.*?)！',html_text)
            order = re.search('fwb">(?P<order>.*?)</p>',html_text)
            tip = re.search('fcgray">(?P<tip>.*?)</p>',html_text)
            if resp and order and tip:            
                respt = resp.group('resp')
                ordert = order.group('order')
                tipt = tip.group('tip')
                print(f'{user}:每日1G,{respt}--->{ordert}--->{tipt}')
                msgg.append(f'{user}:每日1G,{respt}--->{ordert}--->{tipt}')
    except Exception as e:
        print(f'每日1G提交出错,{e}')
        msgg.append(f'每日1G提交出错,{e}')


#每日1G查询
def getEveryDay1G(ck):
    try:
        user = getUserName(ck)
        url = 'https://vip.mini189.cn/yqt_fans/activtiyById/getEveryDay1G'
        headers={
            "User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",    
            "Cookie":ck
        }
        # jsont = requests.post(url=url,headers=headers).json()
        response = mypost(url=url,headers=headers,name='每日1G查询')               
        if response == None:  
            return False
        jsont = response.json()       
        
        if  jsont['status'] != 'success':
            print(f'{user}:出现异常,{jsont["msg"]}')
            msgg.append(f'{user}:出现异常,{jsont["msg"]}')
            print(jsont)
        else:
            if jsont['data']['accountList']:
               userInfoId= jsont['data']['userInfoId']
               customerNumber=jsont['data']['loginNumber']           
               submitOrder1G(userInfoId,customerNumber,ck)  #提交每日1G
               return True  #成功领取1G并触发其他任务
            else:
                print(f'{user}:每日1G暂不可领取,可能今日已领取过')
        return False
    except Exception as e:
        print(f'每日1G查询出错,{e}')
        return False

def getUserName(ck):
    try:
        lock.acquire() 
        for item in dx_cookies:
            if item['ck'] == ck:
                if 'user' in item.keys():                  
                    return item['user'].strip()
        return ck[11:22]
    except Exception as e:
        print(f'出错,{e}')
        return ck[11:22]
    finally:
        lock.release() 

def myget(url,headers,name='默认',timeout=10):
    return myrequest(mth="get",url=url,headers=headers,data=None,name=name,timeout=timeout)    
def mypost(url,headers,data=None,name='默认',timeout=10):
    return myrequest(mth="post",url=url,headers=headers,data=data,name=name,timeout=timeout)
#重试5次
def myrequest(mth,url,headers,data,name,timeout):
    retryTimes=0
    while retryTimes<5:
        try:                  
            if mth.upper() == 'GET':
                return requests.get(url=url,headers=headers,timeout=timeout)
            elif mth.upper() == 'POST':
                return requests.post(url=url,data=data,headers=headers,timeout=timeout)
            else:
                logger.error(f'请求方式未知')
                return None
        except Exception as e:
            retryTimes+=1
            logger.error(f'{name} ,请求异常,尝试重新第{retryTimes}次请求')            
            logger.info(f'{name} ,请求异常,尝试重新第{retryTimes}次请求:{e}')            
    return None
    
if __name__ == '__main__':
    main()