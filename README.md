# Piano Tiles 

Piano Tiles é uma implementação de um jogo musical de piano em Python e Pygame.

```bash
uv sync
```

## Usage

Dê um duplo clique no arquivo game.py para abrir o jogo. Clique em "Iniciar" para começar a jogar. O objetivo do jogo é clicar nas peças sem clicar em nenhum outro lugar na tela para gerar notas musicais. Além disso, se uma peça tocar o chão sem ser clicada, o jogo termina.

Controle:
* Use o movimento do mouse para mover e o botão esquerdo do mouse para clicar nos blocos.

## Carregamento de Músicas MIDI

O jogo suporta carregamento automático de arquivos MIDI! Basta adicionar um arquivo `.mid` na pasta `config/Sounds/` e o jogo irá:

1. **Detectar automaticamente** o arquivo MIDI mais recente na pasta
2. **Extrair as notas** da melodia principal
3. **Gerar os blocos** do jogo baseados nessas notas
4. **Tocar os sons** correspondentes quando você clicar nos blocos

### Como usar:

1. Coloque seu arquivo MIDI (`.mid`) na pasta `config/Sounds/`
2. Execute o jogo normalmente - ele irá carregar automaticamente o arquivo MIDI
3. Se nenhum arquivo MIDI for encontrado, o jogo usará as músicas padrão do `notes.json`

**Nota:** O jogo utiliza os arquivos de som `.ogg` existentes na pasta `config/Sounds/` para tocar as notas. Certifique-se de que seu MIDI use notas dentro da faixa disponível (C1 a C8, incluindo bemóis).


## Download

Faça o download do projeto original aqui: [Download Piano Tiles](https://downgit.github.io/#/home?url=https://github.com/pyGuru123/Python-Games/tree/master/Piano%20Tiles)