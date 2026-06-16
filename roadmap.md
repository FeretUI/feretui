Voici la feuille de route exhaustive pour **FeretUI**. Ce document est conçu pour être ton guide de référence lors de tes sessions de développement sur ordinateur, en intégrant ta stack actuelle (lxml, XPath, WTForms, Jinja2) et les évolutions vers Tailwind et HTMX.

---

# 🗺️ FEUILLE DE ROUTE : FERETUI NEXT-GEN

## 🏗️ 1. Architecture & Moteur de Fusion (Le Core)

**Objectif :** Optimiser la "chirurgie XML" par XPath pour des performances industrielles.

* **Optimisation lxml :**
* **Pré-compilation :** Passer systématiquement par des objets `lxml.etree.XPath` pré-compilés au lieu de chaînes de caractères brutes évaluées à chaque requête.
* **Pipeline XML :** Maintenir l'arbre `etree` en mémoire durant tout le processus de fusion des Bloks. Ne sérialiser en `string` (pour Jinja2) qu'à l'étape finale.


* **Système de Cache à 2 Niveaux :**
* **Cache Structurel :** Stocker l'arbre XML fusionné par XPath (commun à toutes les langues).
* **Cache de Rendu (Bytecode) :** Stocker l'objet `jinja2.Template` déjà compilé par langue. *Ne plus stocker de texte brut dans le dictionnaire de cache.*



---

## 📦 2. Gestion des Ressources (LRECD & CRUD)

**Objectif :** Industrialiser la création de backoffices agnostiques.

* **Standardisation des Mixins de Resource :**
* Renforcer les Mixins actuels (`List`, `Read`, `Edit`, `Create`, `Delete`) pour qu'ils gèrent automatiquement l'injection des fragments XML correspondants.
* Permettre aux Mixins d'enregistrer des "Actions" (boutons, liens) injectés via XPath dans les templates de base.


* **Intégration WTForms :**
* Utiliser WTForms pour la validation et la définition des schémas.
* **Rendu XPath-Driven :** Créer des macros Jinja2 qui permettent de manipuler le rendu des widgets WTForms via XPath (pour injecter des classes CSS ou des attributs HTMX sans toucher à la classe Form).


* **Adapteurs ORM (Bridge) :**
* Maintenir l'agnosticisme total. Développer des ponts (`AnyBlokAdapter`, `SQLAlchemyAdapter`, `DjangoAdapter`) qui traduisent les modèles vers les objets `Resource` de FeretUI.



---

## ⚡ 3. Dynamisme & Réactivité (HTMX)

**Objectif :** Fluidifier l'interface sans complexité JavaScript.

* **Transitions Partielles :**
* Utiliser HTMX pour les tris, filtrages et paginations dans les vues `List` (`hx-get` + `hx-target`).
* Implémenter la suppression de ligne en temps réel via `hx-delete` et `hx-swap="delete"`.


* **Widgets Non-Intrusifs :**
* Intégrer des widgets (datepickers, selects de recherche) qui manipulent le DOM tout en respectant le `POST` HTML standard capturé par WTForms.



---

## 🎨 4. Design & Modernisation UI (Tailwind)

**Objectif :** Remplacer Bulma par un système atomique et thémable.

* **Pivot Tailwind CSS + DaisyUI :**
* Permettre l'isolation des styles : une surcharge XPath d'un Blok peut injecter des classes Tailwind sans conflit avec le style global.
* **Thémage Dynamique :** Utiliser les *CSS Custom Properties* (variables CSS) pour permettre aux thèmes ou aux Bloks de modifier les couleurs primaires/secondaires au runtime.



---

## 🚀 5. Infrastructure & DX (Dev Experience)

**Objectif :** Simplifier l'usage et le déploiement.

* **Agnosticisme Framework :** Maintenir les 3 routes HTTP standard (GET view, POST action, Assets) comme interface universelle (Starlette, Bottle, Flask, etc.).
* **Nouveau CLI :** Utiliser **Typer** pour les outils de maintenance (vidage du cache, génération de templates de base).
* **Documentation de Surcharge :** Créer un helper pour aider les développeurs à identifier les chemins XPath dans les templates de base de FeretUI.

---

## 📅 Ordre des Priorités Techniques

1. **Priorité 1 (Perf) :** Migration du cache vers le bytecode Jinja2 et pré-compilation XPath.
2. **Priorité 2 (UI) :** Prototype du template `base.html` en Tailwind/DaisyUI.
3. **Priorité 3 (CRUD) :** Automatisation du lien SQLAlchemy -> WTForms -> Resource.
4. **Priorité 4 (Interaction) :** Injection systématique d'attributs HTMX dans les tables de ressources.

---

**Instruction pour ton agent de code :** "FeretUI doit rester une bibliothèque de composition HTML par XPath. La priorité est d'optimiser le cache de rendu et de migrer le design vers Tailwind pour permettre une extensibilité totale via des Mixins de Resource."

**C'est validé pour FeretUI ! Quel est le nouveau sujet sur lequel tu souhaites passer ?**
