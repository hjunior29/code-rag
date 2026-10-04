# code-rag — documentação interativa

## Direção
Atlas interativo de recuperação de código: diagramas feitos para explicar uma implementação local, com composição editorial e instrumentos manipuláveis. Não é uma página de venda. A identidade existente e o pedido por menos animações decorativas governam a execução.

## Paleta
Manter os tokens compartilhados em app/web/static/assets/theme.css. Escuro: fundo #10121b, superfície #171a26, superfície elevada #202535, texto #f0eee9, secundário #b0b3c3, borda #303649, violeta #b5b6ff, azul #8dbbff, âmbar #edbd82. Claro: fundo #f8f6f1, superfície #fffdfa, texto #222537, secundário #5b6077, violeta #5550b4, azul #2e64ab, âmbar #926021. Não usar verde. Os acentos em superfícies claras exigem verificar contraste; cores das linhas não substituem descrições textuais.

## Tipografia
Newsreader para títulos e números expressivos; system-ui para explicação e controles. Código e fórmulas usam a fonte monoespaçada do sistema como notação técnica, sem outra fonte baixada. h1 clamp(40px, 5vw, 64px); h2 clamp(30px, 3.8vw, 44px); corpo 16px/1.65. Sem rótulos maiúsculos acima dos títulos, sem pontos finais nos títulos. Os títulos usam uma única fonte, peso e cor, sem palavras em itálico ou acentos de cor.

## Espaçamento e densidade
Unidade de 8px; conteúdo com largura máxima de 1100px, seções separadas por 80–112px, margem lateral mínima 20px. Diagramas entre 280 e 460px; nenhum palco preso ao scroll. Uma interação deve caber num painel; números e explicações ficam junto do desenho.

## Movimento — nível 5/10
Movimento explica transformação e conexão. A figura de abertura tem uma única sequência contínua, ativa somente no viewport. As outras etapas respondem a seleção, arraste ou botão. Web Animations API, SVG e CSS nativos, equivalentes ao caminho leve de animação por transform/opacity documentado pelo Motion. Não importar biblioteca somente para essas transições. Traçados SVG usam stroke-dashoffset em desenhos pequenos. Sem bobbing, parallax, cursor customizado, revelações que escondem conteúdo ou interceptação do scroll.

## Dispositivos visuais — compromisso antes dos componentes
1. Fluxo de indexação com fragmentos, codificador e destinos conectados, com pacote viajando pelas etapas.
2. Mapa semântico com três descrições selecionáveis, assinaturas numéricas e pontos relacionados em vez de barras.
3. Círculo de similaridade manipulável em 360 graus com significado explicado ao lado.
4. Mapa de recuperação que desenha três conexões até os vizinhos após o clique, com resultados identificados.
5. Grafo HNSW irregular e ramificado com níveis selecionáveis e percurso explicado em etapas.
6. Comparação de busca literal e semântica com resultados operáveis nos dois cenários.
7. Fluxo numerado da indexação e instruções reais de execução local.
8. Prompt configurável por sistema operacional, copiável e legível.
Sem luz ambiente ornamental: cores e camadas pertencem aos dados e conexões; o usuário pediu menos poluição visual.

## Regras invariáveis
PT/EN completos, temas claro/escuro persistentes e /search compatível. Tudo na documentação é ilustrativo: não executa indexação ou um modelo. Movimento reduzido mostra os estados finais e mantém controles utilizáveis. Animações canceláveis; loop de abertura suspenso fora da tela e quando a aba fica oculta. Foco visível, alvos de pelo menos 44px, contraste de texto 4.5:1 e títulos grandes 3:1. Sem overflow em 390px. Sliders acessíveis por teclado; mapas têm alternativas por botões. Sem gradiente de texto, terminais fictícios, badges promocionais ou benchmarks inventados. A comparação com grep recupera os painéis e a faixa lateral dos resultados anteriores à skill, conforme pedido explícito do usuário.

## Validação da implementação
- Chromium local: 16 combinações de largura (320, 390, 768, 1440px), idioma e tema sem overflow, traduções ausentes ou títulos ocultos.
- 40 verificações de interação: cosseno em 0/90/180/270/360 graus, descrições de embedding, recuperação de três vizinhos, etapas do grafo, cenários da comparação e sistemas operacionais do prompt.
- Mouse real: arraste até a metade inferior do círculo; clique no mapa cria conexões para os vizinhos e as animações encerram em menos de um segundo. Scroll por roda mantém deslocamento nativo. Teclado: slider chega a 360 graus com End e mantém foco visível. Botão de cópia retorna sucesso ao escrever o prompt.
- Axe: nenhuma violação WCAG A/AA nos temas claro e escuro. As 22 verificações inconclusivas de contraste em SVG foram complementadas com medição de 121 elementos de texto por tema usando cores resolvidas em canvas; nenhum ficou abaixo do requisito. Ruler preto/branco: 21:1.
- Movimento reduzido: nenhuma animação em execução, três conexões e o percurso final presentes; controles continuam funcionais.
- Abertura: amostra local de 90 intervalos de frame com média de 16,67ms e máximo de 16,80ms. Fora do viewport, nenhuma animação fica em execução. A medição não representa dispositivos mais lentos.
- Capturas examinadas: abertura em desktop e celular, embeddings, círculo, grafo em desktop e celular; busca local também renderiza sem erros de JavaScript.
- Auditoria impeccable: removidos rótulos acima dos títulos, pontos finais dos títulos, antigos estilos de listras laterais e estrutura visual de terminal fictício. Comandos reais continuam disponíveis como instruções simples. Sem gradiente de texto, glassmorphism, scroll interceptado ou animação de propriedades de layout.
- Dispositivos entregues: fluxo com fragmento móvel; mapa semântico selecionável; círculo manipulável; traçados de recuperação; grafo ramificado em etapas; comparação interativa; fluxo numerado de indexação; prompt copiável.
- Caminho escolhido: direção e componentes escritos para HTML/CSS/JS; animações nativas, sem novas dependências. Referências de movimento consultadas: https://motion.dev/docs/performance e https://motion.dev/docs/svg-animation.

## Ajustes solicitados após a primeira versão
Header somente com marca, idioma, tema e busca; sem indicadores de seção nem menu de capítulos. Remover legendas de rodapé, notas, avisos estáticos e resumos pequenos; preservar explicações centrais e feedback funcional. Comparação restaurada ao visual anterior, sem tabela. O mapa revela números de proximidade ilustrativos depois das linhas. Selects nativos com seta a 16px da borda e 48px de padding no lado direito.
