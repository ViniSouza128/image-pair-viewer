# image-pair-viewer

**Visualizador interativo de pares de imagens (antes/depois) no navegador.**
Um único arquivo `index.html`. Sem build obrigatório, sem servidor, sem
dependências em runtime, sem login, sem analytics, sem rastreamento.
Suporta 8 idiomas, 21 atalhos de teclado, gestos touch completos, sidebar
de EXIF + GPS, exportação como HTML standalone e CLI opcional em Python.

Você arrasta um lote de imagens, o app **pareia automaticamente pelos
nomes dos arquivos**, e abre um comparador com slider arrastável, lado a
lado, modo solo, zoom ancorado ao cursor, pan, navegação por flick em
mobile, seleção múltipla estilo Windows Explorer, e mais.

Tudo é processado no navegador via File API + Canvas + DataView;
**nenhum byte de imagem sai do dispositivo**. A única requisição externa
é opcional (Nominatim/OpenStreetMap) e só envia coordenadas GPS — nunca
fotos.

URL pública (GitHub Pages): https://vinisouza128.github.io/image-pair-viewer/

---

## Pareamento

O algoritmo de pareamento foi pensado pra cobrir convenções de diversas
marcas e épocas de câmera sem necessidade de configuração manual.

### Como funciona

Extrai **TODOS os runs de 4 ou mais dígitos consecutivos** do nome do
arquivo (sem extensão) e os concatena com `-` como ID composto.

| Convenção                        | Exemplo                          | ID extraído         |
|----------------------------------|----------------------------------|---------------------|
| Canon / iPhone                   | `IMG_0093.jpg`                   | `0093`              |
| Sony Alpha                       | `DSC04321.JPG`                   | `04321`             |
| Nikon                            | `DSC_05123.JPG`                  | `05123`             |
| Fujifilm                         | `DSCF_4567.JPG`                  | `4567`              |
| Panasonic Lumix                  | `P1010234.jpg`                   | `1010234`           |
| Android (data+hora)              | `IMG_20240115_143025.jpg`        | `20240115-143025`   |
| Google Pixel                     | `PXL_20240115_143025.jpg`        | `20240115-143025`   |
| DJI                              | `DJI_0123.JPG`                   | `0123`              |
| GoPro                            | `GOPR0001.JPG`                   | `0001`              |
| Sufixo (versão editada)          | `IMG_0093_edited.jpg`            | `0093`              |
| Marcador curto ignorado          | `IMG_0093_v10.jpg`               | `0093`              |

### Por que ≥ 4 dígitos?

- Cobre toda câmera digital relevante (anos 90 em diante).
- Descarta marcadores curtos tipo `_v2`, `_v10`, `_2025` que confundem
  o pareamento. `IMG_0093.jpg` pareia corretamente com
  `IMG_0093_v10.jpg`: o `10` (2 dígitos) é ignorado, o `0093` (4
  dígitos) prevalece.

### Quem é `before`, quem é `after`?

Dentro de cada grupo com mesmo ID, o nome **MAIS CURTO** vira `before`
(o original), o **mais longo** vira `after` (a versão editada).
Pressupõe que editores adicionam prefixo ou sufixo ao nome (ex.:
`IMG_0093.jpg` + `IMG_0093_edited.jpg`, ou `edited_IMG_0093.jpg`).
Pares com apenas 1 arquivo são silenciosamente ignorados.

### Por que isso funciona?

A heurística cobre **convenções implícitas universais** do mundo da
fotografia: as câmeras numeram sequencialmente, e os editores
preservam o nome original como base ao salvar a versão pós-edição.

---

## Modos de comparação

Três modos selecionáveis na **topbar** (`Slider · Lado a Lado · Solo`)
ou ciclados pela tecla `S`.

### Slider (default)

Imagem `before` por baixo, `after` por cima recortada via
`clip-path:inset(0 0 0 X%)`. A "alça" central pode ser arrastada com
mouse, dedo ou teclas `[` `]` (passos de 5%). Quando o slider está em
0% você só vê o `before`; em 100% só o `after`. **Duplo clique no knob**
retorna ao centro (50%).

Por que `clip-path` e não duas `<img>` em columns? Porque clip-path é
animado pela GPU (zero reflow) e respeita perfeitamente o transform
das duas camadas durante zoom/pan — slider continua alinhado pixel a
pixel mesmo com zoom 8×.

### Lado a Lado

Duas colunas paralelas com as imagens em `object-fit:contain`. Útil
quando você quer ver as duas inteiras sem sobreposição. Em mobile
(orientação retrato) as colunas viram linhas (empilhadas
verticalmente).

### Solo

Uma imagem por vez ocupando toda a área disponível. Toggle
**`Espaço`** (segurar) ou **clique e segure o mouse** alterna
temporariamente entre `before` e `after` enquanto o botão está
pressionado — bom pra checar mudanças com o "olho piscando", técnica
clássica de revisão.

O lado "estável" é o `after` por padrão. Soltar a tecla/botão volta
pra esse lado.

---

## Atalhos de teclado

Implementação completa, 21 atalhos. Ignorados quando o foco está num
`<input>` ou `<textarea>` (você pode digitar normalmente em modais sem
disparar atalhos).

| Tecla              | Ação                                          |
|--------------------|-----------------------------------------------|
| `←` `→`            | Foto anterior / próxima (com wrap-around)     |
| `Espaço` (Solo)    | Segurar = alterna `before`/`after`            |
| `[` `]`            | Slider ±5%                                    |
| `+` `−` (ou `=`)   | Zoom in / out (passo 1.3×)                    |
| `0`                | Reset zoom                                    |
| `Esc`              | Cascata: fecha menu/modal · limpa seleção · expande painéis · reseta zoom |
| `F`                | Tela cheia (Fullscreen API via JS)            |
| `I`                | Painel de informações (toggle sidebar)        |
| `S`                | Cicla entre Slider → Lado a Lado → Solo       |
| `Ctrl`+`A` / `⌘`+`A` | Seleciona todos os pares                    |
| `Delete` / `Backspace` | Remove pares selecionados (com confirmação) |
| `?`                | Modal de ajuda (toggle)                       |

### Cascata do `Esc`

O `Esc` é o **atalho universal de "sair do estado atual"**. Em vez de
fazer só uma coisa, percorre uma fila de prioridade e executa a
primeira que se aplica:

1. **Fecha um menu dropdown aberto** (export menu, lang menu)
2. **Fecha o modal de ajuda** se estiver aberto
3. **Limpa a seleção** se houver pares selecionados
4. **Sai do modo "painéis recolhidos"** (equivalente a clicar de novo
   no botão de collapse no canto inferior direito)
5. **Reseta o zoom** se nenhuma das ações acima se aplicou

Garante que `Esc` "sempre faz a coisa certa" — o usuário não precisa
lembrar atalhos específicos pra cada estado.

### F11 vs F

`F11` (tecla nativa do browser, fullscreen do navegador) e `F` (Fullscreen
API via JS) são caminhos paralelos que não interferem entre si. F11 cobre
toda a tela do SO; F coloca o `<html>` em fullscreen mas mantém
toolbars do navegador escondidas via API.

---

## Mouse e Touch

### Mouse

| Gesto                       | Ação                                       |
|-----------------------------|--------------------------------------------|
| Roda                        | Zoom **ancorado ao cursor** (passo `exp(-Δy×0.0015)`) |
| Arrastar                    | Mover slider · Pan quando há zoom > 1×     |
| Pressionar (modo Solo)      | Segurar = alterna `before`/`after`         |
| Duplo clique no knob        | Slider volta ao centro (50%)               |
| Duplo clique no viewer      | Reset zoom                                 |

**Zoom ancorado ao cursor** = quando você dá scroll na roda, o ponto da
imagem que está sob o cursor permanece sob o cursor depois do zoom. É
o comportamento natural do Photoshop/Lightroom, mais intuitivo que
zoom centralizado.

Matemática: converte coordenada do cursor (screen) pra coordenada
local da imagem (descontando `baseScale * scale` e `panX/panY`),
muda a escala, e recalcula `panX/panY` pra que aquele ponto local
volte a cair sob o cursor.

### Touch

| Gesto                       | Ação                                       |
|-----------------------------|--------------------------------------------|
| Pinça                       | Zoom (ancorado ao centro do gesto)         |
| Arrasto horizontal lento    | Move o slider                              |
| **Flick** horizontal rápido | Vai pra próxima/anterior foto              |
| Toque duplo                 | Reset zoom                                 |
| Toque simples (no viewer)   | Mostra/oculta a interface inteira          |
| Long-press no thumb         | Alterna seleção (≈500ms)                   |

**Detecção de flick**: ao soltar o dedo após um arrasto, o app mede
4 critérios — duração < 320ms, distância > 70px, dominância
horizontal (|dx| > 1.4 × |dy|), velocidade > 0.5 px/ms. Atende todos
os critérios → navega; senão, fica onde está.

**Pinch**: usa Pointer Events (não TouchEvent), captura dois ponteiros
simultâneos, calcula distância inicial e ponto médio, escala
proporcionalmente. O ponto médio é a âncora do zoom — equivalente ao
cursor no mouse wheel.

---

## Painel de informações (sidebar direita)

Acessível por **clique no botão `Info` (I)** da topbar ou tecla `I`.
Mostra metadados detalhados de cada par.

### Campos exibidos

Para **cada lado do par** (`before` e `after`):

- **Arquivo**: nome original (ex.: `IMG_0093_edited.jpg`)
- **Dimensões**: largura × altura em px (ex.: `4108 × 6168`)
- **Tamanho**: em KB/MB (calculado do `File.size` original, não da
  versão re-encodada)

Para **JPEGs** (parser EXIF próprio em JS, sem libraries):

- **Data**: `DateTimeOriginal` ou `DateTime` (formato `YYYY-MM-DD HH:MM:SS`)
- **Autor**: tag `Artist` ou `XPAuthor` (este último é UTF-16 LE em bytes,
  decodificado manualmente)
- **Câmera**: `Make` + `Model` (deduplicados — evita "Canon Canon EOS R5")
- **Lente**: `LensModel` ou `LensMake`
- **ISO**: `ISOSpeedRatings` ou `PhotographicSensitivity`
- **Abertura**: `FNumber` formatado como `f/2.8`
- **Obturador**: `ExposureTime` formatado como `1/400s` ou `1.5s`
- **Focal**: `FocalLength` arredondado em mm
- **Localização**: Cidade, Estado, País (resolvido via Nominatim — veja
  abaixo)
- **Coordenadas**: lat/lon em formato decimal, copiáveis

### Reverse geocoding (GPS → Localização)

Se o EXIF tem coordenadas GPS válidas, o app consulta a API pública
**Nominatim do OpenStreetMap** pra resolver:

```
GET https://nominatim.openstreetmap.org/reverse?lat=...&lon=...&format=json&zoom=10
```

- **Único endpoint externo do app inteiro**. Nenhuma foto sai do
  dispositivo — só lat/lon.
- **Throttle de 1.1 segundo** entre requests (Nominatim exige
  responsabilidade no uso da API pública).
- **Cache em memória** durante a sessão — coordenadas repetidas não
  consultam de novo.
- **Atribuição via OpenStreetMap** (texto pequeno no rodapé do campo,
  como exige a licença do OSM).
- **Falha silenciosa** se offline ou se Nominatim estiver fora do ar —
  mostra "consultando..." e depois nada.

Parser EXIF: lê só os primeiros 128KB do JPEG (EXIF mora sempre no
início). Decodifica o TIFF header (II/MM endianness), navega IFD0 +
EXIF sub-IFD (tag 0x8769) + GPS sub-IFD (tag 0x8825). Suporta tipos
ASCII, SHORT, LONG, RATIONAL, SRATIONAL.

---

## Strip lateral (Abrir, Ordenar, Remover)

No **desktop**, a faixa de miniaturas fica como **painel lateral
esquerdo** (coluna vertical à esquerda do stage); no **mobile**
(<901px) reverte automaticamente pra faixa horizontal embaixo,
preservando a ergonomia em tela vertical.

### 3 botões no topo do painel

- **Abrir fotos** — Adiciona mais fotos à sessão sem perder as atuais.
  Alternativa ao drag-and-drop full-page. Dispara um `<input type=file>`
  hidden via `.click()`.

- **Ordenar** (split-button) — Esquerda cicla o critério; direita
  inverte a direção:
  - **Nome** — ordem alfanumérica do filename
  - **Inserção** — ordem em que foram adicionados na sessão
  - **Captura** — `exif.date`; sem EXIF, vai pro fim
  - **Modificação** — `lastModified` do File
  
  Seta laranja indica direção atual (rotaciona 180° em `desc`). Default:
  `Nome` ascendente (A → Z).

- **Remover** — Sempre visível, em vermelho. Quando nada está
  selecionado, remove o par **atualmente aberto** no viewer. Quando há
  seleção, remove os selecionados (com contagem no label se ≥ 2:
  `Remover (5)`). Abre modal de confirmação antes.

### Tipografia e alturas

Os 3 elementos têm exatamente a **mesma altura** (`--tool-h: 28px`).
Tipografia **fixa em 12px** (não escala com o tamanho dos thumbs) —
casa com `.mode-btn` da topbar. O painel respeita um **piso de 136 px**
de largura, suficiente pras labels mais longas.

### Miniaturas

- Cada thumb é **quadrado**, com a foto encaixada via
  `object-fit:contain` e fundo preto. Sem corte de conteúdo importante
  (cabeças, rostos) — preserva fotos verticais/horizontais com
  letterbox em vez de crop.
- Borda **laranja** indica o par atualmente exibido.
- **Bolinha de seleção** no canto superior direito (sutil em desktop,
  aparece em hover; sempre visível em touch).
- **Shimmer animado** enquanto a foto ainda está sendo processada em
  background (estado `.pending`).
- **Indicador vermelho `!`** se o processamento falhou (estado
  `.failed`).
- ID do par no canto superior esquerdo (`0093`, `04321`, etc.).

### Redimensionar

Borda direita do painel (desktop) ou superior (mobile) é uma
**handle de resize** (cursor `col-resize` ou `row-resize`). Arraste pra
ajustar tamanho. **Duplo clique** na borda volta ao tamanho padrão.
O tamanho **não é persistido** entre sessões (vide seção
"Persistência").

---

## Adicionar mais fotos à sessão

Três formas de incrementar a sessão sem perder o estado atual:

1. **Botão "Abrir fotos"** na coluna de ferramentas da strip
2. **Drag-and-drop** de novos arquivos sobre a janela (a qualquer
   momento — overlay laranja "Solte aqui" aparece)
3. **Atalho de teclado**: nenhum (intencional — adicionar fotos é
   ação deliberada)

### Deduplicação automática

O sistema deduplica por **`name + size + lastModified`** (chave
composta). Se você arrastar uma foto que já está na sessão, ela é
silenciosamente ignorada. Notificação no canto: `"3 novo(s) par(es) ·
2 já estava(m) na sessão"`.

### Estados de notificação

- `"5 novo(s) par(es)"` — sucesso
- `"3 já estava(m) na sessão"` — quando alguns são duplicatas
- `"Nenhum par novo (todos já estavam carregados ou inválidos)"` —
  quando todos são duplicatas
- `"Adicionando..."` — durante processamento em background

---

## Carregamento progressivo

Quando o usuário escolhe muitas fotos, o app **não bloqueia a UI** para
processar tudo de uma vez. Estratégia:

1. **Pareia imediatamente** — apenas inspeciona nomes (rápido).
2. **Mostra o app já** com placeholders animados (`shimmer` ladrilhado)
   nas miniaturas e um spinner no viewer.
3. **Processa em background**, par a par, sequencialmente — gera
   thumbnail (240px) e lê EXIF.
4. **Cada par "resolve" sua miniatura** assim que termina — sem
   re-render completo da strip.
5. Se o usuário **clica num par ainda pendente**, o viewer mostra um
   spinner até a imagem ficar disponível.

Por que sequencial e não paralelo? **Memória**. Processar 50+ imagens
4K em paralelo estoura a heap do navegador. Sequencial mantém o pico
de RAM controlado.

---

## Recolher painéis e redimensionar

### Botão único de collapse-all

Um botão no **canto inferior direito** da área de visualização (com
ícone de "encolher" — 4 setas pra dentro) recolhe **TODOS os painéis
simultaneamente**:

- topbar
- strip lateral esquerda
- sidebar direita
- overlay-bottom (controle de zoom flutuante)

O viewer ocupa **100% da tela** — ideal pra revisão focada. O ícone
inverte pra "expandir" (4 setas pra fora) quando colapsado. Clicar de
novo, ou apertar `Esc`, traz tudo de volta.

O estado **não é persistido** — toda sessão começa expandida.

### Resize de painéis

- **Sidebar direita**: arraste a borda esquerda → ajusta largura
- **Strip esquerda**: arraste a borda direita → ajusta largura
- **Duplo clique** em qualquer borda → volta ao tamanho default do CSS
- Limites: sidebar (240px–60vw), strip (140px–380px no desktop)

As dimensões **não são persistidas** entre sessões. Veja "Persistência".

---

## Seleção múltipla e remoção

Estilo Windows Explorer / macOS Finder. Cada miniatura tem uma
**bolinha de seleção** no canto superior direito.

### Interações

- **Clique na bolinha** → alterna a seleção daquele par (não navega)
- **Clique no corpo do thumb** → navega (não altera seleção)
- **`Ctrl`/`⌘` + clique** anywhere no thumb → alterna seleção
- **`Shift` + clique** → seleciona range entre âncora e clicado
- **`Ctrl`+`A`** → seleciona todos os pares
- **`Delete`** ou **`Backspace`** → remove selecionados (com modal de
  confirmação contando quantos)
- **Clique no espaço vazio da strip** → limpa seleção
- **`Esc`** → limpa seleção (na cascata; só se nada acima se aplicar)
- **Long-press** ~500ms no thumb (mobile) → alterna seleção

### Botão Remover

Está sempre visível na strip-tools. Comportamento dinâmico:

- **0 selecionados** → desabilitado visualmente (opacity .42). Quando
  clicado nesse estado pelo teclado/JS, remove o par **atualmente
  aberto** (com confirmação).
- **1 selecionado** → label `"Remover"`, ativa
- **2+ selecionados** → label `"Remover (5)"`, ativa

A remoção **não afeta os arquivos originais no seu dispositivo** —
só descarta da sessão em memória. Você pode reenviá-los depois.

---

## Idioma

Botão na topbar (mostra a label do idioma ativo: `EN` / `PT` / `ES` /
`FR` / `DE` / `IT` / `JA` / `ZH`) abre um menu com **8 idiomas**:

- 🇺🇸 **English (EN-US)** — *default*
- 🇧🇷 **Português (PT-BR)**
- 🇪🇸 **Español (ES-ES)**
- 🇫🇷 **Français (FR-FR)**
- 🇩🇪 **Deutsch (DE-DE)**
- 🇮🇹 **Italiano (IT-IT)**
- 🇯🇵 **日本語 (JA-JP)**
- 🇨🇳 **中文 (ZH-CN)**

### Por que esses 8 idiomas?

Cobertura por mercados prováveis para um app de comparação de fotos:

- **EN** — alcance global (default neutro)
- **PT** — base original do projeto (Brasil)
- **ES** — América Latina + Espanha
- **FR** — Europa + África francófona
- **DE** — Alemanha (comunidade fotográfica forte)
- **IT** — complementa cobertura europeia
- **JA** — Japão é a pátria das principais marcas de câmera (Canon,
  Nikon, Sony, Fujifilm)
- **ZH** — maior base online do mundo, mercado fotográfico massivo
  (Xiaomi, Huawei)

### Default fixo em EN-US

O default é **fixo em `en-US`** — `navigator.language` é **ignorado**
por design. Razão: comportamento previsível, independente do locale
do browser. Default neutro e global; cada usuário escolhe seu idioma
explicitamente via dropdown.

### O que muda quando você troca o idioma?

- Todas as labels da UI (botões, dicas, mensagens, modal de ajuda)
- O **`<h1>`** da topbar (`Antes / Depois`, `Before / After`, `Vorher
  / Nachher`, `前 / 后`, etc.)
- O **`document.title`** (título da aba do navegador) acompanha o `<h1>`
- Os badges flutuantes no viewer (`Antes`/`Depois` etc.)
- Os labels do painel de informações
- As mensagens de confirmação dos modais

### O que NÃO muda

- O **favicon** (SVG inline com duas bolinhas, azul + laranja)
- O **idioma do README e dos comentários do código** (PT-BR)
- As **chaves dos atalhos** (`F`, `I`, `S` etc. são teclas físicas,
  internacionais por convenção)

### Persistência

A escolha **não é persistida** — a cada reload o idioma volta a
EN-US. Veja "Persistência".

---

## Exportação

Botão na topbar (ícone de download) abre menu com duas opções:

### Galeria offline (todas)

Gera um **HTML único** contendo todos os pares carregados, com o app
inteiro embutido. Útil pra arquivar uma sessão ou compartilhar uma
revisão completa sem dependência de servidor.

- Todas as imagens são **re-encodadas via Canvas** (max 2000px, JPEG
  q=82) e embutidas como **data URLs base64**.
- Resulta em arquivos de 10-50 MB tipicamente; abre direto pelo
  `file://` em qualquer máquina sem rede.
- Mantém **todas as features** do app live (modos, zoom, EXIF,
  atalhos, seleção, troca de idioma — só não permite adicionar/remover
  fotos no exportado).

### Comparador desta foto

Mesmo conceito, mas com apenas **o par atualmente aberto**. HTML
pequeno (poucos MB), ideal pra mandar por email/WhatsApp.

### Como funciona internamente

1. **Clona o `documentElement.innerHTML`** atual (preserva todo o
   layout, idioma traduzido, estado dos painéis).
2. **Re-encoda as imagens** das blob URLs originais para data URLs
   comprimidos (Canvas.toDataURL).
3. **Limpa estado runtime**: remove `src`/`style` das `<img>` (serão
   re-aplicadas pelo startApp), reseta classes, esvazia a strip,
   esconde `uploadScreen`/`loadingScreen`/`btnExport`/`btnReload`.
4. **Injeta um `<script>`** antes do main script com:
   - `window.EMBEDDED_DATA = [...]` — array de pares já processados
   - `window.EMBEDDED_LANG = '...'` — preserva o idioma do export
5. **Serializa** o documento clonado e dispara download via Blob URL +
   `<a download>`.

### Por que `EMBEDDED_LANG`?

Sem isso, o HTML exportado abriria **sempre em en-US** (default fixo
do app), ignorando o idioma que o usuário escolheu na hora do export.
Com `EMBEDDED_LANG`, o init do `currentLang` honra esse valor e o
`applyI18n()` traduz o DOM clonado para o idioma certo.

### Falhas catastróficas

- Se algum par ainda está em `_pending` (processamento background),
  o export é **rejeitado com hint** "Aguarde as fotos terminarem de
  carregar antes de exportar." — não podemos re-encodar uma imagem
  cujo `src` ainda é `null`.
- Se o Canvas falhar (CORS, memória), um `alert()` informa o erro.
  (Alert nativo, intencional — falha catastrófica não deve abrir
  modal que o usuário confunde com confirmação normal.)

---

## Build CLI (opcional)

Alternativa em linha de comando ao "Galeria offline (todas)" do
botão de exportação. Útil pra processar um lote sem abrir a UI —
ou pra automatizar geração de galerias.

```
python _build.py                        # usa o diretório do script
python _build.py --src C:\photos        # pasta explícita
python _build.py --out gallery.html     # arquivo de saída
python _build.py --lang pt-BR           # idioma do HTML gerado
python _build.py --max-full 2400        # imagens embutidas maiores
python _build.py --quality 90           # JPEG quality (default 85)
python _build.py --max-thumb 300        # thumbs maiores
python _build.py --thumb-quality 80     # qualidade das thumbs
```

Idiomas suportados (mesmos 8 do app live): `en-US` (default), `pt-BR`,
`es-ES`, `fr-FR`, `de-DE`, `it-IT`, `ja-JP`, `zh-CN`. O HTML gerado
preserva o idioma escolhido via `window.EMBEDDED_LANG`.

Requer **Python 3.10+** e **Pillow** (`pip install pillow`).

### O que o script faz

1. Lê todas as imagens da pasta com extensões `.jpg|.jpeg|.png|.webp`
   (skipping arquivos que começam com `_`, reservados pra helpers de
   build).
2. **Pareia pelo mesmo critério do `parseId` em JS** — runs de 4+
   dígitos concatenados com `-`. Resultado idêntico ao do app live
   pra qualquer convenção de nome.
3. Aplica `ImageOps.exif_transpose` em cada imagem (auto-rotaciona
   conforme tag EXIF Orientation, importante pra iPhones).
4. **Reduz pra max 2200px** no maior lado / JPEG q=85 e **codifica em
   base64**.
5. **Extrai EXIF**: data, autor, câmera, lente, ISO, abertura,
   obturador, focal + coordenadas GPS se presentes (resolvidas em
   runtime via Nominatim quando o HTML é aberto).
6. **Lê o `index.html`** do diretório (template) e **injeta**
   `window.EMBEDDED_DATA` + `window.EMBEDDED_LANG` antes do `<script>`
   principal — o runtime detecta isso e pula a tela de upload.

### Vantagem arquitetural

O `_build.py` **não duplica HTML/CSS/JS** — ele usa o próprio
`index.html` como template e só injeta dados. Qualquer feature nova
adicionada ao `index.html` é **automaticamente herdada** pelo
`comparador.html` gerado, sem precisar atualizar o Python.

---

## Performance e fluidez

Otimizações cuidadosamente escolhidas, invisíveis ao usuário mas
importantes pra experiência fluida.

### Decode-then-swap atômico

Ao navegar entre fotos, a nova imagem é **pré-decodificada off-DOM**
via `HTMLImageElement.decode()` antes de trocar o `src` no viewer.
As dimensões (`style.width/height`) e o `src` são atualizados no
**MESMO frame** do swap.

**Por que isso importa**: o bug original era que `imgB.src = ...` era
setado ANTES de `imgB.style.width = ...`. Quando você navegava de uma
foto horizontal pra uma vertical, a nova imagem era renderizada por
alguns frames com as dimensões da anterior (esticada). Com
decode-then-swap, a imagem só aparece quando está pronta e nas
dimensões certas. **Sem flash visual.**

### Preload de pares adjacentes

Após carregar o par N, o app dispara `decode()` em background dos
pares N-1 e N+1. Quando o usuário clica em "próxima/anterior", a troca
é **instantânea** — a imagem já está decodificada e em cache.

### Token de cancelamento no `load()`

Navegações rápidas (vários cliques em sequência) cancelam decodes
obsoletos — só o último `load()` vai realmente fazer o swap. Evita
race conditions onde uma imagem antiga "ganha" a corrida e aparece
no lugar da que o usuário realmente queria.

### `decoding="async"` + `fetchpriority="high"`

Nas `<img>` do viewer. Hints pro browser não bloquear o main thread
no decode. As imagens da side-view também têm `decoding="async"` (mas
sem high priority — não são o caminho crítico).

### `will-change: transform` + `backface-visibility: hidden`

Aplicado às camadas de imagem do viewer. Promove os elementos pra
**compositor layer no GPU** — pan/zoom (que mudam `transform`) ficam
**sem repaint na CPU**, muito mais fluidos.

### `contain: layout paint`

Aplicado em `.stage`, `.sidebar` e `.thumbstrip-wrap`. **Isola
regiões de paint**: resize de um painel não força reflow nos outros.
O navegador trata cada painel como uma "ilha" isolada.

### Debounce via `requestAnimationFrame`

O listener de `resize` da janela (que reaplica o layout da sidebar
quando cruza o breakpoint 901px) usa rAF — **máximo 1 chamada por
frame**, mesmo que `resize` dispare a cada pixel arrastado no canto
da janela.

### Atomic DOM updates

Updates do counter, info panel e thumb active class acontecem
**imediatamente** ao clicar — feedback instantâneo. Apenas o swap da
imagem grande aguarda o decode. UX percebida: "cliquei, recebi
resposta na hora; a foto grande chega em ms".

---

## Persistência

**ZERO.** Por design, o app **não grava nada** em `localStorage`,
cookies ou `IndexedDB`. Toda visita começa "do zero" com:

- **Idioma**: en-US (default fixo)
- **Ordenação**: `name` ascendente (A → Z)
- **Painéis**: expandidos (sidebar + strip abertos, viewer não
  colapsado)
- **Resize dos painéis**: tamanho default do CSS
- **Modo**: Slider (compare)
- **Seleção**: vazia
- **Zoom**: 1× (fit-to-viewer)

Durante a sessão o usuário pode mudar tudo (trocar idioma, arrastar o
resizer, ciclar critério de sort, recolher os painéis, selecionar
pares, dar zoom), mas **nada sobrevive ao reload**.

### Por quê?

Decisão de produto:

- O app é uma **ferramenta de uso pontual**, não um workspace
  persistente.
- Não tem login nem identificação de usuário.
- **Visitantes diferentes na mesma máquina não devem ver o estado uns
  dos outros** — privacidade.
- Comportamento previsível: você sempre sabe em que estado vai cair
  ao abrir.

### O que persiste?

**Nada.** Nem `lang`, nem `sort`, nem `sidebarW`, nem `stripW/H`, nem
`allCollapsed`. Validado por auditoria: o código não contém nenhuma
chamada funcional a `.setItem()`, `.getItem()` ou `.removeItem()`.

---

## Privacidade

**Nenhum byte de imagem sai do dispositivo.** O HTML é estático e não
tem código de upload pra servidor:

- Imagens são lidas via **File API** (`FileReader`), criando blob URLs
  que apontam pra arquivo na RAM do navegador.
- EXIF é parseado **localmente** via `DataView` num parser próprio
  (sem libraries externas).
- Thumbs são gerados **localmente** via Canvas + `toDataURL`.
- Re-encode pra export também é local (Canvas).

### Única requisição externa

A **única** requisição de rede do app é o reverse geocoding via
**Nominatim/OpenStreetMap**, e só quando o EXIF tem GPS válido. O
que sai:

```
lat=−15.7942&lon=−47.8825
```

E só isso. Nunca o arquivo de imagem, nunca metadados sensíveis, nunca
identificadores de usuário.

### Sem tracking

Sem Google Analytics, sem Sentry, sem heatmaps, sem cookies. Sem
service worker (não tem nada pra cachear pra "uso offline" — o app já
é offline-first).

---

## Hospedagem

Como é um **arquivo estático único**, qualquer hospedagem serve. Para
**GitHub Pages**: `Settings → Pages → Source: main / root`. O app já
está rodando em
[`vinisouza128.github.io/image-pair-viewer/`](https://vinisouza128.github.io/image-pair-viewer/).

Também roda direto pelo **`file://`** (abra o `index.html` no
browser por duplo clique). Algumas limitações em `file://`:

- `localStorage` pode falhar (não importa — não usamos)
- `Fullscreen API` pode pedir confirmação extra
- `fetch()` pra Nominatim pode falhar (CORS) — sem GPS resolvido nessa
  situação

---

## Limitações

- **HEIC/AVIF** dependem do suporte do navegador. Safari decoda HEIC
  nativamente; Chrome/Firefox geralmente não.
- **EXIF apenas em JPEG**. PNG/WebP têm EXIF possível mas raro — o
  parser ignora.
- Ambas as imagens do par são **forçadas ao mesmo retângulo** (largura
  e altura do `before`) — presume aspect ratio igual entre `before` e
  `after`. Recortes desbalanceados ficam distorcidos.
- **Memória**: 100+ imagens 4K na mesma sessão podem estourar a heap
  do navegador em máquinas com pouca RAM.
- **Comparador.html exportado**: pode ficar grande (10-50 MB) com
  muitas fotos — não dá pra mandar facilmente por email.

---

## Arquitetura

`index.html` é o único arquivo executável (ignorando o `_build.py`
opcional). Contém:

### `<style>` (~1300 linhas)

- **Tokens de design** (CSS custom properties): cores, sombras,
  raios, transições
- **Sistema escalável de thumbs**: variável `--thumb-h` derivando 8
  outras (`--num-fs`, `--sel-size`, `--strip-pad-x` etc.) — resize do
  strip propaga proporcionalmente
- **Tokens de tools fixos** (não escalam com `--thumb-h`): `--tool-h`,
  `--tool-fs`, `--tool-icon`, `--tool-gap`, `--tool-pad` — labels dos
  botões nunca truncam por causa de scaling
- **Layouts**:
  - Desktop: topbar + main (strip esquerda | stage | sidebar direita)
  - Mobile (<901px): strip vira horizontal embaixo; sidebar vira
    bottom-sheet
- **Estados visuais**: `.is-pending`, `.is-loading`, `.all-collapsed`,
  `.ui-hidden`, `.dragging`, `.is-drag`, `.panning`, `.cut-dragging`

### `<body>` (~400 linhas)

Três telas:

1. **upload-screen** (`#uploadScreen`) — drag-and-drop, file input,
   privacidade, regra de pareamento
2. **loading-screen** (`#loadingScreen`) — barra de progresso pro
   processamento background e pra exportação
3. **app** (`#app`) — todo o comparador (topbar, strip lateral,
   stage, sidebar, modals)

Plus modais:

- `#helpModal` — atalhos & gestos
- `#confirmModal` — diálogo custom (substitui `window.confirm`)
- `#dragOverlay` — feedback durante drag-and-drop de arquivos

### `<script>` (~3500 linhas, monolito intencional)

Estrutura em camadas:

1. **i18n** — `I18N` (8 dicionários × 91 chaves), `t(key, params)`,
   `applyI18n()`, `setLang(lang)`, botão de idioma
2. **showConfirm** — modal custom retornando `Promise<bool>`
3. **Upload pipeline** — `parseId`, `pairFiles`, `processImage`,
   `parseExif`, drag-and-drop handlers, file input
4. **`startApp(DATA)`** — IIFE da app principal, ~2500 linhas. Toma
   conta de:
   - Refs do DOM, estado mutável (current, mode, scale, pan, cut,
     selection...)
   - `buildStrip`, `rebuildStrip`, `refreshThumb`, `activateThumb`
   - `load(i)` com decode-then-swap, `preloadAdjacent`
   - Viewer math (`computeBaseScale`, `applyTransform`, `setCut`,
     `setScaleAt` com anchor, `clampPan`)
   - Pointer events (pan, pinch, cut drag, flick)
   - Keyboard (com cascata do `Esc`)
   - Sidebar (collapsed/open, bottom-sheet drag)
   - Sort, selection, remove
   - Add more photos (drag overlay)
   - Export (`reencodeImage`, `buildExportHTML`, `exportItems`,
     `downloadHTML`)
   - Resize handles (`bindResize`, `applyStripScale`)
   - Reverse geocoding (Nominatim cache + throttle)
   - Collapse-all toggle
5. **Bootstrap** — decide entre modo upload (live) ou galeria
   exportada (`window.EMBEDDED_DATA` presente). Honra
   `window.EMBEDDED_LANG` no path de export.

### `_build.py` (~360 linhas, opcional)

Helper CLI em Python que:

- Usa o próprio `index.html` como template (sem duplicação)
- Implementa pareamento idêntico ao JS
- Re-encoda imagens com Pillow (`PIL.Image` + `ImageOps.exif_transpose`)
- Extrai EXIF + GPS coords com a stack da Pillow (`PIL.ExifTags`)
- Injeta `window.EMBEDDED_DATA` + `window.EMBEDDED_LANG` antes do
  script principal

---

## Licença

Copyright © 2026 Vinicius Souza. Todos os direitos reservados.
Veja [LICENSE](LICENSE).

---

## Roadmap (não-prometido)

Ideias que poderiam entrar:

- Modo "diff highlight" — sobrepor visualmente o que mudou entre
  `before` e `after` (gradient absdiff)
- Export como **vídeo** (sequência slider → solo → side de cada par)
- Suporte a **vídeos curtos** comparáveis (não só foto)
- Modo "apresentação" — auto-advance temporizado pra revisão guiada
- **PWA** instalável (mas mantendo política zero-persistência)
- Plugin de **Photoshop / Capture One** que abre direto no comparador
