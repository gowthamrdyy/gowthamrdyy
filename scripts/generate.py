"""Generate a personal GitHub dashboard from public GitHub data; no dependencies."""
import argparse,base64,collections,datetime as dt,html,json,math,re,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; A=ROOT/'assets'; A.mkdir(exist_ok=True)
USER='gowthamrdyy'
p=argparse.ArgumentParser();p.add_argument('--cache',type=Path);args=p.parse_args()
def get(url):
 return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Gowtham-Profile'}),timeout=45).read().decode()
if args.cache:
 raw=(args.cache/'contributions.html').read_text(); user=json.loads((args.cache/'user.json').read_text());repos=json.loads((args.cache/'repos.json').read_text())
else:
 raw=get(f'https://github.com/users/{USER}/contributions');user=json.loads(get(f'https://api.github.com/users/{USER}'));repos=[]
 for page in range(1,20):
  batch=json.loads(get(f'https://api.github.com/users/{USER}/repos?per_page=100&page={page}'));repos+=batch
  if len(batch)<100:break
cells={i:d for d,i in re.findall(r'data-date="([\d-]+)" id="([^"]+)"',raw)}
days=[]
for i,t in re.findall(r'<tool-tip\b[^>]*for="([^"]+)"[^>]*>(.*?)</tool-tip>',raw,re.S):
 if i in cells:
  n=re.search(r'([\d,]+) contributions?',t)
  if not n and 'No contributions' not in t:raise ValueError('Unknown contribution tooltip')
  days.append((cells[i],int(n.group(1).replace(',','')) if n else 0))
days=sorted(set(days));assert len(days)>300,'Incomplete contribution calendar'
end=days[-1][0];start=days[0][0];total=sum(n for _,n in days);active=sum(n>0 for _,n in days)
longest=run=0
for _,n in days:
 run=run+1 if n else 0;longest=max(longest,run)
current=0
for _,n in reversed(days[:-1] if days[-1][1]==0 else days):
 if not n:break
 current+=1
own=[r for r in repos if not r['fork']];langs=collections.Counter(r['language'] for r in own if r['language']);stars=sum(r['stargazers_count'] for r in own)
months=collections.defaultdict(int)
for d,n in days:months[d[:7]]+=n
E=html.escape
BG='#080f1b'; PANEL='#101c2e'; BORDER='#24334b';FG='#e9f2ff';MUT='#9eb1ca';TEAL='#57dfc2';BLUE='#739dff'
def text(x,y,s,size=18,color=FG,weight=400,extra=''):
 return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" {extra}>{E(str(s))}</text>'
def rect(x,y,w,h,fill=PANEL,rx=18):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{BORDER}"/>'
def svg(name,h,parts):
 s=f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{h}" viewBox="0 0 1200 {h}" font-family="Arial,Helvetica,sans-serif"><rect width="1200" height="{h}" rx="24" fill="{BG}"/>'+''.join(parts)+'</svg>'
 (A/name).write_text(s)
def chart(values,x,y,w,h,color=TEAL):
 peak=max(max(values),1);pts=[(x+i*w/max(len(values)-1,1),y+h-v/peak*h) for i,v in enumerate(values)]
 line=' '.join(f'{a:.1f},{b:.1f}' for a,b in pts)
 out=[f'<path d="M{x},{y+h} '+' '.join(f'L{a:.1f},{b:.1f}' for a,b in pts)+f' L{x+w},{y+h} Z" fill="{color}" opacity=".10"/>',f'<polyline points="{line}" fill="none" stroke="{color}" stroke-width="3" stroke-linejoin="round"/>']
 for frac in [0,.5,1]:
  yy=y+h-frac*h;out.insert(0,f'<path d="M{x},{yy}h{w}" stroke="{BORDER}" stroke-dasharray="4 6"/>');out.append(text(x-9,yy+4,round(peak*frac),12,MUT,extra='text-anchor="end"'))
 return ''.join(out)
# Terminal: timed text reveal stays readable without animation.
parts=['''<defs><radialGradient id="aurora"><stop stop-color="#164f86"/><stop offset="1" stop-color="#080f1b"/></radialGradient><linearGradient id="wave"><stop stop-color="#57dfc2"/><stop offset="1" stop-color="#6e6bea"/></linearGradient></defs><rect width="1200" height="610" rx="24" fill="url(#aurora)"/><path d="M650 610Q810 220 1200 190" fill="none" stroke="url(#wave)" stroke-width="100" opacity=".10"/><path d="M730 610Q920 270 1200 250" fill="none" stroke="#57dfc2" stroke-width="2" opacity=".35"/>
<style>.reveal{opacity:1}@keyframes appear{0%,3%{opacity:0}8%,100%{opacity:1}}.cursor{animation:blink 1s steps(1) infinite}@keyframes blink{50%{opacity:0}}@media(prefers-reduced-motion:reduce){.reveal,.cursor{animation:none}}</style>''',rect(0,0,1200,48,'#162135',24)]
for x,c in [(27,'#ff657a'),(50,'#ffcb6b'),(73,'#5de4a6')]:parts.append(f'<circle cx="{x}" cy="24" r="6" fill="{c}"/>')
parts += [text(600,30,'gowthamrdyy / a little about me',13,MUT,extra='text-anchor="middle"'),'<g font-family="Menlo,Consolas,monospace">',text(42,101,'~ $ whoami',19,TEAL),text(42,163,'Gowtham.',54,FG,700),text(44,203,'Think out of the box.',25,BLUE),'<g class="reveal">',text(44,264,'~ $ about',18,TEAL),text(44,303,'CSE + AI & ML student at SRMIST.',20),text(44,336,'I build web apps, explore AI, and learn by making things.',19),text(44,394,'~ $ skills',18,TEAL),text(44,431,'Python  /  JavaScript  /  TypeScript  /  Java  /  SQL',18),text(44,462,'React  /  Next.js  /  FastAPI  /  Node.js',18,MUT),text(44,511,'~ $ mindset',18,TEAL),text(44,546,'Stay curious. Build something useful. Keep improving.',19),'</g>',text(44,583,'~ $',18,TEAL),'<rect class="cursor" x="98" y="568" width="11" height="20" fill="#57dfc2"/>','</g>']
# Each terminal line types in sequence; the default clip remains fully open without CSS.
terminal=''.join(parts)
index=0
def typing(match):
 global index
 index+=1
 begin=3+(index-1)*5
 end=begin+4
 ident=f'type{index}'
 return f'<defs><clipPath id="{ident}"><rect width="1200" height="610" class="{ident}"/></clipPath></defs><style>.{ident}{{animation:{ident} 24s steps(45,end) infinite}}@keyframes {ident}{{0%,{begin}%{{width:0}}{end}%,100%{{width:1200px}}}}@media(prefers-reduced-motion:reduce){{.{ident}{{animation:none}}}}</style><g clip-path="url(#{ident})">'+match.group(0)+'</g>'
# Apply typing only to the terminal content rows, not the name or title.
a=terminal.index('<g class="reveal">');b=terminal.index('</g>',a)
terminal=terminal[:a]+re.sub(r'<text .*?</text>',typing,terminal[a:b])+terminal[b:]
svg('terminal.svg',610,[terminal])
# Real dashboard
parts=[text(40,48,'GITHUB / IN MOTION',14,TEAL,700),text(40,91,'gowthamrdyy',35,FG,700),text(40,121,f'Public activity · {start} to {end}',15,MUT)]
for x,n,label in [(40,total,'Contributions in displayed period'),(330,user['public_repos'],'Public repositories'),(620,stars,'Stars on owned repositories'),(910,user['followers'],'Followers')]:
 parts += [rect(x,151,250,118),text(x+22,204,f'{n:,}',36,FG,700),text(x+22,240,label,13,MUT)]
parts += [rect(40,291,690,268),text(64,328,'The rhythm of building',22,FG,700),text(64,352,'Monthly contributions · edge months may be partial',13,MUT),chart(list(months.values()),92,380,602,130)]
for i,k in enumerate(months):
 if i%3==0 or i==len(months)-1:parts.append(text(92+i*602/(len(months)-1),537,dt.date.fromisoformat(k+'-01').strftime('%b %y'),12,MUT,extra='text-anchor="middle"'))
parts += [rect(750,291,410,268),text(774,328,'Languages across my repos',21,FG,700),text(774,352,'Primary language · owned public repositories',12,MUT)]
colors=[TEAL,BLUE,'#c799ff','#efb96c','#fa83a4']
for i,(lang,num) in enumerate(langs.most_common(5)):
 y=383+i*34;parts += [text(774,y+10,lang,14),f'<rect x="900" y="{y}" width="{190*num/max(langs.values())}" height="10" rx="5" fill="{colors[i]}"/>',text(1135,y+10,num,13,MUT,extra='text-anchor="end"')]
for x,n,l in [(40,current,'Current streak · today may be unfinished'),(420,longest,'Longest streak in this calendar'),(800,active,'Active days in this calendar')]:
 parts += [rect(x,581,360,117),text(x+22,630,f"{n} {'day' if n==1 else 'days'}",31,TEAL,700),text(x+22,666,l,13,MUT)]
parts += [rect(40,720,1120,250),text(65,758,'Small steps. Visible progress.',22,FG,700),text(65,782,'Daily contributions · last 60 days',13,MUT),chart([n for _,n in days[-60:]],96,808,1025,113,BLUE),text(96,947,days[-60][0],12,MUT),text(1120,947,end,12,MUT,extra='text-anchor="end"'),text(40,1000,'Source: public GitHub profile · refreshes when the included workflow runs',13,MUT)]
svg('dashboard.svg',1025,parts)
# Isometric graph, one block per actual calendar day.
parts=[text(40,50,'THE CONTRIBUTION LANDSCAPE',14,TEAL,700),text(40,94,'Built day by day.',36,FG,700),text(40,126,f'{len(days)} days. {total:,} contributions. One ongoing story.',16,MUT)]
peak=max(n for _,n in days)
for i,(date,n) in enumerate(days):
 week=i//7;day=i%7;x=88+week*18+day*17;y=245+week*5.6-day*10;h=0 if not n else 5+math.log1p(n)/math.log1p(peak)*107
 top='#203148' if not n else ['#285c68','#328e98','#40bcae','#6df0c7'][min(3,int(n/max(peak,1)*4))]
 points=lambda coords:' '.join(f'{a:.1f},{b:.1f}' for a,b in coords)
 parts += [f'<g><title>{date}: {n} contributions</title><polygon points="{points([(x,y-h),(x+16,y+5-h),(x+31,y-4-h),(x+15,y-9-h)])}" fill="{top}" stroke="#080f1b" stroke-width=".7"/><polygon points="{points([(x,y-h),(x+16,y+5-h),(x+16,y+5),(x,y)])}" fill="{top}" opacity=".65"/><polygon points="{points([(x+16,y+5-h),(x+31,y-4-h),(x+31,y-4),(x+16,y+5)])}" fill="{top}" opacity=".4"/></g>']
parts += [text(44,570,'THINK',36,FG,700),text(44,610,'OUT OF THE BOX.',36,TEAL,700),text(44,648,'Curiosity → experiments → things that work.',16,MUT),text(1155,648,f'{start} — {end}',13,MUT,extra='text-anchor="end"')]
svg('landscape.svg',680,parts)
(ROOT/'data-summary.json').write_text(json.dumps({'period_start':start,'period_end':end,'contributions':total,'public_repositories':user['public_repos'],'stars_on_owned_repositories':stars,'followers':user['followers'],'current_streak':current,'longest_streak_in_period':longest,'primary_language_repo_counts':dict(langs)},indent=2)+'\n')
print(f'Generated 3 SVGs from {len(days)} real contribution days ({total} contributions).')
