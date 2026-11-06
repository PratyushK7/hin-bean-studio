/* UPI explainer — deterministic 1920x1080 Canvas scenes.
   No external assets, CDNs, APIs, brands or remote requests. */
(() => {
  "use strict";
  const W = 1920, H = 1080;
  const C = {
    bg:"#0b1220", panel:"#121d2d", panel2:"#17263a", cream:"#f1eadc",
    muted:"#99a9b7", dim:"#607387", teal:"#39b6a5", teal2:"#1b8279",
    amber:"#e8ad5c", red:"#e46f68", white:"#fffaf0", line:"#31465b",
    green:"#8acb9a"
  };
  const canvas = document.getElementById("frame");
  const ctx = canvas.getContext("2d", { alpha:false });
  ctx.scale(1,1);

  const clamp = (v,a=0,b=1) => Math.max(a,Math.min(b,v));
  const ease = v => { v=clamp(v); return v*v*(3-2*v); };
  const pop = v => { v=clamp(v); return 1-Math.pow(1-v,3); };

  function rr(x,y,w,h,r,fill,stroke=null,lw=2) {
    ctx.beginPath(); ctx.roundRect(x,y,w,h,r);
    if(fill){ctx.fillStyle=fill;ctx.fill();}
    if(stroke){ctx.lineWidth=lw;ctx.strokeStyle=stroke;ctx.stroke();}
  }
  function circle(x,y,r,fill,stroke=null,lw=2) {
    ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);
    if(fill){ctx.fillStyle=fill;ctx.fill();}
    if(stroke){ctx.lineWidth=lw;ctx.strokeStyle=stroke;ctx.stroke();}
  }
  function line(x1,y1,x2,y2,color=C.line,lw=3,dash=[]) {
    ctx.beginPath();ctx.setLineDash(dash);ctx.moveTo(x1,y1);ctx.lineTo(x2,y2);
    ctx.strokeStyle=color;ctx.lineWidth=lw;ctx.stroke();ctx.setLineDash([]);
  }
  function txt(s,x,y,size=28,color=C.cream,weight=500,align="left") {
    ctx.font=weight+" "+size+"px 'Segoe UI', Arial, sans-serif";
    ctx.fillStyle=color;ctx.textAlign=align;ctx.textBaseline="alphabetic";
    ctx.fillText(String(s),x,y);
  }
  function wrap(s,x,y,maxWidth,size=25,color=C.cream,weight=400,leading=1.35) {
    ctx.font=weight+" "+size+"px 'Segoe UI', Arial, sans-serif";
    ctx.fillStyle=color;ctx.textAlign="left";ctx.textBaseline="alphabetic";
    const words=String(s).split(/\s+/);let row="",yy=y;
    for(const word of words){
      const test=row?row+" "+word:word;
      if(ctx.measureText(test).width>maxWidth && row){ctx.fillText(row,x,yy);row=word;yy+=size*leading;}
      else row=test;
    }
    if(row)ctx.fillText(row,x,yy);
    return yy;
  }
  function label(s,x,y,color=C.teal) {
    txt(s.toUpperCase(),x,y,17,color,700);
  }
  function pill(s,x,y,w,color=C.teal) {
    rr(x,y,w,38,19,color+"20",color,1.5);
    txt(s,x+w/2,y+25,15,color,700,"center");
  }
  function arrow(x1,y1,x2,y2,color=C.teal,p=1,lw=5) {
    const ex=x1+(x2-x1)*ease(p),ey=y1+(y2-y1)*ease(p);
    line(x1,y1,ex,ey,color,lw);
    if(p>0.08){
      const a=Math.atan2(y2-y1,x2-x1),len=17;
      ctx.beginPath();ctx.moveTo(ex,ey);
      ctx.lineTo(ex-len*Math.cos(a-.55),ey-len*Math.sin(a-.55));
      ctx.lineTo(ex-len*Math.cos(a+.55),ey-len*Math.sin(a+.55));
      ctx.closePath();ctx.fillStyle=color;ctx.fill();
    }
  }
  function panel(x,y,w,h,title,sub,accent=C.teal) {
    rr(x,y,w,h,18,C.panel,C.line,2);
    rr(x,y,7,h,4,accent);
    if(title)txt(title,x+30,y+48,25,C.cream,700);
    if(sub)wrap(sub,x+30,y+83,w-60,18,C.muted,400,1.35);
  }
  function node(x,y,w,h,tag,title,sub,accent=C.teal,alpha=1) {
    ctx.save();ctx.globalAlpha=alpha;
    rr(x,y,w,h,18,C.panel2,accent,2);
    txt(tag,x+22,y+31,14,accent,700);
    txt(title,x+22,y+70,24,C.cream,700);
    if(sub)wrap(sub,x+22,y+101,w-44,16,C.muted,400,1.3);
    ctx.restore();
  }
  function base(index,chapter,headline,sub,progress) {
    const g=ctx.createLinearGradient(0,0,W,H);
    g.addColorStop(0,"#101b2b");g.addColorStop(.58,C.bg);g.addColorStop(1,"#101a29");
    ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
    ctx.save();ctx.globalAlpha=.16;ctx.strokeStyle="#597089";ctx.lineWidth=1;
    for(let x=70;x<W;x+=90){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,H);ctx.stroke();}
    for(let y=65;y<H;y+=90){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke();}
    ctx.restore();
    circle(1670,180,300,"#39b6a508");
    label("HINDI EXPLAINER  /  UPI DECODED",100,70,C.muted);
    txt(String(index+1).padStart(2,"0")+" / 16",1820,70,17,C.dim,600,"right");
    txt(headline,100,165,54,C.cream,700);
    if(sub)txt(sub,103,211,22,C.muted,400);
    line(100,1000,1820,1000,C.line,2);
    rr(100,1018,1720,5,3,C.line);
    rr(100,1018,1720*clamp(progress),3,2,C.teal);
    txt(chapter.toUpperCase(),100,970,15,C.muted,700);
    txt("ILLUSTRATIVE FLOW  ·  NOT A BANK SCREEN",1820,970,13,C.dim,600,"right");
  }
  function qr(x,y,size,seed=0) {
    const n=17,cell=size/n;
    rr(x-10,y-10,size+20,size+20,10,C.white);
    function finder(ix,iy){
      ctx.fillStyle=C.bg;ctx.fillRect(x+ix*cell,y+iy*cell,7*cell,7*cell);
      ctx.fillStyle=C.white;ctx.fillRect(x+(ix+1)*cell,y+(iy+1)*cell,5*cell,5*cell);
      ctx.fillStyle=C.bg;ctx.fillRect(x+(ix+2)*cell,y+(iy+2)*cell,3*cell,3*cell);
    }
    finder(0,0);finder(n-7,0);finder(0,n-7);
    for(let r=0;r<n;r++)for(let c=0;c<n;c++){
      const inFinder=(r<7&&c<7)||(r<7&&c>=n-7)||(r>=n-7&&c<7);
      if(inFinder)continue;
      const bit=((r*13+c*7+seed*11+r*c*3)%9)<4;
      if(bit){ctx.fillStyle=C.bg;ctx.fillRect(x+c*cell,y+r*cell,cell*.92,cell*.92);}
    }
  }
  function phone(x,y,scale=1,amount=false) {
    ctx.save();ctx.translate(x,y);ctx.scale(scale,scale);
    rr(0,0,260,475,34,"#080f19","#708295",5);
    rr(13,15,234,445,25,"#eef1e9");
    rr(92,8,76,12,6,"#708295");
    txt("PAYMENT",36,62,15,"#526052",700);
    txt("Scan & pay",36,100,27,"#1d2a28",700);
    rr(31,126,198,174,12,"#fffefa","#d1d9d0",2);
    qr(91,151,78,2);
    txt("ILLUSTRATIVE QR",130,284,11,"#708071",700,"center");
    if(amount){
      txt("Paying to",35,340,13,"#7b897d",500);
      txt("Chai Corner",35,368,20,"#26362e",700);
      txt("₹20.00",35,410,27,"#26362e",700);
      circle(211,405,18,C.green);
      txt("✓",211,413,23,"#14231d",700,"center");
    } else {
      txt("Scan a QR code",130,373,20,"#26362e",600,"center");
      txt("No real account details",130,404,13,"#7b897d",400,"center");
    }
    ctx.restore();
  }
  function teaStall(x,y,scale=1) {
    ctx.save();ctx.translate(x,y);ctx.scale(scale,scale);
    rr(0,155,480,190,12,"#473b32");
    rr(0,130,480,32,6,"#c58c58");
    for(let i=0;i<8;i++){
      ctx.fillStyle=i%2?"#e8ad5c":"#f1eadc";
      ctx.beginPath();ctx.moveTo(i*60,0);ctx.lineTo((i+1)*60,0);ctx.lineTo((i+1)*60+12,118);ctx.lineTo(i*60+12,118);ctx.closePath();ctx.fill();
    }
    line(0,120,480,120,"#9a704c",8);
    for(let i=0;i<3;i++){rr(65+i*105,205,56,70,9,"#e8dfcb","#b5ab99",2);line(78+i*105,220,106+i*105,220,"#9b8f7e",2);}
    circle(420,220,28,"#f0dfc0");rr(390,250,60,83,20,"#607a68");
    ctx.restore();
  }
  function chain(labels,y,active,p=1,x0=150,x1=1770) {
    const n=labels.length,gap=(x1-x0)/Math.max(1,n-1);
    for(let i=0;i<n-1;i++)arrow(x0+i*gap+115,y,x0+(i+1)*gap-115,y,C.line,clamp(p*n-i),4);
    labels.forEach((v,i)=>{
      const x=x0+i*gap,hit=i<=active;
      rr(x-115,y-54,230,108,16,hit?C.panel2:C.panel,C.dim,2);
      circle(x-82,y-1,10,i===active?C.amber:(hit?C.teal:C.dim));
      txt(v[0],x-60,y+8,20,hit?C.cream:C.muted,700);
      txt(v[1],x,y+83,14,C.muted,600,"center");
    });
  }
  function account(x,y,title,value,positive=false) {
    rr(x,y,520,250,18,C.panel,C.line,2);
    label("ILLUSTRATIVE LEDGER",x+30,y+40,C.muted);
    txt(title,x+30,y+91,28,C.cream,700);
    txt(value,x+30,y+166,58,positive?C.green:C.amber,700);
    line(x+30,y+194,x+490,y+194,C.line,2);
    txt("Available balance / entry example",x+30,y+226,15,C.muted,400);
  }
  function scene0(p) {
    teaStall(1170,390,1.1);
    phone(260,300,1.06,true);
    label("THE SMALL PAYMENT",103,300,C.amber);
    txt("₹20",765,470,116,C.cream,700,"center");
    txt("A chai. One QR scan.",770,530,28,C.muted,400,"center");
    arrow(650,620,1090,620,C.teal,p,6);
    pill("PAYMENT SUCCESSFUL",685,690,260,C.green);
    txt("Lekin peeche kaun kaam karta hai?",960,835,29,C.cream,600,"center");
  }
  function scene1(p) {
    phone(165,350,.72,true);
    const labels=[["APP","Interface"],["PSP","Connectivity"],["NPCI","Routing"],["BANKS","Accounts"]];
    chain(labels,570,Math.floor(p*4),p,790,1640);
    txt("Ek tap. Multiple systems.",960,820,36,C.cream,700,"center");
    arrow(390,730,690,730,C.teal,p,5);
  }
  function scene2(p) {
    panel(150,340,620,360,"UPI APP","Payment initiate karne aur status dikhane ka interface.",C.teal);
    pill("INTERFACE",350,760,220,C.teal);
    txt("≠",960,565,100,C.amber,500,"center");
    panel(1150,340,620,360,"BANK ACCOUNT","Actual account entry participating bank ke ledger mein hoti hai.",C.amber);
    rr(1290,730,330,70,12,"#e8ad5c18",C.amber,2);
    txt("ACCOUNT LEDGER",1455,775,20,C.amber,700,"center");
    arrow(770,520,1135,520,C.line,p,4);
    txt("App mein paisa store hone ka model nahi",960,865,24,C.muted,500,"center");
  }
  function scene3(p) {
    const xs=[300,960,1620],ys=570;
    line(xs[0],ys,xs[2],ys,C.line,5);
    const items=[["IMPS","Existing payment rails","Before UPI"],["UPI","Common interface","2016"],["ECOSYSTEM","Apps + banks","Interoperable"]];
    items.forEach((it,i)=>{
      const a=pop(p*3-i);
      circle(xs[i],ys,74,C.panel2,i===1?C.teal:C.dim,3);
      txt(it[0],xs[i],ys+10,26,C.cream,700,"center");
      txt(it[1],xs[i],ys+145,22,C.cream,600,"center");
      pill(it[2],xs[i]-72,ys+184,144,i===1?C.teal:C.amber);
      if(i<2)arrow(xs[i]+90,ys,xs[i+1]-90,ys,C.teal,a,5);
    });
    txt("NPCI ne UPI develop kiya",960,850,27,C.muted,500,"center");
  }
  function scene4(p) {
    const items=[["01","USER + APP","Aapka payment interface"],["02","PSP BANK","App ko UPI se connect karta hai"],["03","NPCI SWITCH","Messages ko route karta hai"],["04","REMITTER BANK","Sender-side account"],["05","BENEFICIARY BANK","Receiver-side account"]];
    const y=400,w=286,g=42,start=125;
    items.forEach((it,i)=>{
      const x=start+i*(w+g),a=pop(p*5-i);
      node(x,y,w,250,it[0],it[1],it[2],i===2?C.amber:C.teal,a);
      if(i<4)arrow(x+w+4,y+125,x+w+g-6,y+125,C.teal,clamp(p*5-i-.2),4);
    });
    rr(255,770,1410,90,14,"#39b6a512",C.teal,2);
    txt("SIMPLIFIED BANK-LINKED UPI FLOW",960,825,24,C.teal,700,"center");
  }
  function scene5(p) {
    account(190,410,"Aapka account","− ₹20",false);
    account(1210,410,"Chai wale ka account","+ ₹20",true);
    arrow(740,535,1175,535,C.teal,p,7);
    pill("REMITTER",365,735,210,C.amber);
    pill("BENEFICIARY",1350,735,230,C.green);
    txt("Sender bank debit  →  Receiver bank credit",960,855,26,C.cream,600,"center");
  }
  function scene6(p) {
    phone(230,310,.82,false);
    rr(690,360,390,330,20,C.panel,C.line,2);
    label("QR RESOLVES TO",730,410,C.muted);
    txt("chai.corner@bank",730,470,30,C.cream,700);
    txt("Destination address",730,520,18,C.muted,400);
    arrow(550,540,670,540,C.teal,p,5);
    rr(1180,350,540,360,C.panel,C.line,2);
    label("VERIFY BEFORE PAY",1220,405,C.amber);
    txt("Chai Corner",1220,480,36,C.cream,700);
    txt("₹20.00",1220,550,48,C.teal,700);
    pill("NAME CHECKED",1220,600,210,C.green);
    arrow(1090,520,1160,520,C.teal,p,5);
    txt("SCAN  →  VERIFY  →  PAY",960,850,30,C.cream,700,"center");
  }
  function scene7(p) {
    const labels=[["APP","Payment"],["PSP","Connect"],["NPCI","Route"],["BANK","Receive"]];
    const x=[230,710,1190,1670],y=560;
    for(let i=0;i<labels.length-1;i++)arrow(x[i]+115,y,x[i+1]-115,y,C.line,clamp(p*4-i),6);
    labels.forEach((v,i)=>{
      node(x[i]-145,y-95,290,190,"PARTICIPANT",v[0],v[1],i===2?C.amber:C.teal,pop(p*4-i));
    });
    const packetX=230+(1670-230)*p;
    rr(packetX-42,y-32,84,64,12,C.amber,C.white,2);
    txt("₹20",packetX,y+8,20,C.bg,700,"center");
    pill("PAYMENT REQUEST",730,780,460,C.teal);
  }
  function scene8(p) {
    rr(180,340,560,480,24,C.panel,C.line,2);
    label("ON YOUR PHONE",225,395,C.muted);
    txt("UPI PIN",225,455,34,C.cream,700);
    const pinX=250;
    for(let i=0;i<4;i++)circle(pinX+i*90,545,16,i<p*4?C.teal:C.line);
    for(let i=0;i<3;i++)for(let j=0;j<3;j++){
      circle(300+j*150,650+i*52,15,C.panel2,C.dim,1);
    }
    arrow(770,565,1080,565,C.teal,p,6);
    rr(1110,355,620,400,22,C.panel,C.teal,2);
    label("REMITTER BANK",1155,410,C.teal);
    txt("AUTHENTICATION",1155,485,34,C.cream,700);
    txt("PIN check + account rules",1155,535,22,C.muted,400);
    pill("APPROVED",1155,610,180,C.green);
    pill("DECLINED",1375,610,180,C.red);
    arrow(1320,555,1230,595,C.green,p,3);
    arrow(1320,555,1460,595,C.red,p,3);
    txt("PIN bank-side transaction ko authorize karta hai",960,865,25,C.cream,500,"center");
  }
  function scene9(p) {
    account(320,410,"Sender balance","₹4,980",false);
    rr(1020,460,540,170,18,C.panel2,C.amber,2);
    label("TRANSACTION ENTRY",1060,505,C.amber);
    txt("− ₹20.00",1060,575,55,C.amber,700);
    arrow(860,535,1000,535,C.amber,p,6);
    pill("DEBIT",1215,680,160,C.amber);
    txt("Illustrative account ledger",960,835,24,C.muted,500,"center");
  }
  function scene10(p) {
    rr(205,390,510,300,20,C.panel,C.line,2);
    label("NPCI ROUTING LAYER",245,445,C.amber);
    txt("Credit request",245,510,35,C.cream,700);
    txt("Destination: beneficiary bank",245,565,20,C.muted,400);
    arrow(745,540,1110,540,C.teal,p,6);
    account(1160,410,"Receiver balance","₹1,020",true);
    pill("CREDIT",1340,735,180,C.green);
  }
  function scene11(p) {
    const labels=[["APP","Interface"],["PSP","Connect"],["NPCI","Route"],["SENDER","Debit"],["RECEIVER","Credit"]];
    const x=[190,565,940,1315,1690],y=510;
    labels.forEach((it,i)=>{
      node(x[i]-130,y-80,260,160,"STAGE",it[0],it[1],i===2?C.amber:C.teal,pop(p*5-i));
      if(i<4)arrow(x[i]+135,y,x[i+1]-135,y,C.teal,clamp(p*5-i-.35),5);
    });
    txt("Request → Authorization → Debit → Credit → Response",960,790,29,C.cream,600,"center");
    pill("ONE CUSTOMER CONFIRMATION",650,850,620,C.green);
  }
  function scene12(p) {
    label("CUSTOMER-FACING",170,340,C.teal);
    rr(160,380,740,190,20,C.panel,C.teal,2);
    txt("Payment confirmation",205,450,34,C.cream,700);
    txt("Authorization + credit response",205,510,22,C.muted,400);
    label("BANK / MEMBER LEVEL",1020,340,C.amber);
    rr(1010,380,750,190,20,C.panel,C.amber,2);
    txt("Clearing & settlement",1055,450,34,C.cream,700);
    txt("Institutional obligation processing",1055,510,22,C.muted,400);
    arrow(900,475,990,475,C.line,p,3);
    txt("RELATED — BUT NOT THE SAME PROCESS",960,720,30,C.cream,700,"center");
    txt("Customer ko instant status mil sakta hai; interbank settlement alag layer hai.",960,780,22,C.muted,400,"center");
  }
  function scene13(p) {
    const nodes=[["PAYMENT STARTED","App request"],["SENDER BANK","Debit / auth"],["NETWORK","Route response"]];
    const y=360;
    nodes.forEach((n,i)=>{
      const x=190+i*570;
      node(x,y,410,150,"FLOW",n[0],n[1],C.teal,pop(p*3-i));
      if(i<2)arrow(x+415,y+75,x+555,y+75,C.teal,clamp(p*3-i-.2),4);
    });
    const branchX=960;
    line(branchX,540,branchX,620,C.line,4);
    arrow(branchX,620,540,720,C.green,clamp(p*3-1),5);
    arrow(branchX,620,960,720,C.amber,clamp(p*3-1.5),5);
    arrow(branchX,620,1380,720,C.red,clamp(p*3-2),5);
    node(250,725,400,155,"OUTCOME A","SUCCESS","Receiver credited",C.green,pop(p*3-1));
    node(760,725,400,155,"OUTCOME B","PENDING","Confirmation delayed",C.amber,pop(p*3-1.5));
    node(1270,725,400,155,"OUTCOME C","DECLINED","Reversal may follow",C.red,pop(p*3-2));
    txt("Pending ka matlab automatically lost nahi hota",960,925,22,C.cream,600,"center");
  }
  function scene14(p) {
    rr(160,365,720,400,22,C.panel,C.line,2);
    label("SENDING MONEY",205,420,C.green);
    txt("Enter PIN to authorize",205,500,35,C.cream,700);
    pill("VALID PAYMENT STEP",205,570,275,C.green);
    rr(1040,365,720,400,22,C.panel,C.line,2);
    label("RECEIVING MONEY",1085,420,C.red);
    txt("No PIN needed to receive",1085,500,35,C.cream,700);
    pill("PIN REQUEST = RED FLAG",1085,570,330,C.red);
    arrow(880,555,1020,555,C.amber,p,4);
    txt("Recipient name verify karo. Unknown collect request approve mat karo.",960,855,25,C.cream,500,"center");
  }
  function scene15(p) {
    circle(960,535,300,"#39b6a510",C.teal,3);
    circle(960,535,225,C.panel2,C.line,2);
    txt("₹20",960,520,110,C.cream,700,"center");
    txt("PAYMENT SUCCESSFUL",960,570,22,C.green,700,"center");
    const pts=[[960,170],[1275,285],[1430,535],[1275,790],[960,900],[645,790],[490,535],[645,285]];
    pts.forEach((pt,i)=>{
      const a=pop(p*8-i);
      line(960,535,pt[0],pt[1],C.teal,2);
      circle(pt[0],pt[1],10+9*a,a?C.teal:C.dim);
    });
    txt("ONE TAP. MANY SYSTEMS.",960,930,34,C.cream,700,"center");
  }

  const renderers=[scene0,scene1,scene2,scene3,scene4,scene5,scene6,scene7,scene8,scene9,scene10,scene11,scene12,scene13,scene14,scene15];
  window.renderFrame = (sceneIndex, progress) => {
    const i=Math.max(0,Math.min(renderers.length-1,Number(sceneIndex)||0));
    const p=clamp(Number(progress)||0);
    ctx.clearRect(0,0,W,H);
    const meta=[
      ["THE ₹20 QUESTION","A tiny payment. A surprisingly large system."],
      ["THE HIDDEN NETWORK","Your phone is only the starting point."],
      ["APP IS NOT THE BANK","Interface aur account alag roles hain."],
      ["A COMMON RAIL","UPI ne apps aur banks ko interoperable banaya."],
      ["THE PARTICIPANTS","Five roles in a simplified bank-linked flow."],
      ["SENDER TO RECEIVER","Remitter bank debits. Beneficiary bank credits."],
      ["SCAN AND VERIFY","QR destination identify karta hai; naam verify karo."],
      ["THE REQUEST PATH","Payment message relevant participants tak jaata hai."],
      ["AUTHORIZATION","UPI PIN sender-side bank transaction authorize karta hai."],
      ["THE DEBIT","Sender ke account ledger mein ₹20 minus hote hain."],
      ["THE CREDIT","Beneficiary bank receiver ke account ko credit karta hai."],
      ["PUT THE FLOW TOGETHER","Ek tap ke peeche messages ki chain hai."],
      ["INSTANT VS SETTLEMENT","Customer confirmation aur bank settlement alag processes hain."],
      ["WHEN STATUS IS PENDING","Delayed confirmation ka matlab lost money zaroori nahi."],
      ["A SIMPLE SAFETY RULE","PIN payment authorize karne ke liye hai, receive karne ke liye nahi."],
      ["THE INVISIBLE INFRASTRUCTURE","One tap. Many systems."]
    ][i];
    base(i,meta[0],meta[0],meta[1],(i+p)/16);
    renderers[i](p);
  };
  window.renderFrame(0,0);
})();
