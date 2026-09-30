const root=".";
const fmt=v=>v==null||v===""||Number.isNaN(Number(v))?"—":Number(v).toLocaleString("ko-KR",{maximumFractionDigits:1});
const pct=v=>v==null||v===""||Number.isNaN(Number(v))?"—":(Number(v)*100).toFixed(1)+"%";

function parseCSV(text){
  text=text.replace(/^\uFEFF/,"").trim();
  const rows=[]; let row=[], cell="", quoted=false;
  for(let i=0;i<text.length;i++){
    const ch=text[i], next=text[i+1];
    if(ch==='"'){
      if(quoted && next==='"'){cell+='"'; i++;}
      else quoted=!quoted;
    }else if(ch===',' && !quoted){row.push(cell);cell="";}
    else if((ch==='\n'||ch==='\r') && !quoted){
      if(ch==='\r' && next==='\n') i++;
      row.push(cell); rows.push(row); row=[]; cell="";
    }else cell+=ch;
  }
  if(cell!==""||row.length){row.push(cell);rows.push(row);}
  if(!rows.length)return[];
  const headers=rows[0].map(x=>x.replace(/^\uFEFF/,"").trim());
  return rows.slice(1).filter(r=>r.some(v=>v!=="")).map(r=>{
    const o={}; headers.forEach((h,i)=>o[h]=(r[i]??"").trim()); return o;
  });
}

async function csv(n){
  const res=await fetch(root+"/data/processed/"+n+"?v="+Date.now(),{cache:"no-store"});
  if(!res.ok) throw new Error(n+" HTTP "+res.status);
  return parseCSV(await res.text());
}
async function json(n){
  const res=await fetch(root+"/data/processed/"+n+"?v="+Date.now(),{cache:"no-store"});
  if(!res.ok) throw new Error(n+" HTTP "+res.status);
  return res.json();
}
function series(a,m){
  return a.filter(x=>x.metric===m&&x.report_type==="annual"&&x.period).sort((x,y)=>x.period.localeCompare(y.period));
}
function rs(a,n){
  return a.filter(x=>x.ratio===n&&x.report_type==="annual"&&x.period).sort((x,y)=>x.period.localeCompare(y.period));
}
function chart(id,labels,sets){
  const el=document.getElementById(id);
  if(!el)return;
  new Chart(el,{type:"line",data:{labels,datasets:sets},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:"bottom"}},scales:{y:{beginAtZero:false}}}});
}

(async()=>{
  try{
    const [f,r,s]=await Promise.all([csv("financials.csv"),csv("ratios.csv"),json("status.json")]);
    document.getElementById("updated").textContent="마지막 수집 "+(s.last_run||"—");

    const rev=series(f,"revenue"), op=series(f,"operating_income"), ni=series(f,"net_income");
    const m=rs(r,"operating_margin"), e=rs(r,"equity_ratio"), c=series(f,"cfo");
    const latest=x=>x.length?x[x.length-1].amount:null;

    document.getElementById("kpis").innerHTML=[
      ["최근 매출액",fmt(latest(rev))],["최근 영업이익",fmt(latest(op))],["최근 순이익",fmt(latest(ni))],
      ["영업이익률",pct(m.at(-1)?.value)],["자기자본비율",pct(e.at(-1)?.value)]
    ].map(x=>'<div class="kpi"><small>'+x[0]+'</small><strong>'+x[1]+'</strong><small>원자료 기준</small></div>').join("");

    chart("profit",rev.map(x=>x.period),[
      {label:"매출액",data:rev.map(x=>+x.amount)},{label:"영업이익",data:op.map(x=>+x.amount)},{label:"순이익",data:ni.map(x=>+x.amount)}
    ]);
    chart("margin",m.map(x=>x.period),[{label:"영업이익률",data:m.map(x=>+x.value*100)}]);
    chart("equity",e.map(x=>x.period),[{label:"자기자본비율",data:e.map(x=>+x.value*100)}]);
    chart("cfo",c.map(x=>x.period),[{label:"CFO",data:c.map(x=>+x.amount)}]);

    const metrics=["revenue","operating_income","net_income","total_assets","total_liabilities","total_equity","cash","receivables","inventory","cfo"];
    const labels={revenue:"매출액",operating_income:"영업이익",net_income:"순이익",total_assets:"총자산",total_liabilities:"총부채",total_equity:"자본총계",cash:"현금",receivables:"매출채권",inventory:"재고자산",cfo:"CFO"};
    const ratios=["operating_margin","net_margin","current_ratio","debt_ratio","equity_ratio","cfo_to_net_income"];
    const rlabels={operating_margin:"영업이익률",net_margin:"순이익률",current_ratio:"유동비율",debt_ratio:"부채비율",equity_ratio:"자기자본비율",cfo_to_net_income:"CFO/순이익"};

    function make(title,type){
      const fs=f.filter(x=>x.report_type===type), periods=[...new Set(fs.map(x=>x.period).filter(Boolean))].sort().reverse();
      let h="<article class='card'><h2>"+title+"</h2><div class='tablewrap'><table><thead><tr><th>기간</th>"+
        metrics.map(x=>"<th>"+labels[x]+"</th>").join("")+ratios.map(x=>"<th>"+rlabels[x]+"</th>").join("")+
        "</tr></thead><tbody>";
      for(const p of periods){
        const z=fs.filter(x=>x.period===p),q=r.filter(x=>x.period===p);
        h+="<tr><td>"+p+"</td>"+
          metrics.map(x=>"<td>"+fmt(z.find(y=>y.metric===x)?.amount)+"</td>").join("")+
          ratios.map(x=>"<td>"+(x.includes("margin")||x==="debt_ratio"||x==="equity_ratio"?pct(q.find(y=>y.ratio===x)?.value):fmt(q.find(y=>y.ratio===x)?.value))+"</td>").join("")+
          "</tr>";
      }
      return h+"</tbody></table></div></article>";
    }
    document.getElementById("tables").innerHTML=make("Annual · 사업보고서","annual")+make("Half-year · 반기보고서","half_year")+make("Quarterly · 분기보고서","quarterly");

    const peers=[["오뚜기","007310","라면·가공식품"],["삼양식품","003230","라면"],["대상","001680","종합식품"],["풀무원","017810","식품 제조·유통"],["동원F&B","049770","식품 제조·유통"],["CJ제일제당","097950","종합식품"]];
    document.getElementById("peers").innerHTML="<thead><tr><th>기업</th><th>종목코드</th><th>주요 사업영역</th></tr></thead><tbody>"+
      peers.map(x=>"<tr><td>"+x[0]+"</td><td>"+x[1]+"</td><td>"+x[2]+"</td></tr>").join("")+"</tbody>";
  }catch(err){
    console.error(err);
    document.getElementById("updated").textContent="데이터 로딩 오류";
    document.getElementById("kpis").innerHTML='<div class="kpi" style="grid-column:1/-1"><small>Dashboard error</small><strong>데이터를 불러오지 못했습니다.</strong><small>'+String(err.message||err)+'</small></div>';
  }
})();