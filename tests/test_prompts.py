"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

class TestPrompts:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para carregar prompts antes de cada teste."""
        self.prompts_path = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
        self.prompts = load_prompts(str(self.prompts_path))
        self.prompt = self.prompts.get("bug_to_user_story_v2", {})

    def test_prompt_has_system_prompt(self):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in self.prompt, "Campo 'system_prompt' não existe"
        assert self.prompt["system_prompt"] is not None, "Campo 'system_prompt' é None"
        assert len(self.prompt["system_prompt"].strip()) > 0, "Campo 'system_prompt' está vazio"
        # Verificar que tem conteúdo mínimo
        assert len(self.prompt["system_prompt"]) > 100, "system_prompt muito curto (< 100 caracteres)"

    def test_prompt_has_role_definition(self):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        system_prompt = self.prompt.get("system_prompt", "").lower()

        # Procurar por indicadores de persona/role
        role_indicators = [
            "você é um",
            "você é uma",
            "você é especializado",
            "você é experiente",
            "você tem",
            "persona:",
        ]

        found_role = any(indicator in system_prompt for indicator in role_indicators)
        assert found_role, (
            f"Prompt não define uma persona clara. "
            f"Procure incluir 'Você é um [role]' no system_prompt"
        )

    def test_prompt_mentions_format(self):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        system_prompt = self.prompt.get("system_prompt", "").lower()

        # Procurar por indicadores de formato esperado
        format_indicators = [
            "formato:",
            "formato esperado",
            "como um",  # Padrão de user story
            "eu quero",
            "para que",
            "critérios de aceitação",
            "user story",
            "quando",
            "então",
        ]

        found_format = any(indicator in system_prompt for indicator in format_indicators)
        assert found_format, (
            f"Prompt não menciona formato esperado. "
            f"Inclua instruções sobre o formato (Como um/Eu quero/Para que ou Dado/Quando/Então)"
        )

    def test_prompt_has_few_shot_examples(self):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        system_prompt = self.prompt.get("system_prompt", "")

        # Procurar por exemplos
        example_indicators = [
            "exemplo",
            "Exemplo",
            "EXEMPLO",
            "bug reportado",
            "user story gerada",
        ]

        found_examples = any(indicator in system_prompt for indicator in example_indicators)
        assert found_examples, "Prompt não contém exemplos (Few-shot Learning)"

        # Contar quantas vezes "Quando" aparece (indicador de múltiplos exemplos)
        when_count = system_prompt.count("Quando")
        assert when_count >= 2, (
            f"Prompt tem poucos exemplos de Few-shot. "
            f"Encontradas {when_count} instâncias de 'Quando' (esperado >= 2)"
        )

    def test_prompt_no_todos(self):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        system_prompt = self.prompt.get("system_prompt", "")
        user_prompt = self.prompt.get("user_prompt", "")

        todos_in_system = "[TODO]" in system_prompt or "[todo]" in system_prompt.lower()
        todos_in_user = "[TODO]" in user_prompt or "[todo]" in user_prompt.lower()

        assert not todos_in_system, "Prompt contém [TODO] no system_prompt. Preencha completamente!"
        assert not todos_in_user, "Prompt contém [TODO] no user_prompt. Preencha completamente!"

    def test_minimum_techniques(self):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        # Verificar campo techniques nos metadados
        techniques = self.prompt.get("techniques", [])

        assert isinstance(techniques, list), "Campo 'techniques' deve ser uma lista"
        assert len(techniques) >= 2, (
            f"Prompt deve usar pelo menos 2 técnicas de Prompt Engineering. "
            f"Encontradas {len(techniques)} (esperado >= 2). "
            f"Exemplos: Few-shot Learning, Role Prompting, Chain of Thought, Skeleton of Thought"
        )

        # Verificar que cada técnica tem informação útil
        for technique in techniques:
            assert isinstance(technique, dict), "Cada técnica deve ser um dicionário"
            assert "name" in technique, "Cada técnica deve ter um 'name'"
            assert len(technique["name"]) > 0, "Nome da técnica não pode estar vazio"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])