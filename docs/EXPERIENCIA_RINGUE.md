# Ringue Neon — controle, combate e experiência

> Histórico da entrega anterior. A revisão atual troca a arena por imagem e
> altera física, personagens e combos. Consulte [RINGUE_BACKGROUND_V2.md](RINGUE_BACKGROUND_V2.md)
> e o README para os parâmetros e resultados vigentes.

Esta entrega mantém o Ringue Neon como única fase. O GDD original foi lido e
preservado; os controles e regras específicos da solicitação atual prevalecem
quando diferem do documento. Não foram utilizados código, personagens, música
ou imagens de Stick Fight ou de outros jogos.

## Controles

| Entrada | Ação |
| --- | --- |
| A / D | Mover |
| Espaço | Pular; soltar cedo reduz a altura |
| Mouse | Apontar braços e golpe |
| Botão esquerdo | Atacar uma vez por clique |
| Q / E ou roda do mouse | Selecionar item |
| X | Descartar |
| Esc | Abrir/fechar pausa |
| R após resultado | Reiniciar |
| Enter | Confirmar; pular a apresentação após tê-la visto uma vez |
| F3 | Ativar/desativar diagnóstico, inicialmente desligado |

Na pausa: Continuar, Reiniciar, Controles, Configurações e Voltar ao menu.
Nas configurações, use cima/baixo para selecionar e esquerda/direita para
ajustar. Preferências duram a sessão: volume geral, música, efeitos, mute,
tremor de 0–100%, partículas baixo/médio/alto, tela cheia e resolução.

## Física e revisão de parâmetros

Parâmetros centralizados em `scripts/balance.py`, em pixels e segundos:

| Parâmetro | Valor |
| --- | ---: |
| Velocidade máxima de corrida | 370 px/s |
| Aceleração no chão | 3600 px/s² |
| Aceleração na inversão | 5400 px/s² |
| Frenagem no chão | 4200 px/s² |
| Aceleração no ar | 1400 px/s² |
| Atrito aéreo | 260 px/s² |
| Gravidade na subida | 1850 px/s² |
| Multiplicador de gravidade na queda | 1,55 |
| Impulso do salto | 820 px/s |
| Velocidade máxima de subida após soltar salto | 270 px/s |
| Coyote time / buffer | 120 ms / 120 ms |
| Hitstun / invulnerabilidade | 130 ms / 220 ms |
| Preparação / recuperação visual de ataque | 45 ms / 120 ms |
| Hit-stop forte / leve | 50 ms / 18 ms |
| Reação da CPU | 140–240 ms |

Estimativas analíticas para conferir o ajuste: chega à velocidade máxima em
cerca de 103 ms; freia em aproximadamente 88 ms (16 px de deslocamento);
inverte de +370 a -370 px/s em cerca de 137 ms. A altura máxima ideal do salto
é aproximadamente 182 px antes da discretização, suficiente para o desnível
de 155 px das plataformas. A descida usa gravidade maior para evitar flutuação.

O controlador usa passos fixos de 1/60 s com delta time, coordenadas fracionárias
e colisões separadas por eixo. Plataformas existentes continuam atravessáveis
de baixo; paredes sólidas são suportadas e testadas pelo mesmo motor, sem
fechar artificialmente as bordas da arena. Knockback só suspende o controle
durante o hitstun; depois a aceleração volta a conduzir o personagem.

## Combate, arma e CPU

O mouse é convertido de coordenadas da janela para a área lógica e, depois,
para o mundo através da câmera. A mira tem zona morta horizontal de 12 px para
orientação do corpo. A direção é capturada no início do golpe; o braço e a
arma percorrem a mesma trajetória usada na colisão. A Panela varre um arco de
65 graus, com uma amostra da trajetória anterior para reduzir falhas entre
quadros. Preparação não causa dano; cada alvo recebe no máximo um acerto por
golpe. Trocar inventário não altera um golpe em andamento. Receber dano o
cancela; ataques continuam disponíveis no ar.

| Ataque | Dano | Alcance adicional | Cooldown | Impulso |
| --- | ---: | ---: | ---: | ---: |
| Soco | 7 | 34 px | 0,32 s | 255 px/s |
| Panela | 10 | 48 px | 0,38 s | 390 px/s |
| Queda da Panela | 8 | Volume varrido durante queda | Um acerto por alvo | 330 px/s |

A Panela é anunciada após seis segundos de luta, com aviso de 1,5 segundo.
Nasce acima da tela, em uma origem vazia; a entrega espera se um corpo estiver
na origem. O marcador permanece no ponto anunciado. Feixe, giro, partículas,
alerta sonoro e impacto antecedem a coleta, liberada 120 ms após tocar o piso.
Há uma única Panela entre cenário e inventários. Descartar não causa dano;
o antigo portador espera um segundo para recolher. Inventário cheio bloqueia
coleta. Ao cair fora da arena, a arma pode ser entregue novamente após o intervalo.

A CPU observa posições atuais, decide em intervalos de reação, tem 10% de
chance de hesitar numa oportunidade de ataque, procura arma quando vale a
pena, evita o círculo durante a queda, recua durante parte dos cooldowns e
pressiona o jogador com pouca vida. Estados: observar, aproximar, manter
distância, atacar, recuar, pular, buscar arma, desviar de item, recuperar-se e
pressionar. Segurança das bordas e recuperação de dano têm prioridade.

## Apresentação e ritmo

Entrada de 650 ms, contagem 3/2/1/LUTE, controles bloqueados durante a
apresentação e opção de pular por Enter nas tentativas seguintes da sessão.
O último golpe inicia 500 ms de encerramento com física do derrotado a 18%
da velocidade; dano/IA/coleta param. O vencedor comemora e o resultado aparece.
Empate de eliminação continua contando como derrota do jogador.

O rig procedural interpola articulações e distingue guarda, corrida,
frenagem, salto, queda, pouso, ataque, hitstun e derrota. Efeitos limitados:
poeira/faíscas, rastros, flash branco, arcos, ondas, coleta, confete de vitória,
paleta vermelha na derrota e reação das luzes a golpes fortes. A vida tem
preenchimento animado e rastro atrasado. O HUD mostra cooldown e rejeição de
golpes prematuros.

Câmera acompanha suavemente o centro, muda discretamente o zoom conforme a
distância e os impactos, e dá leve prioridade à arma em queda. O recorte fica
sempre dentro do mundo. Shake pode ser zerado. A janela suporta redimensionamento,
960×540, 1280×720, 1600×900 e 1920×1080, com proporção e barras laterais/superiores
quando necessário. O HUD permanece dentro da área lógica em todas elas.

## Áudio

`AudioManager` usa três canais reservados para música e até oito efeitos
simultâneos. Há volumes independentes, mute, transição gradual e proteção
contra reiniciar a mesma música. Ringue e camada crítica iniciam sincronizados;
a camada crítica cresce quando alguém chega a 28 de vida ou após 45 s de luta.

Foram gerados 23 WAVs originais: três loops instrumentais de 8 s a 120 BPM,
cinco sons de interface e quinze efeitos. Síntese de bass/kick, notas, ruído,
envelopes e harmônicos metálicos; sem material de terceiros. Variações de tom
e volume são discretas. Arquivos ausentes usam síntese; falha de dispositivo
desativa áudio sem impedir o jogo. Detalhes de substituição estão em
`assets/audio/README.md`.

## Validação reproduzível

```powershell
.\.venv\Scripts\python.exe -m compileall -q main.py scripts tests tools
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m tools.validate_experience --seconds 180
.\.venv\Scripts\python.exe main.py --headless --no-audio --scene ringue --frames 120
```

A ferramenta de validação gera capturas preparadas de contagem, corrida,
salto, ataque, impacto, queda da arma, vida baixa, vitória, pausa, configurações,
derrota, F3 e resolução reduzida. Depois executa duelos automatizados por tempo
real, incluindo reinícios e pausa, verificando vida, unicidade da arma e limite
de partículas. Saída: `.local/experiencia/sessao_headless.json` e PNGs.

Não é um teste humano: as entradas da sessão são programadas, e o mixer SDL
dummy não permite avaliar o som por escuta. Nenhuma validação interativa ou
audição manual é alegada. Resultados medidos estão no README.

## Resultados desta entrega

- Antes das alterações: 32 testes aprovados. Depois: **59 testes aprovados**, sem remover a cobertura anterior.
- Sintaxe: `compileall` sem erros. Inicialização: 120 quadros headless com `--no-audio`, sem falhas.
- Foram executadas três sessões de 180 segundos durante os ajustes. A sessão final percorreu **11.106 quadros em 180,01 s**, com 15 duelos encerrados (11 vitórias e 4 derrotas), pausa e reinícios, sem falhas nas verificações.
- Média observada final: **61,70 FPS**; trabalho por quadro de **9,017 ms em média** e **15,706 ms no percentil 95**. Esse tempo exclui a espera do limitador. O pico foi de 111 partículas; todos os estados da entrega da Panela foram percorridos.
- Medição em SDL dummy, 1280×720, incluindo mixer dummy. Não prevê o desempenho da janela/compositor ou de outro computador. O limitador de maior precisão usa `tick_busy_loop`, que pode consumir mais CPU que uma espera comum; a física mantém passos de 1/60 s.
- Treze capturas foram geradas. As imagens dos nove estados solicitados foram abertas e inspecionadas, além de configurações, derrota e resolução reduzida. Painéis e textos ficaram dentro da janela; o HUD fica separado da área dos combatentes. Não houve teste manual interativo nem audição.

Evidências locais (ignoradas pelo Git): [medição JSON](../.local/experiencia/sessao_headless.json), [corrida](../.local/experiencia/02_corrida.png), [ataque](../.local/experiencia/04_ataque.png), [Panela caindo](../.local/experiencia/06_panela.png) e [pausa](../.local/experiencia/09_pausa.png).

A comparação com a referência confirma a distribuição ciano à esquerda/rosa à direita, fundo azul-escuro, três telões, público em camadas, cordas neon, estrutura inferior e feixe dourado exclusivo da arma. A implementação continua sendo arte procedural simplificada: brilho e volume são mais planos que na ilustração, e a perspectiva é frontal para preservar a leitura das colisões. A sensação de fluidez, força dos golpes e equilíbrio sonoro ainda precisa da avaliação humana descrita abaixo.

## Limitações e teste manual

- Preferências não persistem ao fechar; nenhuma campanha ou save completo foi adicionado.
- Música procedural simples de quatro compassos, sem arranjo longo ou produção de estúdio.
- CPU heurística, sem navegação complexa; avaliar dificuldade e exploração das plataformas.
- Confirmar resposta do teclado/mouse, sensação do salto e do golpe, leitura das poses e conforto do shake.
- Escutar mixagem, loops, transições, volume da Panela e da torcida com alto-falantes/fones reais.
- Testar tela cheia, mudança de resolução, perda de foco e estabilidade de FPS no computador de destino.
- Conferir duelo completo, coleta/descarte, derrota por queda, vitória e reinício rápido.

GDD preservado: SHA-256 `31CB00A4C1DF246C7E66C846CDD3C16508ECE3C8FDDE8AE3EC6317015F4596FA`.
