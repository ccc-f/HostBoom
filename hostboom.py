import requests
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor, as_completed
from requests.packages import chardet
import re
import time 
requests.packages.urllib3.disable_warnings()

class HostBoom:
    def __init__(self):
        self.host_info = []
        self.error_info = []
        self.success_info = []
        self.error_ips = []
        self.r = requests.session()
        self.User_Agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
    
    def detect_ip_alive(self, ips):
        for ip in ips:
            flag = 0
            for h in ['http://', 'https://']:
                try:
                    headers = {'User-Agent': self.User_Agent}
                    target = h + ip
                    self.r.get(target, verify=False, headers=headers, timeout=5)
                except Exception as e:
                    flag += 1
                    if flag == 2:
                        self.error_ips.append(ip)
        print('ip存活检测完成')
        return self.error_ips
    
    def filter_died_subdomain(self, subdomains):
        died_subdomains = []
        for subdomain in subdomains:
            flag = 0
            for h in ['http://', 'https://']:
                try:
                    headers = {'User-Agent': self.User_Agent}
                    target = h + subdomain
                    self.r.get(target, verify=False, headers=headers, timeout=5)
                except Exception as e:
                    flag += 1
                    if flag == 2:
                        died_subdomains.append(subdomain)
        print('域名存活检测完成')
        return died_subdomains

    def host_boom(self, ip, subdomain):
        http_s = ['http://','https://']
        for h in http_s :
            headers = {'Host':subdomain, 'User-Agent': self.User_Agent}
            try:
                req_url = h + ip
                res = self.r.get(req_url, verify=False, headers=headers, timeout=5)
                print('{} ---- {}'.format(req_url, subdomain))
                charset = chardet.detect(res.content)["encoding"]
                res.encoding = charset
                try:
                    title = re.search('<title>(.*)</title>', res.text).group(1)
                except Exception as e:
                    title = u"获取标题失败aacc"
                info = [h+ip, subdomain, len(res.text), title, res.status_code]
                # self.queue.put(info)
                self.host_info.append(info)
            except Exception as e:
                print(req_url + ' --- error')
                error_info = [ip, subdomain ,h]
                self.error_info.append(error_info)

    def verify(self, target, subdomain, title, true_code):
        headers = {'User-Agent': self.User_Agent}
        try:
            res = self.r.get(target, verify=False, headers=headers, timeout=5)
            charset = chardet.detect(res.content)["encoding"]
            res.encoding = charset
            # try:
            #     title = re.search('<title>(.*)</title>', res.text).group(1)
            # except Exception as e:
            #     title = u"获取标题失败aacc"
            direct_code = res.status_code
            if str(direct_code)[0] == '4' and true_code != direct_code:
                # try:
                #     sub_url = target.split('://')[0] + '://' + subdomain
                #     sub_req = self.r.get(sub_url, verify=False, headers=headers, timeout=5)
                #     return [False]
                # except:
                return [True, target, subdomain, title, true_code, direct_code]
            return [False]
        except:
            return [False]
    
    
    def thread_verify(self, threads_count):
        with ThreadPoolExecutor(max_workers=threads_count) as pool:
            all_task = []
            for t in self.host_info:
                req_ip = t[0]
                subdomain = t[1]
                ip = req_ip.split('://')[1]
                # req_subdomain = req_ip.split('://')[0] + '://' + subdomain
                target = req_ip
                length = t[2]
                title = t[3]
                status_code = t[4]
                task = pool.submit(self.verify, target, subdomain, title, status_code)
                all_task.append(task)
            for future in as_completed(all_task):
                try:
                    if future.result()[0]:
                        print('*'*10+'恭喜，发现host碰撞:'+'*'*10)
                        result = [future.result()[1], future.result()[2], future.result()[3], future.result()[4], future.result()[5]]
                        print(result)
                        self.success_info.append(result)
                        print('*'*32)
                except Exception as e:
                    pass
    
    def thread_pool(self, ips, subdomains, threads_count):
        with ThreadPoolExecutor(max_workers=threads_count) as pool:
            all_task = []
            for ip in ips:
                for subdomain in subdomains:
                    task = pool.submit(self.host_boom, ip=ip, subdomain = subdomain)
                    all_task.append(task)
    
    def myprocess(self, ip, subdomains, threads_count):
        with ThreadPoolExecutor(max_workers=threads_count) as pool:
            all_task = []
            for subdomain in subdomains:
                task = pool.submit(self.host_boom, ip=ip, subdomain = subdomain)
                all_task.append(task)

    def process_pool(self, ips, subdomains, process_count, threads_count):
        p = ProcessPoolExecutor(process_count)
        l = []
        for ip in ips:
            obj  = p.submit(self.myprocess, ip, subdomains, threads_count)
            l.append(obj)
        p.shutdown()
    
    @staticmethod
    def read_files(filename):
        with open(filename, 'r', encoding='utf-8')as f:
            lines = f.read().split('\n')
            result = [line.strip() for line in lines if line.strip()]
        return result
    
    @staticmethod
    def output_files(result):
        output_file = str(int(time.time())) + '_success.txt'
        with open(output_file, 'a', encoding='utf-8')as f:
            for r in result:
                f.write(r[0] + ' -- ' + r[1] + ' -- ' + r[2] + ' -- ' + str(r[3]) + ' -- ' + str(r[4]))
                f.write('\n')
    
    def main(self, ips, subdomains):
        self.thread_pool(ips, subdomains, 100)
        # self.process_pool(ips, subdomains, 1, 20)
        print(self.host_info)
        self.thread_verify(10)
        return self.success_info

if __name__ == '__main__':
    start = time.time()
    hb = HostBoom()
    ips_file = 'ips.txt'
    subdomains_file = 'subdomains.txt'
    mode = 'all' # ip、subdomain、all、no
    ips = hb.read_files(ips_file)
    subdomains = hb.read_files(subdomains_file)
    if mode == 'all':
        error_ips = hb.detect_ip_alive(ips)
        alive_ips = list(set(ips) - set(error_ips))
        died_subdomains = hb.filter_died_subdomain(subdomains)
        result = hb.main(alive_ips, died_subdomains)
    elif mode == 'ip':
        error_ips = hb.detect_ip_alive(ips)
        alive_ips = list(set(ips) - set(error_ips))
        result = hb.main(alive_ips, subdomains)
    elif mode == 'subdomain':
        died_subdomains = hb.filter_died_subdomain(subdomains)
        result = hb.main(ips, died_subdomains)
    else:
        result = hb.main(ips, subdomains)
    hb.output_files(result)
    end = time.time()
    print('程序运行时长为：{}s'.format(end-start))