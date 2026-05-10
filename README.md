# image-pair-viewer

Visualizador interativo de pares de imagens. HTML único, sem build,
sem servidor, sem dependências.

Você arrasta um lote de imagens, o app pareia pelo nome e abre
um comparador com slider, lado a lado e modo solo. Tudo é processado
no navegador via File API + Canvas + DataView; nenhum byte sai do
dispositivo.

## Pareamento

Procura **4 dígitos consecutivos depois de um `_`** no nome do
arquivo. Esse número é o ID do par. Dentro do par, o nome **mais
curto** vira `before`, o mais longo vira `after` (assume que edits
acrescentam prefixo ou sufixo).

| Arquivo                 | ID    | Papel  |
|-------------------------|-------|--------|
| `IMG_0093.jpg`          | 0093  | before |
| `IMG_0093_edited.jpg`   | 0093  | after  |
| `edited_IMG_0093.jpg`   | 0093  | after  |
| `GAB_0074.jpg`          | 0074  | before |
| `GAB_0074_v2.jpg`       | 0074  | after  |

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
