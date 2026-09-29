# Ringue Neon — reformulação visual

> Registro histórico da entrega visual anterior. Controles, áudio, física e
> validação atuais estão em [EXPERIENCIA_RINGUE.md](EXPERIENCIA_RINGUE.md) e no README.

## Referência e método

A referência obrigatória foi fornecida como imagem na conversa, após constatar que `docs/referencias/ringue_neon_referencia.png` não existia no projeto. Ela foi analisada visualmente antes das alterações. Nenhum trecho da imagem, personagem ou HUD foi usado como fundo estático: toda a composição é construída por código Pygame, em módulos separados.

As capturas são geradas com `python -m tools.capture_arena`, em 1280×720, utilizando SDL `dummy`. Os cenários de captura são preparados para tornar cada etapa visível e reproduzível; não são uma gravação de uma partida humana. As imagens de aviso, queda, impacto, combate e menu foram abertas e inspecionadas. Não houve teste manual interativo.

## Comparação objetiva

| Elemento da referência | Implementação e verificação nas capturas |
| --- | --- |
| Fundo azul-marinho, luz azul/roxa saturada | Gradiente escuro, ciano `(5,235,255)`, rosa `(255,24,79)`, azul `(25,90,255)` e roxo `(164,44,255)`; glows com transparência e fachos pulsantes. |
| Evento cheio, com profundidade | Três níveis superiores e uma faixa próxima ao ringue, silhuetas, braços e bastões luminosos; torcida desfocada abaixo do piso. |
| Três telões | Dois painéis laterais de 245×176 px com silhuetas próprias e painel central de 294×131 px com troféu geométrico. |
| Combatentes com presença | Altura física de 124 px, antes 76 px: aumento de 63%. Cabeça, tronco, braços, antebraços, pernas e pés articulados; cores separadas e flash de dano. |
| Quatro postes e três cordas | Quatro postes altos, linhas ciano/roxo, piso dividido, reflexão e estrutura mecânica inferior. As duas plataformas suspensas funcionais foram preservadas. |
| Piso no terço inferior | Linha física dos pés em y=550 (76% da altura); a referência coloca os pés aproximadamente em 71%. O cenário se aproxima da composição mantendo a geometria aprovada. |
| Foco dourado na queda | Feixe vertical, marcador pulsante, quadrados descendentes, Panela girando e trilha; amarelo reservado à entrega/arma e seus efeitos. Arma equipada usa acabamento metálico claro. |
| HUD nos cantos e topo central | Retratos, JOGADOR/INIMIGO, barras de 194×18 px e números; título e DUELO separados; três espaços de 90×69 px no canto inferior direito. |
| Luta legível no centro | Nenhum telão ou elemento de primeiro plano cobre os combatentes no piso; HUD fica fora da região central. |

Diferenças mantidas: renderização geométrica mais simples, sem a textura pictórica, perspectiva elaborada e iluminação volumétrica da ilustração. A fidelidade à sensação de impacto e à emoção de um evento competitivo precisa ser avaliada durante partidas humanas, não apenas nas capturas.

## Ajustes feitos após inspecionar as capturas

- Corrigido o texto de controle que apresentava `ESPA?O`.
- Aumentada a intensidade dos fachos e variada a cor das silhuetas para melhorar a leitura da torcida.
- Conferido que o inventário não cobre a luta e que o primeiro plano permanece abaixo dos pés.
- Conferidos flash do atingido, Panela equipada e diferença entre vida atual e barra atrasada.
- Mantido o cenário antigo e a escala visual original dos personagens decorativos do menu.

## Testes e desempenho

Os 22 casos originais permanecem, atualizados para a Panela e para a antecipação real dos golpes. Foram adicionados dez testes para janela sem dano, atributos da Panela, pontos seguros, dano único da queda, impacto/coleta, decisões da CPU, atraso da vida, zoom, limites dos efeitos e congelamento.

Na última medição, o **duelo ativo completo** teve média de **14,400 ms** e percentil 95 de **22,293 ms**. A composição sintética de estresse teve média de 16,164 ms e percentil 95 de 41,529 ms; os passos isolados de simulação tiveram média de 0,094 ms. Houve grande variação entre execuções: uma medição anterior de renderização registrou 7,329 ms de média e 14,307 ms no percentil 95. Os valores não permitem atribuir com segurança diferenças de tempo somente às alterações de código.

São medições locais com SDL `dummy`, sujeitas à carga do computador, sem custo de uma janela gráfica real. O limite do loop continua sendo 60 FPS, mas os picos medidos excederam o orçamento de 16,7 ms: **60 FPS estáveis ainda não foram comprovados**. A medição no computador de destino permanece pendente.

A ferramenta descarta 30 quadros de aquecimento e mede 330 quadros de uma composição de estresse com dois combatentes, luzes, feixe e partículas. Mede também 360 passos reais de simulação em separado. `desempenho.json` registra a execução mais recente, que pode diferir dos valores acima. Glows estáticos são pré-renderizados; superfícies transparentes são reutilizadas e desenhadas apenas nas regiões úteis. Há limites de 180 partículas, 16 ondas e 24 eventos de áudio pendentes.

Também foi acrescentada uma medição integrada de simulação e desenho durante os quadros ativos de um duelo, registrada nos campos `live_*`. A tela de resultado é armazenada após o primeiro desenho, pois a partida já está congelada.

A base do cenário, iluminação ampla e ringue ficam compostos em uma superfície opaca; apenas núcleos de luz pulsantes, torcida intermitente, combatentes e efeitos de ação mudam a cada quadro. Isso evita reconstruir o cenário e alocar superfícies grandes continuamente.

## Arquivos desta reformulação

Alterados:

- `scripts/combat/weapon.py`: Panela, queda perigosa e coleta após impacto.
- `scripts/entities/fighter.py`: tamanho, hitbox, antecipação, recuperação e aterrissagem.
- `scripts/entities/enemy.py`: avaliação da entrega e espera segura.
- `scripts/scenes/ringue_neon.py`: integração dos efeitos e cache do resultado.
- `scripts/scenes/menu.py`: fixa o desenho antigo nos combatentes decorativos.
- `scripts/effects/particles.py`: emissão direcional.
- `scripts/ui/hud.py`: composição e vida atrasada.
- `tests/test_gameplay.py`: os casos existentes adaptados à Panela e à antecipação.
- `README.md`: mecânicas, execução, arquitetura e validação atualizadas.

Criados:

- `scripts/effects/competitive_arena.py`, `neon.py` e `impact.py`.
- `scripts/entities/fighter_art.py`.
- `tests/test_presentation.py`.
- `tools/__init__.py` e `tools/capture_arena.py`.
- `docs/VALIDACAO_VISUAL.md` e capturas temporárias em `.local/capturas/`.

Os arquivos de configuração, geometria JSON, gerenciador do jogo, controles, loja e pausa foram mantidos. `tests/test_scenes.py` permanece intacto. O GDD não foi modificado.

## Verificações manuais pendentes

1. Avaliar semelhança artística com a referência no monitor real e legibilidade em movimento.
2. Jogar duelos completos para avaliar peso, antecipação, recuperação, força da Panela e dificuldade da CPU.
3. Entrar e sair da zona da entrega, tomar o impacto, disputar a coleta e descartar perto das bordas.
4. Avaliar conforto com flash, tremor e zoom de até 3%; ainda não existe opção para reduzir efeitos.
5. Conferir fluidez, latência do teclado, perda de foco, pausa, resultado e reinício em janela real.
6. Avaliar áudio quando um mixer e os sons forem implementados; nesta entrega há somente eventos preparados para essa integração.

GDD preservado, SHA-256: `31CB00A4C1DF246C7E66C846CDD3C16508ECE3C8FDDE8AE3EC6317015F4596FA`. Nenhum commit ou push realizado.
