## 介绍

当前开源的host碰撞工具的缺点在于耗时巨长、输出结果太多，需要人工筛选存在host碰撞的结果，主要原因在于检测思路不够灵活。

所以在尝试了各种检测思路后，开发了一个不花里胡哨但是非常实用的host碰撞工具，方便集成到自己的自动化渗透工具中。

优点在于速度非常快、检测结果明确。

## 使用方法

将ip放入 ips.txt,将域名放入 subdomains.txt

python3运行

```
pip install requests
```

运行程序

```
python hostboom.py
```

最后会输出到 success_timestamp.txt 文件中。

>   内置了几种检测模式：all、ip、subdomain、no
>
>   在第168行左右进行修改  mode = 'all'
>
>   all：保留ip存活、保留subdomian不存活，适合检测大量目标
>
>   ip: 保留ip存活，适合检测大量ip目标或者只想检测内网域名碰撞
>
>   subdomain： 保留subdomian不存活，适合检测少量IP大量域名
>
>   no: 不进行任何操作，耗时长，如果你不差时间的话。

## 检测思路

### 1、筛选过滤IP、域名

为了降低大量IP、subdomians的检测时间。

可选的进行IP、subdomains的存活检测工作，即：

1）移除无法连接的IP

```
http[s]://ip
```

2）移除可以正常访问域名

>   因为一些域名只允许内网访问，在公共dns上无法解析该域名。

```
http[s]://subdomain
```

上述这两步都是可选的，如果你需要目标IP、域名数量过多，需要降低检测时间，可以选择开启。

### 2、获取host碰撞的资产

GET http[s]://ip
Host: subdomain

获取可以正常访问的ip、subdomain

目的是为了获取first_code进入下一步的筛选

### 3、筛选结果

get http[s]://subdomain
获取状态码second_code

筛选依据：

1、second_code是4xx

2、first_code不等于second_code

经过这两步筛选已经能够过滤大部分的无效资产。



## 测试结果

测试目标某集团资产

all模式、ip数量为27、域名数量为213、线程100、timeout 5s

碰撞成功的有7个结果，程序运行时间350s，牛逼！



对比 https://github.com/fofapro/Hosts_scan 0.9kstar 

ip数量为27、域名数量为213、线程100、timeout 5s(原本是30s，但会卡死)

碰撞成功的有**0**个结果，程序运行时间294s，这是否......

