# AGENTS.md

## Objetivo do laboratório

Este projeto é um laboratório inicial de Agentic Engineering em Python.

O agente deve ajudar na análise técnica do código, leitura de arquivos, execução de testes e geração de diagnóstico objetivo.

## Regras obrigatórias

1. Nunca inventar conteúdo de arquivos.
2. Sempre ler este AGENTS.md antes de analisar o projeto.
3. Antes de ler um arquivo específico, listar os arquivos disponíveis.
4. Modificar arquivos somente quando a tarefa solicitar explicitamente alteração.
5. Não executar comandos arbitrários do usuário.
6. As execuções permitidas nesta fase são testes e verificações controladas previamente definidas no código do agente.
7. Sempre responder de forma técnica, objetiva e verificável.
8. Antes de adicionar novos testes, verificar se já existem testes equivalentes.
9. Não duplicar testes com a mesma intenção sem necessidade.
10. Preferir testes parametrizados quando houver muitos cenários semelhantes.
11. Para comparações com float, preferir pytest.approx.
12. Arquivos `.bak` são apenas backups e não devem ser refatorados.
13. O agente deve tratar apenas arquivos-fonte ativos em `src/` e `tests/`.
14. Depois de qualquer alteração, informar exatamente quais arquivos foram modificados.
15. Sempre que possível, apresentar um resumo do diff lógico da alteração.
16. Quando uma ferramenta retornar diff, o agente deve reportar o resumo da alteração e, quando útil, incluir o trecho principal do diff.
17. Arquivos `.bak` e diretórios `backups/` são artefatos de segurança, não código-fonte ativo.
18. Não sugerir alterações em arquivos de backup, como `.bak`, salvo quando a tarefa for explicitamente recuperar uma versão anterior.

## Critérios de qualidade

- Código simples.
- Baixo acoplamento.
- Funções pequenas.
- Testes automatizados.
- Saída clara.
- Diagnóstico baseado em evidências.

## Formato de resposta esperado

Quando analisar o projeto, responder com:

1. Diagnóstico
2. Evidências encontradas
3. Resultado dos testes, quando executados
4. Riscos
5. Próximo passo recomendado

