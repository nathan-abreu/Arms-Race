# Ringue Neon — integração da arena v2

A imagem `assets/imagens/ringue_neon_background_v2.png` é o único ambiente da
fase. O arquivo original não foi alterado. `CompetitiveArena` e o cenário
procedural anterior permanecem arquivados, sem importação nem chamada pela
cena. Menu, loja provisória, GDD e músicas existentes foram preservados.

## Geometria e escala

`scripts/arena_layout.py` centraliza medidas normalizadas. A origem física
dos combatentes é a sola dos pés. O piso está em **0,714 × 720 = 514 px**:
a inspeção da imagem mostrou que 74% alcançaria a borda frontal, abaixo da
superfície útil. Limites em 10,5% e 89,5%: **x=134 e x=1146**. Spawns em
29%/71%; entregas em 40%/50%/60%. Há apenas uma plataforma física, alinhada
à imagem. As plataformas suspensas anteriores não têm representação na
imagem e foram desativadas para não criar colisões invisíveis.

O JSON continua fornecendo regras da fase; `load_level` aplica a geometria
v2. O motor mantém suporte testado a plataformas e paredes para uso futuro.
F3 exibe chão, limites, solas, hurtboxes, hitboxes, mira e pontos de entrega.

A imagem de 1672×941 é carregada e decodificada uma vez por processo. A escala
proporcional para 1280×720 usa filtro suave; o arredondamento subpixel desta
fonte praticamente 16:9 preserva os quatro cantos. A janela recebe a cena
lógica completa com escala suave, sem deformação. Outras proporções recebem
barras para manter 16:9. O destino escalado é reutilizado até a próxima
mudança de resolução. A câmera limita seu recorte às bordas da imagem.

Se faltar a imagem ou ela não puder ser decodificada, o jogo usa um fundo
neutro com guia discreta do piso. Não reativa o cenário procedural antigo.

## Composição animada

`ImageArena` mantém imagem-base, máscaras de telões em perspectiva, cones,
gradientes, névoa, vinheta e superfícies de efeitos em memória. A arte não
é refeita com geometria. Overlays acrescentam:

- Holofotes ciano/azul/violeta com movimento lento e intensificação no impacto.
- Bastões luminosos com fases diferentes e flashes sobre a plateia existente.
- Brilho, varredura e interferência recortados ao interior dos telões. Vida e
  dano modulam o telão correspondente; o centro pulsa sobre o troféu da imagem.
- Pulsos ao longo das cordas existentes e reação ao contato/impacto.
- Brilhos móveis no piso, poeira e névoa azul; luz local de cada combatente.
- Pequenos deslocamentos diferentes de luzes, plateia e poeira para sugerir
  profundidade. A geometria do piso permanece fixa e coerente com a física.
- Escurecimento durante a entrega, reações a combos/coleta/nocaute, holofote
  no vencedor e confetes.

Qualidade em **Pausa → Configurações → Visual / partículas**:

| Nível | Comportamento |
|---|---|
| Baixo | 20 luzes na torcida, efeitos essenciais e até 65 partículas; sem reflexos, névoa ou cones adicionais |
| Médio (padrão) | 55 luzes, cones, névoa, reflexos discretos e até 125 partículas |
| Alto | 105 luzes, flashes, reflexos mais visíveis, poeira extra e até 180 partículas |

Tremor tem controle separado, inclusive zero. O HUD é desenhado após a câmera.

## Combatentes e controle

Silhuetas de **164 px**, ciano e rosa-vermelho, com cabeça quadrada, tronco
sólido, luvas, membros grossos e contorno azul-marinho. Membros traseiros
são mais escuros. Não há círculos de articulação expostos. Poses são
interpoladas; pés em apoio usam a distância percorrida para permanecer
plantados durante a fase de apoio. Pouso comprime as pernas; sombra e reflexo
são elementos dinâmicos. Mira para baixo abre o braço ao lado do tronco.

A separação horizontal resolve aproximação e sobreposição dos corpos. Ela
não bloqueia a passagem por cima quando a diferença de altura é suficiente.
A CPU mira no jogador após a passagem e recua brevemente depois do ataque.

Controles: A/D mover, Espaço pular (soltar cedo reduz a altura), mouse mirar,
clique esquerdo atacar, Q/E ou roda selecionar, X descartar, Esc pausar.
R reinicia após resultado; Enter confirma menus; F3 alterna diagnóstico.

Parâmetros em `scripts/balance.py`: velocidade 380 px/s; aceleração 2800;
frenagem 3400; reversão 5400; aceleração aérea 1820 (65%); impulso de salto
720; gravidade 1900 na subida e 2700 na descida; coyote/buffer 120 ms.
Altura ideal do salto: cerca de 136 px; tempo de aceleração: 136 ms;
parada: 112 ms. São estimativas contínuas; a simulação usa passos de 1/60 s.

## Combo, Panela e áudio

| Golpe | Duração total | Dano | Knockback | Hit-stop |
|---|---:|---:|---:|---:|
| Soco 1 | 230 ms | 7 | 255 px/s | 35 ms |
| Soco 2, outro braço | 250 ms | 8 | 285 px/s | 35 ms |
| Soco 3, forte | 340 ms | 13 | 440 px/s | 65 ms |
| Panela | 380 ms | 10 | 390 px/s | 65 ms |

Preparação de 45 ms; fases ativas de 80/90/115 ms nos socos. Recuperação
ocupa o restante da duração total. Cada clique produz antecipação visual;
um clique nos últimos 100 ms pode ficar na fila para o próximo golpe.
A janela de continuação é de 400 ms após terminar o golpe. Não existe ataque
automático por segurar o botão. Dano cancela o ataque e a fila. Cada golpe
atinge cada alvo uma vez, com volume ligado à luva ou ao bojo da Panela.

A entrega continua única: aviso após 6 s, marcador/alerta por 1,5 s, feixe
semitransparente, queda acelerada giratória e reflexo amarelo. O feixe termina
ao pousar. Há impacto, poeira/faíscas, onda, áudio e tremor. Coleta é liberada
120 ms depois do impacto. Jogador e CPU disputam a mesma arma.

Músicas existentes preservadas. Dois novos efeitos originais sintetizados:
`heavy_hit.wav` e `knockout.wav`. Golpe forte reduz a música brevemente a 42%,
com retorno suave. Passos baixos; pouso proporcional à velocidade; plateia
reage a golpes fortes e coleta. Camada crítica continua ligada à vida baixa.
Nocaute usa efeito próprio e fade da música. Sem dispositivo, permanece
silencioso e jogável. Não houve audição humana para avaliar a mixagem.

## Validação reproduzível

```powershell
.\.venv\Scripts\python.exe -m compileall -q main.py scripts tests tools
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m tools.validate_background --seconds 180
.\.venv\Scripts\python.exe -m tools.validate_background --window --seconds 45
.\.venv\Scripts\python.exe main.py --headless --no-audio --scene ringue --frames 120
```

As capturas preparadas e medições ficam em `.local/background_v2/`, ignorada
pelo Git. `--window` abre a janela real com entradas programadas e alterna
resolução/tela cheia; pode ser encerrado pelo X da janela. Isso não equivale
a jogar manualmente. Os testes antigos continuam, com fixtures atualizadas
para a altura de 164 px, novo chão e alcance vertical do salto.

## Resultados observados

- Antes da alteração: **59 testes aprovados**. Depois: **77 testes aprovados**.
  Cobertura inclui combos/tempos/um dano, braço alternado, buffer/cancelamento,
  Panela, separação e passagem aérea, sola plantada, física, cache/fallback,
  máscaras dos telões, cantos da imagem, qualidade, câmera, resize/fullscreen,
  áudio ausente e ducking. Sintaxe sem erros.
- Inicialização real do programa em modo headless e sem mixer: **120 quadros,
  saída normal**. GDD e PNG conferidos por SHA-256, sem alterações.
- Sessão final headless no nível **Alto**: **180,01 s, 11.178 quadros, 17 duelos**,
  **62,10 FPS**; trabalho médio por quadro **8,232 ms**, p95 **14,600 ms**.
  Pico de 67 partículas, todos os cinco estados da entrega da Panela observados.
  As entradas programadas aguardaram 9 s antes de atacar para exercitar a
  entrega; os 17 resultados foram derrotas. Vitória também foi coberta nos
  testes, nas capturas e na primeira sessão automatizada desta revisão.
- Janela real, driver SDL **windows**, áudio inicializado, nível **Alto**:
  **35,01 s, 1.904 quadros, 2 duelos completos**. Média total **54,39 FPS**,
  incluindo trocas de resolução e entrada/saída da tela cheia. No trecho
  após essas trocas (1.543 quadros), **60,25 FPS**; p95 de trabalho **20,159 ms**.
  Há quadros acima de 16,7 ms: isso não é uma garantia de 60 FPS constantes.
- Alternados **960×540 → 1280×720 em tela cheia → 1280×720 em janela**.
  Também verificado 1000×800 com barras proporcionais. O HUD mantém alinhamento
  e o recorte da câmera permanece dentro da imagem.
- Foram abertas e inspecionadas as capturas de início, corrida, salto, soco,
  combo final, Panela, impacto, vitória, F3, resize e tela cheia. Foi inspecionada
  também uma captura nativa da janela Windows durante uma partida. Um vazamento
  retangular do brilho dos telões foi identificado e corrigido com máscaras.
  Solas no piso, corpos separados e ausência do cenário antigo conferidos.
- Não houve controle manual da partida nem audição humana. A janela real foi
  conduzida por entradas programadas. A sensação e o equilíbrio dependem ainda
  dos testes manuais abaixo.

Evidências: [headless](../.local/background_v2/headless.json),
[janela](../.local/background_v2/janela.json),
[captura nativa Windows](../.local/background_v2/janela_windows_capturada.png),
[início](../.local/background_v2/01_inicio.png),
[combo final](../.local/background_v2/05_combo_final.png),
[Panela](../.local/background_v2/06_panela_caindo.png),
[alinhamento F3](../.local/background_v2/09_alinhamento_f3.png).

## Arquivos desta revisão

Criados:

- `scripts/arena_layout.py`
- `scripts/effects/image_arena.py`
- `scripts/entities/separation.py`
- `tests/test_background_v2.py`
- `tools/validate_background.py`
- `assets/audio/efeitos/heavy_hit.wav`
- `assets/audio/efeitos/knockout.wav`
- `docs/RINGUE_BACKGROUND_V2.md`

Modificados:

- `README.md`, `docs/EXPERIENCIA_RINGUE.md`
- `scripts/ai/brain.py`
- `scripts/audio/manager.py`, `scripts/audio/synth.py`
- `scripts/balance.py`, `scripts/data.py`, `scripts/viewport.py`
- `scripts/combat/melee.py`, `scripts/combat/weapon.py`
- `scripts/effects/camera.py`, `scripts/effects/feedback.py`
- `scripts/entities/fighter.py`, `scripts/entities/fighter_art.py`, `scripts/entities/poses.py`
- `scripts/scenes/options.py`, `scripts/scenes/ringue_neon.py`
- `scripts/ui/debug.py`, `scripts/ui/hud.py`, `scripts/ui/style.py`
- `tests/test_experience.py`, `tests/test_gameplay.py`, `tests/test_presentation.py`

Nenhum arquivo preexistente foi removido. Comparação por SHA-256 confirmou
que GDD, PNG v2, menu e loja permanecem idênticos aos originais desta revisão.
O inventário bruto de alterações está em `.local/background_v2/arquivos.json`.

## Limitações e avaliação manual

- Parallax é uma sugestão de profundidade por overlays; a imagem não possui
  camadas de arte independentes. As cordas desenhadas na base não se deformam;
  sua resposta dinâmica acontece no brilho sobreposto.
- O pequeno zoom da câmera usa escala direta por desempenho; a imagem-base
  e a escala da janela usam filtro suave. Cones usam luz aditiva pré-calculada.
- O fallback garante funcionamento, mas não substitui artisticamente a imagem.
- Confirmar com teclado/mouse reais a sensação de combo, salto, freada, golpes
  verticais e passagem por cima da CPU. Conferir dificuldade e mixagem por escuta.
- Testar conforto do tremor, fluidez no monitor e alternância de tela cheia
  com outras janelas. FPS depende da resolução, qualidade e ambiente Windows.
- Configurações permanecem só na sessão; não foram adicionados saves, fases
  ou loja funcional. Nenhum commit ou push foi executado.
