import os,json,requests
from pathlib import Path
from datetime import date
ROOT=Path(__file__).resolve().parents[1];C=json.loads((ROOT/"config.json").read_text(encoding="utf-8"))
KEY=os.environ.get("DART"+"_"+"API"+"_"+"KEY","");API="https://opendart.fss.or.kr/api";RAW=ROOT/"data/raw";RAW.mkdir(parents=True,exist_ok=True)
if not KEY: raise SystemExit("DART API key is not configured")
def call(name,p):
 p=dict(p);p["crtfc_key"]=KEY
 r=requests.get(API+"/"+name+".json",params=p,timeout=90);r.raise_for_status();return r.json()
for y in range(C["start_year"],2015):
 p={"corp_code":C["corp_code"],"bgn_de":str(y)+"0101","end_de":str(y+1)+"0430","pblntf_ty":"A","last_reprt_at":"Y","sort":"date","sort_mth":"asc","page_no":"1","page_count":"100"}
 xs=[x for x in call("list",p).get("list",[]) if "사업보고서" in x.get("report_nm","")]
 for x in xs[-1:]:
  rno=x["rcept_no"];f=RAW/(str(y)+"_annual_"+rno+".zip")
  if not f.exists():
   r=requests.get(API+"/document.xml",params={"crtfc_key":KEY,"rcept_no":rno},timeout=120);r.raise_for_status();f.write_bytes(r.content)
  print("saved",y,rno)
