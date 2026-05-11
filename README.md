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
| `0` ou `Esc`       | Reset zoom                                 |
| `F`                | Tela cheia                                 |
| `I`                | Painel de informações                      |
| `S`                | Cicla modos                                |
| `?`                | Ajuda                                      |

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

## Strip inferior — Abrir, Ordenar, Remover

A coluna de ferramentas à esquerda das miniaturas tem 3 botões
empilhados:

- **Abrir fotos** — adiciona mais fotos à sessão sem perder as atuais
  (alternativa ao drag-and-drop full-page)
- **Ordenar** (split-button) — clicando no nome cicla entre Nome →
  Inserção → Captura → Modificação. A seta laranja à direita inverte
  a ordem (crescente ↔ decrescente). Default: Nome crescente (A → Z).
- **Remover** — sempre visível, em vermelho. Desabilitado quando
  nada está selecionado. Com 2+ selecionados, vira `Remover (5)`.

A escolha de critério e direção são persistidas em `localStorage`.

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
O estado é persistido entre sessões.

**Resize**: arraste a borda interna da sidebar (esquerda) ou do
strip (topo) pra ajustar tamanho. **Duplo clique** na borda volta
ao tamanho padrão. O tamanho fica salvo em `localStorage`.

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

Botão `PT`/`EN` na topbar alterna PT-BR ↔ EN-US. Detecção inicial:
preferência salva (`localStorage`) → `navigator.language` → fallback
EN-US. A escolha persiste entre sessões.

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
  atalhos).

Sem build. Sem dependências. Sem servidor.

## Licença

Copyright © 2026 Vinicius Souza. Todos os direitos reservados.
Veja [LICENSE](LICENSE).
