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
EXIF (data, câmera, lente, ISO, abertura, obturador, focal) via
parser próprio.

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
