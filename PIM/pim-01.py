import json
import os
from cryptography.fernet import Fernet
import fitz
from PIL import Image
import io
import matplotlib.pyplot as plt
import PyPDF2 as pdf
from datetime import datetime
from statistics import mean, median, mode
#-----------------------------------------------------------------------------------------------#
ARQUIVO_USUARIOS = "usuarios.json"
ARQUIVO_CHAVE = "chave_secreta.key"
ARQUIVO_QUESTOES = "questoes.json"
#-----------------------------------------------------------------------------------------------#
ARQUIVO_MAT_BASICO = "Matemática e estatística - Nível Básico.pdf"
ARQUIVO_MAT_INTERMEDIARIO = "Matemática e estatística - Nível Intermediário.pdf"
ARQUIVO_MAT_AVANCADO = "Matemática e estatística - Nível Avançado.pdf"

ARQUIVO_CIBER_BASICO = "Cibersegurança - Nível Básico.pdf"
ARQUIVO_CIBER_INTERMEDIARIO = "Cibersegurança - Nível Intermediário.pdf"
ARQUIVO_CIBER_AVANCADO = "Cibersegurança - Nível Avançado.pdf"

ARQUIVO_LOGICA_BASICO = "Lógica de Programação em Python - Nível Básico.pdf"
ARQUIVO_LOGICA_INTERMEDIARIO = "Lógica de Programação em Python - Nível Intermediário.pdf"
ARQUIVO_LOGICA_AVANCADO = "Lógica de Programação em Python - Nível Avançado.pdf"
#-----------------------------------------------------------------------------------------------#
#Função Criptografar e Descriptografar
def carregar_chave():
    if os.path.exists(ARQUIVO_CHAVE):
        with open(ARQUIVO_CHAVE, "rb") as file:
            return file.read()
    else:
        chave_secreta = Fernet.generate_key()
        with open(ARQUIVO_CHAVE, "wb") as file:
            file.write(chave_secreta)
        return chave_secreta

chave_secreta = carregar_chave()
fernet = Fernet(chave_secreta)

def criptografar(dado):
    return fernet.encrypt(dado.encode()).decode()

def descriptografar(dados_criptografada):
    return fernet.decrypt(dados_criptografada.encode()).decode()

def dados_descriptografados():
    dados = carregar_usuarios()
    dados_descript = {"usuarios": []}
    
    for usuario in dados["usuarios"]:
        usuario_descript = {}
        for chave, valor in usuario.items():
            if chave in ["nome_usuario", "pontuacao"]:
                usuario_descript[chave] = valor
            else:
                usuario_descript[chave] = descriptografar(valor)
        dados_descript["usuarios"].append(usuario_descript)
    
    return dados_descript
#-----------------------------------------------------------------------------------------------#
def inicializar_arquivo():
    if not os.path.exists(ARQUIVO_USUARIOS):
        with open(ARQUIVO_USUARIOS, "w", encoding='utf-8') as f:
            json.dump({"usuarios": []}, f, ensure_ascii=False, indent=4)


    # Inicializa arquivo de questões se não existir
    if not os.path.exists(ARQUIVO_QUESTOES):
        questoes_exemplo = {
            "quizzes": [
                {
                    "materia": "Matemática",
                    "nivel": "Básico",
                    "questoes": [
                        {
                            "pergunta": "Quanto é 2 + 2?",
                            "alternativas": [
                                {"letra": "A", "texto": "3"},
                                {"letra": "B", "texto": "4"},
                                {"letra": "C", "texto": "5"},
                                {"letra": "D", "texto": "6"}
                            ],
                            "resposta_correta": "B"
                        }
                    ]
                }
            ]
        }
        with open(ARQUIVO_QUESTOES, "w", encoding='utf-8') as f:
            json.dump(questoes_exemplo, f, ensure_ascii=False, indent=4)

def carregar_usuarios():
    inicializar_arquivo()
    try:
        with open(ARQUIVO_USUARIOS, "r", encoding='utf-8') as f: 
            dados = json.load(f)  
        if "usuarios" not in dados:
            dados["usuarios"] = []
        return dados
    except (json.JSONDecodeError, FileNotFoundError):
        return {"usuarios": []}

def salvar_usuarios(dados):
    with open(ARQUIVO_USUARIOS, "w", encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

def gerar_novo_id(usuarios):
    if not usuarios:
        return 1
    try:
        ids = [int(descriptografar(u.get('id', '0'))) for u in usuarios]
        return max(ids) + 1
    except Exception as e:
        print(f"Erro ao gerar novo ID: {e}")
        return len(usuarios) + 1

def verificar_usuario_existente(campo, valor):
    dados = carregar_usuarios()
    for usuario in dados["usuarios"]:
        try:
            if campo == "nome_usuario":
                if usuario["nome_usuario"] == valor:
                    return True
            else:
                valor_criptografado = usuario.get(campo, "")
                if valor_criptografado and descriptografar(valor_criptografado) == valor:
                    return True
        except Exception:
            continue
    return False
#-----------------------------------------------------------------------------------------------#
def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def obter_data_atual():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")
#-----------------------------------------------------------------------------------------------#
def cadastrar_usuario():
    dados = carregar_usuarios()

    nome_usuario = input("Digite o nome do usuário: ").strip()  
    while verificar_usuario_existente("nome_usuario", nome_usuario):
        print("Nome de usuário já existe. Tente outro.")
        nome_usuario = input("Digite o nome do usuário: ").strip()

    idade = input("Digite a idade: ").strip()
    while not idade.isdigit() or int(idade) <= 12:
        print("Você precisa ter 12 anos ou mais para se cadastrar.")
        idade = input("Digite a idade: ").strip()

    senha = input("Digite a senha: ").strip()
    while len(senha) < 6:
        print("A senha deve ter pelo menos 6 caracteres.")
        senha = input("Digite a senha: ").strip()

    nome = input("Digite o seu nome: ").strip()
    sobrenome = input("Digite o sobrenome: ").strip()

    email = input("Digite o email: ").strip()
    while "@" not in email or ".com" not in email or verificar_usuario_existente("email", email):
        if verificar_usuario_existente("email", email):
            print("Email já cadastrado. Tente outro.")
        else:
            print("Email inválido. Deve conter @ e .com")
        email = input("Digite o email: ").strip()
    
    telefone = input("Digite o telefone: ").strip()
    while len(telefone) != 11 or not telefone.isdigit() or verificar_usuario_existente("telefone", telefone):
        if verificar_usuario_existente("telefone", telefone):
            print("Telefone já existe. Tente outro.")
        else:
            print("Telefone inválido. Deve ter 11 dígitos.")
        telefone = input("Digite o telefone: ").strip()

    cpf = input("Digite o CPF: ").strip()
    while len(cpf) != 11 or not cpf.isdigit() or verificar_usuario_existente("cpf", cpf):
        if verificar_usuario_existente("cpf", cpf):
            print("CPF já existe. Tente outro.")
        else:
            print("CPF inválido. Deve ter 11 dígitos.")
        cpf = input("Digite o CPF: ").strip()

    data_nascimento = input("Digite a data de nascimento (DD/MM/AAAA): ").strip()
    endereco = input("Digite o endereço: ").strip()  

    novo_id = gerar_novo_id(dados["usuarios"])

    usuario = {
        "id": criptografar(str(novo_id)),
        "nome_usuario": nome_usuario,
        "idade": criptografar(idade),
        "senha": criptografar(senha),
        "nome": criptografar(nome),
        "sobrenome": criptografar(sobrenome),
        "email": criptografar(email),
        "telefone": criptografar(telefone),
        "cpf": criptografar(cpf),
        "data_nascimento": criptografar(data_nascimento),
        "endereco": criptografar(endereco),
        "pontuacao": 0
    }
    
    dados["usuarios"].append(usuario)
    salvar_usuarios(dados)
    limpar_tela()
    print("\nUsuário cadastrado com sucesso!")
#-----------------------------------------------------------------------------------------------#
def login_usuario():
    dados = carregar_usuarios()

    print("\n--- Área de Login ---")
    nome_usuario = input("Nome de usuário: ").strip()
    senha = input("Senha: ").strip()

    usuario_autenticado = None
    for usuario in dados["usuarios"]:
        if usuario["nome_usuario"] == nome_usuario:
            senha_armazenada = descriptografar(usuario["senha"])
            if senha == senha_armazenada:
                usuario_autenticado = usuario
                break

    if usuario_autenticado:
        nome_completo = f"{descriptografar(usuario_autenticado['nome'])} {descriptografar(usuario_autenticado['sobrenome'])}"
        limpar_tela()
        print(f"\nBem-vindo(a), {nome_completo}!")
        area_logada(usuario_autenticado)
    else:
        print("Usuário ou senha inválidos!")
#-----------------------------------------------------------------------------------------------#
def alterar_senha():
    limpar_tela()
    print("\n=== Alterar Senha ===")
    
    dados = carregar_usuarios()
    nome_usuario = input("Digite seu nome de usuário: ").strip()
    senha_atual = input("Digite sua senha atual: ").strip()
    
    # Encontra o usuário nos dados
    usuario_encontrado = None
    usuario_idx = None
    
    for idx, usuario in enumerate(dados["usuarios"]):
        if usuario["nome_usuario"] == nome_usuario:
            try:
                if descriptografar(usuario["senha"]) == senha_atual:
                    usuario_encontrado = usuario
                    usuario_idx = idx
                    break
            except Exception:
                continue
    
    if not usuario_encontrado:
        print("\nUsuário ou senha inválidos!")
        input("\nPressione Enter para continuar...")
        return
        
    # Verificação adicional de segurança
    print("\nPor favor, confirme seus dados para continuar:")
    cpf_informado = input("Digite seu CPF (apenas números): ").strip()
    endereco_informado = input("Digite seu endereço: ").strip()
    
    try:
        cpf_correto = descriptografar(usuario_encontrado["cpf"])
        endereco_correto = descriptografar(usuario_encontrado["endereco"])
        
        if cpf_informado != cpf_correto or endereco_informado != endereco_correto:
            print("\nDados de verificação incorretos!")
            print("Por segurança, a alteração de senha foi cancelada.")
            input("\nPressione Enter para continuar...")
            return
            
    except Exception as e:
        print("\nErro ao verificar dados!")
        input("\nPressione Enter para continuar...")
        return
    
    # Solicita e valida a nova senha
    nova_senha = input("\nDigite a nova senha: ").strip()
    while len(nova_senha) < 6:
        print("A senha deve ter pelo menos 6 caracteres.")
        nova_senha = input("Digite a nova senha: ").strip()
        
    # Confirma a nova senha
    confirmacao = input("Confirme a nova senha: ").strip()
    if nova_senha != confirmacao:
        print("\nAs senhas não coincidem!")
        input("\nPressione Enter para continuar...")
        return
        
    # Verifica se a nova senha é diferente da atual
    if nova_senha == senha_atual:
        print("\nA nova senha deve ser diferente da senha atual!")
        input("\nPressione Enter para continuar...")
        return
    
    try:
        # Atualiza a senha no sistema
        dados["usuarios"][usuario_idx]["senha"] = criptografar(nova_senha)
        salvar_usuarios(dados)
        print("\nSenha alterada com sucesso!")
    except Exception as e:
        print(f"\nErro ao alterar a senha: {str(e)}")
    
    input("\nPressione Enter para continuar...")
#-----------------------------------------------------------------------------------------------#
def menu():
    while True:
        print("\n--- Jovem Tech: Plataforma de Educação Digital ---")
        print("1. Cadastrar Usuário")
        print("2. Login")
        print("3. Ver Ranking")
        print("4. Média de Idade dos Usuários")
        print("5. Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            cadastrar_usuario()
        elif opcao == "2":
            login_usuario()
        elif opcao == "3":
            mostrar_ranking()
            input("\nPressione Enter para continuar...")
        elif opcao == "4":
            mostrar_graficos()
        elif opcao == "5":
            print("Saindo...")
            break
        else:
            print("Opção inválida. Por favor, escolha uma opção de 1 a 4.")
#-----------------------------------------------------------------------------------------------#
def area_logada(usuario):
    while True:
        limpar_tela()
        print("\n--- Menu do Usuário ---")
        print(f"Usuário: {usuario['nome_usuario']}")
        print(f"Pontuação: {usuario['pontuacao']}\n")
        print("1. Acessar Módulos")
        print("2. Fazer Quiz")
        print("3. Ver Ranking")
        print("4. Ver Meu Histórico")
        print("5. Alterar Senha")
        print("6. Logout")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            menu_modulos(usuario)
        elif opcao == "2":
            materia = input("Digite a matéria (Matemática/Cibersegurança/Lógica de Programação): ").strip()
            nivel = input("Digite o nível (Básico/Intermediário/Avançado): ").strip()
            realizar_quiz_por_materia(usuario, materia, nivel)
        elif opcao == "3":
            mostrar_ranking()
            input("\nPressione Enter para continuar...")
        elif opcao == "4":
            mostrar_historico_quizzes(usuario)
            input("\nPressione Enter para continuar...")
        elif opcao == "5":
            alterar_senha()
        elif opcao == "6":
            print("Logout realizado com sucesso.")
            break
        else:
            print("Opção inválida!")
#-----------------------------------------------------------------------------------------------#
def mostrar_ranking():
    dados = carregar_usuarios()
    if not dados["usuarios"]:
        print("Nenhum usuário cadastrado ainda.")
        return
    
    # Ordena por pontuação decrescente
    usuarios_ordenados = sorted(dados["usuarios"], key=lambda x: x["pontuacao"], reverse=True)
    
    print("\n=== RANKING GERAL ===")
    print("Posição | Nome de Usuário | Pontuação | Quizzes Completos")
    print("-" * 50)
    
    for i, usuario in enumerate(usuarios_ordenados, 1):
        num_quizzes = len(usuario.get("quizzes", []))
        print(f"{i:6} | {usuario['nome_usuario']:15} | {usuario['pontuacao']:9} | {num_quizzes:15}")
#-----------------------------------------------------------------------------------------------#
def mostrar_historico_quizzes(usuario):
    if not usuario.get("quizzes"):
        print("Você ainda não completou nenhum quiz.")
        return
    
    print("\n=== SEU HISTÓRICO DE QUIZZES ===")
    print("Data           | Matéria           | Nível        | Acertos | Pontos")
    print("-" * 60)
    
    for quiz in usuario["quizzes"]:
        print(f"{quiz['data']:14} | {quiz['materia']:16} | {quiz['nivel']:12} | {quiz['acertos']:2}/{quiz['total_questoes']:2} | {quiz['pontos_ganhos']:6}")
#-----------------------------------------------------------------------------------------------#
def menu_modulos(usuario):
    while True:
        limpar_tela()
        print("\n=== MENU DE MÓDULOS ===")
        print("1. Matemática")
        print("2. Cibersegurança")
        print("3. Lógica de Programação")
        print("4. Voltar")

        try:
            opcao = int(input("\nEscolha uma opção: "))

            if opcao == 1:
                menu_matematica(usuario)
            elif opcao == 2:
                menu_ciberseguranca(usuario)
            elif opcao == 3:
                menu_logica_programacao(usuario)
            elif opcao == 4:
                print("Saindo do sistema...")
                break
            else:
                print("Opção inválida. Escolha entre 1 e 4.")
                input("Pressione Enter para continuar...")
        except ValueError:
            print("Por favor, digite um número válido.")
            input("Pressione Enter para continuar...")
#-----------------------------------------------------------------------------------------------#
def menu_matematica(usuario):
    while True:
        limpar_tela()
        print("\n=== MATEMÁTICA ===")
        print("1. Nível Básico")
        print("2. Nível Intermediário")
        print("3. Nível Avançado")
        print("4. Fazer Quiz")
        print("5. Voltar")

        try:
            opcao = int(input("\nEscolha uma opção: "))

            if opcao == 1:
                visualizar_pdf(ARQUIVO_MAT_BASICO)
            elif opcao == 2:
                visualizar_pdf(ARQUIVO_MAT_INTERMEDIARIO)
            elif opcao == 3:
                visualizar_pdf(ARQUIVO_MAT_AVANCADO)
            elif opcao == 4:
                nivel = input("Escolha o nível (Básico/Intermediário/Avançado): ").strip()
                if nivel in ["básico", "intermediário", "avançado"]:
                    realizar_quiz_por_materia(usuario, "Matemática", nivel)
                else:
                    print("Nível inválido!")
            elif opcao == 5:
                break
            else:
                print("Opção inválida. Escolha entre 1 e 5.")
            
            input("\nPressione Enter para continuar...")
        except ValueError:
            print("Por favor, digite um número válido.")
            input("Pressione Enter para continuar...")
#-----------------------------------------------------------------------------------------------#
def menu_ciberseguranca(usuario):
    while True:
        limpar_tela()
        print("\n=== CIBERSEGURANÇA ===")
        print("1. Nível Básico")
        print("2. Nível Intermediário")
        print("3. Nível Avançado")
        print("4. Fazer Quiz")
        print("5. Voltar")

        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "1":
            visualizar_pdf(ARQUIVO_CIBER_BASICO)
        elif opcao == "2":
            visualizar_pdf(ARQUIVO_CIBER_INTERMEDIARIO)
        elif opcao == "3":
            visualizar_pdf(ARQUIVO_CIBER_AVANCADO)
        elif opcao == "4":
            nivel = input("Escolha o nível (Básico/Intermediário/Avançado): ").strip()
            if nivel.lower() in ["básico", "intermediário", "avançado"]:
                realizar_quiz_por_materia(usuario, "Cibersegurança", nivel)
            else:
                print("Nível inválido!")
        elif opcao == "5":
            break
        else:
            print("Opção inválida. Escolha entre 1 e 5.")

        input("\nPressione Enter para continuar...")
#-----------------------------------------------------------------------------------------------#
def menu_logica_programacao(usuario):
    while True:
        limpar_tela()
        print("\n=== LÓGICA DE PROGRAMAÇÃO ===")
        print("1. Nível Básico")
        print("2. Nível Intermediário")
        print("3. Nível Avançado")
        print("4. Fazer Quiz")
        print("5. Voltar")

        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "1":
            visualizar_pdf(ARQUIVO_LOGICA_BASICO)
        elif opcao == "2":
            visualizar_pdf(ARQUIVO_LOGICA_INTERMEDIARIO)
        elif opcao == "3":
            visualizar_pdf(ARQUIVO_LOGICA_AVANCADO)
        elif opcao == "4":
            nivel = input("Escolha o nível (Básico/Intermediário/Avançado): ").strip()
            if nivel.lower() in ["básico", "intermediário", "avançado"]:
                realizar_quiz_por_materia(usuario, "Lógica de Programação", nivel)
            else:
                print("Nível inválido!")
        elif opcao == "5":
            break
        else:
            print("Opção inválida. Escolha entre 1 e 5.")

        input("\nPressione Enter para continuar...")
#-----------------------------------------------------------------------------------------------#
def visualizar_pdf(arquivo_pdf):
    try:
        if not os.path.exists(arquivo_pdf):
            print(f"Erro: Arquivo '{arquivo_pdf}' não encontrado.")
            return False

        print("\nOpções de visualização:")
        print("1. Ver conteúdo textual (recomendado para PDFs com texto)")
        print("2. Ver páginas como imagens (para PDFs escaneados ou complexos)")
        opcao = input("Escolha o modo de visualização (1/2): ").strip()

        if opcao == "1":
            try:
                with open(arquivo_pdf, 'rb') as pdf_file:
                    pdf_reader = pdf.PdfReader(pdf_file)
                    
                    for page_num, page in enumerate(pdf_reader.pages, start=1):
                        texto = page.extract_text()
                        print(f"\n=== Página {page_num} ===")
                        print(texto)
                        
                        if page_num % 2 == 0:
                            input("\nPressione Enter para continuar...")
                            limpar_tela()
            except Exception as e:
                print(f"Erro ao ler PDF como texto: {e}")
        
        elif opcao == "2":
            try:
                doc = fitz.open(arquivo_pdf)
                
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    pix = page.get_pixmap(dpi=150)
                    
                    img = Image.open(io.BytesIO(pix.tobytes()))
                    
                    plt.figure(figsize=(10, 12))
                    plt.imshow(img)
                    plt.title(f"Página {page_num + 1}")
                    plt.axis('off')
                    plt.show()
                    
                    if (page_num + 1) % 2 == 0:
                        continuar = input("Mostrar próxima página? (s/n): ").lower()
                        if continuar != 's':
                            break
            except Exception as e:
                print(f"Erro ao exibir PDF como imagens: {e}")
        else:
            print("Opção inválida.")
            return False
        return True
    
    except Exception as e:
        print(f"Erro ao visualizar PDF: {str(e)}")
        return False
#-----------------------------------------------------------------------------------------------#
def carregar_questoes():
    try:
        with open(ARQUIVO_QUESTOES, "r", encoding='utf-8') as f:
            dados = json.load(f)
            # Verifica se a estrutura está correta
            if not isinstance(dados, dict) or "quizzes" not in dados:
                print("Estrutura do arquivo de questões inválida!")
                return None
            return dados
    except FileNotFoundError:
        print("Arquivo de questões não encontrado!")
        return None
    except json.JSONDecodeError:
        print("Erro ao ler o arquivo de questões!")
        return None
#-----------------------------------------------------------------------------------------------#
def realizar_quiz_por_materia(usuario, materia, nivel):
    dados = carregar_usuarios()
    questoes = carregar_questoes()
    
    if not questoes:
        print("Não foi possível carregar as questões.")
        input("Pressione Enter para continuar...")
        return
    
    # Normaliza os parâmetros de busca
    materia = materia.lower()
    nivel = nivel.lower()
    
    # Encontra o quiz correspondente
    quiz_selecionado = None
    for quiz in questoes["quizzes"]:
        if (quiz["materia"].lower() == materia and 
            quiz["nivel"].lower() == nivel):
            quiz_selecionado = quiz
            break
    
    if not quiz_selecionado:
        print(f"Nenhum quiz encontrado para {materia.capitalize()} - Nível {nivel.capitalize()}")
        input("Pressione Enter para continuar...")
        return
    
    # Inicia o quiz
    limpar_tela()
    print(f"\n=== QUIZ: {materia.upper()} - NÍVEL {nivel.upper()} ===\n")
    
    acertos = 0
    total_questoes = len(quiz_selecionado["questoes"])
    
    for i, questao in enumerate(quiz_selecionado["questoes"], 1):
        print(f"Questão {i}: {questao['pergunta']}\n")
        for alternativa in questao['alternativas']:
            print(f"{alternativa['letra']}) {alternativa['texto']}")
        
        resposta = input("\nSua resposta (A/B/C/D): ").strip().upper()
        while resposta not in ['A', 'B', 'C', 'D']:
            resposta = input("Resposta inválida! Digite A, B, C ou D: ").strip().upper()
        
        if resposta == questao['resposta_correta']:
            print("\n✓ Resposta correta!")
            acertos += 1
        else:
            print(f"\n✗ Resposta incorreta. A correta era {questao['resposta_correta']}")
        
        input("\nPressione Enter para continuar...")
        limpar_tela()
    
    # Calcula pontuação
    pontos = calcular_pontuacao(acertos, nivel)
    
    # Atualiza usuário
    usuario_idx = next((i for i, u in enumerate(dados["usuarios"]) 
                      if u["nome_usuario"] == usuario["nome_usuario"]), None)
    
    if usuario_idx is not None:
        resultado = {
            "materia": materia.capitalize(),
            "nivel": nivel.capitalize(),
            "data": obter_data_atual(),
            "acertos": acertos,
            "total_questoes": total_questoes,
            "pontos_ganhos": pontos
        }
        
        dados["usuarios"][usuario_idx]["pontuacao"] += pontos
        if "quizzes" not in dados["usuarios"][usuario_idx]:
            dados["usuarios"][usuario_idx]["quizzes"] = []
        dados["usuarios"][usuario_idx]["quizzes"].append(resultado)
        salvar_usuarios(dados)
        
        # Atualiza usuário local
        usuario["pontuacao"] += pontos
        if "quizzes" not in usuario:
            usuario["quizzes"] = []
        usuario["quizzes"].append(resultado)
    
    # Mostra resultado
    print("\n=== RESULTADO ===")
    print(f"Acertos: {acertos}/{total_questoes}")
    print(f"Pontuação: {pontos}")
    print(f"Total: {usuario['pontuacao']} pontos")
    input("\nPressione Enter para voltar...")
#-----------------------------------------------------------------------------------------------#
def calcular_pontuacao(acertos, nivel):
    """Calcula pontuação baseada no nível e número de acertos"""
    multiplicador = {
        "Básico": 1,
        "Intermediário": 2,
        "Avançado": 3
    }
    return acertos * multiplicador.get(nivel, 1)
#-----------------------------------------------------------------------------------------------#
def media_idade():
    dados = carregar_usuarios()
    idades = []
    
    for usuario in dados["usuarios"]:
        try:
            idade = int(descriptografar(usuario["idade"]))
            idades.append(idade)
        except Exception:
            continue
    
    if not idades:
        print("Nenhum usuário cadastrado.")
        return None
    
    media = mean(idades)
    mediana = median(idades)
    
    try:
        moda = mode(idades)
    except Exception:
        moda = "Sem moda"
    
    print(f"Média de Idade: {media:.2f}")
    print(f"Mediana de Idade: {mediana}")
    print(f"Moda de Idade: {moda}")
    input("\nPressione Enter para continuar...")
#-----------------------------------------------------------------------------------------------#
def pontuacao_media():
    dados = carregar_usuarios()
    pontuacoes = []
    
    for usuario in dados["usuarios"]:
        try:
            pontuacao = int(usuario["pontuacao"])
            pontuacoes.append(pontuacao)
        except Exception:
            continue
    
    if not pontuacoes:
        print("Nenhum usuário cadastrado.")
        return None
    
    media = mean(pontuacoes)
    mediana = median(pontuacoes)
    
    try:
        moda = mode(pontuacoes)
    except Exception:
        moda = "Sem moda"
    
    print(f"Média de Pontuação: {media:.2f}")
    print(f"Mediana de Pontuação: {mediana}")
    print(f"Moda de Pontuação: {moda}")
    input("\nPressione Enter para continuar...")


def grafico_pontuacao():
    dados = carregar_usuarios()
    pontuacoes = []
    
    for usuario in dados["usuarios"]:
        try:
            pontuacao = int(usuario["pontuacao"])
            pontuacoes.append(pontuacao)
        except Exception:
            continue
    
    if not pontuacoes:
        print("Nenhum usuário cadastrado.")
        return None
    
    plt.hist(pontuacoes, bins=10, color='blue', alpha=0.7)
    plt.title('Distribuição de Pontuação dos Usuários')
    plt.xlabel('Pontuação')
    plt.ylabel('Número de Usuários')
    plt.grid(axis='y', alpha=0.75)
    plt.show()

def grafico_idade():
    dados = carregar_usuarios()
    idades = []
    
    for usuario in dados["usuarios"]:
        try:
            idade = int(descriptografar(usuario["idade"]))
            idades.append(idade)
        except Exception:
            continue
    
    if not idades:
        print("Nenhum usuário cadastrado.")
        return None
    
    plt.hist(idades, bins=10, color='green', alpha=0.7)
    plt.title('Distribuição de Idade dos Usuários')
    plt.xlabel('Idade')
    plt.ylabel('Número de Usuários')
    plt.grid(axis='y', alpha=0.75)
    plt.show()
#-----------------------------------------------------------------------------------------------#
def mostrar_graficos():
    while True:
        limpar_tela()
        print("\n=== GRÁFICOS ===")
        print("1. Gráfico de Pontuação")
        print("2. Gráfico de Idade")
        print("3. Gráfico de Idade e Pontuação")
        print("4. Voltar")

        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "1":
            grafico_pontuacao()
        elif opcao == "2":
            grafico_idade()
        elif opcao == "3":
            grafico_idade_pontuacao()
        elif opcao == "4":
            break
        else:
            print("Opção inválida. Escolha entre 1 e 3.")

        input("\nPressione Enter para continuar...")
#-----------------------------------------------------------------------------------------------#
def grafico_idade_pontuacao():
    dados = carregar_usuarios()
    idades = []
    pontuacoes = []
    
    for usuario in dados["usuarios"]:
        try:
            idade = int(descriptografar(usuario["idade"]))
            pontuacao = int(usuario["pontuacao"])
            idades.append(idade)
            pontuacoes.append(pontuacao)
        except Exception:
            continue
    
    if not idades or not pontuacoes:
        print("Dados insuficientes para gerar gráfico.")
        return None
    _, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Gráfico de idades
    ax1.hist(idades, bins=10, color='green', alpha=0.7)
    ax1.set_title('Distribuição de Idade')
    ax1.set_xlabel('Idade')
    ax1.set_ylabel('Número de Usuários')
    ax1.grid(True, alpha=0.3)
    
    # Gráfico de pontuações
    ax2.hist(pontuacoes, bins=10, color='blue', alpha=0.7)
    ax2.set_title('Distribuição de Pontuação')
    ax2.set_xlabel('Pontuação')
    ax2.set_ylabel('Número de Usuários')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
#-----------------------------------------------------------------------------------------------#
if __name__ == '__main__':
    inicializar_arquivo()
    menu()