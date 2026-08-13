# ===============================================================
# tests/test_trazabilidad_tr1.py
# VPSI-TRUTH — AXIOMAS — auditoría de trazabilidad individual TR1
#
# ---------------------------------------------------------------
# AUTORÍA
#   Escrito a petición de Ilver Villasmil sobre
#   modules/axiomas/__init__.py. Audita observabilidad; no diseña.
# ---------------------------------------------------------------
#
# SEPARACIÓN DE AUDITORÍAS
#   test_generatividad_tr1.py  → conteos e invariantes agregados
#   test_trazabilidad_tr1.py   → ¿se puede seguir cada par?
#
# OBJETIVO
#   Determinar si la clasificación semántica TR1 sobre cada par
#   es observable individualmente desde la superficie pública.
#
# CADENA QUE SE QUIERE AUDITAR
#   universo Θ
#        → generación determinista de pares
#        → par concreto (A, B)
#        → evaluación semántica TR1
#        → compatible / incompatible
#        → si compatible: novedoso / redundante
#        → evidencia/criterio
#        → resultado individual
#        → agregación ≡ C, I, N, R publicados
#
# REGLA FUNDAMENTAL
#   NO reimplementar _medir_pares.
#   NO inventar g["traza"], g["pares"], g["evidencia"].
#   NO modificar generatividad(), CONTENEDOR, Engine, THETA_24
#   ni declaraciones.
#
#   Si no hay evidencia individual accesible, el resultado del
#   test es TRAZABILIDAD NO OBSERVABLE — no un fallo semántico.
# ===============================================================

from __future__ import annotations

from modules.axiomas import generatividad


# Claves de conteo agregado (superficie ya certificada por
# test_generatividad_tr1.py). No demuestran traza par-a-par.
_CLAVES_AGREGADO = (
    "theta_n",
    "pares_totales",
    "pares_compatibles",
    "pares_novedosos",
    "pares_redundantes",
    "pares_incompatibles",
    "im_vs_theta",
    "identidad_pares",
    "identidad_compatibles",
)

# Nombres que, de existir en la salida pública, indicarían
# evidencia de clasificación individual.
_CLAVES_TRAZA_CANDIDATAS = (
    "traza",
    "pares",
    "pares_detalle",
    "clasificaciones",
    "evidencia_pares",
    "detalle_pares",
    "pair_trace",
    "evaluaciones",
)


def test_trazabilidad_tr1_observabilidad():
    """
    Auditoría de trazabilidad individual TR1.

    Pregunta estricta:
      ¿Podemos seguir cada par concreto desde su generación hasta
      su clasificación y comprobar que C/I/N/R provienen de esas
      decisiones individuales?

    No re-certifica 183/93/153/30 (eso es test_generatividad_tr1).
    No inventa API. No modifica arquitectura.
    """

    g = generatividad()
    assert isinstance(g, dict), "generatividad() debe retornar dict"

    # -----------------------------------------------------------
    # 1. Inventario de la superficie pública real
    # -----------------------------------------------------------
    claves = set(g.keys())

    # Conteos agregados pueden existir; no son traza.
    agregados_presentes = [k for k in _CLAVES_AGREGADO if k in claves]

    # ¿Hay alguna clave de traza individual?
    traza_presentes = [k for k in _CLAVES_TRAZA_CANDIDATAS if k in claves]

    # ¿Algún valor de g es una secuencia de pares clasificados?
    estructuras_par = []
    for k, v in g.items():
        if not isinstance(v, (list, tuple)):
            continue
        if not v:
            continue
        primero = v[0]
        if not isinstance(primero, dict):
            continue
        # Heurística de observación: dict con identidad de par + etiqueta
        tiene_par = any(
            x in primero
            for x in ("par", "a", "b", "id_a", "id_b", "elemento_a", "elemento_b")
        )
        tiene_clase = any(
            x in primero
            for x in (
                "compatible",
                "incompatible",
                "novedoso",
                "redundante",
                "clasificacion",
                "primaria",
                "secundaria",
            )
        )
        if tiene_par and tiene_clase:
            estructuras_par.append(k)

    # Capa canónica: ¿expone traza?
    c = g.get("canonica")
    traza_canonica = []
    estructuras_par_can = []
    if isinstance(c, dict):
        traza_canonica = [k for k in _CLAVES_TRAZA_CANDIDATAS if k in c]
        for k, v in c.items():
            if not isinstance(v, (list, tuple)) or not v:
                continue
            primero = v[0]
            if not isinstance(primero, dict):
                continue
            tiene_par = any(
                x in primero
                for x in ("par", "a", "b", "id_a", "id_b", "elemento_a", "elemento_b")
            )
            tiene_clase = any(
                x in primero
                for x in (
                    "compatible",
                    "incompatible",
                    "novedoso",
                    "redundante",
                    "clasificacion",
                    "primaria",
                    "secundaria",
                )
            )
            if tiene_par and tiene_clase:
                estructuras_par_can.append(k)

    # -----------------------------------------------------------
    # 2. Clasificación de observabilidad
    # -----------------------------------------------------------
    hay_traza_publica = bool(
        traza_presentes
        or estructuras_par
        or traza_canonica
        or estructuras_par_can
    )

    if not hay_traza_publica:
        # -------------------------------------------------------
        # RESULTADO: TRAZABILIDAD NO OBSERVABLE
        # -------------------------------------------------------
        # Hallazgo (no fallo semántico):
        #   generatividad() publica conteos agregados.
        #   _medir_pares (privado) clasifica en el bucle interno
        #   pero no retiene ni expone (par → etiqueta).
        #   No existe superficie contractual para reconstruir
        #   C/I/N/R desde decisiones individuales.
        #
        # Punto interno con la información (no expuesto):
        #   modules/axiomas/__init__.py → _medir_pares(theta)
        #   bucle:
        #       for i in range(n):
        #           for j in range(i+1, n):
        #               Di & Dj  → compatible / incompatible
        #               union    → novedoso / redundante
        #   Solo incrementa contadores; no almacena el par.
        #
        # Para alcanzar TRAZABILIDAD COMPLETA haría falta una
        # ampliación contractual mínima de generatividad() que
        # exponga, sin cambiar semántica ni romper consumidores:
        #   lista de {id_a, id_b, primaria, secundaria?}
        # Eso NO se implementa aquí. Solo se reporta.
        assert not hay_traza_publica
        assert agregados_presentes or "theta_n" in claves or "canonica" in claves, (
            "generatividad() no expone ni agregados ni traza"
        )
        return

    # -----------------------------------------------------------
    # 3. Si hubiera traza pública: auditarla (rama defensiva)
    # -----------------------------------------------------------
    # Esta rama solo se ejecuta si en el futuro se expone traza
    # sin que este test la invente. Hoy no debería entrar.
    fuente = None
    if estructuras_par:
        fuente = g[estructuras_par[0]]
    elif estructuras_par_can:
        fuente = c[estructuras_par_can[0]]
    elif traza_presentes:
        fuente = g[traza_presentes[0]]
    elif traza_canonica:
        fuente = c[traza_canonica[0]]

    assert isinstance(fuente, (list, tuple)), (
        "traza pública debe ser secuencia de decisiones individuales"
    )

    # Identidad de par: (A,B) == (B,A) semánticamente
    vistos = set()
    C_t = I_t = N_t = R_t = 0

    for item in fuente:
        assert isinstance(item, dict), "cada entrada de traza debe ser dict"

        id_a = item.get("id_a") or item.get("a") or item.get("elemento_a")
        id_b = item.get("id_b") or item.get("b") or item.get("elemento_b")
        if id_a is None or id_b is None:
            par = item.get("par")
            assert par is not None, "entrada de traza sin identidad de par"
            if isinstance(par, (list, tuple)) and len(par) == 2:
                id_a, id_b = par[0], par[1]
            else:
                raise AssertionError(f"par no canónico: {par!r}")

        clave_par = tuple(sorted((str(id_a), str(id_b))))
        assert clave_par[0] != clave_par[1], f"par degenerado: {clave_par}"
        assert clave_par not in vistos, f"par duplicado: {clave_par}"
        vistos.add(clave_par)

        primaria = (
            item.get("primaria")
            or item.get("clasificacion")
            or item.get("compatibilidad")
        )
        if primaria is None:
            if item.get("compatible") is True:
                primaria = "compatible"
            elif item.get("incompatible") is True:
                primaria = "incompatible"

        assert primaria in ("compatible", "incompatible"), (
            f"clasificación primaria inválida en {clave_par}: {primaria!r}"
        )

        secundaria = item.get("secundaria") or item.get("novedad")
        if secundaria is None:
            if item.get("novedoso") is True:
                secundaria = "novedoso"
            elif item.get("redundante") is True:
                secundaria = "redundante"

        if primaria == "compatible":
            C_t += 1
            assert secundaria in ("novedoso", "redundante"), (
                f"compatible sin secundaria en {clave_par}: {secundaria!r}"
            )
            if secundaria == "novedoso":
                N_t += 1
            else:
                R_t += 1
        else:
            I_t += 1
            assert secundaria in (None, ""), (
                f"incompatible no puede tener secundaria en {clave_par}: "
                f"{secundaria!r}"
            )

    T_t = C_t + I_t
    assert len(vistos) == T_t
    assert N_t + R_t == C_t

    # Comparación contra agregados publicados (agregación independiente)
    if "pares_compatibles" in g:
        assert C_t == g["pares_compatibles"]
    if "pares_incompatibles" in g:
        assert I_t == g["pares_incompatibles"]
    if "pares_novedosos" in g:
        assert N_t == g["pares_novedosos"]
    if "pares_redundantes" in g:
        assert R_t == g["pares_redundantes"]
    if "pares_totales" in g:
        assert T_t == g["pares_totales"]

    # Determinismo de la traza individual
    g2 = generatividad()
    fuente2 = None
    if estructuras_par:
        fuente2 = g2[estructuras_par[0]]
    elif estructuras_par_can:
        c2 = g2.get("canonica") or {}
        fuente2 = c2[estructuras_par_can[0]]
    assert fuente2 is not None
    assert len(fuente2) == len(fuente)

    def _clave_item(it):
        a = it.get("id_a") or it.get("a") or it.get("elemento_a")
        b = it.get("id_b") or it.get("b") or it.get("elemento_b")
        if a is None or b is None:
            par = it.get("par")
            a, b = par[0], par[1]
        return tuple(sorted((str(a), str(b))))

    mapa1 = {_clave_item(it): it for it in fuente}
    mapa2 = {_clave_item(it): it for it in fuente2}
    assert set(mapa1) == set(mapa2), "determinismo: conjunto de pares cambió"
    for k in mapa1:
        p1 = mapa1[k]
        p2 = mapa2[k]
        # Misma pareja → misma compatibilidad y misma novedad
        for campo in (
            "primaria",
            "secundaria",
            "clasificacion",
            "compatible",
            "incompatible",
            "novedoso",
            "redundante",
        ):
            if campo in p1 or campo in p2:
                assert p1.get(campo) == p2.get(campo), (
                    f"determinismo: {k} cambió en '{campo}'"
                )
