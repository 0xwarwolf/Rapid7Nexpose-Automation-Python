import requests, json, time
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

Login_URL = "https://localhost:3780/data/user/login"
API_URL = "https://localhost:3780/api/3/"

session = requests.Session()
login_creds = {
    "nexposeccusername":"addusername",
    "nexposeccpassword":"addpasswd"
}

sess = session.post(Login_URL, data=login_creds, verify=False)
sessionID = sess.json()["sessionID"]

name = input("Enter the scan name: ")
IP = input("Enter the IP: ")
data = '{"name":"' + name + '","description":"abcs","engineID":3,"riskFactor":3,"configID":-1,"templateID":"full-audit-without-web-spider","defaultScanTemplateID":"full-audit-without-web-spider","defaultScanEngineID":3,"discoveryConfigID":-1,"includedTargets":{"addresses":["' + IP + '"],"tags":[],"assetGroups":[]},"configName":"Full audit without Web Spider","modifications":{"siteName":"true"}}'

headers = {
    "Content-Type": "application/json",
    "Nexposeccsessionid": sessionID,
    "Cookie": "nexposeCCSessionID="+sessionID,
    "Content-Length":str(len(data))
}

s = requests.put("https://192.168.1.10:3780/data/scan/config", data=data, headers=headers, verify=False)
siteID = s.text
print(f"Site ID is {siteID}")

s = requests.post(f"https://192.168.1.10:3780/data/site/{siteID}/scan", headers=headers, verify=False)
scanID = s.text
print(f"Scan ID is {scanID}")

reportName = name + " Report"
headers_simple = {
    "Content-Type": "application/json",
    "Nexposeccsessionid": sessionID,
    "Cookie": "nexposeCCSessionID="+sessionID
}
while(True):
    scan = requests.get(f"https://192.168.1.10:3780/api/3/scans/{scanID}", headers=headers_simple, verify=False)
    scanStatus = scan.json()["status"]
    if scanStatus == "finished":
        time.sleep(20)
        data = '{"name":"' + reportName + '","id":{"configID":-1},"owner":"1","reportFrequency":"THIS_TIME_ONLY","reportTemplateID":"highest-risk-vulns","exporterConfig":{"format":"pdf","reportCopyLocation":""},"storeOnServer":1,"storeCopyOnServer":0,"baseline":0,"timezone":"America/Los_Angeles","assetGroups":[],"sites":[],"assets":[],"tags":[],"scans":[' + scanID + '],"filters":{},"users":[],"globalSMTPDistribution":false,"recipients":[],"language":"en-us","parameters":{}}'
        headers = {
            "Content-Type": "application/json",
            "Nexposeccsessionid": sessionID,
            "Cookie": "nexposeCCSessionID="+sessionID,
            "Content-Length":str(len(data))
        }
        generateReport = requests.post("https://192.168.1.10:3780/data/report/configs?generate=true", data=data, headers=headers, verify=False)
        print("Report Generated")
        time.sleep(20)
        reportsPage = session.get("https://192.168.1.10:3780/report/reports.jsp", headers=headers_simple, verify=False)
        # reportURL = reportsPage.text.split("Rapid7.report.initReportList(true, ")[1].split("</script>")[0].split(f'"name" : "{reportName}"')[1].split('"reportFile" : "')[1].split('",')[0]
        reportURL = reportsPage.text.split("Rapid7.report.initReportList(true, ")[1].split("</script>")[0].split('"reportFile" : "')[1].split('",')[0]
        report = session.get("https://192.168.1.10:3780" + reportURL, headers=headers, verify=False)
        open(f"{reportName}.pdf", 'wb').write(report.content)
        break
    else:
        print("Not Yet Completed")
        time.sleep(60)