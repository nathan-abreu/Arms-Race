# Áudio original procedural

Todos os WAVs deste diretório são criados pelo próprio projeto por meio de
osciladores, envelopes e ruído pseudoaleatório. Nenhum sample ou música de
terceiros foi utilizado. O código fonte da composição está em
`scripts/audio/synth.py` (trilhas/efeitos históricos) e
`scripts/audio/layers.py` (efeitos premium em camadas). Gerar arquivos ausentes:

```powershell
.\.venv\Scripts\python.exe -m scripts.audio.synth
.\.venv\Scripts\python.exe -m scripts.audio.layers
```

`musica/menu.wav`, `ringue.wav` e `critical.wav` são loops instrumentais de
8 segundos, 120 BPM, quatro compassos. A camada `critical` começa sincronizada
com `ringue` e ganha volume quando a vida fica baixa. Os loops têm uma rampa
curta nas extremidades para evitar cliques. São trilhas procedurais simples,
não uma produção musical de estúdio.

Para substituir, mantenha nomes, duração de 8 segundos e alinhamento rítmico
das faixas de combate. Use WAV PCM, estéreo, 16 bits, 22050 Hz, com direitos de
uso adequados. O gerador não sobrescreve arquivos existentes. Efeitos normais
usam o arquivo; variações de tom usam versões da síntese original em memória.

Os novos efeitos usam nomes `premium_*.wav`. Os arquivos antigos e a música
foram preservados. Cada receita combina camadas com envelope próprio:
transientes de ruído filtrado, corpo grave, estalo, vento e modos metálicos
não harmônicos. O impacto no chão difere do acerto da Panela no lutador.
`CUES` define camadas, grupo de mixagem e limite de repetições. Para regenerar
apenas os novos efeitos depois de editar as receitas:

```powershell
.\.venv\Scripts\python.exe -m scripts.audio.layers --force
```

O mixer reserva canais independentes: música (3), interface (2), personagem
(3), armas (2), impactos (3), ambiente (2) e plateia (2). Máximo de duas
cópias do mesmo efeito e espaçamento mínimo de 45 ms. Os efeitos são
normalizados a pico 0,72; a mixagem reserva margem para música e efeitos.
Panorama estéreo de potência constante segue a coordenada horizontal.
Variação de tom ±3% e de ganho 94–100%; efeitos são carregados antes da luta.
Impactos fortes aplicam ducking de 4 dB por 150 ms, seguido de retorno suave.

Falha ou ausência de dispositivo mantém o jogo funcional; ausência de WAV
usa a receita procedural. Volume geral/música/efeitos e mute ficam na pausa.
Uma substituição de WAV deve vir acompanhada de uma receita correspondente
se as variações de tom também precisarem usar a nova gravação. A produção
continua sintética; a avaliação de timbre/mixagem em fones reais é manual.
