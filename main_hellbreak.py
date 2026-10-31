import pygame
import sys
import random

pygame.init()

# =====================================================
# 1. JANELA E CONFIGURACOES
# =====================================================
LARGURA, ALTURA = 960, 540
FPS = 60

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Hellbreak - 2D Action")
relogio = pygame.time.Clock()
fonte = pygame.font.Font(None, 28)
fonte_grande = pygame.font.Font(None, 64)
fonte_media = pygame.font.Font(None, 40)

PRETO = (15, 15, 22)
BRANCO = (245, 245, 255)
VERMELHO = (210, 45, 55)
VERMELHO_ESCURO = (90, 20, 30)
CINZA = (55, 55, 70)
CINZA_CLARO = (100, 100, 125)
VERDE = (50, 210, 110)
AMARELO = (255, 200, 55)
LARANJA = (255, 100, 35)
AZUL = (80, 140, 220)
ROXO = (145, 65, 200)
ROXO_ESCURO = (55, 25, 75)

CHAO_Y = 450
MUNDO_LARGURA = 4300
chao = pygame.Rect(0, CHAO_Y, MUNDO_LARGURA, ALTURA - CHAO_Y)

# Plataformas em coordenadas do mundo
plataformas = [
    pygame.Rect(230, 365, 190, 18),
    pygame.Rect(500, 305, 180, 18),
    pygame.Rect(820, 365, 180, 18),
    pygame.Rect(1030, 280, 150, 18),
    pygame.Rect(1320, 360, 190, 18),
    pygame.Rect(1580, 300, 180, 18),
    pygame.Rect(1880, 365, 190, 18),
    pygame.Rect(2140, 290, 180, 18),
    pygame.Rect(2440, 360, 200, 18),
    pygame.Rect(2730, 300, 180, 18),
    pygame.Rect(3050, 360, 200, 18),
    pygame.Rect(3370, 310, 180, 18),
    pygame.Rect(3650, 360, 180, 18),
    pygame.Rect(3910, 300, 180, 18),
]

# Limites das áreas e posição de entrada de cada onda
secoes = [
    {"inicio": 0, "fim": 1050, "nome": "AREA 1 - RUINAS"},
    {"inicio": 1050, "fim": 2200, "nome": "AREA 2 - FORTALEZA"},
    {"inicio": 2200, "fim": 3300, "nome": "AREA 3 - ABISMO"},
    {"inicio": 3300, "fim": MUNDO_LARGURA, "nome": "ARENA DO CHEFE"},
]
indice_secao = 0
onda_gerada = False
barreira_ativa = True
mensagem = ""
tempo_mensagem = 0
jogo_vencido = False

# =====================================================
# 2. JOGADOR
# =====================================================
jogador = pygame.Rect(70, CHAO_Y - 80, 40, 80)
velocidade = 5
velocidade_y = 0.0
gravidade = 0.7
forca_pulo = -14
no_chao = False
direcao = 1

vida_jogador = 100
vida_maxima_jogador = 100
invulnerabilidade_jogador = 0.0

# Ataques do jogador
atacando = False
tipo_ataque = ""
tempo_ataque = 0.0
tempo_entre_ataques = 0.0
ja_acertou = False
dano_ataque = 25
alcance_ataque = 65
altura_ataque = 55
empurrao_ataque = 25
alcance = pygame.Rect(0, 0, 1, 1)

# Sistema de combo: encadeie ataques antes que o tempo acabe
combo = 0
tempo_combo = 0.0
janela_combo = 0.85
multiplicador_combo = 1.0

# Projéteis
projetis = []
velocidade_projetil = 12
dano_projetil = 10
recarga_projetil = 0.0

# =====================================================
# 3. INIMIGOS
# =====================================================
inimigos = []
proximo_id = 0

def criar_inimigo(x, tipo="normal"):
    global proximo_id
    proximo_id += 1
    if tipo == "forte":
        largura, altura, vida, velocidade_ini, dano = 52, 86, 150, 1.7, 15
    else:
        largura, altura, vida, velocidade_ini, dano = 42, 72, 75, 2.1, 10
    rect = pygame.Rect(x, CHAO_Y - altura, largura, altura)
    return {
        "id": proximo_id,
        "rect": rect,
        "tipo": tipo,
        "vida": vida,
        "vida_max": vida,
        "velocidade": velocidade_ini,
        "dano": dano,
        "direcao": -1,
        "estado": "patrulha",
        "tempo_ataque": 0.0,
        "recarga": random.uniform(0.3, 1.0),
        "atordoado": 0.0,
        "invuln": 0.0,
        "empurrao_x": 0.0,
        "vel_y": 0.0,
        "no_chao": True,
        "patrulha_inicio": max(0, x - 100),
        "patrulha_fim": min(MUNDO_LARGURA - 100, x + 140),
        "ja_acertou": False,
    }

# Boss
boss = None
def criar_boss(x):
    return {
        "rect": pygame.Rect(x, CHAO_Y - 150, 100, 150),
        "vida": 650,
        "vida_max": 650,
        "direcao": -1,
        "estado": "aproximando",
        "temporizador": 1.0,
        "recarga": 1.2,
        "invuln": 0.0,
        "empurrao_x": 0.0,
        "vel_y": 0.0,
        "no_chao": True,
        "ja_acertou": False,
        "fase2": False,
        "dano": 18,
    }

# =====================================================
# 4. PARTICULAS
# =====================================================
particulas = []

def criar_impacto(x, y, direcao_particula, pesado=False, roxo=False):
    quantidade = 28 if pesado else 13
    cor = ROXO if roxo else (LARANJA if pesado else AMARELO)
    for _ in range(quantidade):
        extra = 3 if pesado else 0
        particulas.append({
            "x": float(x), "y": float(y),
            "vx": random.uniform(-4, 4) + direcao_particula * (2 + extra),
            "vy": random.uniform(-6, 2),
            "vida": random.randint(12, 25),
            "tamanho": random.randint(2, 6),
            "cor": cor,
        })

def atualizar_particulas():
    for p in particulas[:]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["vy"] += 0.25
        p["vida"] -= 1
        if p["vida"] <= 0:
            particulas.remove(p)

def desenhar_particulas(camera_x):
    for p in particulas:
        tamanho = max(1, p["tamanho"] * p["vida"] // 25)
        pygame.draw.circle(tela, p["cor"],
                           (int(p["x"] - camera_x), int(p["y"])), tamanho)

# =====================================================
# SISTEMA DE ITENS / DROPS
# =====================================================
itens_no_chao = []

def tentar_dropar_item(x, y):
    # Chance de drop: 20% de chance (0.2). Mude para 0.05 se quiser apenas 5%, etc.
    chance_drop = 0.20 
    
    if random.random() < chance_drop:
        # Sorteia o tipo de item: "cura" (vida) ou "bonus" (pontos/força)
        tipo_item = random.choice(["cura", "bonus"])
        
        itens_no_chao.append({
            "rect": pygame.Rect(x, y - 15, 20, 20),
            "tipo": tipo_item,
            "tempo_vida": 10.0 # O item some sozinho após 10 segundos se não for pego
        })
        if inimigo["vida"] <= 0:
                    criar_impacto(r.centerx, r.centery, direcao, pesado=True)
                
                # ---> CHAMA AQUI O DROP DO ITEM <---
                    tentar_dropar_item(r.centerx, r.centery)
                
                    inimigos.remove(inimigo)

# =====================================================
# ATUALIZAR E COLETAR ITENS
# =====================================================
    for item in itens_no_chao[:]:
        item["tempo_vida"] -= dt
        if item["tempo_vida"] <= 0:
            itens_no_chao.remove(item)
            continue
            
        # Se o jogador encostar no item
        if jogador.colliderect(item["rect"]):
            if item["tipo"] == "cura":
                vida_jogador = min(vida_maxima_jogador, vida_jogador + 30) # Cura 30 de vida
            elif item["tipo"] == "bonus":
                # Aqui você pode dar pontos, dinheiro ou bônus temporário de ataque se quiser
                dano_ataque += 5 
                
            itens_no_chao.remove(item)
    # Desenhar itens no chão
    for item in itens_no_chao:
        item_tela = retangulo_tela(item["rect"], camera_x)
        # Cor verde se for cura, Amarelo se for bônus
        cor_item = VERDE if item["tipo"] == "cura" else AMARELO
        pygame.draw.rect(tela, cor_item, item_tela)
        pygame.draw.rect(tela, BRANCO, item_tela, 1) # Borda branca

# =====================================================
# 5. FUNCOES AUXILIARES
# =====================================================
def texto_central(texto, y, cor=BRANCO, fonte_usada=None):
    f = fonte_usada or fonte_media
    imagem = f.render(texto, True, cor)
    tela.blit(imagem, imagem.get_rect(center=(LARGURA // 2, y)))

def barra_vida(x, y, largura, altura, vida, vida_max, cor=VERDE):
    pygame.draw.rect(tela, VERMELHO_ESCURO, (x, y, largura, altura))
    preenchimento = max(0, int(largura * vida / vida_max))
    if preenchimento:
        pygame.draw.rect(tela, cor, (x, y, preenchimento, altura))
    pygame.draw.rect(tela, BRANCO, (x, y, largura, altura), 1)

def retangulo_tela(rect, camera_x):
    return pygame.Rect(rect.x - camera_x, rect.y, rect.width, rect.height)

def atualizar_fisica_personagem(rect, vel_y, plataformas_mundo, pode_pular=False):
    # Esta funcao e usada para inimigos; o jogador tem fisica propria.
    fundo_anterior = rect.bottom
    vel_y += gravidade
    rect.y += int(vel_y)
    no_solo = False
    if vel_y >= 0:
        if fundo_anterior <= CHAO_Y and rect.bottom >= CHAO_Y:
            rect.bottom = CHAO_Y
            vel_y = 0
            no_solo = True
        else:
            for plat in plataformas_mundo:
                if (fundo_anterior <= plat.top and rect.bottom >= plat.top
                        and rect.right > plat.left and rect.left < plat.right):
                    rect.bottom = plat.top
                    vel_y = 0
                    no_solo = True
                    break
    return vel_y, no_solo

def gerar_onda(indice):
    if indice == 0:
        return [criar_inimigo(430), criar_inimigo(700)]
    if indice == 1:
        return [criar_inimigo(1320), criar_inimigo(1510, "forte"),
                criar_inimigo(1800)]
    if indice == 2:
        return [criar_inimigo(2390, "forte"), criar_inimigo(2630),
                criar_inimigo(2900, "forte")]
    return []

def abrir_proxima_secao():
    global indice_secao, onda_gerada, barreira_ativa, mensagem, tempo_mensagem, boss
    if indice_secao < 3:
        indice_secao += 1
        onda_gerada = False
        barreira_ativa = True
        mensagem = secoes[indice_secao]["nome"]
        tempo_mensagem = 2.5
        if indice_secao == 3:
            boss = criar_boss(3800)

def reiniciar_jogo():
    global jogador, vida_jogador, velocidade_y, no_chao, direcao
    global atacando, tipo_ataque, tempo_ataque, tempo_entre_ataques, ja_acertou
    global combo, tempo_combo, multiplicador_combo
    global inimigos, boss, indice_secao, onda_gerada, barreira_ativa
    global mensagem, tempo_mensagem, jogo_vencido, itens_no_chao, projetis

    # Reseta o jogador
    jogador = pygame.Rect(70, CHAO_Y - 80, 40, 80)
    velocidade_y = 0.0
    no_chao = False
    direcao = 1
    vida_jogador = 100
    
    # Reseta estados de ataque e combo
    atacando = False
    tipo_ataque = ""
    tempo_ataque = 0.0
    tempo_entre_ataques = 0.0
    ja_acertou = False
    combo = 0
    tempo_combo = 0.0
    multiplicador_combo = 1.0

    # Reseta fases, inimigos e boss
    indice_secao = 0
    onda_gerada = False
    barreira_ativa = True
    inimigos = []
    boss = None
    
    # Limpa projéteis e itens do chão
    projetis = []
    itens_no_chao = []

    # Mensagem inicial
    mensagem = secoes[0]["nome"]
    tempo_mensagem = 2.5
    jogo_vencido = False

def gerar_onda(indice):
    if indice == 0:
        # Área 1: mais inimigos espalhados pelas ruínas
        return [criar_inimigo(430), criar_inimigo(700), criar_inimigo(950)]
    if indice == 1:
        # Área 2: mistura normais e fortes
        return [criar_inimigo(1320), criar_inimigo(1510, "forte"),
                criar_inimigo(1750), criar_inimigo(1950, "forte"), criar_inimigo(2100)]
    if indice == 2:
        # Área 3: abismo cheio de perigos
        return [criar_inimigo(2390, "forte"), criar_inimigo(2550), 
                criar_inimigo(2700, "forte"), criar_inimigo(2900), criar_inimigo(3100, "forte")]
    return []

# =====================================================
# 6. LOOP PRINCIPAL
# =====================================================
camera_x = 0
executando = True

while executando:
    dt = relogio.tick(FPS) / 1000.0
    dt = min(dt, 0.04)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            executando = False

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                executando = False

            if vida_jogador <= 0 or jogo_vencido:
                if evento.key in (pygame.K_r, pygame.K_SPACE):
                    reiniciar_jogo()
        
            if vida_jogador > 0 and not jogo_vencido:
                # Ataques corpo a corpo (J e K)
                if evento.key in (pygame.K_j, pygame.K_k) and tempo_entre_ataques <= 0:
                    atacando = True
                    ja_acertou = False
                    if evento.key == pygame.K_j:
                        tipo_ataque = "leve"
                        tempo_ataque = 0.20
                        tempo_entre_ataques = 0.28
                        dano_ataque = 25
                        alcance_ataque = 65
                        altura_ataque = 55
                        empurrao_ataque = 25
                    else:
                        tipo_ataque = "pesado"
                        tempo_ataque = 0.32
                        tempo_entre_ataques = 0.62
                        dano_ataque = 40
                        alcance_ataque = 100
                        altura_ataque = 75
                        empurrao_ataque = 55
                    dano_ataque = int(dano_ataque * multiplicador_combo)
                    empurrao_ataque = int(empurrao_ataque * min(1.5, 1.0 + (combo - 1) * 0.10))

                # Ataque à distância (L) - AGORA DENTRO DO LOOP CORRETO!
                if evento.key == pygame.K_l and recarga_projetil <= 0:
                    projetis.append({
                        "rect": pygame.Rect(
                            jogador.centerx,
                            jogador.centery - 5,
                            22,
                            8
                        ),
                        "direcao": direcao
                    })
                    recarga_projetil = 0.35

                # Ataque para levantar o inimigo (Launcher) - Tecla I
                if evento.key == pygame.K_i and tempo_entre_ataques <= 0:
                    atacando = True
                    ja_acertou = False
                    tipo_ataque = "launcher"
                    tempo_ataque = 0.35
                    tempo_entre_ataques = 0.70
                    dano_ataque = 35
                    alcance_ataque = 80
                    altura_ataque = 70
                    empurrao_ataque = 10

    teclas = pygame.key.get_pressed()

    if vida_jogador > 0 and not jogo_vencido:
        if teclas[pygame.K_a]:
            jogador.x -= velocidade
            direcao = -1
        if teclas[pygame.K_d]:
            jogador.x += velocidade
            direcao = 1
        if teclas[pygame.K_SPACE] and no_chao:
            velocidade_y = forca_pulo
            no_chao = False

    # Avanco da fisica do jogador
    fundo_anterior = jogador.bottom
    velocidade_y += gravidade
    jogador.y += int(velocidade_y)
    no_chao = False
    if velocidade_y >= 0:
        if fundo_anterior <= CHAO_Y and jogador.bottom >= CHAO_Y:
            jogador.bottom = CHAO_Y
            velocidade_y = 0
            no_chao = True
        else:
            for plataforma in plataformas:
                if (fundo_anterior <= plataforma.top and jogador.bottom >= plataforma.top
                        and jogador.right > plataforma.left and jogador.left < plataforma.right):
                    jogador.bottom = plataforma.top
                    velocidade_y = 0
                    no_chao = True
                    break

    jogador.left = max(0, min(jogador.left, MUNDO_LARGURA - jogador.width))

    invulnerabilidade_jogador = max(0.0, invulnerabilidade_jogador - dt)
    tempo_entre_ataques = max(0.0, tempo_entre_ataques - dt)
    tempo_combo = max(0.0, tempo_combo - dt)
    if tempo_combo <= 0:
        combo = 0
        multiplicador_combo = 1.0
    if atacando:
        tempo_ataque -= dt
        if tempo_ataque <= 0:
            atacando = False

    alcance = pygame.Rect(0, 0, alcance_ataque, altura_ataque)
    if direcao == 1:
        alcance.midleft = (jogador.right, jogador.centery)
    else:
        alcance.midright = (jogador.left, jogador.centery)

    # Seções: criar uma onda por área e bloquear passagem até vencer
    secao_atual = secoes[indice_secao]
    if not onda_gerada:
        if indice_secao < 3:
            inimigos = gerar_onda(indice_secao)
        else:
            inimigos = []
            if boss is None:
                boss = criar_boss(3800)
        onda_gerada = True
        mensagem = secao_atual["nome"]
        tempo_mensagem = 2.5

    limite_esquerdo = secao_atual["inicio"]
    limite_direito = secao_atual["fim"]
    if barreira_ativa:
        jogador.left = max(jogador.left, limite_esquerdo + 5)
        jogador.right = min(jogador.right, limite_direito - 5)

    # =====================================================
    # ATUALIZAR E COLIDIR PROJÉTEIS
    # =====================================================
    recarga_projetil = max(0.0, recarga_projetil - dt)

    for tiro in projetis[:]:
        # Move o projétil na direção correta
        tiro["rect"].x += tiro["direcao"] * velocidade_projetil

        # 1. Se o tiro saiu dos limites do mapa, remove-o
        if tiro["rect"].right < 0 or tiro["rect"].left > MUNDO_LARGURA:
            projetis.remove(tiro)
            continue

        # 2. Verifica colisão com os inimigos normais
        acertou_inimigo = False
        for inimigo in inimigos[:]:
            if tiro["rect"].colliderect(inimigo["rect"]):
                inimigo["vida"] -= dano_projetil
                inimigo["atordoado"] = 0.15
                criar_impacto(
                    inimigo["rect"].centerx,
                    inimigo["rect"].centery,
                    tiro["direcao"]
                )
                projetis.remove(tiro)
                acertou_inimigo = True
                break
        
        if acertou_inimigo:
            continue

        # 3. Verifica colisão com o Boss (se estiver na fase 3)
        if indice_secao == 3 and boss and boss["vida"] > 0:
            if tiro["rect"].colliderect(boss["rect"]):
                boss["vida"] -= dano_projetil
                boss["invuln"] = 0.22
                criar_impacto(
                    boss["rect"].centerx,
                    boss["rect"].centery,
                    tiro["direcao"],
                    roxo=True
                )
                projetis.remove(tiro)
                break

    # IA dos inimigos comuns: perseguem, avisam o ataque e golpeiam.
    for inimigo in inimigos[:]:
        r = inimigo["rect"]
        inimigo["recarga"] = max(0.0, inimigo["recarga"] - dt)
        inimigo["invuln"] = max(0.0, inimigo["invuln"] - dt)
        inimigo["atordoado"] = max(0.0, inimigo["atordoado"] - dt)

        distancia_x = jogador.centerx - r.centerx
        distancia_y = jogador.centery - r.centery
        vendo = abs(distancia_x) < 330 and abs(distancia_y) < 120

        if inimigo["atordoado"] > 0:
            inimigo["estado"] = "atordoado"
        elif inimigo["estado"] == "preparando":
            # O inimigo fica brevemente parado e sinaliza antes de atacar.
            inimigo["tempo_ataque"] -= dt
            
            # (A linha que atualizava a direção foi apagada daqui!)

            if inimigo["tempo_ataque"] <= 0:
                alcance_inimigo = pygame.Rect(0, 0, 76 if inimigo["tipo"] == "normal" else 94, 62)
                if inimigo["direcao"] == 1:
                    alcance_inimigo.midleft = (r.right, r.centery)
                else:
                    alcance_inimigo.midright = (r.left, r.centery)

                if alcance_inimigo.colliderect(jogador) and invulnerabilidade_jogador <= 0:
                    vida_jogador = max(0, vida_jogador - inimigo["dano"])
                    invulnerabilidade_jogador = 0.85
                    empurrao = inimigo["direcao"]
                    jogador.x += empurrao * (32 if inimigo["tipo"] == "normal" else 46)
                    criar_impacto(jogador.centerx, jogador.centery, empurrao,
                                  pesado=(inimigo["tipo"] == "forte"))
                inimigo["estado"] = "esperando"
                inimigo["recarga"] = 1.0 if inimigo["tipo"] == "normal" else 1.35
        elif vendo:
            inimigo["direcao"] = 1 if distancia_x > 0 else -1
            if abs(distancia_x) <= 78 and inimigo["recarga"] <= 0:
                inimigo["estado"] = "preparando"
                inimigo["tempo_ataque"] = 0.42 if inimigo["tipo"] == "normal" else 0.58
            else:
                inimigo["estado"] = "perseguindo"
                if abs(distancia_x) > 62:
                    r.x += int(inimigo["direcao"] * inimigo["velocidade"])
        else:
            inimigo["estado"] = "patrulha"
            r.x += int(inimigo["direcao"] * inimigo["velocidade"] * 0.55)
            if r.left <= inimigo["patrulha_inicio"]:
                inimigo["direcao"] = 1
            if r.right >= inimigo["patrulha_fim"]:
                inimigo["direcao"] = -1

        inimigo["vel_y"], inimigo["no_chao"] = atualizar_fisica_personagem(
            r, inimigo["vel_y"], plataformas
        )
        r.left = max(limite_esquerdo + 10, r.left)
        r.right = min(limite_direito - 10, r.right)

        # Ataques do jogador
        if (atacando and not ja_acertou and vida_jogador > 0
                and alcance.colliderect(r) and inimigo["invuln"] <= 0):
            if tempo_combo > 0:
                combo += 1
            else:
                combo = 1
            tempo_combo = janela_combo
            multiplicador_combo = min(2.0, 1.0 + (combo - 1) * 0.15)
            dano_atual = int(dano_ataque * multiplicador_combo)
        #---------------------------------------------------------------
            inimigo["vida"] -= dano_ataque
            inimigo["invuln"] = 0.18
            inimigo["atordoado"] = 0.22
            inimigo["estado"] = "atordoado"
            inimigo["empurrao_x"] = direcao * empurrao_ataque
            r.x += inimigo["empurrao_x"]
            inimigo["direcao"] = direcao
            ja_acertou = True
            criar_impacto(r.centerx, r.centery, direcao,
                          pesado=(tipo_ataque == "pesado" or combo >= 3))
            if inimigo["vida"] <= 0:
                criar_impacto(r.centerx, r.centery, direcao, pesado=True)
                inimigos.remove(inimigo)
        # ---> SE FOR O LANÇADOR, JOGA O INIMIGO PARA O ALTO! <---
            if tipo_ataque == "launcher":
                inimigo["vel_y"] = -13.0  # Força do Pulo/Lançamento para cima
                inimigo["no_chao"] = False
            else:
                inimigo["empurrao_x"] = direcao * empurrao_ataque
                r.x += inimigo["empurrao_x"]
                
            inimigo["direcao"] = direcao
            ja_acertou = True
            criar_impacto(r.centerx, r.centery, direcao, pesado=True, roxo=(tipo_ataque == "launcher"))
            
            if inimigo["vida"] <= 0:
                criar_impacto(r.centerx, r.centery, direcao, pesado=True)
                inimigos.remove(inimigo)

    # Fim da onda comum
    if indice_secao < 3 and onda_gerada and not inimigos:
        barreira_ativa = False
        if jogador.centerx >= limite_direito - 90:
            abrir_proxima_secao()

    # Boss final
    if indice_secao == 3 and boss and boss["vida"] > 0 and vida_jogador > 0:
        br = boss["rect"]
        boss["invuln"] = max(0.0, boss["invuln"] - dt)
        boss["recarga"] = max(0.0, boss["recarga"] - dt)
        boss["temporizador"] -= dt
        boss["fase2"] = boss["vida"] <= boss["vida_max"] * 0.5

        dx = jogador.centerx - br.centerx
        boss["direcao"] = 1 if dx > 0 else -1
        if boss["estado"] == "aproximando":
            if abs(dx) > 115:
                br.x += boss["direcao"] * (2.0 if not boss["fase2"] else 2.8)
            else:
                boss["estado"] = "preparando"
                boss["temporizador"] = 0.65 if not boss["fase2"] else 0.45
                boss["ja_acertou"] = False

        elif boss["estado"] == "preparando":
            if boss["temporizador"] <= 0:
                boss["estado"] = "investida"
                boss["temporizador"] = 0.38 if not boss["fase2"] else 0.48
                boss["ja_acertou"] = False

        elif boss["estado"] == "investida":
            br.x += boss["direcao"] * (10 if not boss["fase2"] else 14)
            zona_boss = br.inflate(12, 8)
            if (zona_boss.colliderect(jogador) and not boss["ja_acertou"]
                    and invulnerabilidade_jogador <= 0):
                vida_jogador = max(0, vida_jogador - boss["dano"])
                invulnerabilidade_jogador = 1.0
                boss["ja_acertou"] = True
                jogador.x += boss["direcao"] * 50
                criar_impacto(jogador.centerx, jogador.centery, boss["direcao"], roxo=True)
            if boss["temporizador"] <= 0:
                boss["estado"] = "recuperando"
                boss["temporizador"] = 0.8 if not boss["fase2"] else 0.55

        elif boss["estado"] == "recuperando":
            if boss["temporizador"] <= 0:
                boss["estado"] = "aproximando"
                boss["recarga"] = 0.5

        boss["vel_y"], boss["no_chao"] = atualizar_fisica_personagem(
            br, boss["vel_y"], plataformas
        )
        br.left = max(limite_esquerdo + 40, min(br.left, limite_direito - br.width - 20))

        if (atacando and not ja_acertou and alcance.colliderect(br)
                and boss["invuln"] <= 0):
            dano_final = dano_ataque
            if tipo_ataque == "pesado":
                dano_final += 5
            boss["vida"] = max(0, boss["vida"] - dano_final)
            boss["invuln"] = 0.22
            br.x += direcao * (empurrao_ataque // 3)
            ja_acertou = True
            criar_impacto(br.centerx, br.centery, direcao,
                          pesado=(tipo_ataque == "pesado"), roxo=True)
            if boss["vida"] <= 0:
                criar_impacto(br.centerx, br.centery, direcao, pesado=True, roxo=True)
                jogo_vencido = True
                mensagem = "BOSS DERROTADO!"
                tempo_mensagem = 5.0

    # Dano de contato apenas se nenhum ataque do inimigo estiver acertando
    # (os inimigos comuns causam dano na finalizacao de seu ataque, nao por contato).

    if invulnerabilidade_jogador > 0:
        invulnerabilidade_jogador = max(0.0, invulnerabilidade_jogador - dt)

    if tempo_mensagem > 0:
        tempo_mensagem -= dt

    # Camera segue o jogador
    camera_x = max(0, min(jogador.centerx - LARGURA // 2, MUNDO_LARGURA - LARGURA))

    atualizar_particulas()

    # =====================================================
    # 7. DESENHO
    # =====================================================
    tela.fill(PRETO)

    # Fundo em camadas para dar sensacao de profundidade
    for i in range(18):
        x_mundo = i * 260
        x_tela = int(x_mundo - camera_x * 0.35)
        if -80 <= x_tela <= LARGURA + 80:
            pygame.draw.rect(tela, (24, 23, 38), (x_tela, 150, 95, 300))
            pygame.draw.polygon(tela, (35, 25, 48), [
                (x_tela - 25, 150), (x_tela + 45, 75), (x_tela + 120, 150)
            ])
            pygame.draw.rect(tela, (45, 25, 48), (x_tela + 28, 220, 12, 100))

    # Pontos de luz
    for x in range(30, LARGURA, 80):
        pygame.draw.circle(tela, (45, 35, 58),
                           (x, 100 + (x % 3) * 25), 3)

    # Chao visivel
    chao_visivel = pygame.Rect(-camera_x, CHAO_Y, MUNDO_LARGURA, ALTURA - CHAO_Y)
    pygame.draw.rect(tela, CINZA, chao_visivel)
    pygame.draw.line(tela, CINZA_CLARO, (0, CHAO_Y), (LARGURA, CHAO_Y), 3)

    # Plataformas
    for p in plataformas:
        if -200 < p.x - camera_x < LARGURA + 200:
            ps = retangulo_tela(p, camera_x)
            pygame.draw.rect(tela, CINZA, ps)
            pygame.draw.line(tela, AZUL, ps.topleft, ps.topright, 3)
            for x in range(ps.left + 15, ps.right, 35):
                pygame.draw.line(tela, CINZA_CLARO, (x, ps.y + 5), (x + 10, ps.y + 5), 2)

    # Barreiras das areas
    if barreira_ativa and indice_secao < 3:
        bx = int(secao_atual["fim"] - camera_x)
        if -30 <= bx <= LARGURA + 30:
            pygame.draw.rect(tela, ROXO_ESCURO, (bx - 8, 150, 16, 300))
            for yy in range(160, 450, 35):
                pygame.draw.line(tela, ROXO, (bx - 8, yy), (bx + 8, yy + 15), 3)

    # Jogador
    desenhar_jogador = (invulnerabilidade_jogador <= 0
                         or int(pygame.time.get_ticks() / 100) % 2 == 0)
    jogador_tela = retangulo_tela(jogador, camera_x)
    if desenhar_jogador:
        pygame.draw.rect(tela, VERMELHO, jogador_tela)

    # Projéteis

    for tiro in projetis:

        pygame.draw.rect(
            tela,
            AZUL,
            retangulo_tela(
                tiro["rect"],
                camera_x
            )
        )

    # Ataque visivel
    alcance_tela = retangulo_tela(alcance, camera_x)
    if atacando:
        cor_ataque = LARANJA if tipo_ataque == "pesado" else AMARELO
        pygame.draw.rect(tela, cor_ataque, alcance_tela,
                         4 if tipo_ataque == "pesado" else 2)

    # Inimigos
    for inimigo in inimigos:
        r = inimigo["rect"]
        cor = BRANCO if inimigo["invuln"] > 0 else (
            LARANJA if inimigo["tipo"] == "forte" else (170, 55, 65))
        rs = retangulo_tela(r, camera_x)
        pygame.draw.rect(tela, cor, rs)
        barra_vida(rs.x, rs.y - 15, rs.width, 7, inimigo["vida"], inimigo["vida_max"])
        if inimigo["estado"] == "preparando":
            pygame.draw.circle(tela, AMARELO, (rs.centerx, rs.top - 22), 7)
            largura_aviso = 76 if inimigo["tipo"] == "normal" else 94
            aviso_ataque = pygame.Rect(0, 0, largura_aviso, 62)
            if inimigo["direcao"] == 1:
                aviso_ataque.midleft = (rs.right, rs.centery)
            else:
                aviso_ataque.midright = (rs.left, rs.centery)
            pygame.draw.rect(tela, AMARELO, aviso_ataque, 2)
    
    # Encontrar o inimigo mais próximo para a mira
    inimigo_alvo = None
    menor_distancia = 250  # Raio máximo de alcance da mira (em pixels)

    for inimigo in inimigos:
        distancia = abs(jogador.centerx - inimigo["rect"].centerx)
        if distancia < menor_distancia:
            menor_distancia = distancia
            inimigo_alvo = inimigo

    # Se houver um inimigo na mira, desenha um indicador sobre ele
    if inimigo_alvo and inimigo_alvo["vida"] > 0:
        rs_alvo = retangulo_tela(inimigo_alvo["rect"], camera_x)
        # Desenha um triângulo ou marcador de mira no topo do inimigo
        pygame.draw.polygon(tela, AMARELO, [
            (rs_alvo.centerx, rs_alvo.top - 12),
            (rs_alvo.centerx - 6, rs_alvo.top - 22),
            (rs_alvo.centerx + 6, rs_alvo.top - 22)
        ])
    
    # Boss
    if indice_secao == 3 and boss and boss["vida"] > 0:
        brs = retangulo_tela(boss["rect"], camera_x)
        cor_boss = BRANCO if boss["invuln"] > 0 else (
            (190, 45, 75) if not boss["fase2"] else ROXO)
        pygame.draw.rect(tela, cor_boss, brs)
        # Olhos
        olho_x = brs.centerx + (18 * boss["direcao"])
        pygame.draw.circle(tela, AMARELO, (olho_x, brs.y + 35), 8)
        # Barra do boss no topo
        texto_boss = fonte.render("ABOMINACAO", True, BRANCO)
        tela.blit(texto_boss, (LARGURA // 2 - texto_boss.get_width() // 2, 78))
        barra_vida(LARGURA // 2 - 220, 102, 440, 20,
                   boss["vida"], boss["vida_max"], ROXO if boss["fase2"] else VERMELHO)
        if boss["estado"] == "preparando":
            aviso = fonte.render("CUIDADO!", True, AMARELO)
            tela.blit(aviso, (brs.centerx - aviso.get_width() // 2, brs.y - 30))

    desenhar_particulas(camera_x)

    # Interface
    pygame.draw.rect(tela, VERMELHO_ESCURO, (20, 55, 200, 20))
    largura_barra = int(200 * vida_jogador / vida_maxima_jogador)
    if largura_barra > 0:
        pygame.draw.rect(tela, VERDE, (20, 55, largura_barra, 20))
    pygame.draw.rect(tela, BRANCO, (20, 55, 200, 20), 1)
    tela.blit(fonte.render(f"VIDA: {vida_jogador}/{vida_maxima_jogador}", True, BRANCO), (20, 80))
    tela.blit(fonte.render("A/D: mover | ESPACO: pular | J: leve | K: pesado | Encadeie ataques!", True, BRANCO), (20, 20))
    if combo > 0 and tempo_combo > 0:
        cor_combo = AMARELO if combo < 3 else LARANJA
        texto_combo = fonte_media.render(f"COMBO x{combo}  +{int((multiplicador_combo - 1) * 100)}% DANO", True, cor_combo)
        tela.blit(texto_combo, (20, 145))
        pygame.draw.rect(tela, CINZA, (20, 185, 150, 7))
        pygame.draw.rect(tela, AMARELO, (20, 185, int(150 * tempo_combo / janela_combo), 7))

    nome_secao = secoes[indice_secao]["nome"]
    texto_secao = fonte.render(nome_secao, True, AZUL)
    tela.blit(texto_secao, (LARGURA - texto_secao.get_width() - 20, 20))

    if barreira_ativa and indice_secao < 3:
        texto_objetivo = fonte.render(f"Derrote os inimigos: {len(inimigos)} restantes", True, BRANCO)
        tela.blit(texto_objetivo, (20, 115))
    elif indice_secao < 3:
        tela.blit(fonte.render("Area liberada! Avance para a direita.", True, VERDE), (20, 115))

    if tempo_mensagem > 0 and mensagem:
        texto_central(mensagem, 150, AMARELO, fonte_media)

    if vida_jogador <= 0:
        texto_central("GAME OVER", ALTURA // 2 - 15, VERMELHO, fonte_grande)
        texto_central("Pressione 'R' ou ESPAÇO para Renascer", ALTURA // 2 + 35, BRANCO, fonte)

    if jogo_vencido:
        texto_central("BOSS DERROTADO!", ALTURA // 2 - 20, AMARELO, fonte_grande)
        texto_central("Pressione 'R' ou ESPAÇO para Jogar Novamente", ALTURA // 2 + 30, BRANCO, fonte_media)

    pygame.display.flip()

pygame.quit()
sys.exit()
