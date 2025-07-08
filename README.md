*Projeto desenvolvido no âmbito da unidade curricular de Inteligência Artificial (2024/2025), no segundo semestre.*

**Connect Four – Adversarial Search e Árvores de Decisão**

*Descrição*
O objetivo principal foi desenvolver um sistema capaz de jogar Connect Four contra um jogador humano ou outro algoritmo, usando:
MCTS com UCT como estratégia de jogo;
ID3 para treinar uma árvore de decisão com base em estados do jogo gerados por MCTS;

*Capacidade de jogar em três modos:*
- Humano vs Humano
- Humano vs Computador
- Computador vs Computador (MCTS vs Árvores de Decisão)

*Funcionalidades*
- Implementação completa de Connect Four em modo texto
- MCTS com UCT e parametrização do número de simulações
- Geração de dataset de treino a partir de partidas MCTS
- Algoritmo ID3 para aprender e jogar com base em dados
- Discretização para datasets numéricos (Iris)

*Testes em dois datasets:*
- iris (para validação do ID3)
- estados do jogo Connect Four (gerado via MCTS)

*Como jogar*
Certifica-te de que estás no diretório do projeto e executa: python3 play.py

*Requisitos*
