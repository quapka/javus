Repository description
----------------------
This repository consists of the code, materials and diploma thesis sources.

Diploma thesis topic
--------------------
The current topic of the thesis is: Security analysis of JavaCard Virtual Machine

And the topic description is (in Czech):

Předběžné zadání:
Cílem práce je provést přehled známých útoků na vykonání kódu v rámci virtuálního stroje platformy JavaCard a vytvořit automatizovaný bezpečnostní testovací nástroj analyzující (ne)použitelnost těchto útoků na aktuálních čipových kartách. Útoky mohou být např. založeny na nedokonalé kontrole typů operandů (např. předaných přes Shareable interface), záměrnou modifikací bytecode karetní aplikace před nahráním na kartu nebo nedostatečné separace paměťového prostoru.
Práce pokryje tyto konkrétní kroky:

    Popis provádění kódu aplikace v rámci JavaCard RE a seznam známých bezpečnostních opatření.
    Rešerše publikovaných úroků na JavaCard RE.
    Sběr a spuštění existujících implementací kódu testujících přítomnost potenciálních zranitelností.
    Vytvoření automatizované aplikace pro test (ne)možnosti provádět potenciálně problematické operace.
    Pokus o návrh vlastních útoků na JavaCard RE a jejich případná integrace do testovacího nástroje.
    Vyhodnocení na vybraných reálných kartách.

TODOs
-----
- since each attack will have it's own applet (therefore an AID) we should have a reasonable way of assigning RIDs and PIXs
    - one RID is enough
    - PIX based on type of attack?

- categorize the attacks

General notes from meetings
---------------------------

vynechat Connected
attack using side effects - multiple calls
apdu buffer object
 - write to apdu in one applet and read them in
catching various exceptions

let Petr send the diploma thesis related to the topic

Trello board
- papers: abstracts
- tools
