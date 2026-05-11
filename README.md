# image-pair-viewer

Visualizador interativo de pares de imagens. HTML único, sem build,
sem servidor, sem dependências.

Você arrasta um lote de imagens, o app pareia pelo nome e abre
um comparador com slider, lado a lado e modo solo. Tudo é processado
no navegador via File API + Canvas + DataView; nenhum byte sai do
dispositivo.

## Pareamento

Extrai **todos os runs de 4+ dígitos consecutivos** do nome do
arquivo e usa-os como ID composto. Funciona com convenções de
diversas marcas/épocas:

| Convenção                       | Exemplo                          | ID extraído         |
|---------------------------------|----------------------------------|---------------------|
| Canon / iPhone                  | `IMG_0093.jpg`                   | `0093`              |
| Sony Alpha                      | `DSC04321.JPG`                   | `04321`             |
| Nikon                           | `DSC_05123.JPG`                  | `05123`             |
| Fujifilm                        | `DSCF_4567.JPG`                  | `4567`              |
| Panasonic Lumix                 | `P1010234.jpg`                   | `1010234`           |
| Android (data+hora)             | `IMG_20240115_143025.jpg`        | `20240115-143025`   |
| Google Pixel                    | `PXL_20240115_143025.jpg`        | `20240115-143025`   |
| DJI                             | `DJI_0123.JPG`                   | `0123`              |
| GoPro                           | `GOPR0001.JPG`                   | `0001`              |

Dentro de cada grupo (mesmo ID), o nome **mais curto** vira `before`
e o mais longo vira `after` (assume que edits adicionam prefixo ou
sufixo). Marcadores de versão curtos como `_v2` ou `_v10` são
ignorados pelo parser, então `IMG_0093.jpg` paréia corretamente com
`IMG_0093_v10.jpg`.

Pares incompletos (1 só arquivo com aquele ID) são ignorados.

## Modos

- **Slider** — alça arrastável divide a tela.
- **Lado a Lado** — duas colunas paralelas.
- **Solo** — uma imagem por vez. Segure `Espaço` (ou clique e segure
  o mouse) para alternar momentaneamente.

## Atalhos

| Tecla              | Ação                                       |
|--------------------|--------------------------------------------|
| `←` `→`            | Foto anterior / próxima                    |
| `Espaço` (Solo)    | Segurar = alterna `before`/`after`         |
| `[` `]`            | Slider ±5%                                 |
| `+` `−`            | Zoom in / out                              |
| `0`                | Reset zoom                                 |
| `Esc`              | Fecha menu/modal · limpa seleção · **expande painéis** · reseta zoom (cascata) |
| `F`                | Tela cheia                                 |
| `I`                | Painel de informações                      |
| `S`                | Cicla modos                                |
| `Ctrl`+`A`         | Seleciona todos os pares                   |
| `Delete`           | Remove pares selecionados                  |
| `?`                | Ajuda                                      |

A tecla `Esc` segue uma **cascata de prioridade** — só executa a próxima
ação se a anterior não se aplicar: 1) fecha um menu dropdown aberto;
2) fecha o modal de ajuda; 3) limpa a seleção; 4) sai do modo "painéis
recolhidos" (equivalente a clicar de novo no botão de collapse);
5) reseta o zoom. Garante que `Esc` é um único atalho universal de
"sair do estado atual".

## Mouse / Toque

| Gesto                 | Ação                                    |
|-----------------------|-----------------------------------------|
| Roda / Pinça          | Zoom ancorado ao cursor                 |
| Arrasto               | Slider · pan com zoom                   |
| Duplo clique          | Reset zoom                              |
| Duplo clique no knob  | Slider volta a 50%                      |
| Flick horizontal      | (Mobile) próxima/anterior               |
| Toque simples         | (Mobile) ocultar/mostrar interface      |

## Painel de informações

Para cada lado do par: nome, dimensões, tamanho. Para JPEGs, lê
EXIF (data, câmera, lente, ISO, abertura, obturador, focal, autor)
via parser próprio. Se houver coordenadas GPS no EXIF, consulta a
API pública do Nominatim/OpenStreetMap pra resolver Cidade, Estado
e País — esse é o único endpoint externo do app; somente
lat/lon saem do dispositivo (nunca as fotos), com cache em memória
e throttle de 1.1 s por request.

## Strip lateral — Abrir, Ordenar, Remover

No **desktop**, a faixa de miniaturas fica como **painel lateral
esquerdo** (coluna vertical à esquerda do stage); no **mobile**
(< 901px) reverte automaticamente pra faixa horizontal embaixo,
preservando a ergonomia em tela vertical.

No topo do painel há 3 botões empilhados:

- **Abrir fotos** — adiciona mais fotos à sessão sem perder as atuais
  (alternativa ao drag-and-drop full-page)
- **Ordenar** (split-button) — clicando no nome cicla entre Nome →
  Inserção → Captura → Modificação. A seta laranja à direita inverte
  a ordem (crescente ↔ decrescente). Default: Nome crescente (A → Z).
- **Remover** — sempre visível, em vermelho. Desabilitado quando
  nada está selecionado. Com 2+ selecionados, vira `Remover (5)`.

A escolha de critério e direção **NÃO** são persistidas — a cada
reload o sort volta pro default (`name` / `asc`). Veja a seção
"Persistência" mais abaixo.

Os 3 elementos (Abrir, Ordenar, Remover) têm tipografia fixa de
12 px e altura 28 px, casando com os botões da topbar. O painel
respeita um piso de 136 px de largura, suficiente pras labels mais
longas com folga.

As miniaturas usam `object-fit:contain` — a foto inteira sempre cabe
no card, podendo sobrar barras pretas nas laterais (foto vertical)
ou em cima/embaixo (foto horizontal). Isso evita o problema comum
do `cover` de cortar cabeças ou conteúdo importante em fotos com
aspect ratio diferente do quadrado do card.

## Adicionar mais fotos à sessão

Três formas de incrementar a sessão sem perder o estado atual:

1. **Botão "Abrir fotos"** na coluna de ferramentas da strip
2. **Arrastar arquivos** sobre qualquer parte da página — quando o
   usuário começa a arrastar, um overlay laranja com borda tracejada
   aparece ("Solte as fotos aqui") indicando a área de drop. Funciona
   tanto na tela inicial quanto durante o uso do app.
3. **Drop direto na tela inicial** (antes de carregar qualquer foto)

Pares com ID já presente são silenciosamente ignorados; um toast
sumariza "X novo(s) par(es) · Y já estava(m) na sessão". Apenas
arquivos com MIME `image/*` ou extensão de imagem são aceitos —
outros tipos são descartados.

## Carregamento progressivo

Quando você seleciona um lote de fotos, o app abre **imediatamente**
com miniaturas em shimmer (animação de carregamento) — sem tela de
loading separada. Os pares são processados em background, e cada
miniatura "se resolve" assim que sua imagem está pronta. Se você
clicar num par ainda pendente, o viewer mostra um spinner até a
imagem ficar disponível.

## Recolher painéis e redimensionar

Um **único botão** no canto inferior direito da view central recolhe
TODOS os painéis simultaneamente (topbar, strip, sidebar), expandindo
o viewer pra ocupar a tela toda. Clicar de novo expande tudo de volta.
O estado NÃO é persistido — a cada reload os painéis voltam expandidos.

**Resize**: arraste a borda interna da sidebar (esquerda) ou do
strip (topo) pra ajustar tamanho. **Duplo clique** na borda volta
ao tamanho padrão. O tamanho vale só durante a sessão atual.

Ao aumentar a altura da strip, **tudo escala junto** proporcionalmente:
miniaturas maiores, botões maiores, textos maiores, bolinha de
seleção maior — controlado por uma CSS variable única (`--thumb-h`).
Encolher = tudo encolhe junto.

`F11` (tela cheia nativa do navegador) e a tecla `F` (Fullscreen API
via JS) continuam funcionando paralelamente — não interferem entre si.

## Seleção múltipla e remoção

Cada miniatura tem uma **bolinha de seleção** no canto superior
direito (sutil em desktop, aparece em hover; sempre visível em
touch). Comportamento estilo Windows Explorer / Finder:

- Clique na **bolinha** → alterna a seleção daquele par (sem navegar)
- Clique no **corpo do thumb** → navega (não altera seleção)
- **Ctrl/⌘+clique** anywhere no thumb → alterna seleção
- **Shift+clique** → seleciona range entre âncora e clicado
- **Ctrl+A** → seleciona todos os pares
- **Delete** ou **Backspace** → remove selecionados (com modal de confirmação)
- Clique no **espaço vazio da strip** → limpa seleção
- **Esc** → limpa seleção
- **Long-press** ~500 ms no thumb (mobile) → alterna seleção

O botão **Remover** está sempre visível na strip-tools. Quando
nenhum par está selecionado, ele remove o par **atualmente aberto**
no viewer. Quando há seleção, remove os selecionados (com contagem
no label se 2+).

## Idioma

Botão na topbar (mostra a label do idioma ativo: `EN` / `PT` / `ES` /
`FR` / `DE` / `IT` / `JA` / `ZH`) abre um menu com 8 idiomas:

- 🇺🇸 **English (EN-US)** — *default*
- 🇧🇷 **Português (PT-BR)**
- 🇪🇸 **Español (ES-ES)**
- 🇫🇷 **Français (FR-FR)**
- 🇩🇪 **Deutsch (DE-DE)**
- 🇮🇹 **Italiano (IT-IT)**
- 🇯🇵 **日本語 (JA-JP)**
- 🇨🇳 **中文 (ZH-CN)**

O default é **fixo em EN-US** — `navigator.language` é ignorado por
design (default neutro para alcance global). Cada visita começa em
inglês; o usuário escolhe outro idioma via dropdown se quiser. A
escolha **não** é persistida — a cada reload volta a EN-US.

O **título da aba** do navegador (`document.title`) acompanha o
idioma — ex.: muda entre "Before / After", "Antes / Depois",
"Antes / Después", "Avant / Après", "Vorher / Nachher",
"Prima / Dopo", "ビフォー / アフター", "前 / 后". O **favicon** é um
SVG inline com as duas bolinhas (azul `--before` + laranja `--after`)
que formam a logo da marca.

## Exportação

Botão na topbar (ícone de download) abre menu com duas opções:

- **Galeria offline (todas)** — gera um HTML único contendo todos
  os pares carregados, com o mesmo comparador embutido. Útil pra
  arquivar ou abrir em outra máquina sem refazer o upload.
- **Comparador desta foto** — gera um HTML pequeno só com o par
  atualmente exibido, ideal pra mandar pra alguém via mensagem ou
  email.

Em ambos os casos, as imagens são re-encodadas em JPEG comprimido
(máx 2000 px, qualidade 82) embutidas como data URLs. O HTML
resultante é totalmente standalone — abre direto pelo `file://`
e funciona com todos os recursos do app live (slider, lado a lado,
solo, zoom, EXIF, atalhos).

## Build CLI (opcional)

Alternativa em linha de comando ao "Galeria offline (todas)" do
botão de exportação. Útil pra processar um lote sem abrir a UI.

```
python _build.py                        # usa o diretório do script
python _build.py --src C:\photos        # pasta explícita
python _build.py --out gallery.html     # arquivo de saída
python _build.py --lang pt-BR           # idioma do HTML gerado
python _build.py --max-full 2400        # imagens embutidas maiores
```

Idiomas suportados (mesmos 8 do app live): `en-US` (default), `pt-BR`,
`es-ES`, `fr-FR`, `de-DE`, `it-IT`, `ja-JP`, `zh-CN`. O HTML gerado
preserva o idioma escolhido via `window.EMBEDDED_LANG`, e ainda permite
trocar de idioma via o dropdown da topbar quando aberto.

Requer Python 3.10+ e Pillow (`pip install pillow`). O script:

1. Lê todas as imagens da pasta (`.jpg|.jpeg|.png|.webp`).
2. Pareia pelo mesmo critério do `parseId` em JS (runs de 4+ dígitos
   concatenados com `-`).
3. Reduz cada foto pra max 2200 px / JPEG q=85 e codifica em base64.
4. Extrai EXIF (data, autor, câmera, lente, ISO, abertura, obturador,
   focal) + coordenadas GPS se presentes (resolvidas em runtime via
   Nominatim quando o HTML é aberto).
5. Lê o `index.html` do diretório e injeta `window.EMBEDDED_DATA = [...]`
   antes do `<script>` principal — o runtime detecta e pula a tela
   de upload.

Vantagem: qualquer feature nova adicionada ao `index.html` é
automaticamente herdada pelo `comparador.html` gerado, sem precisar
atualizar o `_build.py`.

## Performance e fluidez

Algumas otimizações invisíveis ao usuário, mas importantes:

- **Decode-then-swap atômico**: ao navegar entre fotos, a nova imagem é
  pré-decodificada off-DOM via `HTMLImageElement.decode()` antes de
  trocar o `src` no viewer. As dimensões (`style.width/height`) e o
  `src` são atualizados no MESMO frame, eliminando o flash de "imagem
  esticada" quando a orientação muda (vertical ↔ horizontal).
- **Preload de pares adjacentes**: após carregar o par N, dispara
  `decode()` em background dos pares N-1 e N+1. Quando o usuário
  clica em "próxima/anterior", a troca é instantânea.
- **`decoding="async"` + `fetchpriority="high"`** nas `<img>` do viewer:
  hints pro browser não bloquear o main thread no decode.
- **`will-change: transform` + `backface-visibility: hidden`** nas
  camadas de imagem: promove pra compositor layer no GPU; pan/zoom
  ficam fluidos sem repaint na CPU.
- **`contain: layout paint`** em `.stage`, `.sidebar` e `.thumbstrip-wrap`:
  isola regiões de paint — resize de um painel não força reflow nos
  outros.
- **Debounce via `requestAnimationFrame`** no listener de `resize` da
  janela: arrastar o canto da janela dispara `applySidebar` no máximo
  uma vez por frame, em vez de a cada pixel.
- **Token de cancelamento** no `load()`: navegações rápidas (vários
  cliques em sequência) cancelam decodes obsoletos — só o último vai
  realmente swap.

## Persistência

**ZERO.** Por design, o app não grava nada em `localStorage`,
cookies ou `IndexedDB`. Toda visita começa "do zero" com:

- idioma seguindo `navigator.language`
- ordenação `name` / `asc`
- painéis expandidos (sidebar + strip abertos)
- resize dos painéis no default do CSS

Durante a sessão o usuário pode mudar tudo (trocar idioma, arrastar
o resizer, ciclar critério de sort, recolher os painéis), mas nada
sobrevive ao reload. Decisão de produto: o app é uma ferramenta de
uso pontual, não tem login, e visitantes diferentes na mesma máquina
não devem ver o estado uns dos outros.

O botão **"Recolher painéis"** (canto inferior direito do stage)
também esconde o controle de zoom flutuante (`overlay-bottom`)
junto com topbar/sidebar/strip — view 100% limpa para revisão
focada. Clicar de novo traz tudo de volta.

## Hospedagem

Como é um arquivo estático único, qualquer hospedagem serve. Para
GitHub Pages: `Settings → Pages → Source: main / root`.

Também roda direto pelo `file://` (abre o `index.html` no browser).

## Limitações

- HEIC/AVIF dependem do suporte do navegador.
- EXIF só em JPEG.
- Ambas as imagens do par são forçadas ao mesmo retângulo —
  presume aspect ratio igual entre `before` e `after`.

## Arquitetura

`index.html` contém:

- **CSS** — tema dark, layout responsivo (sidebar desktop, bottom
  sheet mobile).
- **HTML** — três telas: upload, loading, app.
- **JS** — duas partes: pareamento + leitura de arquivos + parser
  EXIF; e `startApp(DATA)` com toda a interatividade (pointer
  events, transforms CSS para zoom ancorado, navegação, modos,
  atalhos). i18n inline (4 idiomas) com `t(key)` e `data-i18n*`.

`_build.py` (opcional) é um helper CLI em Python que processa
uma pasta de fotos e gera `comparador.html` standalone reusando
o `index.html` como template e injetando `window.EMBEDDED_DATA`.

Sem build obrigatório. Sem dependências em runtime. Sem servidor.

## Licença

Copyright © 2026 Vinicius Souza. Todos os direitos reservados.
Veja [LICENSE](LICENSE).
