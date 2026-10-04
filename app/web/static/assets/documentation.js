// A composição vem da referência; as simulações não consultam a API.
const $ = selector => document.querySelector(selector);
const $$ = selector => [...document.querySelectorAll(selector)];
const english = {
  "index.commands": "Run in your terminal",
  "diagram.flow": "Code snippets go through the model and arrive in the index",
  "vectors.input": "Choose the input text",
  "vectors.signature": "Some numbers from the vector",
  "vectors.diagram": "Two nearby authentication descriptions and a distant file description",
  "hnsw.steps": "Graph search steps",
  "hnsw.shortcut": "1. Take a shortcut",
  "hnsw.refine": "2. Narrow down the region",
  "hnsw.neighbors": "3. Find neighbors",

  "skip": "Skip to content",
  "navigation": "Documentation navigation",
  "nav.search": "Search ↗",
  "hero.title": "How code-rag works",
  "hero.description": "code-rag splits files, computes embeddings and retrieves snippets by similarity. A local implementation to understand the process and adapt to your own project.",
  "hero.queryLabel": "question",
  "hero.query": "where is the token validated?",
  "hero.scroll": "↓ how it works",
  "diagram.code": "1 \u00b7 Code snippets",
  "diagram.model": "2 \u00b7 Embedding model",
  "diagram.index": "3 \u00b7 Vector index",
  "index.title": "From a folder to an index",
  "index.description": "The indexing command reads your folder and prepares snippets for future queries. The folder is mounted read-only.",
  "index.walk": "Discover files",
  "index.walkBody": "Skips dependencies, builds, lockfiles and binaries. Indexable text files up to 512 KB continue.",
  "index.chunk": "Split the code",
  "index.chunkBody": "Tree-sitter extracts symbols in Python, Go, Java, TypeScript and JavaScript. Other text uses 100-line windows with 15 overlapping lines by default.",
  "index.reuse": "Reuse and embed",
  "index.reuseBody": "The text hash identifies reusable embeddings. The model computes vectors for new or changed snippets in batches.",
  "index.store": "Store in Postgres",
  "index.storeBody": "One transaction replaces the project index. Each snippet keeps its file, symbol, lines and embedding.",
  "vectors.title": "From text to meaning",
  "vectors.description": "The model turns a snippet into a list of numbers: its embedding. Different descriptions of the same subject may have similar representations. Select a phrase to follow the result.",
  "cosine.title": "Compare vectors by their angle",
  "cosine.description": "The more similar the question and snippet vectors, the more likely the snippet is to cover what you are looking for. Rotate the point around the entire circle: the angle changes similarity and helps explain the comparison. ",
  "cosine.diagram": "Two vectors with an adjustable angle",
  "cosine.query": "a · question",
  "cosine.chunk": "b · snippet",
  "cosine.score": "similarity",
  "cosine.angle": "angle",
  "cosine.control": "Rotate the point or adjust the angle from 0\u00b0 to 360\u00b0",
  "space.title": "Retrieve the nearest snippets",
  "space.description": "Your question uses the same model as indexing. Its vector is compared with snippet vectors, and the closest form the result. Click the map or choose a topic.",
  "space.diagram": "Illustrative map of snippets grouped by topic",
  "space.hint": "click to position the question",
  "space.questions": "Question topics",
  "space.auth": "Authentication",
  "space.cache": "Cache",
  "space.files": "Files",
  "hnsw.title": "Find paths through the graph",
  "hnsw.description": "HNSW connects vectors in layers. Search starts with a few shortcuts, moves down to more detailed connections, and looks for neighbors of the question. Explore each step or follow the entire path.",
  "hnsw.trace": "Show the path →",
  "hnsw.graphDiagram": "A branching graph in three layers, from shortcuts to neighbors",
  "compare.title": "Same query, different criteria",
  "compare.description": "When you know the name, literal search works well. When you describe behavior, embeddings may relate your question to code. Both approaches are useful.",
  "compare.cases": "Comparison scenarios",
  "compare.natural": "Describe the behavior",
  "compare.exact": "Search the exact name",
  "compare.literal": "literal text",
  "setup.title": "Run it on your machine",
  "setup.description": "Clone the repository, prepare the environment and index your own folder. Use your terminal or copy the prompt below to get help from an assistant.",
  "setup.environment": "Prepare and index",
  "setup.requirements": "Git, Make and Docker with Compose. On Windows, use WSL2. Run the commands from the repository folder.",
  "setup.repo": "Repository and instructions ↗",
  "setup.verify": "Verify and connect",
  "setup.verifyBody": "Check /health and /api/projects. Search at /search queries the snippets you have indexed. An agent can use the same index through MCP.",
  "setup.search": "Open local search →",
  "setup.promptTitle": "Prompt to configure the project with an assistant",
  "setup.os": "Operating system",
  "setup.auto": "Identify with the assistant",
  "setup.promptLabel": "Setup prompt",
  "setup.copy": "Copy prompt",
  "footer.search": "Local search",
  "footer.setup": "Setup",
  "footer.repo": "Repository ↗"
};
const portuguese = {};
$$('[data-i18n]').forEach(element => { portuguese[element.dataset.i18n] = element.innerHTML; });
$$('[data-label]').forEach(element => { portuguese[element.dataset.label] = element.getAttribute('aria-label'); });
let language = 'pt';
try { language = localStorage.getItem('coderag-how-language') === 'en' ? 'en' : 'pt'; } catch (_) {}
const localized = values => values[language === 'en' ? 1 : 0];
const t = key => (language === 'en' ? english : portuguese)[key] || key;
const save = (key, value) => { try { localStorage.setItem(key, value); } catch (_) {} };
const selectButtons = (selector, key, value) => $$(selector).forEach(button => button.setAttribute('aria-pressed', String(button.dataset[key] === String(value))));
const number = value => value.toLocaleString(language === 'en' ? 'en-US' : 'pt-BR', {minimumFractionDigits:2,maximumFractionDigits:2});
const svgElement = (tag, attrs = {}) => {
  const element = document.createElementNS('http://www.w3.org/2000/svg', tag);
  Object.entries(attrs).forEach(([key, value]) => element.setAttribute(key, String(value)));
  return element;
};
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
function renderTheme() {
  const dark = document.documentElement.dataset.theme === 'dark';
  const label = localized(dark ? ['Ativar tema claro','Switch to light theme'] : ['Ativar tema escuro','Switch to dark theme']);
  $('#theme-toggle').setAttribute('aria-label',label); $('#theme-toggle').title = label;
  $('#theme-toggle use').setAttribute('href',dark ? '#i-sun' : '#i-moon');
}
$('#theme-toggle').addEventListener('click', () => {
  const theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
  document.documentElement.dataset.theme = theme; save('coderag-how-theme',theme); renderTheme();
});

// Os números e as posições são exemplos didáticos; nenhum modelo roda na página.
const embedExamples = [
  {label:['Validar um token de acesso.','Validate an access token.'],detail:['Autenticação · A','Authentication · A'],vec:[.42,-.18,.91,-.32,.57,.28],x:150,y:116},
  {label:['Confirmar a autenticidade de uma credencial JWT.','Confirm the authenticity of a JWT credential.'],detail:['Autenticação · B','Authentication · B'],vec:[.38,-.14,.86,-.28,.51,.31],x:190,y:145},
  {label:['Salvar uma imagem enviada pelo usuário.','Save an image uploaded by a user.'],detail:['Arquivos · C','Files · C'],vec:[-.31,.42,-.08,.65,-.49,.18],x:338,y:227}
];
let embeddingSelection=0;
const ease='cubic-bezier(.22,.61,.36,1)';
function animateElement(element,frames,options={}) {
  element.getAnimations().forEach(animation=>animation.cancel());
  if(reducedMotion.matches)return;
  return element.animate(frames,{duration:650,easing:ease,...options});
}
function drawConnection(path,delay=0,duration=650){
  const length=path.getTotalLength();
  path.style.strokeDasharray=length;path.style.strokeDashoffset='0';
  animateElement(path,[{strokeDashoffset:String(length)},{strokeDashoffset:'0'}],{duration,delay,fill:'backwards'});
}
function renderVectors(animate=false) {
  const options=$('#embed-options');options.replaceChildren();
  embedExamples.forEach((example,index)=>{
    const button=document.createElement('button');button.type='button';button.className='embedding-choice';button.dataset.embedding=index;button.setAttribute('aria-pressed',String(index===embeddingSelection));
    const label=document.createElement('span');label.textContent=localized(example.detail);
    const text=document.createElement('strong');text.textContent=localized(example.label);button.append(label,text);
    button.addEventListener('click',()=>{embeddingSelection=index;renderVectors(true);});options.append(button);
  });
  const example=embedExamples[embeddingSelection];
  $('#embed-values').textContent='[ '+example.vec.map(number).join(' / ')+' / … ]';
  const map=$('#embed-map');map.replaceChildren();
  for(let x=40;x<=420;x+=40)map.append(svgElement('line',{x1:x,y1:30,x2:x,y2:280,stroke:'var(--grid)'}));
  for(let y=40;y<=280;y+=40)map.append(svgElement('line',{x1:20,y1:y,x2:420,y2:y,stroke:'var(--grid)'}));
  map.append(svgElement('ellipse',{cx:166,cy:132,rx:79,ry:69,fill:'var(--tint)'}));
  const connection=svgElement('path',{d:'M150 116L190 145',stroke:'var(--accent)','stroke-width':2,fill:'none'});map.append(connection);
  embedExamples.forEach((item,index)=>{
    const group=svgElement('g');const color=index===2?'var(--gold)':index===1?'var(--blue)':'var(--accent)';
    if(index===embeddingSelection)group.append(svgElement('circle',{cx:item.x,cy:item.y,r:20,fill:'var(--bg-0)',stroke:color,'stroke-width':1.5}));
    group.append(svgElement('circle',{cx:item.x,cy:item.y,r:7,fill:color}));
    const letter=svgElement('text',{x:item.x+15,y:item.y-13,fill:color});letter.textContent=['A','B','C'][index];group.append(letter);map.append(group);
    if(animate&&index===embeddingSelection)animateElement(group,[{transform:'translateY(8px)'},{transform:'translateY(0px)'}]);
  });
  const auth=svgElement('text',{x:92,y:49});auth.textContent=t('space.auth');map.append(auth);
  const files=svgElement('text',{x:303,y:282});files.textContent=t('space.files');map.append(files);
  $('#embed-insight').textContent=localized(embeddingSelection===2?
    ['C fala de salvar imagens. Seus números são diferentes e seu ponto fica longe das duas descrições de autenticação.','C is about saving images. Its numbers differ, placing it away from the two authentication descriptions.']:
    ['A e B usam palavras diferentes para falar de validar credenciais. Seus vetores parecidos aproximam os dois pontos.','A and B use different words to describe validating credentials. Their similar vectors bring the two points together.']);
  if(animate)drawConnection(connection);
}

function renderCosine() {
  const angle=Number($('#cos-angle').value),rad=angle*Math.PI/180,x=230+Math.cos(rad)*130,y=210-Math.sin(rad)*130;
  $('#cos-a').setAttribute('x2',x);$('#cos-a').setAttribute('y2',y);$('#cos-handle').setAttribute('cx',x);$('#cos-handle').setAttribute('cy',y);
  const arc=[];for(let i=0;i<=60;i++){const theta=rad*i/60;arc.push(`${i?'L':'M'}${230+Math.cos(theta)*40},${210-Math.sin(theta)*40}`);}$('#cos-arc').setAttribute('d',arc.join(''));
  const cosine=Math.abs(Math.cos(rad))<1e-12?0:Math.cos(rad);$('#cos-big').textContent=number(cosine);$('#cos-ang').textContent=`${angle}°`;$('#cos-dot').textContent=(cosine>=0?'+':'')+number(cosine);
  const verdict=cosine>.7?
    ['Significado parecido: o trecho pode tratar do que você perguntou, mesmo usando outras palavras.','Similar meaning: the snippet may cover what you asked about, even using different words.']:
    cosine>.2?['Há alguma relação de significado, mas este trecho pode não responder à sua pergunta.','There is some relation in meaning, but this snippet may not answer your question.']:
    cosine>=-.2?['Pouca relação de significado: esse trecho provavelmente trata de outro assunto.','Little relation in meaning: this snippet probably covers another subject.']:
    ['Significados bem diferentes: este trecho tende a ser menos relevante para a pergunta.','Very different meanings: this snippet tends to be less relevant to your question.'];
  $('#cos-verdict').textContent=localized(verdict);
  $('#cos-angle').setAttribute('aria-valuetext',`${angle}°, ${localized(['similaridade','similarity'])} ${number(cosine)}`);
}
$('#cos-angle').addEventListener('input',renderCosine);
let draggingPointer=null;
function dragCosine(event){
  if(event.pointerId!==draggingPointer)return;
  const point=new DOMPoint(event.clientX,event.clientY).matrixTransform($('#cos-svg').getScreenCTM().inverse());
  if(Math.hypot(point.x-230,point.y-210)<8)return;
  const angle=(Math.atan2(210-point.y,point.x-230)*180/Math.PI+360)%360;
  $('#cos-angle').value=Math.round(angle);renderCosine();
}
$('#cos-handle').addEventListener('pointerdown',event=>{draggingPointer=event.pointerId;event.currentTarget.setPointerCapture(event.pointerId);event.preventDefault();dragCosine(event);});
$('#cos-handle').addEventListener('pointermove',dragCosine);
['pointerup','pointercancel','lostpointercapture'].forEach(type=>$('#cos-handle').addEventListener(type,()=>{draggingPointer=null;}));

const scatterData = [
 {x:180,y:140,c:0,name:'validate_token',file:'auth.py:12'}, {x:225,y:112,c:0,name:'verify_jwt',file:'session.py:24'}, {x:148,y:182,c:0,name:'parse_bearer',file:'middleware.py:36'}, {x:242,y:170,c:0,name:'require_auth',file:'routes.py:18'}, {x:190,y:213,c:0,name:'check_session',file:'session.py:44'},
 {x:440,y:182,c:1,name:'refresh_cache',file:'cache.py:19'}, {x:489,y:160,c:1,name:'invalidate_cache',file:'store.py:52'}, {x:514,y:220,c:1,name:'get_cached',file:'cache.py:41'}, {x:433,y:252,c:1,name:'cache_key',file:'keys.py:8'}, {x:475,y:285,c:1,name:'set_ttl',file:'store.py:32'},
 {x:718,y:146,c:2,name:'save_image',file:'files.py:16'}, {x:753,y:181,c:2,name:'upload_file',file:'storage.py:28'}, {x:671,y:193,c:2,name:'write_bytes',file:'files.py:38'}, {x:710,y:233,c:2,name:'read_file',file:'storage.py:12'}, {x:784,y:227,c:2,name:'make_thumbnail',file:'images.py:55'}
];
const scatterColors=['var(--accent)','var(--accent-2)','var(--gold)'];
let mapQuery=[206,152],activeQuery=0;
function updateMapQuery(x,y,animate=false){
  mapQuery=[x,y];const group=$('#map-query');group.getAnimations({subtree:true}).forEach(animation=>animation.cancel());group.replaceChildren();
  const top=scatterData.map(point=>({...point,distance:Math.hypot(point.x-x,point.y-y)})).sort((a,b)=>a.distance-b.distance).slice(0,3);
  const placedLabels=[];
  const occupied=scatterData.concat({x,y});
  top.forEach((point,index)=>{
    const path=svgElement('path',{d:`M${x} ${y}L${point.x} ${point.y}`,fill:'none',stroke:scatterColors[point.c],'stroke-width':2,'data-neighbor':point.name});group.append(path);
    const ring=svgElement('circle',{cx:point.x,cy:point.y,r:10,fill:'none',stroke:scatterColors[point.c],'stroke-width':1.5});group.append(ring);
    // Valor de proximidade do desenho, independente do índice e do modelo reais.
    const value=number(Math.max(0,1-point.distance/400));
    const candidates=[[55,-26],[55,26],[-55,-26],[-55,26],[60,0],[-60,0],[0,-44],[0,44]];
    const position=candidates.map(([dx,dy])=>({x:point.x+dx,y:point.y+dy})).find(candidate=>
      candidate.x>98&&candidate.x<852&&candidate.y>84&&candidate.y<364&&
      !occupied.some(node=>Math.abs(node.x-candidate.x)<48&&Math.abs(node.y-candidate.y)<28)&&
      !placedLabels.some(label=>Math.abs(label.x-candidate.x)<78&&Math.abs(label.y-candidate.y)<38)
    )||{x:point.x+55,y:point.y-44};
    placedLabels.push(position);
    const labelX=position.x,labelY=position.y;
    const label=svgElement('g',{class:'vector-label','data-vector-value':value});
    label.append(svgElement('rect',{x:labelX-36,y:labelY-16,width:72,height:32,rx:6}));
    const text=svgElement('text',{x:labelX,y:labelY,class:'vector-value'});text.textContent=value;label.append(text);group.append(label);
    if(animate){
      drawConnection(path,index*110,600);
      animateElement(ring,[{opacity:0},{opacity:1}],{delay:450+index*110,fill:'backwards',duration:250});
      animateElement(label,[{opacity:0},{opacity:1}],{delay:600+index*110,fill:'backwards',duration:180});
    }
  });
  const question=svgElement('circle',{cx:x,cy:y,r:8,fill:'var(--text-strong)',stroke:'var(--accent)','stroke-width':2});group.append(question);
  if(animate)animateElement(question,[{opacity:.4},{opacity:1}],{duration:250});
  $('#map-summary').textContent=top.map(point=>`${point.name}: ${number(Math.max(0,1-point.distance/400))}`).join(' · ');
}
function renderScatter(){
 const svg=$('#scatter-svg');svg.replaceChildren();
 for(let x=100;x<900;x+=100)svg.append(svgElement('line',{x1:x,y1:65,x2:x,y2:320,stroke:'var(--grid)'}));
 for(let y=100;y<=300;y+=100)svg.append(svgElement('line',{x1:60,y1:y,x2:850,y2:y,stroke:'var(--grid)'}));
 scatterData.forEach(point=>{
  const dot=svgElement('circle',{cx:point.x,cy:point.y,r:5,fill:scatterColors[point.c],stroke:'var(--bg-0)','stroke-width':1.5});
  const title=svgElement('title');title.textContent=`${point.name} · ${point.file}`;dot.append(title);
  dot.addEventListener('pointerenter',event=>{const wrap=$('#space .space-wrap').getBoundingClientRect(),tip=$('#scatter-tip');tip.textContent=title.textContent;tip.style.left=Math.max(10,Math.min(wrap.width-190,event.clientX-wrap.left))+'px';tip.style.top=(event.clientY-wrap.top+12)+'px';tip.style.opacity=1;});
  dot.addEventListener('pointerleave',()=>{$('#scatter-tip').style.opacity=0;});svg.append(dot);
 });
 svg.append(svgElement('g',{id:'map-query'}));updateMapQuery(...mapQuery);
 $('#scatter-legend').replaceChildren();[t('space.auth'),t('space.cache'),t('space.files')].forEach((name,index)=>{const row=document.createElement('div');row.className='row';const swatch=document.createElement('span');swatch.className='sw';swatch.style.background=scatterColors[index];row.append(swatch,document.createTextNode(name));$('#scatter-legend').append(row);});
 selectButtons('[data-query]','query',activeQuery);
}
$('#scatter-svg').addEventListener('click',event=>{const point=new DOMPoint(event.clientX,event.clientY).matrixTransform(event.currentTarget.getScreenCTM().inverse());if(point.x<60||point.x>850||point.y<65||point.y>320)return;activeQuery=-1;selectButtons('[data-query]','query',activeQuery);updateMapQuery(point.x,point.y,true);});
$$('[data-query]').forEach(button=>button.addEventListener('click',()=>{activeQuery=Number(button.dataset.query);selectButtons('[data-query]','query',activeQuery);updateMapQuery(...[[206,152],[475,230],[732,196]][activeQuery],true);}));

// Um grafo pequeno explica as camadas e as escolhas sucessivas.
const graphNodes=[
 [70,140,0],[165,94,0],[159,219,0],
 [300,86,1],[359,148,1],[286,201,1],[374,255,1],[415,88,1],[430,200,1],[314,278,1],[391,39,1],
 [564,88,2],[620,61,2],[680,98,2],[551,160,2],[605,145,2],[657,159,2],[707,151,2],[565,222,2],[617,214,2],[670,224,2],[711,244,2],[555,285,2],[618,281,2],[674,289,2],[728,93,2],[518,115,2],[722,295,2],[517,250,2]
];
const graphEdges=[[0,1],[0,2],[1,2],[1,3],[2,5],[3,4],[3,7],[3,10],[4,5],[4,7],[4,8],[5,6],[5,9],[6,8],[6,9],[7,8],[7,10],[8,15],[7,12],[11,12],[11,14],[11,26],[12,13],[13,16],[13,17],[13,25],[14,15],[14,18],[15,16],[15,19],[16,17],[16,20],[17,21],[18,19],[18,22],[18,28],[19,20],[19,23],[20,21],[20,24],[21,27],[22,23],[23,24],[24,27],[25,17],[26,14],[28,22]];
const graphRoute=[[0,1],[1,3],[3,4],[4,8],[8,15],[15,19],[19,20]];
let graphStep=2,graphTimers=[];
const graphWide=matchMedia('(min-width:761px)');
function cancelGraphSequence(){graphTimers.forEach(clearTimeout);graphTimers=[];$('#hnsw-svg').getAnimations({subtree:true}).forEach(animation=>animation.cancel());}
function renderHnsw(animate=false){
 const graph=$('#hnsw-svg');graph.replaceChildren();
 const wide=graphWide.matches;
 graph.setAttribute('viewBox',wide?'0 0 760 340':'0 0 350 650');
 const nodes=wide?graphNodes:graphNodes.map(([x,y,layer])=>layer===0?[x+45,y*.55+10,layer]:layer===1?[(x-250)*1.25+30,(y-39)*.42+235,layer]:[(x-500)*1.2+20,(y-61)*.48+430,layer]);
 const labelPositions=wide?[[25,325],[250,325],[515,325]]:[[25,172],[25,372],[25,590]];
 const labels=[['L2 · atalhos','L2 · shortcuts'],['L1 · aproximação','L1 · narrowing down'],['L0 · vizinhos','L0 · neighbors']];
 labelPositions.forEach(([x,y],index)=>{const label=svgElement('text',{x,y});label.textContent=localized(labels[index]);graph.append(label);});
 graphEdges.forEach(([a,b])=>{const first=nodes[a],second=nodes[b];graph.append(svgElement('line',{x1:first[0],y1:first[1],x2:second[0],y2:second[1],stroke:'var(--line)','stroke-width':1}));});
 const route=graphRoute.slice(0,[1,4,7][graphStep]);
 route.forEach(([a,b],index)=>{const first=nodes[a],second=nodes[b],path=svgElement('path',{d:`M${first[0]} ${first[1]}L${second[0]} ${second[1]}`,stroke:'var(--accent)','stroke-width':2.5,fill:'none','data-route-edge':index});graph.append(path);if(animate)drawConnection(path,index*160,350);});
 const visited=new Set(route.flat());
 nodes.forEach(([x,y,layer],index)=>{graph.append(svgElement('circle',{cx:x,cy:y,r:visited.has(index)?6:4,fill:visited.has(index)?'var(--accent)':'var(--muted-2)',opacity:layer>graphStep?.4:1}));});
 const last=nodes[route[route.length-1][1]];
 graph.append(svgElement('circle',{cx:last[0],cy:last[1],r:13,fill:'none',stroke:'var(--accent)','stroke-width':1.5}));
 const question=svgElement('text',{x:wide?665:249,y:wide?188:610});question.textContent=localized(['pergunta','question']);graph.append(question);graph.append(svgElement('circle',{cx:wide?694:289,cy:wide?207:574,r:5,fill:'var(--blue)'}));
 selectButtons('[data-graph-step]','graphStep',graphStep);
 $('#graph-explanation').textContent=localized([
  ['Poucos nós na camada superior oferecem atalhos para uma região do índice.','A few nodes in the upper layer offer shortcuts to a region of the index.'],
  ['A busca desce e compara os vizinhos conectados para se aproximar da região da pergunta.','The search moves down and compares connected neighbors to get closer to the question’s region.'],
  ['Na camada mais detalhada, explora os vizinhos e seleciona candidatos semelhantes à pergunta.','In the most detailed layer, it explores neighbors and selects candidates similar to the question.']
 ][graphStep]);
}
$$('[data-graph-step]').forEach(button=>button.addEventListener('click',()=>{cancelGraphSequence();graphStep=Number(button.dataset.graphStep);renderHnsw(true);}));
graphWide.addEventListener('change',()=>{cancelGraphSequence();renderHnsw();});
$('#trace-search').addEventListener('click',()=>{
 cancelGraphSequence();if(reducedMotion.matches){graphStep=2;renderHnsw();return;}
 graphStep=0;renderHnsw(true);
 graphTimers.push(setTimeout(()=>{graphStep=1;renderHnsw(true);},850));
 graphTimers.push(setTimeout(()=>{graphStep=2;renderHnsw(true);graphTimers=[];},1950));
});

const compareCorpus=[
 {file:'auth.py:12',name:'validate_token',text:'def validate_token(token):',score:.86},
 {file:'session.py:24',name:'verify_jwt',text:'return jwt.decode(token, key)',score:.79},
 {file:'README.md:8',name:'authentication_notes',text:'validate_token checks an access token.',score:.66}
];
let comparisonCase=0;
function renderComparison(){
 selectButtons('[data-compare]','compare',comparisonCase);
 const query=comparisonCase?'validate_token':localized(['onde um token é validado?','where is a token validated?']);
 const grep=$('#grep-cmp-body'),rag=$('#rag-cmp-body');grep.replaceChildren();rag.replaceChildren();
 for(const column of [grep,rag]){const line=document.createElement('p');line.className='query-line';line.textContent=`“${query}”`;column.append(line);}
 const matches=compareCorpus.filter(item=>item.text.includes(query));
 matches.forEach(item=>{const line=document.createElement('div');line.className='cmp-line';const file=document.createElement('span');file.className='p';file.textContent=item.file;line.append(file,document.createTextNode(`: ${item.text}`));grep.append(line);});
 if(!matches.length){const empty=document.createElement('p');empty.className='empty-line';empty.textContent=localized(['Nenhuma ocorrência literal nessas linhas. Tente outra palavra ou um padrão.','No literal match in these lines. Try another word or a pattern.']);grep.append(empty);}
 compareCorpus.slice(0,comparisonCase?3:2).forEach(item=>{const hit=document.createElement('div');hit.className='hit';const score=document.createElement('span');score.className='score';score.textContent=number(item.score);const name=document.createElement('div');name.className='qn';name.textContent=item.name;const file=document.createElement('div');file.className='meta';file.textContent=item.file;hit.append(score,name,file);rag.append(hit);});
}
$$('[data-compare]').forEach(button=>button.addEventListener('click',()=>{comparisonCase=Number(button.dataset.compare);renderComparison();}));

function renderSetupPrompt() {
  const os = document.getElementById('setup-os').value;
  const environment = os === 'auto' ? localized(['Primeiro identifique meu sistema operacional e adapte os comandos a ele.','First identify my operating system and adapt the commands to it.']) : localized([`Meu sistema operacional é ${os}.`,`My operating system is ${os}.`]);
  const target = localized(['Pergunte o caminho absoluto da pasta de código que quero indexar antes de iniciar a indexação. Confirme comigo qual pasta usar e que ela existe.','Ask me for the absolute path of the code folder I want to index before starting indexing. Confirm which folder to use with me and check that it exists.']);
  const prompt = language === 'en' ? `Help me configure and run the code-rag reference project on my own machine. This is a local code retrieval implementation, not a hosted service. Repository: https://github.com/hjunior29/code-rag.

${environment} ${target}

Start by checking Git, Make, Docker and Docker Compose, whether Docker is running, and whether ports 8000 and 5433 are available. If this project is already running, identify its containers and reuse the existing setup. On Windows, use WSL2 with Docker integration. If a prerequisite is missing, explain how to install it for my system. If you cannot access my terminal, give me the steps and ask me to share the relevant output.

Clone the repository or use my existing checkout. Read README.md, Makefile, docker-compose.yml and .env.example before changing configuration. Run make setup to create .env if needed, preserving an existing configuration. For a new installation, use the default FastEmbed provider with BAAI/bge-small-en-v1.5, running locally without an API key. Explain that the initial model download needs internet and is cached in a Docker volume; remote embedding providers would send text to the configured API.

Run make up and verify the containers. Then index my folder with make index DIR= followed by its absolute path. Explain that the folder is mounted read-only and indexing runs in the terminal, not through the documentation page. Diagnose any errors using make ps and make logs; do not delete volumes or reset an existing database to resolve an error without discussing the data loss with me.

Check http://localhost:8000/health and http://localhost:8000/api/projects. Show me the documentation at http://localhost:8000/ and the local search interface at http://localhost:8000/search. Use a question about my code to verify that search returns real snippets with file paths, symbols and line numbers.

If I want to use an agent with MCP, explain the endpoint http://localhost:8000/mcp and its search_code, find_symbol and list_projects tools. If Claude Code is installed, show the command claude mcp add --transport http code-rag http://localhost:8000/mcp.

At the end, summarize what was configured, the project indexed, how to reindex with make index, how to stop it with make down, and any unresolved issues. Do not claim a check passed unless you actually verified it.` : `Me ajude a configurar e executar o projeto de referência code-rag na minha própria máquina. Ele é uma implementação local de recuperação de código, sem serviço hospedado. Repositório: https://github.com/hjunior29/code-rag.

${environment} ${target}

Comece verificando Git, Make, Docker e Docker Compose, se o Docker está em execução e se as portas 8000 e 5433 estão disponíveis. Se este projeto já estiver rodando, identifique seus containers e reutilize a configuração existente. No Windows, use WSL2 com integração ao Docker. Se faltar algum pré-requisito, explique como instalar no meu sistema. Se você não tiver acesso ao meu terminal, me oriente nos passos e peça as saídas relevantes.

Clone o repositório ou use meu checkout existente. Leia README.md, Makefile, docker-compose.yml e .env.example antes de alterar a configuração. Execute make setup para criar o .env se necessário, preservando uma configuração já existente. Em uma instalação nova, use o provedor padrão FastEmbed com BAAI/bge-small-en-v1.5, que roda localmente sem chave de API. Explique que o download inicial do modelo precisa de internet e fica em cache num volume Docker; provedores remotos de embeddings enviariam os textos à API configurada.

Execute make up e verifique os containers. Depois indexe minha pasta com make index DIR= seguido do caminho absoluto. Explique que a pasta é montada somente para leitura e que a indexação acontece pelo terminal, não pela página de documentação. Diagnostique erros com make ps e make logs; não apague volumes nem resete uma base existente para resolver um erro sem discutir comigo a perda de dados.

Confira http://localhost:8000/health e http://localhost:8000/api/projects. Me mostre a documentação em http://localhost:8000/ e a interface de busca local em http://localhost:8000/search. Use uma pergunta sobre meu código para verificar se a busca retorna trechos reais com arquivo, símbolo e linhas.

Se eu quiser usar um agente com MCP, explique o endpoint http://localhost:8000/mcp e as ferramentas search_code, find_symbol e list_projects. Se o Claude Code estiver instalado, mostre o comando claude mcp add --transport http code-rag http://localhost:8000/mcp.

Ao terminar, resuma o que foi configurado, o projeto indexado, como reindexar com make index, como parar com make down e qualquer pendência. Só diga que uma verificação passou se ela tiver sido realmente feita.`;
  document.getElementById('setup-prompt').value = prompt;
  document.getElementById('copy-prompt').dataset.copy = prompt;
}

$('#setup-os').addEventListener('change',renderSetupPrompt);
$('#copy-prompt').addEventListener('click',async()=>{
 try{await navigator.clipboard.writeText($('#copy-prompt').dataset.copy);$('#copy-status').textContent=localized(['Prompt copiado.','Prompt copied.']);}
 catch(_){$('#copy-status').textContent=localized(['Selecione o texto e copie manualmente.','Select the text and copy it manually.']);}
});
function setLanguage(value){
 language=value;document.documentElement.lang=value==='en'?'en':'pt-BR';document.title=localized(['Como funciona · code-rag','How it works · code-rag']);document.querySelector('meta[name=description]').content=localized(['Como funciona o code-rag: indexação local, embeddings, recuperação por similaridade e configuração.','How code-rag works: local indexing, embeddings, similarity retrieval and setup.']);
 $$('[data-i18n]').forEach(element=>{element.innerHTML=t(element.dataset.i18n);});$$('[data-label]').forEach(element=>{element.setAttribute('aria-label',t(element.dataset.label));});
 selectButtons('[data-language]','language',language);save('coderag-how-language',language);$('#copy-status').textContent='';cancelGraphSequence();renderTheme();renderVectors();renderCosine();renderScatter();renderHnsw();renderComparison();renderSetupPrompt();
}
$$('[data-language]').forEach(button=>button.addEventListener('click',()=>setLanguage(button.dataset.language)));

// O fluxo de abertura só consome animação enquanto estiver visível.
let heroVisible=true;
const heroRoute=$('.hero-route'),heroLength=heroRoute.getTotalLength();
const payloadFrames=Array.from({length:41},(_,index)=>{
 const progress=index/40,point=heroRoute.getPointAtLength(heroLength*progress);
 const scale=progress<.35?1:progress<.65?.7:.45;
 return {offset:progress,transform:`translate(${point.x}px, ${point.y}px) scale(${scale})`,opacity:progress<.04||progress>.96?0:1};
});
const heroPayloadAnimation=$('#hero-payload').animate(payloadFrames,{duration:7000,iterations:Infinity,easing:'linear'});
heroPayloadAnimation.pause();
function syncMotion(){
 const active=heroVisible&&!document.hidden&&!reducedMotion.matches;
 $('.hero-svg-wrap').classList.toggle('motion-active',active);
 if(active)heroPayloadAnimation.play();else heroPayloadAnimation.pause();
 $('#hero-payload').style.visibility=reducedMotion.matches?'hidden':'visible';
 if(reducedMotion.matches){
   document.getAnimations().filter(animation=>!(animation.effect instanceof KeyframeEffect)||!animation.effect.target.closest?.('.hero-svg-wrap')).forEach(animation=>animation.cancel());
   cancelGraphSequence();graphStep=2;renderHnsw();
 }
}
if('IntersectionObserver' in window)new IntersectionObserver(entries=>{heroVisible=entries[0].isIntersecting;syncMotion();},{threshold:.1}).observe($('.hero-svg-wrap'));
document.addEventListener('visibilitychange',()=>{syncMotion();if(document.hidden){cancelGraphSequence();renderHnsw();}});
reducedMotion.addEventListener('change',syncMotion);
syncMotion();
setLanguage(language);
