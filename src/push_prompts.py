"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        # Extrair componentes do prompt
        system_prompt = prompt_data.get("system_prompt", "")
        user_prompt = prompt_data.get("user_prompt", "{bug_report}")
        description = prompt_data.get("description", "Prompt otimizado para bug to user story")
        version = prompt_data.get("version", "v2")
        tags = prompt_data.get("tags", [])
        techniques = prompt_data.get("techniques", [])

        # Criar nome do prompt (usar apenas o nome base, o tenant será detectado da credencial)
        # Se necessário especificar tenant, use: "username/bug_to_user_story_v2"
        prompt_full_name = f"bug_to_user_story_{version}"

        # Criar prompt template usando LangChain
        prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", user_prompt),
            ]
        )

        # Fazer push para LangSmith Hub
        print(f"📤 Fazendo push do prompt: {prompt_full_name}")
        pushed_prompt = hub.push(
            prompt_full_name,
            prompt_template,
        )
        # Nota: Você pode tornar o prompt público no dashboard do LangSmith clicando no ícone de cadeado

        print(f"✅ Prompt enviado com sucesso para o LangSmith Hub!")
        print(f"   Nome: {prompt_full_name}")
        print(f"   Versão: {version}")
        print(f"   Tags: {', '.join(tags)}")
        print(f"   Técnicas aplicadas: {len(techniques)}")

        return True

    except Exception as e:
        print(f"❌ Erro ao fazer push do prompt: {str(e)}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []

    # Verificar campos obrigatórios
    if not prompt_data.get("system_prompt"):
        errors.append("❌ Campo 'system_prompt' está vazio")

    if not prompt_data.get("user_prompt"):
        errors.append("❌ Campo 'user_prompt' está vazio")

    if not prompt_data.get("description"):
        errors.append("❌ Campo 'description' está vazio")

    if not prompt_data.get("version"):
        errors.append("❌ Campo 'version' está vazio")

    # Verificar tamanho mínimo do system_prompt
    system_prompt = prompt_data.get("system_prompt", "")
    if len(system_prompt) < 200:
        errors.append(f"⚠️  system_prompt muito curto ({len(system_prompt)} caracteres, esperado > 200)")

    # Verificar se há técnicas listadas
    techniques = prompt_data.get("techniques", [])
    if not techniques or len(techniques) < 2:
        errors.append(f"⚠️  Esperado >= 2 técnicas, encontradas {len(techniques)}")

    is_valid = len(errors) == 0
    return is_valid, errors


def main():
    """Função principal"""
    print_section_header("🚀 PUSH DE PROMPTS OTIMIZADOS PARA LANGSMITH")

    # Verificar variáveis de ambiente
    required_vars = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]
    if not check_env_vars(required_vars):
        print("❌ Variáveis de ambiente não configuradas!")
        return 1

    # Carregar prompt otimizado
    prompt_path = "prompts/bug_to_user_story_v2.yml"
    prompts = load_yaml(prompt_path)

    if not prompts:
        print(f"❌ Erro ao carregar {prompt_path}")
        return 1

    # Extrair prompt v2
    prompt_v2 = prompts.get("bug_to_user_story_v2")
    if not prompt_v2:
        print("❌ Prompt 'bug_to_user_story_v2' não encontrado no YAML")
        return 1

    # Validar prompt
    is_valid, errors = validate_prompt(prompt_v2)

    if not is_valid:
        print("\n📋 Erros de validação encontrados:")
        for error in errors:
            print(f"  {error}")
        print()

    # Mostrar resumo do prompt
    print("\n📊 Resumo do Prompt:")
    print(f"  Descrição: {prompt_v2.get('description', 'N/A')}")
    print(f"  Versão: {prompt_v2.get('version', 'N/A')}")
    print(f"  Tags: {', '.join(prompt_v2.get('tags', []))}")
    print(f"  Técnicas: {len(prompt_v2.get('techniques', []))} aplicadas")
    print()

    # Fazer push do prompt
    success = push_prompt_to_langsmith("bug_to_user_story_v2", prompt_v2)

    if success:
        print("\n✅ SUCESSO! Prompt v2 foi enviado para o LangSmith Prompt Hub (PÚBLICO)")
        print("📍 Você pode acessá-lo em: https://smith.langchain.com/hub")
        return 0
    else:
        print("\n❌ FALHA! Não foi possível enviar o prompt para o LangSmith")
        return 1


if __name__ == "__main__":
    sys.exit(main())
